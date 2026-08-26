export const meta = {
  name: 'senior-review',
  description: 'Senior-grade multi-agent code review, token-budgeted. Code is gathered ONCE by the main loop and passed inline (agents do not re-explore), verification is BATCHED (one pass judges all findings), and the whole pipeline scales to diff size (lite / standard / deep). The enemy is context-blindness, not triviality — context-grounded small findings are kept as non-blocking nits; context-blind findings are killed regardless of size. Returns a structured, verified, calibrated review object for the main loop to render into the HTML template.',
  phases: [
    { title: 'Context', detail: 'one shared intent + architecture + convention map from the inline code (front-loaded constraints)' },
    { title: 'Review', detail: 'independent multi-lens reviewers over inline code (count scales with diff size)' },
    { title: 'Sweep', detail: 'completeness critic — only for standard/deep, capped, stops on consecutive dry rounds' },
    { title: 'Verify', detail: 'BATCHED adversarial verification — one pass judges every finding; deep mode runs two for independence' },
    { title: 'Calibrate', detail: 'moderator dedups, separates blocking vs non-blocking, orders design-first, adds praise' },
  ],
}

// ── args (gathered ONCE by the skill's main loop — agents must NOT re-fetch) ──
// {
//   kind, title, number, repo, prUrl, base, head, headSha, projectRoot,
//   scenario,                             // 'peer-pr' | 'pre-submit' | 'wip' | 'audit' — who the review is for
//   changedFiles: [string],
//   additions, deletions,                 // for size classification
//   diffText: string,                     // full unified diff (git/gh), gathered once
//   files: [{ path, content }],           // line-numbered FULL content of changed files, gathered once
//   prBody, commits, existingComments, linkedIssue,
//   mode,                                 // optional override: 'lite' | 'standard' | 'deep'
//   truncatedFiles: [string],             // files whose content was capped (agents may Read these on demand)
// }
// args may arrive as a parsed object OR as a JSON-encoded string (harness-dependent).
// Parse defensively — otherwise A.additions/changedFiles/bundlePath are all undefined,
// which silently collapses size-classification to 'lite' and disables inline code.
let A = args || {}
if (typeof A === 'string') { try { A = JSON.parse(A) } catch (_) { A = {} } }
const FILES = A.files || []

// ── Review SCENARIO: who the review is FOR and what question it answers. ──────
// Orthogonal to target kind (pr/branch/path) and size mode (lite/standard/deep).
// This is what stops every review from coming out shaped like a third-party PR
// verdict ("approve / 머지 가능") when the user actually asked for a pre-submit
// self-check, a mid-development direction check, or a plain code analysis.
const SCENARIO = ['peer-pr', 'pre-submit', 'wip', 'audit'].includes(A.scenario) ? A.scenario
  : (A.kind === 'pr' ? 'peer-pr' : A.kind === 'path' ? 'audit' : 'pre-submit')
const SCN = {
  'peer-pr': {
    framing: `A submitted PR by another author is under review before merge. Reader = the PR author. Verdict question: "should this be merged?" Judge the change as submitted; respect the author's stated intent per the doctrine.`,
    verdicts: ['approve', 'approve-with-nits', 'comment', 'request-changes'],
    blockingVerdict: 'request-changes', softVerdict: 'comment',
    roiFrame: `Is the approach proportional to the problem? Was the change worth its size/complexity vs a smaller alternative? Does it meet the requester's intent?`,
    validityFrame: `PR-level axes (problem↔solution fit, change-size justification, ROI, requester-intent fit, simpler-alternative, hidden cost)`,
  },
  'pre-submit': {
    framing: `The AUTHOR is checking their OWN work before opening a PR. Reader = the author themself. Verdict question: "is this ready to submit, and what will reviewers flag?" Do NOT role-play merge authority — no approve/request-changes language, no "can be merged". Frame every finding as a pre-submit action: fix now / preempt (defensible trade-off, but explain it in the PR description BEFORE a reviewer asks) / fine as-is. Predicting what a human reviewer will push back on is first-class output. The intent doctrine FLIPS here: the question is not "respect the author's intent" (the author is the reader) but "is that intent VISIBLE from the code/commits alone?" — invisible intent WILL be questioned downstream, so point at where to make it explicit.`,
    verdicts: ['ready', 'ready-with-notes', 'needs-work'],
    blockingVerdict: 'needs-work', softVerdict: 'ready-with-notes',
    roiFrame: `Will this survive review as-is? Is the change-size defensible, or should it be split into smaller PRs? Which decisions need preemptive justification in the PR description?`,
    validityFrame: `submission-readiness axes (scope coherence — one PR one purpose, change-size defensibility / split-worthiness, intent visibility, reviewer burden)`,
  },
  wip: {
    framing: `Mid-development direction check — the code is NOT finished and the author KNOWS it. Reader = the author themself. Verdict question: "is the direction right, before more code gets stacked on it?" Design/architecture findings outrank everything (they are cheapest to fix NOW). Do NOT flag obvious incompleteness (TODOs, missing tests, stub error handling, debug prints) as defects — raise it only if the half-built shape suggests the FINAL shape will be wrong, and label it \`question\`. Polish-level nits are low-value at this stage; report only the ones that will be harder to fix later.`,
    verdicts: ['on-track', 'adjust-course', 'rethink'],
    blockingVerdict: 'rethink', softVerdict: 'adjust-course',
    roiFrame: `Is the chosen direction proportional to the problem? Is there a simpler path still available NOW, before more code accumulates on this foundation?`,
    validityFrame: `direction axes (problem↔approach fit, foundation soundness — what gets expensive if this continues, simpler-alternative-still-available)`,
  },
  audit: {
    framing: `An EXISTING codebase/scope is being analyzed — there is no diff and no author awaiting a merge verdict. Reader = whoever maintains or must understand this code. Verdict question: "how healthy is this code, where are the risks, what should improve first?" Replace the "author intent" doctrine with HISTORICAL CONTEXT: code may predate current conventions or encode constraints that no longer apply — judge by today's carrying cost and risk, not by "I'd write it differently today". Prioritize by risk × blast-radius. Structural observations — including GOOD structure worth preserving — are first-class output, not just defects.`,
    verdicts: ['healthy', 'healthy-with-debt', 'needs-attention', 'at-risk'],
    blockingVerdict: 'needs-attention', softVerdict: 'healthy-with-debt',
    roiFrame: `Where does maintenance cost concentrate? Which debt is worth paying down first (risk × change-frequency), and which is fine to leave?`,
    validityFrame: `health axes (architecture fitness for current requirements, risk concentration, debt worth paying vs leaving, test/doc coverage of the riskiest paths)`,
  },
}[SCENARIO]

