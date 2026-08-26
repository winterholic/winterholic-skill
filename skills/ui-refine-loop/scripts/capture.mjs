#!/usr/bin/env node
/**
 * 캡처 + 1b 측정 드라이버.
 *
 *   node scripts/capture.mjs --url http://localhost:3000 --routes /orders \
 *     --out .ui-refine/round-0 [--config .ui-refine.json] [--calibrate]
 *
 * 산출물 (--out 아래):
 *   plain/<id>.png     원본        — 픽셀 diff·회귀 판정용
 *   badged/<id>.png    번호 배지본 — 비평가 첨부용
 *   measure/<id>.json  1b 측정 + 요소 번호→셀렉터 매핑
 *   summary.json       라운드 점수 카운트 + 불변식 재료
 */
import { mkdir, writeFile, readFile } from 'node:fs/promises';
import { join, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createRequire } from 'node:module';

const HERE = dirname(fileURLToPath(import.meta.url));

// 이 스크립트는 스킬 디렉터리에 있고 playwright 는 대상 프로젝트에 설치돼 있다.
// ESM 은 스크립트 위치 기준으로 해석하므로 cwd 기준으로 다시 찾아준다.
const { chromium } = await (async () => {
  try { return await import('playwright'); } catch { /* 스킬 디렉터리엔 없다 */ }
  const req = createRequire(join(process.cwd(), 'noop.js'));
  for (const pkg of ['playwright', 'playwright-core', '@playwright/test']) {
    try {
      // playwright 본체는 CJS 라 dynamic import 하면 named export 가 안 잡힌다. require 로 받는다.
      const mod = req(pkg);
      if (mod?.chromium) return mod;
    } catch { /* 다음 후보 */ }
  }
  console.error(
    'playwright 를 찾지 못했다. 대상 프로젝트에서 `npm i -D playwright` 후 다시 실행하거나,\n' +
    '프로젝트 루트에서 이 스크립트를 실행하라 (cwd 기준으로 해석한다).');
  process.exit(3);
})();

// SKILL.md §0-3 기본값. 곱으로 폭발하므로 넓히는 것은 사용자가 명시할 때만.
const DEFAULT_VIEWPORTS = [
  { name: '360', width: 360, height: 800 },
  { name: '1440', width: 1440, height: 900 },
];
const DEFAULT_STATES = ['default', 'long-ko-text'];

const args = parseArgs(process.argv.slice(2));
if (!args.url || !args.out) {
  console.error('usage: capture.mjs --url <url> --out <dir> [--routes /a,/b] [--config f] [--calibrate]');
  process.exit(1);
}

const config = args.config ? JSON.parse(await readFile(args.config, 'utf8')) : {};
const routes = (args.routes || '/').split(',').map((s) => s.trim());
const viewports = config.viewports || DEFAULT_VIEWPORTS;
const states = config.states || DEFAULT_STATES;
/**
 * ★ **미디어 축** — 지금까지 `colorScheme:'light'` 가 하드코딩돼 있어 **다크 모드가 통째로
 *   미감사**였다. 다크 블록 안에서만 선언되는 토큰·미정의 변수·색 뒤집힘은 라이트로 재면
 *   원리적으로 하나도 안 잡힌다(조건부 규칙은 `matchMedia` 평가에서 false 로 빠진다).
 *   인쇄도 같다 — `@media print` 는 화면 캡처에서 항상 false 라, 인쇄 정본 문서가 만점을 받는다.
 * ⚠️ 축을 늘리면 세트가 곱으로 폭발하므로(§0-3) **기본은 라이트·screen 그대로**다.
 *   `.ui-refine.json` 에 `"colorSchemes": ["light","dark"]` / `"media": "print"` 를 줄 때만 늘어난다.
 */
const colorSchemes = config.colorSchemes || [config.colorScheme || 'light'];
const media = config.media || 'screen';
// collect.js 는 ESM 이지만 page.evaluate 안에서는 모듈이 아니라 스크립트로 실행된다.
// `export` 키워드가 남아 있으면 SyntaxError 가 난다.
const source = (await readFile(join(HERE, 'collect.js'), 'utf8')).replace(/^export\s+/gm, '');

