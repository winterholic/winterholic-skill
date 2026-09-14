// probe_selftest.mjs — ui_probe.js 실브라우저 negative control.
//
// "통과했다"가 아니라 **"심어둔 결함을 실제로 검출하는가"** 를 본다. probe_fixture.html 에는
// 결함이 의도적으로 심어져 있고, 오탐을 잡기 위한 대조군(깨끗한 문단·gradient 배경)도 함께 있다.
// 계측기를 고친 뒤에는 이걸 먼저 돌려 "검사가 실패할 수 있는지"를 확인한다.
//
//   PLAYWRIGHT_PATH=<프로젝트>/node_modules/playwright node probe_selftest.mjs
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
// playwright 는 이 스킬의 의존성이 아니다. 이미 설치된 프로젝트의 것을 빌려 쓴다.
// 경로는 PLAYWRIGHT_PATH 환경변수로 지정한다. 없으면 전역 해석을 시도한다.
let chromium;
try {
  ({ chromium } = require(process.env.PLAYWRIGHT_PATH || 'playwright'));
} catch (e) {
  console.error('확인 못함: playwright 를 찾지 못했다. 이 스킬의 의존성이 아니므로 정상이다.');
  console.error('  예) PLAYWRIGHT_PATH=C:/프로젝트/node_modules/playwright node probe_selftest.mjs');
  process.exit(2);
}
import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

const HERE = new URL('.', import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1');
const PROBE = HERE + 'ui_probe.js';
const FIXTURE = HERE + 'probe_fixture.html';

const src = readFileSync(PROBE, 'utf8');
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 390, height: 664 } });
await page.goto(pathToFileURL(FIXTURE).href);
await page.waitForTimeout(300);

const r = await page.evaluate((s) => {
  // eslint-disable-next-line no-eval
  (0, eval)(s);
  return window.__uiProbe();
}, src);
await browser.close();

const checks = [];
const ok = (name, cond, detail) => checks.push({ name, pass: !!cond, detail });

ok('identity: 실제 웹 뷰포트를 찍는다', r.identity.viewport.h === 664, `h=${r.identity.viewport.h}`);
ok('identity: 빌드 마커를 읽는다', r.identity.buildMarker === 'fixture-v1', String(r.identity.buildMarker));
ok('scrollTruth: 문서가 아니라 내부 상자가 스크롤함을 잡는다',
   r.scrollTruth.fullPageCaptureIsMisleading === true,
   `documentScrolls=${r.scrollTruth.documentScrolls}, inner=${r.scrollTruth.innerScrollers.length}`);
ok('glyphVsBoxGaps: min-height 로 벌어진 박스-글리프 차이를 잡는다',
   r.glyphVsBoxGaps.some((g) => g.between.join(' ').includes('credit')),
   JSON.stringify(r.glyphVsBoxGaps.slice(0, 2)));
ok('contrast: gradient 배경은 계산하지 않고 unmeasurable 로 넘긴다',
   r.contrast.unmeasured.some((u) => u.reason.includes('gradient') || u.reason.includes('background-image')),
   JSON.stringify(r.contrast.unmeasured.slice(0, 2)));
ok('contrast: gradient 위 텍스트를 대비 미달로 오탐하지 않는다',
   !r.contrast.fails.some((f) => f.selector.includes('grad')),
   JSON.stringify(r.contrast.fails.map((f) => f.selector)));
ok('contrast: 단색 배경의 진짜 미달은 잡는다',
   r.contrast.fails.some((f) => f.selector.includes('lowcontrast')),
   JSON.stringify(r.contrast.fails.slice(0, 3)));
ok('overflow: 잘린 요소를 잡는다',
   r.overflow.clipped.some((c) => c.selector.includes('clip')),
   JSON.stringify(r.overflow.clipped.slice(0, 2)));
ok('scaleOutliers: 스케일 밖 값(7·13)을 잡는다',
   r.scaleOutliers.some((s) => s.value === 7) && r.scaleOutliers.some((s) => s.value === 13),
   JSON.stringify(r.scaleOutliers.slice(0, 5)));
ok('typography: keep-all 없는 한글 블록을 잡는다',
   r.typography.koreanWithoutKeepAll.length > 0,
   `${r.typography.koreanWithoutKeepAll.length}건`);
ok('typography: keep-all 있는 대조군은 안 잡는다',
   !r.typography.koreanWithoutKeepAll.some((k) => k.selector.includes('clean')),
   JSON.stringify(r.typography.koreanWithoutKeepAll.map((k) => k.selector)));
ok('typography: 한글 제목 행간 1.0 미만을 경고한다',
   r.typography.belowMinFont.some((b) => b.warn && b.warn.includes('받침')),
   JSON.stringify(r.typography.belowMinFont.slice(0, 3)));
ok('touchTargets: 24px 미만을 잡는다',
   r.touchTargets.some((t) => t.selector.includes('tiny')),
   JSON.stringify(r.touchTargets.slice(0, 3)));
ok('blindSpots: 미로드 이미지를 사각지대로 남긴다',
   r.blindSpots.some((b) => b.kind.includes('미로드')),
   JSON.stringify(r.blindSpots));
ok('readMe: 확인 못한 것이 있으면 경고 문구를 낸다',
   r.unmeasured.length > 0 && r.readMe.includes('확인 못함'),
   `${r.unmeasured.length}건 / ${r.readMe.slice(0, 60)}`);
ok('truncated: 이 규모에서는 절단이 없어야 한다',
   Array.isArray(r.truncated) && r.truncated.length === 0,
   JSON.stringify(r.truncated));

const failed = checks.filter((c) => !c.pass);
for (const c of checks) console.log(`${c.pass ? 'PASS' : 'FAIL'}  ${c.name}${c.pass ? '' : '\n        ' + c.detail}`);
console.log(`\n${checks.length - failed.length}/${checks.length} 통과`);
process.exit(failed.length ? 1 : 0);