// Size signal: PRs/branches give additions+deletions; an audit has no diff, so
// fall back to total inlined line count (otherwise it silently misclassifies as lite).
const estLines = FILES.reduce((n, f) => n + ((f.content || '').split('\n').length), 0)
const changedLines = ((A.additions || 0) + (A.deletions || 0)) || (A.diffText ? 0 : estLines)
const nFiles = (A.changedFiles || A.files || []).length

// Size classification → scales agent count (the real cost driver) to the change size.
// lite is DEMOTED: it proved too shallow to catch correctness blockers, so it now only
// triggers for truly trivial / non-correctness changes (tiny edits, docs, config). Any
// real code change of meaningful size goes to standard (the floor for correctness review).
const MODE = A.mode || (
  (changedLines <= 40 && nFiles <= 2) ? 'lite'
  : (changedLines <= 600 && nFiles <= 15) ? 'standard'
  : 'deep'
)
const CFG = {
  lite:     { sweepRounds: 0, verifiers: 1 },   // trivial/doc PRs only
  standard: { sweepRounds: 1, verifiers: 2 },   // 2 verifiers — restores severity calibration (kills over-severe T1s)
  deep:     { sweepRounds: 2, verifiers: 2 },
}[MODE]

log(`scenario=${SCENARIO}, mode=${MODE} (${changedLines} lines, ${nFiles} files) → sweepRounds=${CFG.sweepRounds}, verifiers=${CFG.verifiers}`)

// ── Stability guard ①: fail LOUD on missing inputs instead of silently degrading.
// (The 'lite-misfire' incident came from args arriving as a string → everything undefined
//  → silent blind review. Surface these conditions so the run is never quietly worthless.)
const hasCode = !!(A.bundlePath || A.diffText || FILES.length)
if (!hasCode) {
  log('⚠ STABILITY WARNING: no code source in args (bundlePath / diffText / files all empty). Agents will have NO code to review — the run is likely worthless. The main loop must pass a bundlePath or inline diff. Aborting-degraded: continuing only so the failure is visible in output.')
}
if (A.additions == null && A.deletions == null && !(A.changedFiles || []).length && !FILES.length) {
  log('⚠ STABILITY WARNING: no size signal (additions/deletions/changedFiles/files) → mode auto-detection may be wrong. Pass additions+deletions, files[], or an explicit mode.')
}

// ── The code, inlined ONCE. This is the single biggest token lever: agents read
//    from here instead of each running git/Read/grep (which multiplied turns × context). ──
const truncNote = (A.truncatedFiles && A.truncatedFiles.length)
  ? `\n> NOTE: these files were too large to inline fully and are truncated to the changed regions: ${A.truncatedFiles.join(', ')}. You MAY Read them on demand if a finding hinges on an unshown part.`
  : ''
// Two delivery modes, both avoiding per-agent exploration:
//  (a) inline   — diffText + files[] embedded in the prompt (best token efficiency).
//  (b) bundlePath — a single local file (diff + all changed files) read ONCE per agent
//                   (keeps the main-loop tool call small for big PRs).
const FORBID = '**Do NOT run `git`/`gh`/`grep` or browse the repo, and do NOT read the changed files individually.** Re-fetching/exploring is the #1 token waste and is forbidden. The ONLY exception: if a finding genuinely hinges on an UNCHANGED file (a caller/callee not provided), you may Read that single file once — and say so.'
let CODE
if (A.diffText || FILES.length) {
  CODE = [
    '## The change under review — ALL the code you need is inline below.', FORBID, '',
    '### Unified diff (what this PR changed vs base)', '```diff',
    (A.diffText || '(diff not provided)').slice(0, 200000), '```', '',
    '### Full content of changed files (line-numbered current state)' + truncNote,
    ...FILES.map((f) => `\n#### ${f.path}\n\`\`\`\n${f.content}\n\`\`\``),
  ].join('\n')
} else if (A.bundlePath) {
  CODE = [
    '## The change under review',
    `**Read this ONE local file EXACTLY ONCE — it contains the full unified diff plus the line-numbered full content of every changed file:** \`${A.bundlePath}\``,
    FORBID,
  ].join('\n')
} else {
  CODE = '## The change under review\n(No code provided in args — fall back to reading the diff once via the target JSON, but do not explore further.)'
}