const browser = await chromium.launch({
  args: ['--force-device-scale-factor=1', '--disable-gpu'], // 렌더 비결정성 제거
});

const results = [];
const emptyShots = [];
const blindFrames = [];
const scaleByVp = new Map();
const skippedStates = [];

for (const route of routes) {
  for (const vp of viewports) {
   for (const scheme of colorSchemes) {
    for (const state of states) {
      const ctx = await browser.newContext({
        viewport: { width: vp.width, height: vp.height },
        deviceScaleFactor: 1,
        colorScheme: scheme,
        storageState: config.storageState || undefined,
      });
      const page = await ctx.newPage();
      // 인쇄 CSS 는 이 한 줄이 없으면 **규칙 순회 자체가 안 된다**(조건 평가가 항상 false).
      if (media !== 'screen') await page.emulateMedia({ media });

      if (config.stateRoutes?.[state]) await applyRouteFixture(page, config.stateRoutes[state]);

      await installCls(page);
      await page.goto(new URL(route, args.url).href, { waitUntil: 'networkidle' });

      // ⚠️ 긴 한글 텍스트 상태는 `word-break:keep-all` 부작용을 보려는 것이다.
      //    **한국어 화면이 아니면 의미가 없고 해롭다** — 실측: 아랍어 RTL 페이지에 한글을 주입했더니
      //    기본 상태 0건이던 화면에서 `scale 1px(52곳)`·`cell-padding` 같은 쓰레기 지적이 쏟아졌다.
      //    ⚠️ 주입은 `addInitScript` 라 **탐색 전에** 걸어야 한다. 그래서 한 번 로드해 언어를 보고,
      //       한국어면 주입을 건 뒤 **다시 로드**한다. 아니면 이 상태를 빼고 **뺐다고 보고한다.**
      if (state === 'long-ko-text') {
        const korean = await page.evaluate(() => {
          const lang = (document.documentElement.lang || '').toLowerCase();
          if (lang.startsWith('ko')) return true;
          return /[가-힣]/.test(document.body.innerText || '');
        });
        if (!korean) {
          skippedStates.push(`${route} @${vp.name}`);
          await ctx.close();
          continue;
        }
        await applyLongKoText(page);
        await page.goto(new URL(route, args.url).href, { waitUntil: 'networkidle' });
      }
      await stabilize(page);

      // 스킴·미디어가 id 에 없으면 다른 조건의 샷이 서로를 덮어쓴다.
      const mediaTag = `${scheme === 'light' ? '' : `__${scheme}`}${media === 'screen' ? '' : `__${media}`}`;
      const id = `${route.replace(/[^\w]/g, '_')}__${vp.name}__${state}${mediaTag}`;

      // page.evaluate 의 문자열은 표현식으로 평가된다. 함수 선언문을 넣으려면 IIFE 로 감싼다.
      const inBrowser = (call) => `(() => { ${source}\nreturn ${call}; })()`;

      // ⚠️ 스케일은 **라우트 × 뷰포트마다** 뽑는다. 캐시 범위를 넓히면 두 가지로 부러진다:
      //    ① 뷰포트 — Pico 는 360 에서 루트 폰트가 16px, 1440 에서 20px 이라 `1rem` 토큰의
      //       px 값이 달라진다. 첫 샷의 스케일을 다른 뷰포트에 쓰면 전부 이탈로 잡힌다(실측 22건).
      //    ② 라우트 — 문서마다 토큰 스케일이 다를 수 있다. 실측(html-report 산출물 4종)에서
      //       첫 문서의 `--s-*` 가 나머지 3개에 적용돼 **지적이 60 → 103 건으로 부풀었다.**
      //    같은 디자인시스템이면 재추출은 결과가 같고 비용은 evaluate 1회라 싸다.
      const scaleKey = `${route}|${vp.name}|${scheme}|${media}`;
      if (!scaleByVp.has(scaleKey)) {
        scaleByVp.set(scaleKey, await page.evaluate(inBrowser('extractScale()')));
      }
      const scaleInfo = scaleByVp.get(scaleKey);

      // spacingBase: 기준 단위 × 정수배로 스케일을 정의하는 방식(Tailwind v4 등).
      // 값 목록이 없으므로 base 를 그대로 넘겨 정수배 여부로 판정하게 한다.
      const cfg = { ...config,
                    spacingScale: config.spacingScale || scaleInfo.scale,
                    spacingBase: config.spacingBase || scaleInfo.base || 0,
                    fullPage: !!config.fullPage };
      const measure = await page.evaluate(inBrowser(`collectPage(${JSON.stringify(cfg)})`));
      measure.scale = scaleInfo;   // 뷰포트별로 다를 수 있어 샷마다 기록한다
      measure.cls = await page.evaluate(() => window.__uirCls || 0);
      measure.id = id;
      measure.route = route;
      measure.viewport = vp.name;
      measure.state = state;
      measure.colorScheme = scheme;
      measure.media = media;

      await mkdir(join(args.out, 'plain'), { recursive: true });
      await mkdir(join(args.out, 'badged'), { recursive: true });
      await mkdir(join(args.out, 'measure'), { recursive: true });

      // 원본 먼저 — 배지가 픽셀 diff 를 오염시키면 자기 잡음 캘리브레이션이 무의미해진다
      // 측정 범위와 캡처 범위를 반드시 일치시킨다 — 어긋나면 비평가가 못 본 것을 중재자가 검증하게 된다
      const shot = { animations: 'disabled', caret: 'hide', scale: 'css', fullPage: !!config.fullPage };
      await page.screenshot({ path: join(args.out, 'plain', `${id}.png`), ...shot });
      if (args.calibrate) {
        await page.screenshot({ path: join(args.out, 'plain', `${id}.b.png`), ...shot });
      }

      await page.evaluate(`(() => { ${source}\nreturn paintBadges(); })()`);
      await page.screenshot({ path: join(args.out, 'badged', `${id}.png`), ...shot });

      await writeFile(join(args.out, 'measure', `${id}.json`), JSON.stringify(measure, null, 2));
      results.push(measure);
      await ctx.close();

      // 캡처가 유의미한 화면을 잡았는지 확인한다.
      // ⚠️ 이게 없어서 404 페이지(DOM 6노드)를 찍고도 `findings=0 / counts={}` 가 나왔고,
      //    그게 「완벽하게 깨끗한 화면」과 구분되지 않았다. 조용히 통과시키지 않는다.
      if (measure.domNodeCount < 20 || measure.elements.length < 3) {
        console.error(
          `  ⚠️ ${id}: DOM ${measure.domNodeCount}노드 / 측정대상 ${measure.elements.length}개 —` +
          ` 화면이 비어 있다. 404·라우팅 실패·렌더 전 캡처를 의심하라.` +
          ` (--routes 에 절대경로를 주면 --url 의 경로가 날아간다)`);
        emptyShots.push(id);
      }
      // ⚠️ **교차 출처 iframe 은 원리적으로 못 읽는다.** 그 화면은 "지적 없음"이 아니라
      //    "그만큼 감사하지 못함"이다. 조용히 넘기면 미감사 영역이 깨끗한 것으로 둔갑한다.
      if (measure.blindSpots) {
        const bs = measure.blindSpots;
        if (bs.count) {
          console.error(
            `  ⚠️ ${id}: 교차 출처 iframe ${bs.count}개는 내용을 읽을 수 없어 미감사다` +
            ` (${bs.crossOriginFrames.join(', ')}). 이 영역은 사람이 직접 봐야 한다.`);
        }
        if (bs.cssCount) {
          console.error(
            `  ⚠️ ${id}: 교차 출처 스타일시트 ${bs.cssCount}개를 읽을 수 없어` +
            ` ${bs.suppressed.join('·')} 판정을 **보류**했다 (${bs.crossOriginStyleSheets.join(', ')}).` +
            `\n     그 시트에 선언된 토큰·포커스 규칙을 못 보므로 "지적 없음"이 아니라 "감사 못함"이다.` +
            `\n     감사하려면 그 CSS 를 같은 출처로 서빙하거나 <link crossorigin> 을 주라.`);
        }
        blindFrames.push({ id, ...bs });
      }
      console.error(`[captured] ${id}  findings=${measure.findings.length}` +
                    (measure.frames ? `  frames=${measure.frames}` : ''));
    }
   }
  }
}

