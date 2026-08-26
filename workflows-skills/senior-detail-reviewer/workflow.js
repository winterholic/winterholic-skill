export const meta = {
  name: 'senior-detail-reviewer',
  description: 'Read-only second-opinion judge over a senior-review report, token-budgeted. Findings and code are parsed/gathered ONCE by the main loop and passed inline (agents never re-explore). TWO independent opus judges classify every finding in a BATCHED pass (false-positive / valid / needs-human); a false-positive verdict MUST cite quoted evidence or it does not count. JS reconciles: a finding is ruled false-positive ONLY on unanimous, evidence-backed agreement — otherwise it stays valid (never bury a real bug) or escalates to needs-human. NO code edits, NO git. Returns a structured judgment for the main loop to append to the report.',
  phases: [
    { title: 'Judge', detail: 'two independent opus judges classify every finding in a batched pass', model: 'opus' },
  ],
}

// ── args (assembled ONCE by the main loop — agents must NOT re-parse the HTML) ──
// {
//   reportPath,                  // senior-review HTML path (main loop appends the judgment round)
//   projectRoot, base,           // for context only — this skill does NOT edit or run git
//   scenario,                    // inherited from the senior-review run
//   findings: [{ fid, file, line, severityClass, label, blocking, title, problem, recommendation }],
//   diffText,                    // current diff (inline, gathered once)
//   files: [{ path, content }],  // line-numbered content of files the findings touch (inline, once)
// }
let A = args || {}
if (typeof A === 'string') { try { A = JSON.parse(A) } catch (_) { A = {} } }
const FINDINGS = (A.findings || []).map((f, i) => ({ ...f, fid: (f.fid != null ? f.fid : i) }))
const FILES = A.files || []
const SCENARIO = A.scenario || 'peer-pr'

// ── Fail LOUD on missing inputs ──
if (!FINDINGS.length) log('⚠ STABILITY WARNING: no findings parsed from the report — nothing to judge. Main loop must pass args.findings parsed from the senior-review HTML.')
if (!(A.diffText || FILES.length)) log('⚠ STABILITY WARNING: no inline code (diffText/files) — judges will be blind and likely mislabel false-positives.')

// Praise / pure-FYI carry no judgment work.
const ACTIONABLE = FINDINGS.filter((f) => !['good', 'info'].includes(f.severityClass) && f.label !== 'praise' && f.label !== 'FYI')
const NON_ACTIONABLE = FINDINGS.filter((f) => !ACTIONABLE.includes(f))
if (NON_ACTIONABLE.length) log(`${NON_ACTIONABLE.length} non-actionable finding(s) (praise/FYI) skipped`)

// ── The code, inlined ONCE. This is a READ-ONLY skill: no agent edits anything. ──
const FORBID = '**This is a READ-ONLY judgment. Do NOT edit any file, do NOT run `git`/`gh`, do NOT browse the repo.** All the code you need is inline below. The ONLY exception: a verdict genuinely hinges on an UNCHANGED file not shown (a caller/callee) — then Read that single file once and say so.'
const CODE = [
  '## The code under review — inline, gathered once.', FORBID, '',
  '### Current diff', '```diff', (A.diffText || '(diff not provided)').slice(0, 200000), '```', '',
  '### Full content of the files the findings touch (line-numbered)',
  ...FILES.map((f) => `\n#### ${f.path}\n\`\`\`\n${f.content}\n\`\`\``),
].join('\n')

const GROUND = `## What this run does
A senior-review already produced findings on this code. You are a SECOND-OPINION judge: for each finding decide whether it is a real, valid problem or a false-positive — nothing is fixed here, this is pure judgment for a human reviewer who wants to know which of the review's findings to trust.

## Review scenario (inherited): ${SCENARIO}
The original review judged the code under this frame; honor it.

## Project (context only — you do NOT edit or run git)
\`\`\`json
${JSON.stringify({ projectRoot: A.projectRoot, base: A.base, scenario: SCENARIO }, null, 2)}
\`\`\`

${CODE}

## Project rules
Read root + nested \`CLAUDE.md\`, \`README\`, \`CONVENTIONS.md\` ONLY IF a convention decides a specific verdict. Do not browse otherwise.`