const GROUND = `## Review scenario — ${SCENARIO} (this shapes EVERY judgment and every word you write)
${SCN.framing}

## OUTPUT LANGUAGE — 한국어 (non-negotiable)
Every natural-language field VALUE you output (problem, statedIntent, architecture, priorDecisionConflict, conventions, openQuestions, title, recommendation, plainTalk, impact, summary, designValidity prose, praise, etc.) MUST be written in Korean. If the PR body / code comments / source material are in English, translate the MEANING into natural Korean prose — never copy English sentences verbatim into a field value. Keep verbatim only: code, identifiers, file paths, JSON keys, and fixed enum/label tokens (severity/action/label values like \`critical\`, \`required\`, \`issue\`). This deliverable is a Korean review document; an English field value is a defect.

## Review target
\`\`\`json
${JSON.stringify({ ...A, diffText: undefined, files: undefined }, null, 2)}
\`\`\`

${CODE}

## Project rules
Read root + nested \`CLAUDE.md\`, \`README\`, \`CONVENTIONS.md\`/\`CONTRIBUTING.md\` ONLY IF you need a convention to judge a specific finding — these are the few files worth a Read. Do not browse the repo.

## Non-negotiable review doctrine (front-loaded — read before judging)
1. Judge from a **traced data/control flow**, never from the surface shape of a line. Before writing "this could break", trace whether the bad input is actually reachable in the code shown. Unconfirmed reachability ⇒ label \`question\`, never \`issue\`.
2. **Respect author intent** (as adapted by the scenario above — pre-submit asks "is the intent visible?", audit asks "what historical constraint produced this?"). A trade-off documented in the PR body / commit message / code comment / user-stated context is prima-facie an intentional choice. To raise it you must show it is *harmful*, not merely *different from how you'd do it*. "I would have done it differently" is not a finding.
3. **Cite the engineering principle** (SRP / YAGNI / DRY / Law of Demeter / least-privilege / etc.) every Tier-1/Tier-2 finding violates. No principle ⇒ downgrade to \`question\` or drop.
4. **Tiers:** T1 = observable failure (crash, data loss, exploitable security, broken API contract). T2 = established-pattern violation with concrete carrying cost. T3 = small/cosmetic but real (readability, local consistency, easy-to-misuse shape). Reporting a context-grounded T3 is GOOD — mark it \`nitpick\` (non-blocking). The only style you must NOT report is what a linter/formatter/type-checker auto-fixes.
5. **The enemy is context-blindness, not triviality.** Finding small things thoroughly is GOOD. What is NOT good is flagging a small thing while ignoring the bigger picture — the overall purpose of the change/scope, the overall code/architecture, the author's intent. Before keeping any finding (big or small) ask: *does this still make sense when I zoom out to what the whole change/scope is doing and how the whole codebase is structured?* A small finding that survives that zoom-out is welcome (label \`nitpick\`). A finding of ANY size that only makes sense by staring at one line in isolation — surface pattern-matching, unreachable when traced, or contradicting a trade-off the PR intentionally made — is noise; drop it. Never drop a finding just for being small; never keep one just for being big.
6. You **report only** findings in these categories: design/architecture, correctness/bugs, security/safety, intent-implementation gap, convention/consistency (documented or codebase-wide), doc-sync, design-validity/ROI, context-grounded readability nits, and **shared-context-map corrections** (if the map below misread the architecture / picked the wrong epicenter / missed a convention — label \`thought\`/\`question\`). (Allowlist — if a thought fits no category, drop it.)`

const FINDINGS_SCHEMA = {
  type: 'object',
  properties: {
    lane: { type: 'string' },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          title: { type: 'string' },
          file: { type: 'string', description: 'project-root-relative path' },
          line: { type: 'string', description: 'line or range, e.g. 42 or 22~26' },
          tier: { type: 'integer', enum: [1, 2, 3] },
          label: { type: 'string', enum: ['issue', 'suggestion', 'nitpick', 'question', 'thought', 'praise', 'FYI'] },
          blocking: { type: 'boolean' },
          principle: { type: 'string', description: 'named engineering principle violated, or empty for question/praise/FYI' },
          evidence: { type: 'string', description: 'the TRACED reasoning — where data comes from, where it flows, why it actually breaks. NOT a restatement of the line.' },
          reachability: { type: 'string', enum: ['confirmed', 'unconfirmed', 'n-a'] },
          recommendation: { type: 'string', description: 'concrete fix, ideally option A / option B' },
        },
        required: ['title', 'file', 'line', 'tier', 'label', 'blocking', 'principle', 'evidence', 'reachability', 'recommendation'],
      },
    },
  },
  required: ['lane', 'findings'],
}