await browser.close();

// 사전식 비교용 카운트. 집계 축은 캡처 세트 전체 합 — 화면별 벡터면 A가 좋아지고 B가
// 나빠질 때 비교가 성립하지 않는다. 토큰 수정이 전역에 퍼지므로 세트 합이어야 한다.
const summary = {
  capturedAt: null, // 워크플로 스크립트에서 시각을 주입한다
  scale: Object.fromEntries(scaleByVp),
  // 판정 종류를 늘리면 여기와 score.mjs 의 ORDER 를 함께 고친다.
  // 한쪽만 고치면 새 지표가 점수에 반영되지 않아 조용히 무시된다.
  counts: Object.fromEntries(
    [...new Set(results.flatMap((r) => Object.keys(r.counts)))]
      .map((k) => [k, sum(results, k)])),
  cls: Math.max(...results.map((r) => r.cls || 0)), // 합은 화면 수에 비례해 의미가 없다
  invariants: {
    domNodeCount: results.reduce((a, r) => a + r.domNodeCount, 0),
    textHash: results.map((r) => `${r.id}:${r.textHash}`).join('|'),
  },
  shots: results.map((r) => ({ id: r.id, route: r.route, viewport: r.viewport, state: r.state,
                               colorScheme: r.colorScheme, media: r.media,
                               findings: r.findings.length, elements: r.elements.length })),
};
summary.emptyShots = emptyShots;
if (blindFrames.length) summary.blindSpots = blindFrames;   // 교차 출처 iframe = 감사 사각지대
if (skippedStates.length) {
  summary.skippedStates = { 'long-ko-text': skippedStates };
  console.error(`\nℹ️ 한국어 화면이 아니라 long-ko-text 상태를 뺐다: ${skippedStates.join(', ')}`);
}

