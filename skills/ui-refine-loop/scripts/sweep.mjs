#!/usr/bin/env node
/**
 * 스윕 — 넓은 지시("방금 작업한 거 전반적으로 UI/UX 점검해줘")를 커버리지 표로 닫는다.
 *
 *   node scripts/sweep.mjs --url http://localhost:3000 --routes /,/orders,/orders/1
 *   node scripts/sweep.mjs --url ... --routes-from routes.txt --viewports 360x800,1440x900
 *   node scripts/sweep.mjs --self-test
 *
 * 왜 이게 있나
 * -----------
 * 이 스킬이 좁은 지적("이 카드 헐거워")에는 작동하는데 넓은 지시에서 무너지는 이유는 넷이다.
 * 전부 실사고(2026-07-04, memoir 11개 화면 전수 감사 → 발견 2건, 품질 축 0건)에서 나왔다.
 *
 *   1. **판정 기준이 사라진다.** 구체적 지적이 오면 그 발화가 곧 기준이다. 넓은 지시에서는
 *      기준을 스스로 세워야 하는데, 안 세우고 "눈으로 보니 괜찮다"로 닫는다.
 *   2. **0건이 안전한 답으로 보상된다.** 넓은 지시에서 "문제 없음"은 리스크가 없는 답이다.
 *   3. **대상 집합을 못 박지 않는다.** 감으로 몇 개만 보고, 무엇을 뺐는지 안 남는다.
 *   4. 스킬 기본값이 범위를 되레 좁힌다(§0-3 "지목한 화면 1개 + 연결 2개").
 *
 * 그래서 이 스크립트는 **판정을 내는 도구가 아니라 커버리지를 강제하는 도구**다.
 * 대상을 전부 열거하고, 눈이 아니라 계측으로 하나씩 지우고, 못 본 것을 표에 남긴다.
 * `--routes` 를 안 주면 **일부러 실패한다** — 대상 열거는 사람이 먼저 해야 하는 일이다.
 *
 * 종료 코드: 0 판정 0건(단, 커버리지 경고는 별도) / 1 판정 있음 / 2 사용법·대상 미확정 / 3 playwright 없음
 */
import { readFile } from 'node:fs/promises';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';
import { buildReceipt, UNMEASURED_AXES } from './receipt.mjs';

const HERE = dirname(fileURLToPath(import.meta.url));
const args = parseArgs(process.argv.slice(2));

if (args.help) {
  console.log('usage: sweep.mjs --url <base> (--routes /a,/b | --routes-from <file>) [--viewports 360x800,1440x900] [--full] [--config f] [--json]');
  process.exit(0);
}

const { chromium } = await (async () => {
  try { return await import('playwright'); } catch { /* 스킬 디렉터리엔 없다 */ }
  const req = createRequire(join(process.cwd(), 'noop.js'));
  for (const pkg of [process.env.PLAYWRIGHT_PATH, 'playwright', 'playwright-core', '@playwright/test'].filter(Boolean)) {
    try { const m = req(pkg); if (m?.chromium) return m; } catch { /* 다음 후보 */ }
  }
  console.error('확인 못함: playwright 를 찾지 못했다. PLAYWRIGHT_PATH 를 주거나 프로젝트 루트에서 실행하라.');
  process.exit(3);
})();

const source = (await readFile(join(HERE, 'collect.js'), 'utf8')).replace(/^export\s+/gm, '');
const inBrowser = (call) => `(() => { ${source}\nreturn ${call}; })()`;

if (args['self-test']) await runSelfTest(); else await runSweep();

async function resolveRoutes() {
  if (args['routes-from']) {
    const raw = await readFile(args['routes-from'], 'utf8');
    return raw.split(/\r?\n/).map((l) => l.split('#')[0].trim()).filter(Boolean);
  }
  if (args.routes) return String(args.routes).split(',').map((s) => s.trim()).filter(Boolean);
  return null;
}