// ── Phase 0: shared context / intent / architecture map (1 agent) ─────────────
phase('Context')
const CONTEXT_SCHEMA = {
  type: 'object',
  properties: {
    problem: { type: 'string' },
    statedIntent: { type: 'string' },
    architecture: { type: 'string' },
    epicenterFile: { type: 'string' },
    priorDecisionConflict: { type: 'string' },
    conventions: { type: 'array', items: { type: 'string' } },
    readerLevel: { type: 'string' },
    changedFilesDigest: { type: 'array', items: { type: 'string' } },
    uiChange: { type: 'boolean' },
    openQuestions: { type: 'array', items: { type: 'string' } },
  },
  required: ['problem', 'statedIntent', 'architecture', 'epicenterFile', 'priorDecisionConflict', 'conventions', 'readerLevel', 'changedFilesDigest', 'uiChange', 'openQuestions'],
}

const context = await agent(
  `${GROUND}

You are the lead reviewer building the SHARED context map that every downstream reviewer relies on. Do NOT list defects yet — understand *what this change is and why*, using the inline code above. Be concrete: name real files, real flows, real conventions. Your "epicenterFile" and "conventions" steer the whole review.`,
  { label: 'context-map', phase: 'Context', schema: CONTEXT_SCHEMA, model: 'sonnet' }
)

const SHARED = `${GROUND}

## Shared context map (built by the lead reviewer — front-loaded constraints)
\`\`\`json
${JSON.stringify(context, null, 2)}
\`\`\`
Lead with the epicenter file. Judge against the listed conventions. Honor stated intent per the doctrine. The map was built by ONE reviewer — if your reading of the inline code shows it got the architecture/epicenter/conventions wrong, report that as a finding.`

// ── Phase 1: multi-lens fan-out — lens set scales with mode ───────────────────
phase('Review')
// High-value defect taxonomy: the recurring high-severity bug CLASSES that single
// passes tend to miss (and that varied between runs). Naming them explicitly makes
// every correctness pass sweep the same classes → higher recall, lower run-to-run variance.
const TAXONOMY = `\n\nDeliberately hunt these high-severity classes (each has bitten this codebase before):\n  (a) **empty-vs-error conflation** — a function returns the SAME value ([] / None / 0 / "") for "nothing found" AND for "operation failed", and a caller treats the failure as a valid-empty case, taking a destructive action (e.g. wiping state, deleting offsets). Trace every \`return []\`/\`return None\`/\`except: pass\` against what the caller then does.\n  (b) **failure-path side effects / partial completion** — op does step A then step B; if B fails after A committed, the system is left in a state that loops or double-acts (e.g. compress→unlink: unlink fails → file reprocessed forever; ship→commit: commit fails → re-ship).\n  (c) **crash/restart recovery & checkpoint atomicity** — partial writes, temp-file→rename windows, offsets/state stale or duplicated after SIGKILL/restart; is recovery at-least-once (acceptable) or actually corrupting?\n  (d) **boundary assumption drift** — units/null/timezone/encoding/ownership/path-shape mismatch between two modules each individually correct.\n  (e) **unbounded growth / resource leak** — files/dirs/memory/handles that accumulate and are never reclaimed.\n  (f) **concurrency** — races, double-processing, missing idempotency/lock/fencing.\nFor each: trace it; if reachable & harmful → finding with the class named; if defended upstream → don't report.`
const LANE_LIB = {
  design: `LENS: DESIGN & ARCHITECTURE (highest altitude — review as a staff engineer). Do the interactions make sense? Is decomposition/layering right, or is there speculative over-engineering (YAGNI) or a missing abstraction? Does it contradict a prior architectural decision? A technically-correct implementation of the wrong design is net-negative — say so. Design blockers outrank any line nit.`,
  correctness: `LENS: CORRECTNESS & BUGS. Trace flows for real defects: logic errors, off-by-one, async/concurrency races, type/unit/null/timezone/encoding mismatches at boundaries, unhandled edge cases (empty/huge input, partial failure, concurrent calls), error handling that swallows failures, invariants whose break-site and crash-site are far apart. The valuable bug is the one that only shows when you follow the call chain.${TAXONOMY}`,
  security: `LENS: SECURITY & SAFETY. Authz/authn bypass, secret exposure, injection (SQL/template/command), unsafe deserialization, SSRF, missing rate limits, excessive privilege. Before asserting a security finding, CONFIRM reachability from the inline code (tainted input actually reaches the sink, not validated upstream). If you cannot confirm from the code shown, label \`question\` and state what to check. Do not pattern-match "looks like X = dangerous".`,
  'intent-gap': `LENS: INTENT-IMPLEMENTATION GAP. Compare code against statedIntent. Does it actually do what the author intended, or drift subtly? LLM-generated tells: unnecessary abstraction, duplicate of an existing helper, code that runs but diverges from intent, dead scaffolding. Also: is intent visible without the diff (PR/commit description, why-comments, naming)? Invisible intent is itself a finding.`,
  convention: `LENS: CONVENTION & CONSISTENCY + DOC-SYNC. Does it follow the conventions in the context map (cite the specific rule)? A convention violation only counts if documented or codebase-wide — else it's preference, drop it. DOC-SYNC: did a public-contract change (API sig, CLI flag, config key, env var, response schema) leave README/docs/docstrings/CHANGELOG stale? Stale docs mislead — a finding even when the code is correct.`,
  roi: `LENS: DESIGN-VALIDITY / ROI (whole-change level). A review of a *piece of work*, not just code. Separate "it works" from "it was worth it". ${SCN.roiFrame} Does added complexity/cost/risk buy a real improvement in outcomes, or are results ~the same? Big changes carry a big burden of proof — if results are similar, raise it as \`question\`/\`suggestion\`. Demand the rationale, don't blame.`,
  // merged lenses for lite mode (fewer agents, same coverage)
  'correctness-design': `LENS: CORRECTNESS + DESIGN (combined). (1) Bugs via flow tracing — logic/off-by-one/races/boundary mismatches/edge cases/error-swallowing/split invariants. (2) Design — do the pieces interact sensibly; over-engineering (YAGNI) or missing abstraction; does it fight a prior decision. Design blockers outrank line nits.${TAXONOMY}`,
  'intent-convention-roi': `LENS: INTENT + CONVENTION + ROI (combined). (1) Does the code match statedIntent or drift? invisible intent = finding. (2) Documented/codebase-wide convention violations + doc-sync (stale README/docs/CHANGELOG after a contract change). (3) Whole-change level: ${SCN.roiFrame}`,
}
const LANE_SETS = {
  lite: ['correctness-design', 'security', 'intent-convention-roi'],
  standard: ['design', 'correctness', 'security', 'intent-gap', 'convention'],
  deep: ['design', 'correctness', 'security', 'intent-gap', 'convention', 'roi'],
}
const lanes = LANE_SETS[MODE]

