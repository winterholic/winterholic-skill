export const meta = {
  name: 'senior-loop-developer',
  description: 'Processes a senior-review report end-to-end, token-budgeted. Findings are parsed ONCE by the main loop and passed inline (agents do not re-explore to triage). Triage is BATCHED (one opus-xhigh pass classifies every finding: false-positive / fix / defer — false-positives MUST cite evidence or they are downgraded to defer). Only findings classified "fix" spawn coding agents, grouped by file, modeled by risk (nitpick→sonnet, logic/dangerous→opus). Verification is BATCHED and runs in a SEPARATE agent from the coder (no self-review bias). One coding retry on rejection, then defer. Returns a structured result for the main loop to append to the report.',
  phases: [
    { title: 'Triage', detail: 'one opus-xhigh batched pass classifies every finding: false-positive / fix / defer', model: 'opus' },
    { title: 'Code', detail: 'coding agents grouped by file, only for fix-classified findings; model by risk' },
    { title: 'Verify', detail: 'BATCHED adversarial verification in a separate agent — did each fix resolve the finding without regression?', model: 'opus' },
  ],
}

// ── args (assembled ONCE by the skill's main loop — agents must NOT re-parse the HTML) ──
// {
//   reportPath,                  // senior-review HTML path (main loop appends the processing round to it)
//   projectRoot,                 // absolute repo path the fixes are applied in
//   branch,                      // working branch the main loop already created/checked out
//   base,                        // base ref for diffs
//   scenario,                    // inherited from the senior-review run (pre-submit / peer-pr / wip / audit)
//   findings: [{                 // parsed by the main loop FROM the senior-review HTML cards
//     fid, file, line, severityClass, label, blocking, title, problem, recommendation
//   }],
//   diffText,                    // current branch diff (inline, gathered once — for triage context)
//   files: [{ path, content }],  // line-numbered content of files the findings touch (inline, gathered once)
// }
let A = args || {}
if (typeof A === 'string') { try { A = JSON.parse(A) } catch (_) { A = {} } }
const FINDINGS = (A.findings || []).map((f, i) => ({ ...f, fid: (f.fid != null ? f.fid : i) }))
const FILES = A.files || []
const SCENARIO = A.scenario || 'pre-submit'

// ── Fail LOUD on missing inputs (senior-review / lite-research lesson) ──
if (!FINDINGS.length) log('⚠ STABILITY WARNING: no findings parsed from the report — nothing to process. Main loop must pass args.findings parsed from the senior-review HTML.')
if (!A.projectRoot) log('⚠ STABILITY WARNING: no projectRoot — coding agents cannot locate files to edit.')
if (!(A.diffText || FILES.length)) log('⚠ STABILITY WARNING: no inline code (diffText/files) — triage will be blind and likely misjudge false-positives.')

// Skip findings that are not actionable defects (praise / pure FYI carry no fix work).
const ACTIONABLE = FINDINGS.filter((f) => !['good', 'info'].includes(f.severityClass) && f.label !== 'praise' && f.label !== 'FYI')
const NON_ACTIONABLE = FINDINGS.filter((f) => !ACTIONABLE.includes(f))
if (NON_ACTIONABLE.length) log(`${NON_ACTIONABLE.length} non-actionable finding(s) (praise/FYI) skipped from processing`)

// ── The code, inlined ONCE. Triage/verify agents read from here, never re-explore. ──
const FORBID = '**For TRIAGE and VERIFY you must NOT run `git`/`gh`/`grep` or browse the repo** — re-exploring is the #1 token waste. ALL the code you need to judge is inline below. The ONLY exception: a judgment genuinely hinges on an UNCHANGED file not shown (a caller/callee) — then Read that single file once and say so. (Coding agents are the exception: they DO edit real files.)'
const CODE = (A.bundlePath && !FILES.length && !A.diffText) ? [
  '## The code under review — in ONE local file.',
  '**For TRIAGE and VERIFY: Read this ONE local file EXACTLY ONCE — it contains the full line-numbered content of every file the findings touch. Do NOT run `git`/`gh`/`grep` or browse the repo beyond this one Read** (coding agents excepted — they edit real files):',
  '`' + A.bundlePath + '`',
].join('\n') : [
  '## The code under review — inline, gathered once.', FORBID, '',
  '### Current branch diff', '```diff', (A.diffText || '(diff not provided)').slice(0, 200000), '```', '',
  '### Full content of the files the findings touch (line-numbered)',
  ...FILES.map((f) => `\n#### ${f.path}\n\`\`\`\n${f.content}\n\`\`\``),
].join('\n')