// ⚠️ **빈 화면은 아닌데 유독 작은 화면**을 경고한다.
//    실측: 아직 다 쓰이지 않은 파일을 측정해 80 노드짜리 미완성 문서가 "findings 0" 으로 나왔고,
//    하마터면 「깨끗한 문서」로 보고할 뻔했다. 빈 화면 검사(DOM<20)는 404 만 잡고 이걸 통과시킨다.
//    같은 실행 안의 다른 라우트와 견줘 한 자릿수 배 이상 작으면 사람이 확인해야 한다.
//    ⚠️ 이건 오류가 아니라 **확인 요청**이다 — 짧은 문서는 정상적으로 존재한다.
{
  const byRoute = new Map();
  for (const r of results) {
    const cur = byRoute.get(r.route) || 0;
    byRoute.set(r.route, Math.max(cur, r.domNodeCount));
  }
  const sizes = [...byRoute.values()];
  const max = Math.max(...sizes);
  // ⚠️ 배수는 **판단선**이다(실측으로 정한 값이 아니다). 미완성 문서를 잡은 실제 사례가
  //    80 vs 435 노드(5.4배)였어서 그보다 낮게 잡았다. 경고일 뿐 종료 코드는 바꾸지 않는다.
  const SIZE_OUTLIER = 4;
  const small = [...byRoute.entries()].filter(([, n]) => n * SIZE_OUTLIER < max);
  if (small.length) {
    console.error(`\n⚠️ 규모가 유독 작은 라우트: ${small.map(([r, n]) => `${r}(${n}노드)`).join(', ')}`);
    console.error(`   같은 실행의 최대치는 ${max}노드다. 렌더 미완·작성 중인 파일·로딩 실패를 의심하라.`);
    console.error('   짧은 문서면 정상이다 — 판단은 사람이 한다.');
    summary.smallRoutes = small.map(([route, nodes]) => ({ route, nodes }));
  }
}
await writeFile(join(args.out, 'summary.json'), JSON.stringify(summary, null, 2));
console.log(JSON.stringify(summary.counts));
if (emptyShots.length) {
  console.error(`\n⚠️ 빈 화면 ${emptyShots.length}/${results.length}장: ${emptyShots.join(', ')}`);
  console.error('   이 상태의 점수는 비교에 쓰지 마라 — 빈 화면은 모든 지표가 0 이라 항상 이긴다.');
  process.exit(4);
}