// Lane plan. Stability ④: in deep mode, run the CORRECTNESS lane TWICE (independent),
// because that lane carries the blockers and is the most variance-prone — union stabilizes
// blocker recall for the costliest PRs at ~+1 agent.
const CORR_LANE = (key) => key === 'correctness' || key === 'correctness-design'
const lanePlan = lanes.map((key) => ({ key, label: `review:${key}`, prompt: LANE_LIB[key] }))
if (MODE === 'deep') {
  lanePlan.push({
    key: 'correctness', label: 'review:correctness#2',
    prompt: LANE_LIB.correctness + `\n\n(SECOND, INDEPENDENT correctness pass. Assume the first reviewer took the obvious path; deliberately probe what they likely skipped — error branches, the failure side of every I/O call, cross-file boundary assumptions, and the rarely-hit edge of each loop. Surface defects the happy-path read misses.)`,
  })
}
const runLane = (l) =>
  agent(`${SHARED}\n\n## Your assigned lens\n${l.prompt}\n\nReview ONLY through this lens, using the inline code (do not re-fetch). Apply the doctrine (trace, respect intent, cite principle, tier, allowlist, zoom-out). Return findings; an empty list is honest if your lens finds nothing real. Do not invent findings to look thorough.`,
    { label: l.label, phase: 'Review', schema: FINDINGS_SCHEMA, model: 'sonnet' })

const round1 = await parallel(lanePlan.map((l) => () => runLane(l)))

// Stability ②: a lane that returns null silently drops a whole review dimension.
// Surface every failure; retry the CORRECTNESS lane once (it carries the blockers).
for (let i = 0; i < lanePlan.length; i++) {
  if (round1[i]) continue
  log(`⚠ lane '${lanePlan[i].key}' returned no result (dimension would be lost)`)
  if (CORR_LANE(lanePlan[i].key)) {
    log(`retrying critical lane '${lanePlan[i].key}' once`)
    round1[i] = await runLane(lanePlan[i])
    if (!round1[i]) log(`⚠ retry of '${lanePlan[i].key}' also failed — correctness coverage is INCOMPLETE this run`)
  }
}

// ── collect + dedup ──
const key = (f) => `${(f.file || '').toLowerCase()}::${String(f.line || '').split('~')[0].trim()}`
const seen = new Set()
let all = []
const ingest = (arr) => {
  for (const r of (arr || []).filter(Boolean)) {
    for (const f of (r.findings || [])) {
      const k = key(f)
      if (seen.has(k)) continue
      seen.add(k)
      all.push({ ...f, lane: r.lane })
    }
  }
}
ingest(round1)

