export const meta = {
  name: 'spar-council',
  description: "Spar Council mode — a heterogeneous-role mini debate (advocate / devil's advocate / optional judge). SINGLE round, hard-capped: no rebuttals, no loops, 2-3 agents total. Context is gathered ONCE by the main loop and passed inline (agents do not re-explore). Council agents write INDEPENDENT briefs (no cross-exposure in the round — structural sycophancy guard); the optional judge is the only agent that sees both. The main loop synthesizes — it does not relay.",
  phases: [
    { title: 'Council', detail: 'advocate + critic in parallel, independent briefs over inline context' },
    { title: 'Judge', detail: 'optional 3rd agent — weighs both briefs, commits to a side (only when args.judge)' },
  ],
}

// ── args (gathered ONCE by the skill's main loop — agents must NOT re-fetch) ──
// {
//   topic: string,           // the decision or bug, 1-2 sentences
//   kind: 'design' | 'bug',
//   position: string,        // main reasoner's current best guess / leading option — what the advocate defends
//   alternatives: [string],  // competing options / hypotheses — the critic's starting ammunition
//   context: string,         // ALL relevant material inline: code excerpts, constraints, prior debate state
//   userStance: string,      // what the user thinks, if stated
//   judge: boolean,          // spawn the 3rd (judge) agent? default false — main synthesizes instead
// }
// args may arrive as a parsed object OR a JSON-encoded string (harness-dependent) — parse defensively.
let A = args || {}
if (typeof A === 'string') { try { A = JSON.parse(A) } catch (_) { A = {} } }

// Fail LOUD on missing inputs instead of silently degrading (senior-review 'lite-misfire' lesson).
if (!A.topic || !A.position) {
  log('⚠ STABILITY WARNING: topic/position missing — the council has nothing concrete to argue. Main loop must pass both.')
}
if (!A.context) {
  log('⚠ STABILITY WARNING: no inline context — agents are forbidden from exploring, so briefs will be shallow. Pass code/constraints inline via args.context.')
}

const FORBID = '**Do NOT explore the repo (no grep / glob / directory browsing / broad reading).** Everything you need is inline below — per-agent re-exploration is the #1 token waste and is forbidden. ONLY exception: if your argument genuinely hinges on ONE specific file named in the context, you may Read that single file once — and say so in your brief.'

const GROUND = `## The question under debate
**${A.topic || '(no topic provided)'}** — kind: ${A.kind || 'design'}

## Leading position (the main reasoner's current best guess)
${A.position || '(none provided)'}

## Competing alternatives
${(A.alternatives || []).map((x, i) => `${i + 1}. ${x}`).join('\n') || '(none stated — identify the strongest one yourself)'}

## User's stance
${A.userStance || '(not stated)'}

## Inline context (gathered once by the main loop — this is ALL you get)
${A.context || '(none provided)'}

${FORBID}

## Debate doctrine (anti-sycophancy — non-negotiable)
1. Your brief is INDEPENDENT. You have not seen any other agent's output; do not imagine one to converge with. Heterogeneity is the entire value of this council — consensus-seeking is its documented failure mode.
2. Commit to your assigned role even if you privately lean the other way. BUT honesty outranks the role: if after real effort your side is indefensible, say so explicitly with confidence "low" — a forced argument poisons the synthesis.
3. Every claim needs a basis: the inline context, or a NAMED engineering principle / known failure pattern. No basis ⇒ mark the point "추정".
4. Be concrete — name files, flows, failure modes, costs, scales. "It depends" without naming what it depends ON is a non-answer.
5. This is your ONLY round. There is no rebuttal. Front-load your strongest material; cut the throat-clearing.`

const BRIEF_SCHEMA = {
  type: 'object',
  properties: {
    role: { type: 'string', enum: ['advocate', 'critic'] },
    verdict: { type: 'string', description: 'one-sentence bottom line of this brief' },
    confidence: { type: 'string', enum: ['high', 'medium', 'low'] },
    arguments: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          point: { type: 'string' },
          basis: { type: 'string', description: 'what in the inline context — or which named principle / failure pattern — supports this. "추정" if neither.' },
        },
        required: ['point', 'basis'],
      },
    },
    hiddenAssumptions: { type: 'array', items: { type: 'string' }, description: 'assumptions the position silently relies on (advocate: ones you accept and why; critic: ones that break first)' },
    falsifiableCheck: { type: 'string', description: 'ONE concrete check (command, test, log to read, observation) that would settle the biggest open question cheaply' },
  },
  required: ['role', 'verdict', 'confidence', 'arguments', 'hiddenAssumptions', 'falsifiableCheck'],
}