const GROUND = `## What this run does
A senior-review already produced findings on this code. You are part of a pipeline that PROCESSES those findings: decide which are false-positives, which to fix, which to defer to the human — then fix the fixable, then verify the fixes.

## Review scenario (inherited): ${SCENARIO}
The original review judged the code under this frame; honor it.

## Project
\`\`\`json
${JSON.stringify({ projectRoot: A.projectRoot, branch: A.branch, base: A.base, scenario: SCENARIO }, null, 2)}
\`\`\`

${CODE}

## Project rules
Read root + nested \`CLAUDE.md\`, \`README\`, \`CONVENTIONS.md\` ONLY IF a convention decides a specific judgment. Do not browse otherwise.`

// ── Phase 1: BATCHED triage (one opus-xhigh pass; split into 2 parallel if many) ──
phase('Triage')
const TRIAGE_SCHEMA = {
  type: 'object',
  properties: {
    verdicts: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          fid: { type: 'integer', description: 'the finding id being classified' },
          category: { type: 'string', enum: ['false-positive', 'fix', 'defer'] },
          reason: { type: 'string', description: 'why this classification — traced from the inline code' },
          evidence: {
            type: 'string',
            description: 'false-positive ONLY: the QUOTED basis (code line / PR/commit text / doc / convention) proving the finding is wrong or the choice was intentional & harmless. An empty/weak evidence here means it is NOT a real false-positive — it will be downgraded to defer.',
          },
          riskClass: {
            type: 'string',
            enum: ['nitpick', 'logic', 'dangerous', 'n-a'],
            description: 'fix ONLY: nitpick=cosmetic/local/doc, logic=behavior-changing code, dangerous=security/data-safety/concurrency. n-a otherwise.',
          },
          blastRadius: {
            type: 'string',
            enum: ['contained', 'cross-cutting', 'n-a'],
            description: 'fix candidates: contained=changes stay within this PR scope; cross-cutting=touches shared utils / public interfaces / changes behavior of OTHER features / exceeds this PR scope. cross-cutting MUST be defer, not fix.',
          },
          fixPlan: { type: 'string', description: 'fix ONLY: concrete change to make (file:line + what). Empty otherwise.' },
          deferReason: { type: 'string', description: 'defer ONLY: why a human must decide — blast radius, ambiguity, or scope. Empty otherwise.' },
        },
        required: ['fid', 'category', 'reason', 'evidence', 'riskClass', 'blastRadius', 'fixPlan', 'deferReason'],
      },
    },
  },
  required: ['verdicts'],
}

const triageDoctrine = `You are the TRIAGE judge — opus, maximum rigor. Classify EACH finding into exactly one category. This is the safety-critical step: a wrong "false-positive" silently buries a real bug; a wrong "fix" lets an agent touch code it shouldn't.

THREE categories:
1. **false-positive** — the finding is wrong, OR the author intentionally chose this as a harmless trade-off. **You MUST quote concrete evidence** from the inline code / PR/commit text / a doc / an established convention. The bar: would a careful senior, shown your evidence, agree it's a non-issue? If you cannot quote evidence — if your reason is only "seems fine" or "probably intentional" — it is NOT a false-positive. Downgrade to **defer**. (Self-rationalization is the failure mode this guards against: do not talk yourself out of a real bug.)
2. **fix** — a real defect/improvement that is safe to auto-fix IN THIS PR. Requires blastRadius=contained. Assign riskClass (nitpick / logic / dangerous) and a concrete fixPlan. Includes: dangerous code (always fix), behavior bugs, and grounded nitpicks worth the small safe improvement.
3. **defer** — real, but a human must decide. Triggers: **blastRadius=cross-cutting** (touches shared utils / public interfaces / other features' behavior / exceeds this PR's scope — the "외인수급" class: a "simple" change that ripples outward), genuine ambiguity, or a blocking issue whose right fix is unclear. Leave it; explain in deferReason.

RULES:
- A finding with blastRadius=cross-cutting is ALWAYS defer, even if blocking. The cost of an agent silently rewriting a shared util across the codebase is worse than leaving it for the human.
- When torn between fix and defer → defer. When torn between false-positive and defer → defer. Defer is the safe sink.
- Trace from the inline code, not the finding's surface wording.`