// ---------- helpers ----------

function sum(rs, kind) {
  return rs.reduce((a, r) => a + (r.counts[kind] || 0), 0);
}

/** 캡처 아티팩트 제거 — 3층이 이 단계를 참조한다. 여기가 비면 중재자가 판단으로 떠안는다. */
async function stabilize(page) {
  /**
   * ★ **내부 스크롤 셸** — 문서가 아니라 앱 셸 안쪽 컨테이너가 스크롤하는 구조(모바일 앱을
   *   흉내내는 SPA 가 흔히 그렇다)에서는 `fullPage` 가 **아무 일도 하지 않는다.** 문서 높이가
   *   항상 뷰포트 높이라 스크린샷이 정확히 viewport 크기로 나오고, 그 아래 콘텐츠는 캡처에도
   *   측정에도 안 들어간다 — 비평가는 첫 화면만 보고 "지적 없음"을 낸다(실측: 전 라우트가
   *   1440×900 으로 고정, 긴 약관 문서의 90% 가 미감사).
   *   `.ui-refine.json` 의 `"injectCss"` 로 그 높이 잠금을 풀어 문서가 자연 스크롤하게 만든다.
   * ⚠️ 레이아웃을 건드리는 주입이므로 **고정·sticky 요소의 위치 판정은 이 패스에서 신뢰하지
   *   않는다.** 주입 없는 패스와 함께 돌려 두 벌로 본다.
   */
  if (config.injectCss) await page.addStyleTag({ content: config.injectCss });
  await page.addStyleTag({
    content: `
      *::-webkit-scrollbar{display:none!important}
      *{scrollbar-width:none!important}
      [data-nextjs-toast],[data-nextjs-dialog],#__next-build-watcher,
      nextjs-portal,
      .vite-error-overlay,#webpack-dev-server-client-overlay,
      [class*="devtools"],[id*="hmr"]{display:none!important}
`,
  });
  // ⚠️ 화면 밖 섹션의 렌더를 건너뛰는 최적화(`content-visibility:auto`)는 **측정을 통째로 가린다.**
  //    실측: 40개 섹션 문서에서 fullPage 로도 측정 대상이 30개였다(강제 후 164개).
  //    ⚠️ **`auto` 만 푼다.** `hidden` 은 저자가 일부러 감춘 것(닫힌 아코디언 등)이라
  //       통째로 `visible` 로 덮으면 숨긴 콘텐츠가 측정에 끌려 들어온다.
  //    ⚠️ **임베드 문서(iframe)에도 걸어야 한다.** 메인 프레임에만 걸면 임베드 안이 건너뛴 채
  //       측정된다 — 측정이 iframe 까지 들어가게 된 이상 전처리도 같은 범위여야 한다.
  for (const frame of page.frames()) {
    try {
      await frame.evaluate(() => {
        for (const el of document.querySelectorAll('*')) {
          if (getComputedStyle(el).contentVisibility === 'auto') el.style.contentVisibility = 'visible';
        }
      });
    } catch { /* 교차 출처 프레임은 접근 불가 — collectPage 가 사각지대로 보고한다 */ }
  }
  /**
   * ★ **지연 로딩 이미지** — `loading="lazy"` 는 뷰포트에 들어와야 발화한다. 첫 화면
   *   아래 이미지는 캡처에 **빈 상자**로 찍히고, 비평가는 그걸 "사진이 안 나오는 결함"
   *   으로 보고한다(실측: 원본 URL 은 전부 200 인데 타일 5개가 비어 보였다 —
   *   하마터면 멀쩡한 자리표시 컴포넌트를 고칠 뻔했다).
   *   전부 eager 로 바꾸고 디코딩까지 기다린다. 실패한 이미지는 여기서 걸러지지 않으므로
   *   "빈 상자 = 진짜 결함"이 된다.
   */
  for (const frame of page.frames()) {
    try {
      await frame.evaluate(async () => {
        // 스크롤 컨테이너까지 한 번 훑어야 IntersectionObserver 기반 지연 로딩이 발화한다.
        // eager 로 바꾸는 것만으로는 부족했다 — 클라이언트 컴포넌트가 나중에 그리는
        // 이미지는 그 시점에 DOM 에 없다.
        const scrollers = [document.scrollingElement, ...document.querySelectorAll('*')].filter((el) => {
          if (!el) return false;
          const cs = getComputedStyle(el);
          return el === document.scrollingElement ||
            (/(auto|scroll)/.test(cs.overflowY) && el.scrollHeight > el.clientHeight + 8);
        });
        for (let pass = 0; pass < 2; pass++) {
          for (const el of scrollers) {
            const h = el.clientHeight || 600;
            for (let y = 0; y <= el.scrollHeight; y += h) { el.scrollTop = y; await new Promise((r) => setTimeout(r, 40)); }
            el.scrollTop = 0;
          }
          const imgs = [...document.querySelectorAll('img')];
          for (const img of imgs) { img.loading = 'eager'; if (img.dataset.src && !img.src) img.src = img.dataset.src; }
          await Promise.all(imgs.map((img) => (img.complete && img.naturalWidth ? null : img.decode().catch(() => {}))));
        }
      });
    } catch { /* 교차 출처 프레임은 접근 불가 */ }
  }
  await page.evaluate(() => document.activeElement?.blur?.()); // 포커스 링 제거
  await page.evaluate(() => document.fonts?.ready);
  await page.waitForTimeout(300); // 애니메이션·토스트 잔상 소거
}