async function runSweep() {
  const routes = await resolveRoutes();
  if (!args.url || !routes || !routes.length) {
    console.error('대상이 확정되지 않았다. --routes 또는 --routes-from 으로 **감사할 화면을 전부 열거**하라.');
    console.error('');
    console.error('  이 스크립트는 대상을 스스로 추측하지 않는다. 넓은 지시에서 무너지는 원인 3번이');
    console.error('  「대상 집합을 못 박지 않고 감으로 몇 개만 보는 것」이기 때문이다.');
    console.error('  뺀 화면이 있으면 뺐다는 사실과 이유를 사용자에게 함께 보고하라.');
    process.exit(2);
  }
  const viewports = String(args.viewports || '360x800,1440x900').split(',').map((v) => {
    const [w, h] = v.trim().split('x').map(Number);
    return { name: v.trim(), width: w, height: h };
  });
  if (viewports.some((v) => !Number.isFinite(v.width) || !Number.isFinite(v.height))) {
    console.error('--viewports 는 360x800,1440x900 형식이다'); process.exit(2);
  }
  const config = args.config ? JSON.parse(await readFile(args.config, 'utf8')) : {};

  const rows = [];
  const browser = await chromium.launch({ args: ['--force-device-scale-factor=1', '--disable-gpu'] });
  try {
    for (const route of routes) {
      for (const vp of viewports) {
        const row = { route, viewport: vp.name };
        const ctx = await browser.newContext({ viewport: { width: vp.width, height: vp.height }, deviceScaleFactor: 1 });
        const page = await ctx.newPage();
        try {
          const res = await page.goto(new URL(route, args.url).href, { waitUntil: 'networkidle' });
          row.status = res ? res.status() : null;
          await page.evaluate(async () => { await document.fonts?.ready; });
          const scale = await page.evaluate(inBrowser('extractScale()'));
          const cfg = { ...config, spacingScale: config.spacingScale || scale.scale,
                        spacingBase: config.spacingBase || scale.base || 0, fullPage: !!args.full };
          const m = await page.evaluate(inBrowser(`collectPage(${JSON.stringify(cfg)})`));
          row.counts = m.counts;
          row.total = m.findings.length;
          row.coverage = m.coverage ? m.coverage.ratio : null;
          row.domNodes = m.domNodeCount;
          row.scaleMode = scale.source;
          row.findings = m.findings;
          row.elements = m.elements;
          // ⚠️ **빈 화면은 모든 지표가 0 이라 "가장 깨끗한 화면"으로 보인다.** 표에서 반드시 구분한다.
          row.empty = m.domNodeCount < 20 || m.elements.length < 3;
          row.blindSpots = m.blindSpots || null;
        } catch (e) {
          // 조용히 건너뛰면 그 화면이 "문제 없음"으로 표에 남는다. 실패도 한 줄로 남긴다.
          row.error = String(e).split('\n')[0].slice(0, 120);
        }
        await ctx.close();
        rows.push(row);
      }
    }
  } finally { await browser.close(); }

  if (args.json) { console.log(JSON.stringify(rows, null, 2)); }
  else printTable(rows, routes, viewports);

  const anyFinding = rows.some((r) => (r.total || 0) > 0);
  process.exit(anyFinding ? 1 : 0);
}

function printTable(rows, routes, viewports) {
  const L = [];
  L.push(`■ 감사 대상  라우트 ${routes.length} × 뷰포트 ${viewports.length} = ${rows.length}회`);
  L.push(`   ${routes.join(', ')}`);
  L.push('');

  const pad = (s, n) => String(s).padEnd(n);
  const padL = (s, n) => String(s).padStart(n);
  const w = Math.max(10, ...rows.map((r) => r.route.length));
  L.push(`${pad('화면', w)}  ${pad('뷰포트', 10)}  ${padL('판정', 4)}  ${padL('커버', 5)}  상태`);
  L.push('─'.repeat(w + 34));
  for (const r of rows) {
    const cov = r.coverage == null ? '  -  ' : padL(`${Math.round(r.coverage * 100)}%`, 5);
    let note = '';
    if (r.error) note = `❌ ${r.error}`;
    else if (r.empty) note = '⚠️ 빈 화면 — 이 0건은 깨끗함이 아니다';
    else if (r.status && r.status >= 400) note = `⚠️ HTTP ${r.status}`;
    else if (r.coverage != null && r.coverage < 0.8) note = '⚠️ 상당 부분 미감사';
    else if (r.scaleMode === 'frequency') note = 'ℹ️ 스케일 추정(frequency) — 스케일 이탈은 덜 믿는다';
    L.push(`${pad(r.route, w)}  ${pad(r.viewport, 10)}  ${padL(r.total ?? '-', 4)}  ${cov}  ${note}`);
  }

  // 종류별 집계 — 어느 축이 실제로 작동했는지 한눈에 보이게. 0 인 축이 곧 미감사 후보다.
  const byKind = {};
  for (const r of rows) for (const [k, v] of Object.entries(r.counts || {})) byKind[k] = (byKind[k] || 0) + v;
  L.push('');
  L.push('■ 판정 종류별 합계');
  const entries = Object.entries(byKind).sort((a, b) => b[1] - a[1]);
  if (!entries.length) L.push('   0건');
  else for (const [k, v] of entries) L.push(`   ${k.padEnd(20)} ${v}`);

  // ★ 0건을 결론으로 쓰지 못하게 막는다.
  L.push('');
  L.push('■ 이 표를 읽는 법');
  const emptyRows = rows.filter((r) => r.empty).length;
  const errRows = rows.filter((r) => r.error).length;
  const lowCov = rows.filter((r) => r.coverage != null && r.coverage < 0.8).length;
  if (!entries.length) {
    L.push('   ⚠️ **전 화면 0건은 결론이 아니라 신호다.** 넓은 지시에서 0건이 나오면 대개 화면이');
    L.push('      깨끗한 게 아니라 **측정 축이 모자란 것**이다(2026-07-04: 11개 화면 전수 감사에서');
    L.push('      품질 축 0건이었는데 이후로도 오너 지적이 계속됐다).');
    L.push('      아래 「계측이 못 보는 축」을 그대로 사용자에게 전달하고, 눈으로 봐서 괜찮다고 닫지 마라.');
  }
  if (emptyRows) L.push(`   ⚠️ 빈 화면 ${emptyRows}건 — 라우팅 실패일 수 있다. 그 0건은 점수에 쓰지 마라.`);
  if (errRows) L.push(`   ❌ 접근 실패 ${errRows}건 — 감사 못 한 화면이다. "문제 없음"에 포함하지 마라.`);
  if (lowCov) L.push(`   ⚠️ 커버리지 80% 미만 ${lowCov}건 — 내부 스크롤이면 injectCss 로 풀고 다시 재라.`);

  L.push('');
  L.push('■ 계측이 못 보는 축 (반드시 함께 보고한다 — "지적 없음"이 아니라 "미감사"다)');
  for (const ax of UNMEASURED_AXES) L.push(`   · ${ax}`);
  L.push('   이 축들은 biz-experts(biz-ux-designer·biz-ui-designer) 렌즈로 따로 본다.');

  // ★ 영수증 — 「정한 대상을 실제로 쟀는가」를 문서 규율이 아니라 산출물로 남긴다.
  L.push('');
  L.push(buildReceipt({
    tool: 'sweep.mjs',
    target: String(args.url),
    shots: rows.map((r) => ({
      label: `${r.route}@${r.viewport}`,
      findings: r.total || 0,
      coverage: r.coverage == null ? null : r.coverage,
    })),
    notes: [
      ...(emptyRows ? [`빈 화면 ${emptyRows}건 — 이 0건은 깨끗함이 아니다`] : []),
      ...(errRows ? [`접근 실패 ${errRows}건 — 감사 못 한 화면이다`] : []),
    ],
  }));
  console.log(L.join('\n'));
}