// ── Phase 1.5: completeness sweep — only standard/deep, capped, dry-aware ─────
if (CFG.sweepRounds > 0) {
  phase('Sweep')
  const SWEEP_SCHEMA = {
    type: 'object',
    properties: { gaps: { type: 'array', items: { type: 'object', properties: { target: { type: 'string' }, why: { type: 'string' } }, required: ['target', 'why'] } } },
    required: ['gaps'],
  }
  let dry = 0
  for (let round = 1; round <= CFG.sweepRounds && dry < 1; round++) {
    const seenList = all.map((f) => `- [${f.lane}] ${f.file}:${f.line} — ${f.title}`).join('\n') || '(none yet)'
    const critic = await agent(
      `${SHARED}\n\n## Findings so far\n${seenList}\n\nYou are the completeness critic. A single pass misses defects (Fagan). Using the inline code, name GAPS not yet examined: a changed file/flow not traced, a category under-covered, or a claim asserted-but-unverified. **Explicitly check whether each high-value class was swept — empty-vs-error conflation, failure-path side effects, crash/restart atomicity, boundary drift, unbounded growth, concurrency — and target any that no finding has covered yet.** Be specific. If coverage is genuinely thorough, return empty gaps — do NOT manufacture gaps.`,
      { label: `sweep-critic-r${round}`, phase: 'Sweep', schema: SWEEP_SCHEMA, model: 'sonnet' }
    )
    const gaps = (critic && critic.gaps) || []
    if (!gaps.length) { dry++; continue }
    const found = await parallel(
      gaps.slice(0, 4).map((g) => () =>
        agent(`${SHARED}\n\n## Targeted sweep\nExamine specifically: **${g.target}**\nWhy it may hide a missed defect: ${g.why}\n\nUse the inline code (do not re-fetch). Return only REAL findings (full doctrine). Empty list is fine.`,
          { label: `sweep:${g.target.slice(0, 24)}`, phase: 'Sweep', schema: FINDINGS_SCHEMA, model: 'sonnet' })
      )
    )
    const before = all.length
    ingest(found)
    if (all.length === before) dry++
  }
}

all = all.map((f, i) => ({ ...f, vid: i }))
log(`collected ${all.length} candidate findings`)

// ── Phase 2: BATCHED adversarial verification (1 agent for all; deep=2) ───────
// The old design ran 1-2 skeptics PER finding (dozens of agents, each re-reading
// code). Batching = one pass sees all findings + inline code and votes on each.
phase('Verify')
let survivors = all.map((f) => ({ ...f, survived: true }))
if (all.length) {
  const VERIFY_SCHEMA = {
    type: 'object',
    properties: {
      verdicts: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            vid: { type: 'integer', description: 'the finding id being judged' },
            refuted: { type: 'boolean', description: 'factually wrong, unreachable in the inline code, or already-defended — NOT "true just because small"' },
            contextBlind: { type: 'boolean', description: 'only makes sense staring at one line in isolation — ignores whole-PR purpose / overall code / traced flow / author intent. Kill this regardless of size.' },
            intentionalTradeoff: { type: 'boolean', description: 'author deliberately chose this as an acceptable trade-off AND you cannot show real harm' },
            groundedEvenIfSmall: { type: 'boolean', description: 'regardless of how minor, genuinely grounded in context and a careful senior would still flag it as a non-blocking nit' },
            adjustedTier: { type: 'integer', enum: [1, 2, 3] },
            reason: { type: 'string' },
          },
          required: ['vid', 'refuted', 'contextBlind', 'intentionalTradeoff', 'groundedEvenIfSmall', 'adjustedTier', 'reason'],
        },
      },
    },
    required: ['verdicts'],
  }
  const candidateList = all.map((f) => `### vid=${f.vid} [T${f.tier}/${f.label}] ${f.file}:${f.line}\n${f.title}\n  evidence: ${f.evidence}\n  reco: ${f.recommendation}`).join('\n\n')
  const verifyPrompt = (stance) =>
    `${SHARED}\n\n## Candidate findings to judge (${all.length})\n${candidateList}\n\nYou are an independent skeptic with no stake in these findings. ${stance} Judge EACH finding (one verdict per vid) against the inline code — do not re-fetch.\n\nThe question is NOT "is this too trivial" — a careful senior flags grounded small things. The question is whether each finding survives a ZOOM-OUT: given what the WHOLE change/scope does, the overall code, the conventions, and the author's intent (as framed by the scenario) — does it still hold, or does it only look like a problem when you stare at one line in isolation (context-blind ⇒ kill, any size)? Set groundedEvenIfSmall=true for findings that survive the zoom-out even if minor. Default refuted/contextBlind=true only when a finding genuinely fails this test.`
  const stances = CFG.verifiers >= 2
    ? ['Try hard to REFUTE each on facts and reachability.', 'Judge each strictly on context-grounding vs surface pattern-matching, and on author intent.']
    : ['Judge each on facts, reachability, context-grounding, and author intent — refute the unfounded, keep the grounded (even if small).']
  const passes = (await parallel(
    stances.map((s, i) => () => agent(verifyPrompt(s), { label: `verify-batch-${i + 1}`, phase: 'Verify', schema: VERIFY_SCHEMA, model: 'sonnet' }))
  )).filter(Boolean)

  // gather verdicts per vid
  const byVid = new Map(all.map((f) => [f.vid, []]))
  for (const p of passes) for (const v of (p.verdicts || [])) if (byVid.has(v.vid)) byVid.get(v.vid).push(v)

  survivors = all.map((f) => {
    const v = byVid.get(f.vid) || []
    if (f.label === 'praise') return { ...f, survived: true, verdicts: v }
    if (!v.length) return { ...f, survived: true, verdicts: v } // no verdict returned ⇒ keep, moderator backstops
    const tier = Math.max(f.tier, ...v.map((x) => x.adjustedTier || f.tier))
    const refuted = v.filter((x) => x.refuted).length
    const blind = v.filter((x) => x.contextBlind).length
    const grounded = v.filter((x) => x.groundedEvenIfSmall).length
    // Tier-weighted: T3 → 1 vote kills (suppress nit noise); T1/T2 with ≥2 verifiers
    // → needs BOTH to kill (a lone "looks fine" can't bury a subtle crash/security bug).
    const killNeeded = (v.length >= 2 && tier <= 2) ? 2 : 1
    if (refuted >= killNeeded) return null
    if (blind >= killNeeded) return null
    if (v.length >= 2 && v.every((x) => x.intentionalTradeoff)) return null
    if (tier === 3 && grounded < 1 && (refuted || blind)) return null
    return { ...f, tier, survived: true, verdicts: v }
  }).filter(Boolean)
}
log(`${survivors.length}/${all.length} findings survived verification`)