const JUDGE_SCHEMA = {
  type: 'object',
  properties: {
    verdicts: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          fid: { type: 'integer' },
          category: { type: 'string', enum: ['false-positive', 'valid', 'needs-human'] },
          reason: { type: 'string', description: 'the traced reasoning behind this verdict' },
          evidence: {
            type: 'string',
            description: 'false-positive ONLY: the QUOTED basis (code line / PR/commit text / doc / convention) proving the finding is wrong or the choice was intentional & harmless. Empty/weak evidence = the verdict does NOT count as a false-positive.',
          },
          adjustedTier: { type: 'integer', enum: [1, 2, 3], description: 'valid ONLY: your read of the true severity tier (T1 observable failure / T2 pattern violation w/ cost / T3 small-but-real). May differ from the original.' },
          note: { type: 'string', description: 'valid: optional severity/priority note for the human. needs-human: what exactly the human must check (cross-file/business-logic/runtime).' },
        },
        required: ['fid', 'category', 'reason', 'evidence', 'adjustedTier', 'note'],
      },
    },
  },
  required: ['verdicts'],
}

const judgeDoctrine = `You are an INDEPENDENT second-opinion judge — opus, maximum rigor. You have NOT seen the other judge's verdicts; do not imagine one to agree with. Classify EACH finding into exactly one category:

1. **false-positive** — the finding is factually wrong, unreachable when traced, OR the author intentionally chose this as a harmless trade-off. **You MUST quote concrete evidence** (code line / PR/commit text / doc / established convention). The bar: shown your evidence, would a careful senior agree it's a non-issue? If your reason is only "seems fine" / "probably intentional" with nothing quoted, it is NOT a false-positive — classify it valid or needs-human. (This guards against talking yourself out of a real bug.)
2. **valid** — a real problem the original review correctly caught. Set adjustedTier to your honest read of its severity (you may disagree with the original — e.g. an at-least-once behavior wrongly marked critical is really T3). Optional note on priority.
3. **needs-human** — you genuinely cannot decide false-positive vs valid from the inline code alone: it hinges on cross-file wiring not shown, business-logic intent, external/runtime state, or data you can't see. Say precisely what to check in note.

RULES:
- Judge from the TRACED data/control flow in the inline code, never the finding's surface wording.
- When torn between false-positive and valid → do NOT call it false-positive; use needs-human (or valid if you lean real). False-positive is the highest bar and needs quoted evidence.
- Respect author intent as framed by the scenario, but "different from how I'd do it" is not a false-positive.`

let allVerdicts = [[], []]
if (ACTIONABLE.length) {
  const renderFinding = (f) => `### fid=${f.fid} [${f.severityClass}/${f.label}${f.blocking ? '/blocking' : ''}] ${f.file}:${f.line}\n${f.title}\n  problem: ${f.problem}\n  recommendation: ${f.recommendation}`
  const list = ACTIONABLE.map(renderFinding).join('\n\n')
  const runJudge = (stance, tag) =>
    agent(`${GROUND}\n\n${judgeDoctrine}\n\n${stance}\n\n## Findings to judge (${ACTIONABLE.length})\n${list}\n\nReturn one verdict per fid. Every fid must appear exactly once.`,
      { label: `judge${tag}`, phase: 'Judge', schema: JUDGE_SCHEMA, model: 'opus' })

  // Two independent judges with slightly different stances (diversity beats redundancy).
  const stances = [
    'STANCE: try hard to REFUTE each finding on facts and reachability — but only mark false-positive when you can quote the evidence that refutes it.',
    'STANCE: judge each on context-grounding and author intent vs surface pattern-matching — keep genuinely grounded findings valid even if small, and only mark false-positive with quoted evidence.',
  ]
  const passes = await parallel(stances.map((s, i) => () => runJudge(s, `:${i + 1}`)))
  allVerdicts = passes.map((p) => (p && p.verdicts) || [])
  if (!passes[0] || !passes[1]) log(`⚠ ${passes.filter(Boolean).length}/2 judges returned — reconciliation will be one-sided; treat with caution.`)
}

