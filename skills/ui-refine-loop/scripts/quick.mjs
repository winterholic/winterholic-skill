#!/usr/bin/env node
/**
 * T0 단발 진단 — 라운드도, 비평가도, 산출 파일도 없다.
 *
 *   node scripts/quick.mjs --url http://localhost:3000/orders
 *   node scripts/quick.mjs --url ... --viewport 1440x900 --full
 *   node scripts/quick.mjs --self-test        # 실브라우저 negative control
 *
 * 왜 이게 있나
 * -----------
 * 이 스킬은 2026-08-16 이후 UI 세션 94건 동안 **한 번도 호출되지 않았다.** 도구가 없어서가
 * 아니라 **진입 비용이 요청 크기와 안 맞아서**다. "이 카드가 좀 헐거워 보여" 한마디에
 * 3라운드 멀티에이전트 루프와 12항목 사전점검을 켤 이유가 없으니, 매번 다른 경로로 샜다.
 *
 * 그래서 이 파일은 **한 화면을 한 번 재고 사람이 읽는 문단으로 끝낸다.** 30초 안에 끝나고
 * 아무 파일도 남기지 않는다. 여기서 구조 문제가 드러나면 그때 T1·T2 로 올린다.
 *
 * 보고 순서가 곧 설계다 — **무엇을 못 봤는지를 먼저 말한다.** 판정 목록을 먼저 보이면
 * 사람은 그걸 전부로 읽는다(실측 2026-08-15: 문서의 19% 만 감사하고 "accept" 를 냈다).
 *
 * 종료 코드: 0 정상 / 1 사용법 오류 / 3 playwright 없음 / 4 빈 화면(404·렌더 실패)
 */
import { readFile } from 'node:fs/promises';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
import { buildReceipt } from './receipt.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const args = parseArgs(process.argv.slice(2));

if (args.help || (!args.url && !args['self-test'])) {
  console.log('usage: quick.mjs --url <url> [--viewport 1440x900] [--full] [--config .ui-refine.json] [--json]');
  console.log('       quick.mjs --self-test');
  process.exit(args.help ? 0 : 1);
}

// playwright 는 이 스킬의 의존성이 아니라 **대상 프로젝트에서 빌려 쓴다.** 없으면 조용히
// 넘어가지 않고 exit 3 으로 끝낸다 — "확인 못함"을 "문제 없음"으로 읽히게 두지 않는다.
const { chromium } = await (async () => {
  try { return await import('playwright'); } catch { /* 스킬 디렉터리엔 없다 */ }
  const req = createRequire(join(process.cwd(), 'noop.js'));
  for (const pkg of [process.env.PLAYWRIGHT_PATH, 'playwright', 'playwright-core', '@playwright/test'].filter(Boolean)) {
    try { const m = req(pkg); if (m?.chromium) return m; } catch { /* 다음 후보 */ }
  }
  console.error('확인 못함: playwright 를 찾지 못했다.');
  console.error('  대상 프로젝트 루트에서 실행하거나 PLAYWRIGHT_PATH=<프로젝트>/node_modules/playwright 를 주라.');
  process.exit(3);
})();

const source = (await readFile(join(HERE, 'collect.js'), 'utf8')).replace(/^export\s+/gm, '');
const inBrowser = (call) => `(() => { ${source}\nreturn ${call}; })()`;

if (args['self-test']) await runSelfTest(); else await runOnce();