/** 긴 한글 텍스트 상태 — word-break: keep-all 부작용은 lorem ipsum 으로 재현되지 않는다. */
async function applyLongKoText(page) {
  await page.addInitScript(() => {
    const LONG = '대한민국의영토는한반도와그부속도서로한다국회의원의수는법률로정하되이백인이상으로한다';
    // ⚠️ **`document.querySelectorAll('*')` 로 돌면 안 된다.** `*` 에는 head 의 `<style>`·`<title>` 이
    //    들어가고, 인라인 `<style>` 의 자식 텍스트 노드는 **CSS 본문 전체**다. 그걸 한글로 덮으면
    //    스타일이 통째로 죽어 **무스타일 화면을 재게 된다** — 실측: 인라인 style 픽스처에서
    //    body 배경 투명·패딩 0·색 초기화. 그 상태의 지적(스케일 폴백·정렬 무더기)은 전부 쓰레기다.
    //    외부 CSS 를 쓰는 화면에서는 안 터져서 오래 안 보였다(테스트베드가 대부분 외부 CSS 였다).
    const SKIP = new Set(['SCRIPT', 'STYLE', 'TITLE', 'NOSCRIPT', 'TEXTAREA', 'TEMPLATE']);
    window.addEventListener('load', () => {
      document.body.querySelectorAll('*').forEach((el) => {
        if (SKIP.has(el.tagName)) return;
        const t = Array.from(el.childNodes).find(
          (n) => n.nodeType === Node.TEXT_NODE && n.textContent.trim().length > 3);
        if (t) t.textContent = LONG.slice(0, Math.max(8, t.textContent.trim().length * 2));
      });
    });
  });
}

async function applyRouteFixture(page, fixture) {
  await page.route(fixture.pattern, (r) =>
    r.fulfill({ status: fixture.status ?? 200, contentType: 'application/json',
                body: JSON.stringify(fixture.body ?? {}) }));
}

async function installCls(page) {
  await page.addInitScript(() => {
    window.__uirCls = 0;
    // layout-shift 는 Chromium 전용. 0건을 "shift 없음"으로 읽으면 안 된다.
    try {
      new PerformanceObserver((list) => {
        for (const e of list.getEntries()) if (!e.hadRecentInput) window.__uirCls += e.value;
      }).observe({ type: 'layout-shift', buffered: true });
    } catch { window.__uirCls = null; }
  });
}

function parseArgs(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i++) {
    if (!argv[i].startsWith('--')) continue;
    const key = argv[i].slice(2);
    const next = argv[i + 1];
    if (!next || next.startsWith('--')) { out[key] = true; } else { out[key] = next; i++; }
  }
  return out;
}
