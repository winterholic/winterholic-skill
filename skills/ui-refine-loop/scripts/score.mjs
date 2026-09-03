#!/usr/bin/env node
/**
 * 5층 채택 판정 — 하드 불변식 → 사전식 비교 → 타이브레이크.
 *
 *   node scripts/score.mjs --prev .ui-refine/round-0 --next .ui-refine/round-1 \
 *     [--resolved 3] [--pixel-budget 0.02]
 *
 * 종료 코드: 0 채택 / 1 기각(롤백) / 2 불변식 위반(무조건 기각)
 * stdout 에 판정 JSON.
 */
import { readFile } from 'node:fs/promises';
import { join } from 'node:path';

// 앞 항이 같을 때만 다음 항을 본다. 가중치를 지어낼 근거가 없고 단위가 통약 불가하다.
// 대비·타겟은 1a 라 매 라운드 자동수정돼 항상 0 인 죽은 항이므로 넣지 않는다.
// 앞쪽일수록 사용자가 먼저 다치는 것. 읽기·조작을 막는 것 → 구조가 깨진 것 → 리듬이 어긋난 것 순.
const ORDER = [
  'overflow',          // 잘려서 못 읽음
  'undefined-var',     // 속성이 통째로 무효 — 값이 0 으로 무너진다
  'overlap',           // 겹쳐서 못 누름
  'collapsed',         // 상자가 무너져 내용이 들어갈 자리가 없다 — 요소 소실의 전조
  'dead-column',       // 화면 한쪽이 통째로 죽음 — 대개 margin:auto 누락
  'empty-cell',        // 결측/0 구분 불가 — 값을 오독한다
  'decimals',          // 자릿수 혼재 — 숫자를 오독한다
  'placeholder-label', // 입력 중 필드 정체 소실
  'required-mark',     // 필수 규칙 혼재
  'table-header',      // 스크롤 시 열 의미 소실
  'affordance',        // 클릭 가능 여부 불명
  'focus-missing',     // 키보드 사용자 위치 소실
  'hierarchy',         // 묶임이 뒤집힘
  'num-align',
  'row-height',
  'cell-padding',
  'double-indent',
  'repeat-padding',
  'control-ratio',
  'weight-variety',
  'input-width',
  'pad-asym',
  'gap-asym',
  'tabular-nums',
  'scale',
  'alignment',
  'cls',               // 로딩 중 레이아웃이 튄다 — SKILL.md 5-2 의 마지막 항
];

/**
 * ⚠️ CLS 는 건수가 아니라 실수라 그대로 비교하면 **측정 잡음이 곧 판정**이 된다.
 *    그렇다고 임계를 지어내면 이 스킬이 스스로 금지한 짓이다.
 *    → **Web Vitals 가 공개 표준으로 선언한 구간(0.1 / 0.25)** 으로 이산화해서 비교한다.
 *      우리가 만든 값이 아니라 밖에서 선언된 것을 읽는 것이라 원칙과 어긋나지 않는다.
 *    실측 배경: `cls: 0 → 0.9` 인 라운드가 `accept` 로 통과했다(ORDER 에 없어 표시만 됐다).
 */
function clsBand(v) {
  const x = Number(v) || 0;
  return x <= 0.1 ? 0 : (x <= 0.25 ? 1 : 2);
}

const args = parseArgs(process.argv.slice(2));
if (args.help) {
  console.log('usage: score.mjs --prev <round-dir> --next <round-dir> [--resolved N] [--self-test]');
  process.exit(0);
}
if (args['self-test']) runSelfTest();
if (!args.prev || !args.next) {
  console.error('usage: score.mjs --prev <round-dir> --next <round-dir> [--resolved N]');
  process.exit(2);
}
const prev = JSON.parse(await readFile(join(args.prev, 'summary.json'), 'utf8'));
const next = JSON.parse(await readFile(join(args.next, 'summary.json'), 'utf8'));

const schemaErrors = [...validateSummary(prev, 'prev'), ...validateSummary(next, 'next')];
if (schemaErrors.length) emit({ verdict: 'reject-invariant', violations: schemaErrors }, 2);

const violations = checkInvariants(prev, next, Number(args['pixel-budget'] ?? 0.02));
if (violations.length) {
  emit({ verdict: 'reject-invariant', violations }, 2);
}

// cls 는 counts 밖에 있으므로 비교 직전에 합류시킨다(ORDER 의 마지막 항).
const prevScore = { ...prev.counts, cls: clsBand(prev.cls) };
const nextScore = { ...next.counts, cls: clsBand(next.cls) };
const cmp = lexCompare(prevScore, nextScore);

/**
 * ★ 사전식만으로는 **1순위 1건 개선이 하위 전 항의 무제한 악화를 산다.**
 *   실측: `overflow 3→2` 하나로 `alignment 2→202`·`scale 1→81`·`pad-asym 0→30` 이 통과했다.
 *   사전식을 고른 이유는 "통약 불가한 단위를 가중합하지 않는다"였는데, **건수 총량**은
 *   가중치를 지어내지 않고도 셀 수 있다(모든 판정을 1로 세는 것이 곧 무가중이다).
 *   → 채택은 「사전식 개선」과 「총 건수 비증가」를 **둘 다** 만족해야 한다.
 *   트레이드오프가 실제로 있는 수정(하나 고치고 둘 생김)은 사람이 봐야 하므로 기각이 맞다.
 */