async function measure(url, { width, height, full, config }) {
  const browser = await chromium.launch({ args: ['--force-device-scale-factor=1', '--disable-gpu'] });
  try {
    const ctx = await browser.newContext({ viewport: { width, height }, deviceScaleFactor: 1 });
    const page = await ctx.newPage();
    await page.goto(url, { waitUntil: 'networkidle' });
    await page.evaluate(async () => { await document.fonts?.ready; });
    const scale = await page.evaluate(inBrowser('extractScale()'));
    const cfg = { ...config, spacingScale: config.spacingScale || scale.scale,
                  spacingBase: config.spacingBase || scale.base || 0, fullPage: !!full };
    const m = await page.evaluate(inBrowser(`collectPage(${JSON.stringify(cfg)})`));
    m.scale = scale;
    m.identity = await page.evaluate(() => ({
      url: location.href, title: document.title,
      // 지금 이 화면이 내가 재려던 그 화면인지 — "옛 프로세스 응답을 재고 완료를 보고한" 사고 방지
      lang: document.documentElement.lang || '(없음)',
      ua: navigator.userAgent.slice(0, 40),
    }));
    return m;
  } finally { await browser.close(); }
}

async function runOnce() {
  const [width, height] = (args.viewport || '1440x900').split('x').map(Number);
  if (!Number.isFinite(width) || !Number.isFinite(height)) {
    console.error('--viewport 는 1440x900 형식이다'); process.exit(1);
  }
  const config = args.config ? JSON.parse(await readFile(args.config, 'utf8')) : {};
  const m = await measure(args.url, { width, height, full: !!args.full, config });

  if (args.json) { console.log(JSON.stringify(m, null, 2)); }
  else { report(m, { width, height }); }

  if (m.domNodeCount < 20 || m.elements.length < 3) {
    console.error('\n⚠️ 화면이 비어 있다 — 404·라우팅 실패·렌더 전 캡처를 의심하라.');
    process.exit(4);
  }
}

/** 사람이 읽는 보고. **못 본 것을 먼저 말한다.** */
function report(m, vp) {
  const c = m.coverage;
  const L = [];
  L.push(`■ 대상  ${m.identity.url}`);
  L.push(`         ${vp.width}×${vp.height} · "${m.identity.title}" · lang=${m.identity.lang} · DOM ${m.domNodeCount}노드`);

  L.push('');
  L.push('■ 이번에 본 범위 (판정보다 먼저 읽는다)');
  if (c) {
    const pct = Math.round(c.ratio * 100);
    L.push(`   커버리지 ${pct}%  —  잰 높이 ${c.measuredH}px / 전체 ${c.docH + c.innerHidden}px (mode=${c.mode})`);
    if (c.innerHidden > 0) {
      L.push(`   ⚠️ 내부 스크롤 상자가 ${c.innerHidden}px 를 감추고 있다. 이 구조에서는 fullPage 가 아무 일도 안 한다.`);
      for (const s of c.innerScroll) L.push(`      ${s.selector}  보이는 높이 ${s.visibleH}px / 감춘 ${s.hidden}px`);
      L.push('      → .ui-refine.json 의 injectCss 로 높이 잠금을 풀고 다시 재라.');
    } else if (c.mode === 'viewport' && c.docH > c.viewportH) {
      L.push(`   ⚠️ 첫 화면만 쟀다. 아래 ${c.docH - c.viewportH}px 는 미감사다 — --full 을 주면 전체를 잰다.`);
    }
    if (pct < 100) L.push('   못 본 영역은 "지적 없음"이 아니라 "감사 못함"이다. 보고할 때 그대로 옮긴다.');
  }
  if (m.blindSpots) {
    const b = m.blindSpots;
    if (b.count) L.push(`   ⚠️ 교차 출처 iframe ${b.count}개는 원리적으로 못 읽는다: ${b.crossOriginFrames.join(', ')}`);
    if (b.cssCount) L.push(`   ⚠️ 교차 출처 스타일시트 ${b.cssCount}개를 못 읽어 ${b.suppressed.join('·')} 판정을 보류했다`);
  }
  L.push(`   스페이싱 스케일 모드 = ${m.scale?.source ?? '?'}${m.scale?.scale?.length ? ` [${m.scale.scale.join(', ')}]` : ''}`);
  if (m.scale?.source === 'frequency') {
    L.push('   ⚠️ frequency 는 추정 폴백이다 — 스케일 이탈 지적은 그만큼 덜 믿는다.');
  }

  const byNum = new Map(m.elements.map((e) => [e.n, e]));
  const structural = m.findings.filter((f) => f.kind === 'narrow-column');
  const rest = m.findings.filter((f) => f.kind !== 'narrow-column');

  if (structural.length) {
    L.push('');
    L.push('■ 구조 신호 — 자동수정 금지, 오너 확인 사항');
    for (const f of structural) {
      L.push(`   ▶ ${f.detail}`);
      for (const t of f.targets) L.push(`      #${t} ${byNum.get(t)?.selector ?? ''}`);
    }
    L.push('   승인 경계(existing-screen-edit 규율 7)에 걸린다. 다열 시안을 먼저 보이고 승인을 받는다.');
  }

  L.push('');
  if (!rest.length) {
    L.push(`■ 판정 0건 — 단, 위 커버리지 범위 안에서만이다.`);
  } else {
    const groups = new Map();
    for (const f of rest) { if (!groups.has(f.kind)) groups.set(f.kind, []); groups.get(f.kind).push(f); }
    L.push(`■ 판정 ${rest.length}건 (${groups.size}종)`);
    for (const [kind, fs] of [...groups].sort((a, b) => b[1].length - a[1].length)) {
      L.push(`   ${kind} ${fs.length}건`);
      for (const f of fs.slice(0, 3)) {
        const sel = f.targets.map((t) => byNum.get(t)?.selector).filter(Boolean)[0];
        L.push(`      ${f.detail}${sel ? `  ← ${sel}` : ''}`);
      }
      if (fs.length > 3) L.push(`      … 그 외 ${fs.length - 3}건 (--json 으로 전부 본다)`);
    }
  }
  L.push('');
  L.push('■ 다음 단계');
  L.push('   이 결과는 관찰이다. 원인이 아니다 — SKILL.md 3.5층대로 경쟁 가설을 세워 반증한 뒤 고친다.');
  L.push('');
  L.push(buildReceipt({
    tool: 'quick.mjs',
    target: m.identity.url,
    shots: [{ label: `${vp.width}x${vp.height}`, findings: m.findings.length,
              coverage: m.coverage ? m.coverage.ratio : null }],
    notes: m.blindSpots ? ['교차 출처 리소스가 있어 일부 판정을 보류했다'] : [],
  }));
  console.log(L.join('\n'));
}

