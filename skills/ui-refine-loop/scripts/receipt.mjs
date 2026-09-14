/**
 * 실행 영수증 — "실제로 쟀는가"를 사후에 확인할 수 있게 만든다.
 *
 * 왜 있나: 2026-09-07 외부 평가자(skills-estimate)가 이 스킬의 가장 깊은 구멍을 짚었다 —
 *   *"「대상을 안 정하고 넘어가는」 우회는 코드로 막혔지만, 「정한 대상에 대해 실제로 계측했다」는
 *   정직성은 여전히 에이전트 자율에 의존한다."*
 * 표만 그럴듯하게 채워 넣는 것을 문서 규율로는 못 막는다. 그래서 계측기가 **자기가 무엇을 쟀는지**
 * 를 요약하고 그 요약의 지문을 함께 찍는다. 보고할 때 이 블록을 그대로 옮기게 하면,
 * 안 돌리고 쓴 보고서는 영수증을 못 만든다.
 *
 * ⚠️ 이건 위조 방지 장치가 **아니다.** 마음먹고 지어내는 것을 막지 못한다. 막는 것은
 *    「돌린 셈 치고 넘어가기」라는 훨씬 흔한 실패다. 같은 하네스의 `decision_receipt.py` 와 같은 계열.
 * ⚠️ 영수증에는 **못 본 것**이 반드시 함께 들어간다. 판정만 들어간 영수증은 「지적 없음」과
 *    「감사 못함」을 다시 섞는다.
 */
import { createHash } from 'node:crypto';

/** 계측이 원리적으로 못 보는 축. 보고에서 빠지면 그 보고는 두 가지를 섞은 것이다. */
export const UNMEASURED_AXES = [
  '발견가능성(스크롤·접힘·탭 뒤의 콘텐츠를 알아챌 단서)',
  '카피·문구(라벨이 실제로 이해되는가)',
  '브랜드·톤(제품답게 보이는가)',
  '상호작용(hover·open·error 상태, 애니메이션)',
  '켜지 않은 모드(다크·인쇄·로그인 필요 화면)',
];

/**
 * @param {object} p
 * @param {string} p.tool      실행한 스크립트 이름
 * @param {string} p.target    base URL 또는 파일 URL
 * @param {Array}  p.shots     [{ label, findings, coverage }]
 * @param {string[]} [p.notes] 추가로 남길 한 줄들(빈 화면·접근 실패 등)
 */
export function buildReceipt({ tool, target, shots, notes = [] }) {
  const at = new Date().toISOString();
  // 지문의 재료는 **측정 결과**다. 대상 목록만으로는 "열어보기만 해도" 같은 값이 나온다.
  const canon = shots
    .map((s) => `${s.label}:${s.findings}:${s.coverage == null ? 'na' : s.coverage.toFixed(3)}`)
    .sort()
    .join('|');
  const digest = createHash('sha256').update(`${tool}\u0000${target}\u0000${canon}`).digest('hex').slice(0, 12);

  const L = [];
  L.push('■ 실행 영수증 — 보고할 때 이 블록을 그대로 옮긴다');
  L.push(`   도구 ${tool} · 시각 ${at}`);
  L.push(`   대상 ${target}`);
  L.push(`   실측 ${shots.length}회: ${shots.map((s) => s.label).join(', ')}`);
  const covs = shots.map((s) => s.coverage).filter((c) => c != null);
  if (covs.length) {
    L.push(`   커버리지 최저 ${Math.round(Math.min(...covs) * 100)}% / 최고 ${Math.round(Math.max(...covs) * 100)}%`);
  }
  L.push(`   판정 합계 ${shots.reduce((a, s) => a + (s.findings || 0), 0)}건`);
  for (const n of notes) L.push(`   ${n}`);
  L.push('   못 본 축(계측 밖 — "지적 없음"이 아니라 "감사 못함"):');
  for (const a of UNMEASURED_AXES) L.push(`     · ${a}`);
  L.push(`   지문 ${digest}`);
  L.push('   ⚠️ 이 영수증이 없는 보고는 계측하지 않은 것으로 간주한다.');
  return L.join('\n');
}