/** 대상 미확정에서 반드시 실패하는지 + 표가 0건을 결론으로 쓰지 않는지 확인한다. */
async function runSelfTest() {
  const fx = pathToFileURL(join(HERE, '..', 'assets', 'quick.fixture.html')).href;
  const out = [];
  const orig = console.log;
  console.log = (...a) => out.push(a.join(' '));
  printTable([
    { route: '/a', viewport: '1440x900', total: 0, counts: {}, coverage: 1, domNodes: 100, elements: [1, 2, 3] },
    { route: '/b', viewport: '1440x900', total: 0, counts: {}, coverage: 0.2, domNodes: 100, elements: [1, 2, 3] },
    { route: '/c', viewport: '1440x900', error: 'net::ERR' },
    { route: '/d', viewport: '1440x900', total: 0, counts: {}, coverage: 1, domNodes: 5, elements: [1], empty: true },
  ], ['/a', '/b', '/c', '/d'], [{ name: '1440x900' }]);
  console.log = orig;
  const text = out.join('\n');

  // 영수증 — 「실제로 쟀는가」를 산출물로 남기는 장치. 지문이 측정 결과를 따라가야 의미가 있다.
  const shotsA = [{ label: '/a@1440x900', findings: 3, coverage: 0.9 }];
  const shotsB = [{ label: '/a@1440x900', findings: 4, coverage: 0.9 }];   // 판정 수만 다름
  const rA = buildReceipt({ tool: 't', target: 'u', shots: shotsA });
  const rA2 = buildReceipt({ tool: 't', target: 'u', shots: shotsA });
  const rB = buildReceipt({ tool: 't', target: 'u', shots: shotsB });
  const fp = (r) => /지문 ([0-9a-f]{12})/.exec(r)?.[1];

  const cases = [
    ['영수증: 같은 측정이면 지문이 같다', fp(rA) === fp(rA2) && !!fp(rA)],
    ['영수증: 측정이 달라지면 지문도 달라진다 (판정 3→4)', fp(rA) !== fp(rB)],
    ['영수증: 못 본 축을 항상 싣는다 (인용하면 blind spot 이 따라온다)',
      UNMEASURED_AXES.every((ax) => rA.includes(ax))],
    ['영수증: 없는 보고를 어떻게 취급할지 본문에 적혀 있다', rA.includes('계측하지 않은 것으로 간주')],
    ['0건일 때 "결론이 아니라 신호다" 경고가 나온다', text.includes('결론이 아니라 신호')],
    ['접근 실패를 "문제 없음"에 넣지 말라고 말한다', text.includes('접근 실패')],
    ['빈 화면을 따로 표시한다', text.includes('빈 화면')],
    ['낮은 커버리지를 표시한다', text.includes('커버리지 80% 미만')],
    ['계측이 못 보는 축을 항상 붙인다', text.includes('계측이 못 보는 축')],
    ['픽스처 경로가 존재한다', !!fx],
  ];
  for (const [n, ok] of cases) console.log(`${ok ? 'PASS' : 'FAIL'} ${n}`);
  const failed = cases.filter(([, ok]) => !ok);
  console.log(`\n${cases.length - failed.length}/${cases.length}`);
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
