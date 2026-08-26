export const meta = {
  name: 'lite-research',
  description: 'Lightweight investigation harness — 2-4 heterogeneous agents, SINGLE round, hard-capped (no loops in this script). Three kinds: external (web facts — primary-source searcher + counterexample hunter + optional batched verifier), codebase (1-2 read-only Explore scouts on different angles), compare (two independent advocates, main loop judges). Question and context are passed inline ONCE; the main loop synthesizes with source-weighted judgment — it does not relay.',
  phases: [
    { title: 'Gather', detail: 'heterogeneous gatherers in parallel, mutually blind' },
    { title: 'Verify', detail: 'ONE batched skeptic judges all claims (external std only)' },
  ],
}

// ── args (assembled ONCE by the main loop) ──
// {
//   question: string,          // the single question to answer, 1-2 sentences
//   kind: 'external' | 'codebase' | 'compare',
//   context: string,           // everything relevant the main already knows: constraints, stack, prior findings, user's situation
//   depth: 'lite' | 'std',     // lite = gatherers only, std = + batched verifier (external) / second scout (codebase)
//   options: [string, string], // compare only: the two options under comparison
//   projectRoot: string,       // codebase only: absolute path to search in
// }
let A = args || {}
if (typeof A === 'string') { try { A = JSON.parse(A) } catch (_) { A = {} } }
const KIND = A.kind || 'external'
const DEPTH = A.depth || 'lite'

// Fail LOUD on missing inputs (spar/senior-review lesson — never silently degrade).
if (!A.question) log('⚠ STABILITY WARNING: no question — agents have nothing to investigate. Main loop must pass args.question.')
if (KIND === 'compare' && (!A.options || A.options.length < 2)) log('⚠ STABILITY WARNING: compare kind needs args.options = [A, B].')
if (KIND === 'codebase' && !A.projectRoot) log('⚠ STABILITY WARNING: codebase kind without projectRoot — scouts may search the wrong tree.')

const GROUND = `## The question
**${A.question || '(none provided)'}**

## What the main loop already knows (do not re-derive)
${A.context || '(no context provided)'}

## Investigation doctrine (non-negotiable)
1. Your output is an INDEPENDENT report — you have not seen any other agent's output; do not imagine one to agree with.
2. Every claim carries a SOURCE (URL / file:line / named doc). A claim without a source is marked confidence "low" and sourceType "inference" — never dressed up as fact.
3. Distinguish "no evidence found" from "evidence of absence" — say which one you have.
4. TOKEN BUDGET: this is a LIGHT pass — at most ~5 searches / ~3 page fetches (or ~12 tool calls for code scouting). Depth-first on the most promising lead, not breadth-first sweeping. If the budget runs out, report gaps honestly instead of stretching.
5. This is your ONLY round. No follow-up pass exists. Front-load the strongest findings.`

const CLAIMS_SCHEMA = {
  type: 'object',
  properties: {
    role: { type: 'string' },
    answerDraft: { type: 'string', description: 'your best one-paragraph answer to the question from your angle' },
    claims: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          cid: { type: 'integer', description: 'sequential id starting at 1' },
          claim: { type: 'string' },
          source: { type: 'string', description: 'URL / file:line / named doc — or "추정" if none' },
          sourceType: { type: 'string', enum: ['official', 'community', 'code', 'inference'] },
          confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
        },
        required: ['cid', 'claim', 'source', 'sourceType', 'confidence'],
      },
    },
    gaps: { type: 'array', items: { type: 'string' }, description: 'what you could NOT confirm within budget' },
  },
  required: ['role', 'answerDraft', 'claims', 'gaps'],
}

phase('Gather')
let gathered = []