let triageVerdicts = []
if (ACTIONABLE.length) {
  const renderFinding = (f) => `### fid=${f.fid} [${f.severityClass}/${f.label}${f.blocking ? '/blocking' : ''}] ${f.file}:${f.line}\n${f.title}\n  problem: ${f.problem}\n  recommendation: ${f.recommendation}`
  const runTriage = (subset, tag) =>
    agent(`${GROUND}\n\n${triageDoctrine}\n\n## Findings to classify (${subset.length})\n${subset.map(renderFinding).join('\n\n')}\n\nReturn one verdict per fid. Every fid must appear exactly once.`,
      { label: `triage${tag}`, phase: 'Triage', schema: TRIAGE_SCHEMA, model: 'opus' })

  // Batch by default; split into 2 parallel passes only when the list is large (keeps attention sharp).
  if (ACTIONABLE.length > 12) {
    const mid = Math.ceil(ACTIONABLE.length / 2)
    const passes = (await parallel([
      () => runTriage(ACTIONABLE.slice(0, mid), ':1'),
      () => runTriage(ACTIONABLE.slice(mid), ':2'),
    ])).filter(Boolean)
    triageVerdicts = passes.flatMap((p) => p.verdicts || [])
  } else {
    const p = await runTriage(ACTIONABLE, '')
    triageVerdicts = (p && p.verdicts) || []
  }
}

// Join verdicts back to findings; default any missing verdict to defer (never silently drop).
const vByFid = new Map(triageVerdicts.map((v) => [v.fid, v]))
const classified = ACTIONABLE.map((f) => {
  const v = vByFid.get(f.fid)
  if (!v) { log(`⚠ no triage verdict for fid=${f.fid} — defaulting to defer`); return { ...f, category: 'defer', deferReason: 'triage returned no verdict (defaulted to defer for safety)' } }
  return { ...f, ...v }
})

// ── Safety downgrades (JS-enforced, not left to the model) ──
//  (a) false-positive without real evidence  → defer
//  (b) fix with cross-cutting blast radius     → defer (the 외인수급 guard)
for (const f of classified) {
  if (f.category === 'false-positive' && (!f.evidence || f.evidence.trim().length < 12)) {
    log(`⚠ fid=${f.fid} marked false-positive without evidence → downgraded to defer`)
    f.category = 'defer'; f.deferReason = `오탐 주장에 근거 부족 → 보류로 강등. 원 사유: ${f.reason}`
  }
  if (f.category === 'fix' && f.blastRadius === 'cross-cutting') {
    log(`⚠ fid=${f.fid} fix has cross-cutting blast radius → downgraded to defer`)
    f.category = 'defer'; f.deferReason = `영향범위 광범위(공용/인터페이스/타기능/스코프 초과) → 자동수정 금지, 보류. 처리안: ${f.fixPlan}`
  }
}

const falsePositives = classified.filter((f) => f.category === 'false-positive')
let toFix = classified.filter((f) => f.category === 'fix')
const deferred = classified.filter((f) => f.category === 'defer')
log(`triage: ${falsePositives.length} false-positive, ${toFix.length} fix, ${deferred.length} defer (of ${ACTIONABLE.length} actionable)`)

// ── Phase 2: coding — only for fix-classified findings, grouped by FILE ──
// One agent per file (a file's multiple findings are fixed together to avoid edit races).
// Model by the file group's HIGHEST risk: any logic/dangerous → opus, else sonnet.
phase('Code')
const FIX_RESULT_SCHEMA = {
  type: 'object',
  properties: {
    file: { type: 'string' },
    applied: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          fid: { type: 'integer' },
          summary: { type: 'string', description: 'what was changed, concretely' },
          changedLines: { type: 'string', description: 'the line range(s) edited, e.g. 42-48' },
        },
        required: ['fid', 'summary', 'changedLines'],
      },
    },
    failed: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          fid: { type: 'integer' },
          why: { type: 'string', description: 'why it could not be applied (e.g. needs cross-file change after all)' },
        },
        required: ['fid', 'why'],
      },
    },
  },
  required: ['file', 'applied', 'failed'],
}