// ── Phase 3: moderator — dedup, calibrate, order, praise, design-validity ─────
phase('Calibrate')
const FINAL_SCHEMA = {
  type: 'object',
  properties: {
    verdict: { type: 'string', enum: SCN.verdicts },
    summary: { type: 'string', description: '1-3 sentence conclusion answering the scenario verdict question — does this improve code health? blockers?' },
    blockingCount: { type: 'integer' },
    nonBlockingCount: { type: 'integer' },
    designValidity: {
      type: 'object',
      properties: {
        axes: { type: 'array', items: { type: 'object', properties: { axis: { type: 'string' }, judgment: { type: 'string', enum: ['good', 'check', 'medium', 'critical'] }, basis: { type: 'string' } }, required: ['axis', 'judgment', 'basis'] } },
        conclusion: { type: 'string' },
      },
      required: ['axes', 'conclusion'],
    },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' }, title: { type: 'string' }, file: { type: 'string' }, line: { type: 'string' },
          sourceVids: { type: 'array', items: { type: 'integer' }, description: 'the vid(s) of the verified survivor(s) this card represents. Exactly one unless you are merging true duplicates. EVERY survivor vid must appear in some card.' },
          label: { type: 'string', enum: ['issue', 'suggestion', 'nitpick', 'question', 'thought', 'praise', 'FYI'] },
          principle: { type: 'string' }, problem: { type: 'string' }, recommendation: { type: 'string' },
          plainTalk: { type: 'string' }, impact: { type: 'string' },
        },
        required: ['id', 'title', 'file', 'line', 'sourceVids', 'label', 'principle', 'problem', 'recommendation'],
      },
    },
    praise: { type: 'array', items: { type: 'string' } },
    openQuestions: { type: 'array', items: { type: 'object', properties: { who: { type: 'string' }, what: { type: 'string' }, how: { type: 'string' }, expected: { type: 'string' } }, required: ['who', 'what', 'how', 'expected'] } },
    suppressed: { type: 'array', items: { type: 'string' } },
    uiChange: { type: 'boolean' },
  },
  required: ['verdict', 'summary', 'blockingCount', 'nonBlockingCount', 'designValidity', 'findings', 'praise', 'openQuestions', 'suppressed', 'uiChange'],
}

// Severity is DECIDED BY VERIFICATION, not by the moderator. The deep-mode measurement
// showed the moderator silently downgrading verified T1 blockers (compress-loop, ship/finalize)
// to 'medium' during calibration. So we compute severityClass/actionTag/blocking in JS from the
// verifier-assigned tier+label, hand them to the moderator as FIXED, and forbid re-judging.
// The moderator's job shrinks to: dedup true duplicates, order, write prose. (Over-severity is
// already handled upstream by the 2 verifiers — role separation.)
const SEV_BY_TIER = { 1: ['critical', 'required'], 2: ['medium', 'recommended'], 3: ['minor', 'optional'] }
const present = (f) => {
  const lbl = f.label
  let severityClass, actionTag, blocking = false
  if (lbl === 'praise') { severityClass = 'good'; actionTag = 'fyi' }
  else if (lbl === 'question') { severityClass = 'check'; actionTag = 'fyi' }
  else if (lbl === 'thought' || lbl === 'FYI') { severityClass = 'info'; actionTag = 'fyi' }
  else { [severityClass, actionTag] = SEV_BY_TIER[f.tier] || SEV_BY_TIER[3]; blocking = !!f.blocking && f.tier <= 2 && (lbl === 'issue' || lbl === 'suggestion') }
  const { verdicts, survived, ...rest } = f   // keep vid — it is the merge key for the moderator
  return { ...rest, severityClass, actionTag, blocking }
}
const presented = survivors.map(present)
const byVid = new Map(presented.map((p) => [p.vid, p]))