if (KIND === 'external') {
  const plan = [
    {
      label: 'gather:official',
      prompt: `${GROUND}\n\n## Your angle: OFFICIAL / PRIMARY SOURCES\nHunt official documentation, release notes, changelogs, specs, vendor announcements, primary maintainer statements. Prefer the most recent dated source; note the date. Version-sensitive claims MUST name the version.`,
    },
    {
      label: 'gather:field',
      prompt: `${GROUND}\n\n## Your angle: FIELD REPORTS & COUNTEREXAMPLES\nHunt what official sources won't say: GitHub issues, bug trackers, postmortems, Stack Overflow, HN/Reddit practitioner reports. Your job is the FAILURE side — known breakages, regressions, "works except when", migration pain, abandoned-project signals. If the field broadly confirms the happy path, say so honestly.`,
    },
  ]
  gathered = await parallel(plan.map((p) => () => agent(p.prompt, { label: p.label, phase: 'Gather', schema: CLAIMS_SCHEMA })))
} else if (KIND === 'codebase') {
  const plan = [
    {
      label: 'scout:definition',
      prompt: `${GROUND}\n\n## Your angle: DEFINITION & STRUCTURE\nIn ${A.projectRoot || '(project root unspecified)'}: find where the thing is DEFINED — types, classes, schemas, configs, the module that owns it. Report concrete file:line. Read-only.`,
    },
    {
      label: 'scout:usage',
      prompt: `${GROUND}\n\n## Your angle: USAGE & FLOW\nIn ${A.projectRoot || '(project root unspecified)'}: find where the thing is USED — call sites, wiring, tests, error paths. Who depends on it and how does data flow through it. Report concrete file:line. Read-only.`,
    },
  ]
  const n = DEPTH === 'std' ? 2 : 1
  gathered = await parallel(plan.slice(0, n).map((p) => () =>
    agent(p.prompt, { label: p.label, phase: 'Gather', schema: CLAIMS_SCHEMA, agentType: 'Explore' })))
} else if (KIND === 'compare') {
  const [optA, optB] = A.options || ['(option A)', '(option B)']
  const mk = (mine, other) => `${GROUND}\n\n## Your role: ADVOCATE for **${mine}**\nMake the strongest honest case for ${mine} over ${other} IN THIS CONTEXT (not in general). Ground arguments in the inline context and verifiable facts (cite sources). Name the real costs of your side and why they're worth it — a forced defense poisons the synthesis; if your side is indefensible here, say so with confidence "low".`
  gathered = await parallel([
    () => agent(mk(optA, optB), { label: `advocate:${String(optA).slice(0, 16)}`, phase: 'Gather', schema: CLAIMS_SCHEMA }),
    () => agent(mk(optB, optA), { label: `advocate:${String(optB).slice(0, 16)}`, phase: 'Gather', schema: CLAIMS_SCHEMA }),
  ])
}

const reports = gathered.filter(Boolean)
if (!reports.length) {
  log('⚠ all gatherers failed — nothing to synthesize. Main loop should answer directly (solo) and tell the user the harness run was lost.')
  return { question: A.question, kind: KIND, depth: DEPTH, reports: [], verification: null, failed: true }
}
if (reports.length < gathered.length) log(`⚠ ${gathered.length - reports.length} gatherer(s) lost — synthesis will be one-sided. Main loop must weigh accordingly and say so.`)

// ── Batched verification: ONE skeptic judges every claim (external std only).
// Per-claim verifier fan-out is the #1 cost driver in heavy research harnesses — never do that here.
phase('Verify')
let verification = null
if (KIND === 'external' && DEPTH === 'std' && reports.length) {
  const allClaims = reports.flatMap((r, ri) => (r.claims || []).map((c) => ({ ...c, gid: `${ri + 1}-${c.cid}`, from: r.role })))
  const VERIFY_SCHEMA = {
    type: 'object',
    properties: {
      verdicts: {
        type: 'array',
        items: {
          type: 'object',
          properties: {
            gid: { type: 'string' },
            verdict: { type: 'string', enum: ['confirmed', 'refuted', 'unverifiable'] },
            reason: { type: 'string' },
            correction: { type: 'string', description: 'the corrected fact if refuted, else empty' },
          },
          required: ['gid', 'verdict', 'reason', 'correction'],
        },
      },
      conflicts: { type: 'array', items: { type: 'string' }, description: 'claims that genuinely contradict each other across reports — escalation signal' },
    },
    required: ['verdicts', 'conflicts'],
  }
  verification = await agent(
    `${GROUND}\n\n## Claims to judge (${allClaims.length})\n${allClaims.map((c) => `- [${c.gid}] (${c.sourceType}/${c.confidence}) ${c.claim} — src: ${c.source}`).join('\n')}\n\nYou are ONE independent skeptic judging ALL claims in a single pass — try to REFUTE each on facts, source quality, version mismatch, and date staleness. Spot-check at most 3 cited sources (budget). "inference"-type claims default to unverifiable unless trivially derivable. List genuine cross-report contradictions in conflicts — that list decides whether the main loop escalates to deep-research.`,
    { label: 'verify:batch', phase: 'Verify', schema: VERIFY_SCHEMA }
  )
  if (!verification) log('⚠ verifier lost — claims go to the main loop UNVERIFIED. Synthesis must label them as such.')
}

// 1-round hard cap is structural: no loops exist in this script (spar workflow.js와 동일 원칙).
return {
  question: A.question,
  kind: KIND,
  depth: DEPTH,
  reports,
  verification,
  // Main loop: SYNTHESIZE per SKILL.md — weigh by sourceType+verdict, surface gaps/conflicts,
  // escalate to deep-research only on unresolved conflicts the user cares about.
}