// ── Round 1 (and only): advocate + critic, parallel, mutually blind ───────────
phase('Council')
const [advocate, critic] = await parallel([
  () => agent(`${GROUND}

## Your role: ADVOCATE (옹호자)
Steelman the leading position as its best possible defender. Make the STRONGEST honest case: what it buys, why its costs are worth paying, why each listed alternative loses. You are not a cheerleader — name the position's real weaknesses yourself, then show why they don't change the verdict. If they do change the verdict, say so.`,
    { label: 'council:advocate', phase: 'Council', schema: BRIEF_SCHEMA }),
  () => agent(`${GROUND}

## Your role: DEVIL'S ADVOCATE (비판자)
Attack the leading position as its strongest honest opponent. Hunt: the failure mode it ignores, the hidden assumption that breaks first, the regime (scale / edge case / timeline / team reality) where it goes wrong, the cheaper alternative it dismisses too fast. Then name the STRONGEST competing alternative and the conditions under which it wins. You are not contrarian theater — if the position survives every attack you can honestly mount, report that (confidence "low" on refutation) instead of manufacturing objections.`,
    { label: 'council:critic', phase: 'Council', schema: BRIEF_SCHEMA }),
])

if (!advocate && !critic) {
  log('⚠ both council agents failed — nothing to synthesize. Main loop should fall back to Quick mode.')
  return { topic: A.topic, briefs: { advocate: null, critic: null }, judge: null, failed: true }
}
if (!advocate) log('⚠ advocate brief lost — synthesis will be one-sided (critic only). Weigh accordingly.')
if (!critic) log('⚠ critic brief lost — synthesis will be one-sided (advocate only). Weigh accordingly.')

// ── Optional judge: the ONLY agent that sees both briefs ──────────────────────
let judge = null
if (A.judge && advocate && critic) {
  phase('Judge')
  const JUDGE_SCHEMA = {
    type: 'object',
    properties: {
      winner: { type: 'string', enum: ['advocate', 'critic', 'split'] },
      reasoning: { type: 'string', description: 'which arguments actually rest on the inline context vs hand-waving, and why the winner wins' },
      decisiveFactor: { type: 'string', description: 'the single consideration that most determines the answer' },
      whatWouldChangeMyMind: { type: 'string' },
      recommendation: { type: 'string', description: 'concrete next step — often the cheapest falsifiableCheck from either brief' },
    },
    required: ['winner', 'reasoning', 'decisiveFactor', 'whatWouldChangeMyMind', 'recommendation'],
  }
  judge = await agent(`${GROUND}

## Advocate brief
\`\`\`json
${JSON.stringify(advocate, null, 2)}
\`\`\`

## Critic brief
\`\`\`json
${JSON.stringify(critic, null, 2)}
\`\`\`

## Your role: JUDGE (판정자)
Weigh both briefs on merit and COMMIT. Sycophantic convergence ("both have a point") is the documented failure mode of LLM debate — a verdict without a side is a non-verdict. Separate context-grounded arguments from hand-waving (the basis field tells you which is which), name the decisive factor, and pick a winner. "split" is allowed ONLY with the explicit condition that separates the two regimes (e.g. "below X scale critic wins, above it advocate wins").`,
    { label: 'council:judge', phase: 'Judge', schema: JUDGE_SCHEMA })
}

// 1-round hard cap is structural: no loops exist in this script. Do not add rounds —
// accuracy degrades with debate rounds (arXiv 2509.05396; Nature s41598-026-42705-7).
return {
  topic: A.topic,
  kind: A.kind,
  position: A.position,
  briefs: { advocate, critic },
  judge,
  // Main loop: SYNTHESIZE per SKILL.md — do not relay raw briefs. Weigh them, update your own
  // stance with confidence, surface the cheapest falsifiableCheck, and hand the ball to the user.
}