const total = (c) => Object.values(c).reduce((a2, b2) => a2 + (Number(b2) || 0), 0);
const regressions = Object.entries(nextScore)
  .filter(([k, v]) => (Number(v) || 0) > (Number(prevScore[k]) || 0))
  .map(([k, v]) => `${k}: ${prevScore[k] ?? 0} → ${v}`);

if (cmp === 'worse') {
  emit({ verdict: 'reject', reason: 'lexicographic-regression', diff: diffCounts(prev, next) }, 1);
}

if (cmp === 'better') {
  if (total(nextScore) > total(prevScore)) {
    emit({ verdict: 'reject', reason: 'total-regression',
           detail: `상위 항은 개선됐지만 총 건수가 ${total(prevScore)} → ${total(nextScore)} 로 늘었다`,
           regressions, diff: diffCounts(prev, next) }, 1);
  }
  emit({ verdict: 'accept', reason: 'lexicographic-improvement',
         regressions, diff: diffCounts(prev, next) }, 0);
}

// 동점. "엄격히 초과"를 쓰면 이 스킬의 최대 수익 구간(시각 위계 수정)이 1층 점수를 바꾸지
// 않아 매 라운드 기각된다 — 스킬이 아무것도 고치지 않게 된다.
// 타이브레이커는 LLM finding 을 점수에 넣는 게 아니라 동점 판정에만 쓰므로
// 오탐이 순위를 뒤집지 못한다.
const resolved = Number(args.resolved ?? 0);
if (resolved > 0) {
  emit({ verdict: 'accept', reason: `tie-break: ${resolved} findings resolved`,
         diff: diffCounts(prev, next) }, 0);
}

emit({ verdict: 'reject', reason: 'tie with no resolved findings', diff: diffCounts(prev, next) }, 1);

// ---------- 판정 ----------

/**
 * 요소를 지우면 모든 결정론적 지표가 동시에 개선된다 — 불변식이 없으면 빈 화면이 만점이다.
 * 그래서 점수보다 먼저 본다.
 */
function checkInvariants(a, b, pixelBudget) {
  const v = [];
  if (b.invariants.domNodeCount < a.invariants.domNodeCount) {
    v.push(`DOM 노드 수 감소: ${a.invariants.domNodeCount} → ${b.invariants.domNodeCount}`);
  }
  if (b.invariants.textHash !== a.invariants.textHash) {
    v.push('텍스트 콘텐츠 해시 변경 — 수정이 문구를 건드렸다');
  }
  const captureKey = (s) => JSON.stringify(s.shots.map(({ route, viewport, state, colorScheme, media }) =>
    ({ route, viewport, state, colorScheme, media })));
  if (captureKey(a) !== captureKey(b)) v.push('캡처 세트 변경 — 같은 라우트·뷰포트·상태가 아니다');
  return v;
}

function validateSummary(s, label) {
  const v = [];
  if (s?.schemaVersion !== 2) v.push(`${label}: summary schemaVersion 2가 필요하다`);
  if (!s?.counts || typeof s.counts !== 'object') v.push(`${label}: counts 누락`);
  if (!s?.invariants || !Number.isFinite(s.invariants.domNodeCount) || typeof s.invariants.textHash !== 'string') {
    v.push(`${label}: invariants.domNodeCount/textHash 누락`);
  }
  if (!Array.isArray(s?.shots) || s.shots.length === 0) v.push(`${label}: shots 누락 또는 빈 배열`);
  if (s?.emptyShots?.length) v.push(`${label}: 빈 화면이 포함되어 점수 비교 불가`);
  return v;
}

function lexCompare(a, b) {
  for (const k of ORDER) {
    const pa = a[k] ?? 0, pb = b[k] ?? 0;
    if (pb < pa) return 'better';
    if (pb > pa) return 'worse';
  }
  return 'tie';
}

function diffCounts(a, b) {
  const d = {};
  for (const k of ORDER) d[k] = `${a.counts[k] ?? 0} → ${b.counts[k] ?? 0}`;
  d.cls = `${a.cls ?? 0} → ${b.cls ?? 0}`;
  return d;
}

function emit(obj, code) {
  console.log(JSON.stringify(obj, null, 2));
  process.exit(code);
}

function runSelfTest() {
  const shot = { route: '/', viewport: '360', state: 'default', colorScheme: 'light', media: 'screen' };
  const base = { schemaVersion: 2, counts: { overflow: 1 }, cls: 0,
    invariants: { domNodeCount: 30, textHash: 'same' }, shots: [shot], emptyShots: [] };
  const cases = [
    ['valid', validateSummary(base, 'x').length === 0],
    ['schema-missing', validateSummary({ ...base, schemaVersion: undefined }, 'x').length === 1],
    ['empty-shot', validateSummary({ ...base, emptyShots: ['x'] }, 'x').length === 1],
    ['dom-regression', checkInvariants(base, { ...base, invariants: { ...base.invariants, domNodeCount: 29 } }, 0.02).length === 1],
    ['capture-drift', checkInvariants(base, { ...base, shots: [{ ...shot, viewport: '1440' }] }, 0.02).length === 1],
  ];
  const failed = cases.filter(([, ok]) => !ok);
  for (const [name, ok] of cases) console.log(`${ok ? 'PASS' : 'FAIL'} ${name}`);
  process.exit(failed.length ? 1 : 0);
}

function parseArgs(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i++) {
    if (!argv[i].startsWith('--')) continue;
    const key = argv[i].slice(2);
    const nxt = argv[i + 1];
    if (!nxt || nxt.startsWith('--')) { out[key] = true; } else { out[key] = nxt; i++; }
  }
  return out;
}