/**
 * 실브라우저 negative control.
 *
 * ⚠️ **통과 개수는 근거가 아니다.** 이 테스트의 값은 대조군에 있다 — 픽스처에 일부러 넣은
 *    「정상인데 오탐하기 쉬운 것」이 안 잡히는지를 함께 본다. 잡히면 FAIL 이다.
 */
async function runSelfTest() {
  const fx = pathToFileURL(join(HERE, '..', 'assets', 'quick.fixture.html')).href;
  const wide = await measure(fx, { width: 1440, height: 900, full: false, config: {} });
  const narrowVp = await measure(fx, { width: 800, height: 900, full: false, config: {} });

  const kinds = (m) => new Set(m.findings.map((f) => f.kind));
  const wideKinds = kinds(wide);
  const nc = wide.findings.filter((f) => f.kind === 'narrow-column');
  const sel = (m, n) => m.elements.find((e) => e.n === n)?.selector || '';

  // 타이포·세로공간은 별도 픽스처다 — quick.fixture 는 내부 스크롤 셸이라 첫 뷰포트 밖 요소가
  // 측정에서 빠진다(설계대로다). 관심사를 섞지 않고 문서 스크롤 픽스처로 따로 잰다.
  const typoFx = pathToFileURL(join(HERE, '..', 'assets', 'typo.fixture.html')).href;
  const typo = await measure(typoFx, { width: 1280, height: 900, full: true, config: {} });
  const tsel = (n) => typo.elements.find((e) => e.n === n)?.selector || '';
  const hit = (kind, re) => typo.findings.some((f) => f.kind === kind
    && f.targets.some((t) => re.test(tsel(t))));
  const anyIn = (re) => typo.findings.some((f) => f.targets.some((t) => re.test(tsel(t))));

  const cases = [
    // ── 검출 ──
    ['narrow-column 검출 (1440에서 좁은 기둥 + 좌우 빈 띠)', nc.length === 1],
    ['narrow-column 이 지목한 것이 #doc-column 이다',
      nc.length === 1 && /doc-column/.test(nc.map((f) => f.targets.map((t) => sel(wide, t)).join()).join())],
    ['커버리지가 내부 스크롤 상자를 신고한다', wide.coverage.innerHidden > 0],
    ['커버리지 비율이 1 미만으로 떨어진다', wide.coverage.ratio < 1],
    ['감춘 높이를 실제로 센다 (>500px)', wide.coverage.innerHidden > 500],
    // ── 대조군: 잡히면 안 되는 것 ──
    ['대조군 ① 800px 뷰포트에서는 narrow-column 을 내지 않는다 (모바일은 한 기둥이 정상)',
      !kinds(narrowVp).has('narrow-column')],
    ['대조군 ② 좌우에 레일이 있는 다열 영역은 narrow-column 이 아니다',
      !nc.some((f) => f.targets.some((t) => /two-col/.test(sel(wide, t))))],
    ['대조군 ③ 중앙정렬 좁은 기둥이라도 dead-column 으로는 안 잡힌다 (대칭은 dead-column 소관 아님)',
      !wide.findings.some((f) => f.kind === 'dead-column' && f.targets.some((t) => /doc-column/.test(sel(wide, t))))],
    ['대조군 ④ 정상 화면을 통째로 결함으로 만들지 않는다 (판정 30건 미만)', wide.findings.length < 30],

    // ── 글씨 크기·행간 (사용자가 지목한 범주 중 계측이 비어 있던 축) ──
    ['font-too-small 검출 (9px < 하한 11px)', hit('font-too-small', /typo-bad/)],
    ['ko-line-height 검출 (한글 행간 0.9 — 받침 겹침)', hit('ko-line-height', /typo-bad/)],
    ['heading-size 검출 (제목 14px < 본문 17px)', hit('heading-size', /typo-bad/)],
    ['heading-lineheight 검출 (제목이 본문 행간 1.7 상속)', hit('heading-lineheight', /typo-bad/)],
    // ── 세로 공간 ──
    ['dead-row 검출 (화면 높이 상자인데 아래 90% 가 빔)', hit('dead-row', /tall-empty/)],

    // ── 대조군: 정상 타이포·정상 배치는 한 건도 나오면 안 된다 ──
    ['대조군 ⑤ #typo-ok 구역에서는 판정이 0건이다 (11px 각주·본문 행간 1.7·큰 제목)',
      !anyIn(/typo-ok/)],
    ['대조군 ⑥ 가운데 정렬 상자는 dead-row 가 아니다 (남는 공간은 배치다)',
      !typo.findings.some((f) => f.kind === 'dead-row' && f.targets.some((t) => /tall-centered/.test(tsel(t))))],
  ];

  for (const [name, ok] of cases) console.log(`${ok ? 'PASS' : 'FAIL'} ${name}`);
  const failed = cases.filter(([, ok]) => !ok);
  console.log(`\n${cases.length - failed.length}/${cases.length}`);
  if (failed.length) {
    console.log('\n[디버그] wide kinds:', [...wideKinds].join(', '));
    console.log('[디버그] coverage:', JSON.stringify(wide.coverage));
  }
  process.exit(failed.length ? 1 : 0);
}

function parseArgs(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i++) {
    if (!argv[i].startsWith('--')) continue;
    const key = argv[i].slice(2);
    const nxt = argv[i + 1];
    if (!nxt || nxt.startsWith('--')) out[key] = true; else { out[key] = nxt; i++; }
  }
  return out;
}