const groupByFile = (items) => {
  const m = new Map()
  for (const f of items) { const k = f.file || '(unknown)'; if (!m.has(k)) m.set(k, []); m.get(k).push(f) }
  return [...m.entries()]
}
const modelFor = (group) => group.some((f) => f.riskClass === 'logic' || f.riskClass === 'dangerous') ? 'opus' : 'sonnet'

const codeOneFile = (file, group) => {
  const planList = group.map((f) => `- fid=${f.fid} [${f.riskClass}] ${file}:${f.line} — ${f.title}\n    문제: ${f.problem}\n    처리안: ${f.fixPlan}`).join('\n')
  const model = modelFor(group)
  return agent(
    `${GROUND}

You are the CODING agent for ONE file: **${file}** in ${A.projectRoot}. Apply the approved fixes below — these were already triaged as safe, contained, in-scope. You MAY Read this file (and a directly-related caller/callee if a fix needs it) and you MUST Edit the real file to apply each fix.

## Approved fixes for ${file}
${planList}

RULES:
- Apply each fix per its 처리안. Keep changes minimal and contained — do NOT refactor beyond the fix, do NOT touch shared utilities or public interfaces (if a fix turns out to need that, mark it failed with why — do not do it).
- Match surrounding style. Comments only explain WHY (non-obvious business rules), never the obvious.
- If applying one fix would conflict with another or with the PR's intent, apply what's safe and mark the rest failed.
- Return what you applied (with changed line ranges) and what you could not.`,
    { label: `code:${file.split('/').pop()}`, phase: 'Code', schema: FIX_RESULT_SCHEMA, model }
  )
}

let fixResults = []
if (toFix.length) {
  const groups = groupByFile(toFix)
  log(`coding ${toFix.length} fix(es) across ${groups.length} file(s)`)
  fixResults = (await parallel(groups.map(([file, group]) => () => codeOneFile(file, group)))).filter(Boolean)
}

// Map applied/failed back to findings.
const appliedByFid = new Map()
for (const r of fixResults) for (const a of (r.applied || [])) appliedByFid.set(a.fid, { ...a, file: r.file })
const codeFailedByFid = new Map()
for (const r of fixResults) for (const fa of (r.failed || [])) codeFailedByFid.set(fa.fid, { ...fa, file: r.file })

// ── Phase 3: BATCHED verification in a SEPARATE agent (no self-review bias) ──
// The verifier did not write the code; it judges whether each applied fix actually
// resolved the original finding AND introduced no regression.
phase('Verify')
const VERIFY_SCHEMA = {
  type: 'object',
  properties: {
    verdicts: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          fid: { type: 'integer' },
          verdict: { type: 'string', enum: ['resolved', 'not-resolved', 'regression-risk'] },
          reason: { type: 'string' },
        },
        required: ['fid', 'verdict', 'reason'],
      },
    },
  },
  required: ['verdicts'],
}