// ── JS reconciliation (deterministic — not left to a model) ──
// false-positive ONLY on unanimous, evidence-backed agreement. Otherwise valid (never bury a
// real bug) unless BOTH judges (or the lone survivor) said needs-human.
const byFid = new Map()
for (const pass of allVerdicts) for (const v of pass) {
  if (!byFid.has(v.fid)) byFid.set(v.fid, [])
  byFid.get(v.fid).push(v)
}
const hasEvidence = (v) => v.category === 'false-positive' && v.evidence && v.evidence.trim().length >= 12

const falsePositives = [], valid = [], needsHuman = []
for (const f of ACTIONABLE) {
  const vs = byFid.get(f.fid) || []
  if (!vs.length) { needsHuman.push({ fid: f.fid, title: f.title, file: f.file, line: f.line, why: '판정자가 이 지적에 대한 verdict를 반환하지 않음 — 사람이 직접 확인 필요' }); continue }
  const fpVotes = vs.filter(hasEvidence)
  const validVotes = vs.filter((v) => v.category === 'valid')
  const humanVotes = vs.filter((v) => v.category === 'needs-human')
  const unanimousFP = fpVotes.length === vs.length && vs.length >= 1 // all present votes are evidence-backed FP

  if (unanimousFP && vs.length === 2) {
    falsePositives.push({ fid: f.fid, title: f.title, file: f.file, line: f.line, reason: fpVotes.map((v) => v.reason).join(' / '), evidence: fpVotes.map((v) => v.evidence).join(' | '), agreement: 'unanimous' })
  } else if (validVotes.length >= 1) {
    const tier = Math.min(...validVotes.map((v) => v.adjustedTier || f.tier || 2))
    const disputed = fpVotes.length >= 1 // one judge said FP, the other said valid
    valid.push({ fid: f.fid, title: f.title, file: f.file, line: f.line, adjustedTier: tier, note: [...validVotes.map((v) => v.note).filter(Boolean), disputed ? '⚠ 판정 갈림: 한 명은 오탐 주장(근거 병기) — 사람이 최종 확인 권장' : ''].filter(Boolean).join(' · '), disputed })
  } else if (humanVotes.length >= 1) {
    needsHuman.push({ fid: f.fid, title: f.title, file: f.file, line: f.line, why: humanVotes.map((v) => v.note || v.reason).filter(Boolean).join(' / ') || '코드만으로 오탐/유효 확정 불가' })
  } else {
    // e.g. lone FP without evidence, or a single unanimous-but-unpaired FP → conservative: needs-human
    needsHuman.push({ fid: f.fid, title: f.title, file: f.file, line: f.line, why: `오탐 주장이 만장일치·근거 요건을 못 채움 → 보수적으로 사람 확인. 사유: ${vs.map((v) => v.reason).join(' / ')}` })
  }
}

log(`judged ${ACTIONABLE.length}: ${falsePositives.length} false-positive (unanimous+evidence), ${valid.length} valid, ${needsHuman.length} needs-human`)

return {
  reportPath: A.reportPath,
  scenario: SCENARIO,
  readOnly: true,
  falsePositives,
  valid,
  needsHuman,
  skipped: NON_ACTIONABLE.map((f) => ({ fid: f.fid, title: f.title, label: f.label })),
  stats: {
    totalFindings: FINDINGS.length,
    actionable: ACTIONABLE.length,
    falsePositives: falsePositives.length,
    valid: valid.length,
    needsHuman: needsHuman.length,
  },
}