const final = await agent(
  `${SHARED}

## Verified surviving findings — each has a \`vid\`. Severity is ALREADY fixed (severityClass/blocking shown).
\`\`\`json
${JSON.stringify(presented, null, 2)}
\`\`\`

You are the moderator. You **CANNOT change severity** — it is computed downstream from each card's \`sourceVids\`. Your job: dedup, order, clear prose, ids.
- For every output card, set \`sourceVids\` to the vid(s) it represents — exactly one vid, unless you are merging TRUE duplicates (same issue from different lenses) into one card, then list all merged vids.
- **EVERY survivor vid MUST appear in exactly one card's sourceVids.** Do not omit any. (If you drop one, it gets auto-recovered downstream and your review will look careless.)
- Write \`title\`/\`problem\`/\`recommendation\` (and optional \`plainTalk\`/\`impact\`) as clear prose; for a merged card, combine the sources' evidence.
- **Order**: blocking-severity cards first (design/architecture, then epicenter file, then others), non-blocking nits last.
- **designValidity**: ${SCN.validityFrame} — only those that apply; small changes can be 1-axis.
- **verdict**: answer the scenario's verdict question with one of: ${SCN.verdicts.join(' / ')}. Write the summary in the scenario's voice (e.g. pre-submit speaks TO the author about submitting, audit speaks about code health — never "merge" language outside peer-pr).
- **praise**: ≥1 genuine item (non-negotiable). **openQuestions**: who/what/how/expected. **suppressed**: only auto-fixable lint noise or one-representative-of-a-repeated-pattern.
Spend your effort on clarity, dedup, and ordering — not severity (it's locked).`,
  { label: 'moderate-calibrate', phase: 'Calibrate', schema: FINAL_SCHEMA, model: 'sonnet' }
)

// ── Stability guard ③ (STRUCTURAL): severity is now computed in JS from each card's
// sourceVids → the moderator cannot downgrade or drop a blocker. Any survivor the moderator
// omitted is auto-recovered as its own card. This FIXES (not just detects) the demotion the
// deep-mode measurement exposed.
const SEV_RANK = { critical: 4, medium: 3, check: 2, minor: 1, info: 0, good: 0 }
const used = new Set()
const finalFindings = (final.findings || []).map((f) => {
  const src = (f.sourceVids || []).map((v) => byVid.get(v)).filter(Boolean)
  src.forEach((s) => used.add(s.vid))
  if (!src.length) return f // moderator-invented card with no valid source — keep as-is (rare)
  const top = src.slice().sort((a, b) => (SEV_RANK[b.severityClass] || 0) - (SEV_RANK[a.severityClass] || 0))[0]
  // severity is taken from the highest-severity source; blocking if ANY source blocks. Authoritative.
  return { ...f, severityClass: top.severityClass, actionTag: top.actionTag, blocking: src.some((s) => s.blocking), principle: f.principle || top.principle || '' }
})
// Auto-recover any survivor the moderator silently omitted (hard no-loss guarantee).
const recovered = []
for (const p of presented) {
  if (used.has(p.vid)) continue
  recovered.push({
    id: `recovered-${p.vid}`, title: p.title, file: p.file, line: p.line, sourceVids: [p.vid],
    severityClass: p.severityClass, actionTag: p.actionTag, blocking: p.blocking, label: p.label,
    principle: p.principle || '', problem: p.evidence || p.title, recommendation: p.recommendation || '',
  })
  log(`⚠ recovered finding the moderator omitted: vid=${p.vid} [${p.severityClass}] ${p.file}:${p.line} — ${p.title}`)
}
// blocking first, then by severity, recovered extras keep their computed severity in place
const order = (f) => (f.blocking ? 0 : 10) + (4 - (SEV_RANK[f.severityClass] || 0))
final.findings = [...finalFindings, ...recovered].sort((a, b) => order(a) - order(b))
// Recompute counts + verdict authoritatively (the moderator's self-reported numbers are not trusted).
final.blockingCount = final.findings.filter((f) => f.blocking).length
final.nonBlockingCount = final.findings.filter((f) => !f.blocking && f.severityClass !== 'good').length
if (final.blockingCount > 0) final.verdict = SCN.blockingVerdict
else if (final.verdict === SCN.blockingVerdict) final.verdict = SCN.softVerdict

const inBlockers = presented.filter((f) => f.blocking)
const droppedBlockers = recovered.some((f) => f.blocking)
if (droppedBlockers) log(`⚠ STABILITY NOTE: ${recovered.filter((f) => f.blocking).length} blocking finding(s) were omitted by the moderator and AUTO-RECOVERED (no loss). Counts/verdict recomputed in JS.`)

return {
  target: A,
  mode: MODE,
  scenario: SCENARIO,
  context,
  review: final,
  stats: { mode: MODE, lanes: lanePlan.length, sweepRounds: CFG.sweepRounds, verifiers: CFG.verifiers, candidates: all.length, survived: survivors.length, finalFindings: (final.findings || []).length },
  integrity: { codeSource: hasCode, blockerSurvivors: inBlockers.length, blockingOut: final.blockingCount, recoveredCount: recovered.length, recoveredBlockers: recovered.filter((f) => f.blocking).length, severityAuthority: 'js-from-sourceVids' },
}