const verifyApplied = async (appliedItems, tag) => {
  if (!appliedItems.length) return []
  // Gather the post-fix diff ONCE so the verifier sees real changes, not claims.
  const postDiff = await agent(
    `In ${A.projectRoot}, output ONLY the result of \`git diff ${A.base || 'HEAD'}\` (the current uncommitted/branch changes). No commentary — your entire response is the raw diff. If too large, include the hunks touching: ${[...new Set(appliedItems.map((a) => appliedByFid.get(a.fid)?.file).filter(Boolean))].join(', ')}.`,
    { label: `collect-diff${tag}`, phase: 'Verify', model: 'sonnet' }
  )
  const items = appliedItems.map((f) => {
    const a = appliedByFid.get(f.fid)
    return `### fid=${f.fid} ${f.file}:${f.line}\n  원 지적: ${f.problem}\n  처리안: ${f.fixPlan}\n  적용내용: ${a ? a.summary + ' (lines ' + a.changedLines + ')' : '(unknown)'}`
  }).join('\n\n')
  const v = await agent(
    `${GROUND}

## Post-fix diff (the ACTUAL changes the coding agents made)
\`\`\`diff
${(postDiff || '(diff unavailable)').slice(0, 150000)}
\`\`\`

You are the independent VERIFIER (opus). You did NOT write these fixes — judge them skeptically. For EACH fix below decide:
- **resolved** — the change genuinely addresses the original 지적, correctly.
- **not-resolved** — the change does not actually fix the 지적 (missed the point, incomplete, wrong).
- **regression-risk** — it may fix the 지적 but introduces a NEW problem (breaks a caller, changes behavior elsewhere, new edge case).

Judge from the actual diff, not the claimed 적용내용. One verdict per fid.

## Fixes to verify (${appliedItems.length})
${items}`,
    { label: `verify-batch${tag}`, phase: 'Verify', schema: VERIFY_SCHEMA, model: 'opus' }
  )
  return (v && v.verdicts) || []
}

const appliedFindings = toFix.filter((f) => appliedByFid.has(f.fid))
let verdicts = await verifyApplied(appliedFindings, '')
let vMap = new Map(verdicts.map((v) => [v.fid, v]))

// ── One coding retry for rejected fixes, then defer (hard cap) ──
const rejected = appliedFindings.filter((f) => { const v = vMap.get(f.fid); return v && v.verdict !== 'resolved' })
if (rejected.length) {
  log(`${rejected.length} fix(es) rejected by verification → one retry`)
  const groups = groupByFile(rejected.map((f) => ({ ...f, fixPlan: `${f.fixPlan}\n    [재시도 — 1차 검증 반려 사유: ${vMap.get(f.fid)?.reason}] 이 반려 사유를 반드시 해소할 것.` })))
  const retryResults = (await parallel(groups.map(([file, group]) => () => codeOneFile(file, group)))).filter(Boolean)
  for (const r of retryResults) for (const a of (r.applied || [])) appliedByFid.set(a.fid, { ...a, file: r.file })
  const retried = rejected.filter((f) => appliedByFid.has(f.fid))
  const retryVerdicts = await verifyApplied(retried, ':retry')
  for (const v of retryVerdicts) vMap.set(v.fid, v)
}

// ── Final classification of each fix attempt ──
const fixed = [], fixDeferred = []
for (const f of toFix) {
  const v = vMap.get(f.fid)
  const applied = appliedByFid.get(f.fid)
  if (applied && v && v.verdict === 'resolved') {
    fixed.push({ fid: f.fid, title: f.title, file: f.file, line: f.line, riskClass: f.riskClass, summary: applied.summary, changedLines: applied.changedLines })
  } else {
    const why = !applied
      ? (codeFailedByFid.get(f.fid)?.why || '코딩 에이전트가 적용하지 못함')
      : `검증 반려(${v?.verdict || 'no-verdict'}): ${v?.reason || '재시도 후에도 미해결'}`
    fixDeferred.push({ fid: f.fid, title: f.title, file: f.file, line: f.line, reason: `자동수정 실패 → 보류. ${why}` })
  }
}

const allDeferred = [
  ...deferred.map((f) => ({ fid: f.fid, title: f.title, file: f.file, line: f.line, reason: f.deferReason || f.reason, blocking: f.blocking })),
  ...fixDeferred,
]

log(`done: ${fixed.length} fixed, ${falsePositives.length} false-positive, ${allDeferred.length} deferred`)

return {
  reportPath: A.reportPath,
  branch: A.branch,
  scenario: SCENARIO,
  falsePositives: falsePositives.map((f) => ({ fid: f.fid, title: f.title, file: f.file, line: f.line, reason: f.reason, evidence: f.evidence })),
  fixed,
  deferred: allDeferred,
  skipped: NON_ACTIONABLE.map((f) => ({ fid: f.fid, title: f.title, label: f.label })),
  stats: {
    totalFindings: FINDINGS.length,
    actionable: ACTIONABLE.length,
    fixed: fixed.length,
    falsePositives: falsePositives.length,
    deferred: allDeferred.length,
  },
}
