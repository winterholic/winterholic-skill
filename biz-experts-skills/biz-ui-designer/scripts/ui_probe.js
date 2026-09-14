/**
 * ui_probe.js — 시각 UI 진단용 단발 계측기 (의존성 없음)
 *
 * 왜 있나: "고쳤다"가 거짓이었던 실사고에서 공통 원인은 **측정 축이 틀렸거나, 측정 대상이
 * 지금 화면이 아니었거나, 도구가 못 본 영역을 깨끗하다고 읽은 것**이었다. 이 파일은 그 세 가지를
 * 각각 막는다 — 글리프 기준으로 재고, 페이지 신원을 함께 찍고, 못 본 것을 blindSpots 로 남긴다.
 *
 * 쓰는 법 (둘 중 하나)
 *   1) DevTools 콘솔에 파일 전체를 붙여넣는다 → 결과 JSON 이 출력되고 `window.__uiProbeLast` 에 남는다.
 *   2) Playwright:
 *        const src = require('fs').readFileSync('ui_probe.js', 'utf8');
 *        const r = await page.evaluate(src + '; __uiProbe();');
 *
 * 옵션: __uiProbe({ scale: [4,8,12,16,24,32], root: '#app', minFont: 11 })
 *
 * 읽는 법: `blindSpots` 와 `unmeasured` 가 비어 있지 않으면 **그 영역은 "문제 없음"이 아니라
 * "확인 못함"이다.** 보고할 때 그대로 옮긴다.
 */
(function () {
  'use strict';

  const DEFAULTS = {
    scale: [0, 2, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64],
    root: null,        // null = document.body
    minFont: 11,       // px, 하한 점검용
    maxSample: 400,    // 요소 표본 상한(대형 페이지 보호)
  };

  // 목록을 자를 때마다 "몇 개 중 몇 개를 보여주는지"를 기록한다. 잘린 사실을 안 남기면
  // 사용자는 상한만큼만 보고 "이게 전부"라고 읽는다 — 못 본 것을 깨끗함으로 읽는 것과 같은 실패다.
  const _trunc = [];
  function cap(arr, n, label) {
    if (arr.length > n) _trunc.push({ what: label, found: arr.length, shown: n });
    return arr.slice(0, n);
  }

  const px = (v) => Math.round(v * 100) / 100;
  const isVisible = (el, cs) =>
    cs.display !== 'none' && cs.visibility !== 'hidden' && Number(cs.opacity) !== 0 &&
    el.getClientRects().length > 0;

  // ── 1. 페이지 신원 — "내가 잰 게 지금 그 화면인가" ─────────────────────────
  function identity() {
    const build = document.querySelector('meta[name="build"],meta[name="version"]');
    return {
      url: location.href,
      title: document.title,
      viewport: { w: window.innerWidth, h: window.innerHeight },
      screen: { w: screen.width, h: screen.height },
      dpr: window.devicePixelRatio,
      // 기기 해상도와 실제 웹 뷰포트가 다르다(사파리 하단바·안드로이드 내비).
      // 세로 예산은 반드시 viewport.h 로 잡는다.
      viewportLoss: px(screen.height - window.innerHeight),
      buildMarker: build ? build.getAttribute('content') : null,
      documentReady: document.readyState,
      stylesheets: document.styleSheets.length,
      measuredAt: new Date().toISOString(),
    };
  }

  // ── 2. 측정 범위 진실성 — 문서가 아니라 내부 상자가 스크롤하는가 ─────────────
  function scrollTruth(rootEl) {
    const scrollers = [];
    const all = document.querySelectorAll('*');
    for (let i = 0; i < all.length; i++) {
      const el = all[i];
      const cs = getComputedStyle(el);
      const oy = cs.overflowY, ox = cs.overflowX;
      const scrollableY = (oy === 'auto' || oy === 'scroll') && el.scrollHeight - el.clientHeight > 4;
      const scrollableX = (ox === 'auto' || ox === 'scroll') && el.scrollWidth - el.clientWidth > 4;
      if (scrollableY || scrollableX) {
        scrollers.push({
          selector: shortSelector(el),
          hiddenY: px(el.scrollHeight - el.clientHeight),
          hiddenX: px(el.scrollWidth - el.clientWidth),
          visibleRatio: px(el.clientHeight / Math.max(el.scrollHeight, 1)),
        });
      }
    }
    const docScrolls = document.documentElement.scrollHeight - window.innerHeight > 4;
    return {
      documentScrolls: docScrolls,
      innerScrollers: cap(scrollers, 20, '내부 스크롤 컨테이너'),
      // 이게 true 면 fullPage 스크린샷·문서 기준 측정이 화면 대부분을 놓친다.
      fullPageCaptureIsMisleading: !docScrolls && scrollers.length > 0,
      note: !docScrolls && scrollers.length > 0
        ? '문서가 아니라 내부 상자가 스크롤한다 → fullPage 캡처/문서 높이 측정은 일부만 본다. 해당 상자를 직접 스크롤하며 재야 한다.'
        : null,
    };
  }

  // ── 3. 글리프 기준 여백 — 요소 박스는 padding·min-height 에 속는다 ──────────
  function glyphBox(el) {
    const t = firstTextNode(el);
    if (!t) return null;
    const r = document.createRange();
    r.selectNodeContents(t);
    const rect = r.getBoundingClientRect();
    r.detach && r.detach();
    return rect.width || rect.height ? rect : null;
  }
  function firstTextNode(el) {
    const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT, {
      acceptNode: (n) => (n.nodeValue && n.nodeValue.trim() ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT),
    });
    return w.nextNode();
  }

  /** 형제 사이의 "보이는 간격"을 글리프 기준과 박스 기준 둘 다 낸다. 두 값이 다르면
   *  박스 기준으로 보고하던 숫자가 사용자 눈과 어긋나 있었다는 뜻이다. */
  function verticalGaps(rootEl) {
    const out = [];
    const parents = new Set();
    rootEl.querySelectorAll('*').forEach((el) => el.parentElement && parents.add(el.parentElement));
    let n = 0;
    for (const p of parents) {
      if (n > DEFAULTS.maxSample) { _trunc.push({ what: '형제 쌍 표본', found: '>' + DEFAULTS.maxSample, shown: DEFAULTS.maxSample }); break; }
      const kids = Array.from(p.children).filter((k) => {
        const cs = getComputedStyle(k);
        return isVisible(k, cs) && cs.position !== 'absolute' && cs.position !== 'fixed';
      });
      for (let i = 0; i + 1 < kids.length; i++) {
        const a = kids[i], b = kids[i + 1];
        const ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();
        if (rb.top < ra.bottom - 1) continue;           // 같은 줄이거나 겹침
        const boxGap = px(rb.top - ra.bottom);
        const ga = glyphBox(a), gb = glyphBox(b);
        const glyphGap = ga && gb ? px(gb.top - ga.bottom) : null;
        if (glyphGap !== null && Math.abs(glyphGap - boxGap) >= 2) {
          out.push({
            between: [shortSelector(a), shortSelector(b)],
            boxGap, glyphGap,
            delta: px(glyphGap - boxGap),
            why: '박스 기준과 글리프 기준이 다르다. 사용자가 보는 여백은 glyphGap 쪽이다.',
          });
        }
        n++;
      }
    }
    return cap(out, 30, '글리프-박스 여백 불일치');
  }

  // ── 4. 넘침·잘림 ─────────────────────────────────────────────────────────
  function overflow(rootEl) {
    const clipped = [], bleeding = [];
    const els = cap(Array.from(rootEl.querySelectorAll('*')), 3000, '요소 표본(넘침 검사)');
    for (const el of els) {
      const cs = getComputedStyle(el);
      if (!isVisible(el, cs)) continue;
      const hiddenish = cs.overflow === 'hidden' || cs.overflowY === 'hidden' || cs.overflowX === 'hidden';
      if (hiddenish && (el.scrollHeight - el.clientHeight > 2 || el.scrollWidth - el.clientWidth > 2)) {
        clipped.push({
          selector: shortSelector(el),
          clippedY: px(el.scrollHeight - el.clientHeight),
          clippedX: px(el.scrollWidth - el.clientWidth),
        });
      }
      const r = el.getBoundingClientRect();
      if (r.width > 0 && (r.left < -1 || r.right > window.innerWidth + 1)) {
        bleeding.push({ selector: shortSelector(el), left: px(r.left), right: px(r.right) });
      }
    }
    return {
      pageScrollX: px(document.documentElement.scrollWidth - document.documentElement.clientWidth),
      clipped: cap(clipped, 25, '잘린 요소'),
      bleedingOutsideViewport: cap(bleeding, 25, '뷰포트 밖 요소'),
    };
  }

  // ── 5. 간격 스케일 이탈 ──────────────────────────────────────────────────
  function scaleOutliers(rootEl, scale) {
    const counts = new Map();
    const els = cap(Array.from(rootEl.querySelectorAll('*')), 2000, '요소 표본(스케일 검사)');
    const props = ['paddingTop', 'paddingBottom', 'paddingLeft', 'paddingRight', 'gap', 'rowGap', 'columnGap'];
    for (const el of els) {
      const cs = getComputedStyle(el);
      if (!isVisible(el, cs)) continue;
      for (const p of props) {
        const v = parseFloat(cs[p]);
        if (!isFinite(v) || v === 0) continue;
        if (!scale.includes(Math.round(v))) {
          const key = Math.round(v);
          counts.set(key, (counts.get(key) || 0) + 1);
        }
      }
    }
    return Array.from(counts.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 15)
      .map(([value, count]) => ({ value, count }));
  }

  // ── 6. 타이포·위계 ───────────────────────────────────────────────────────
  function typography(rootEl, minFont) {
    const sizes = new Map(), weights = new Map(), tooSmall = [], noKeepAll = [];
    const els = cap(Array.from(rootEl.querySelectorAll('*')), 2000, '요소 표본(타이포 검사)');
    for (const el of els) {
      const cs = getComputedStyle(el);
      if (!isVisible(el, cs)) continue;
      const t = firstTextNode(el);
      if (!t) continue;
      const fs = Math.round(parseFloat(cs.fontSize));
      sizes.set(fs, (sizes.get(fs) || 0) + 1);
      weights.set(cs.fontWeight, (weights.get(cs.fontWeight) || 0) + 1);
      if (fs < minFont) tooSmall.push({ selector: shortSelector(el), fontSize: fs });
      // 한글이 있는데 keep-all 이 아니면 어절 중간에서 깨질 수 있다.
      if (/[가-힣]/.test(t.nodeValue) && cs.wordBreak !== 'keep-all') {
        noKeepAll.push({ selector: shortSelector(el), wordBreak: cs.wordBreak, sample: t.nodeValue.trim().slice(0, 20) });
      }
      // 한글 큰 제목에 1.0 미만 행간은 받침이 겹친다.
      const lh = parseFloat(cs.lineHeight);
      if (/[가-힣]/.test(t.nodeValue) && isFinite(lh) && fs >= 20 && lh / fs < 1.0) {
        tooSmall.push({ selector: shortSelector(el), lineHeightRatio: px(lh / fs), warn: '한글 제목 행간 1.0 미만 — 받침 겹침' });
      }
    }
    return {
      sizeCount: sizes.size,
      sizes: Array.from(sizes.entries()).sort((a, b) => a[0] - b[0]).map(([v, c]) => ({ px: v, count: c })),
      weightCount: weights.size,
      belowMinFont: cap(tooSmall, 25, '최소 폰트 미만·행간 경고'),
      koreanWithoutKeepAll: cap(noKeepAll, 25, 'keep-all 없는 한글 블록'),
    };
  }

  // ── 7. 터치 타깃 (인라인 예외 포함) ───────────────────────────────────────
  function touchTargets(rootEl) {
    const small = [];
    const els = rootEl.querySelectorAll('a,button,[role="button"],input,select,summary,[onclick]');
    for (const el of els) {
      const cs = getComputedStyle(el);
      if (!isVisible(el, cs)) continue;
      const r = el.getBoundingClientRect();
      if (r.width >= 24 && r.height >= 24) continue;
      // WCAG 2.5.8 인라인 예외: 문장 안에 있고 크기가 본문 line-height 에 제약되는 타깃.
      const parent = el.parentElement;
      const inSentence = parent && getComputedStyle(el).display.startsWith('inline') &&
        (parent.textContent || '').trim().length > (el.textContent || '').trim().length + 3;
      small.push({
        selector: shortSelector(el),
        w: px(r.width), h: px(r.height),
        inlineException: !!inSentence,
        note: inSentence ? '인라인 예외 대상 — 세로 여백을 억지로 늘리지 말 것' : '최소 24px 미만',
      });
    }
    return cap(small, 25, '작은 터치 타깃');
  }

  // ── 8. 대비 — 잴 수 있는 것만 재고 나머지는 unmeasured 로 ──────────────────
  function parseRGB(s) {
    const m = String(s).match(/rgba?\(([^)]+)\)/);
    if (!m) return null;
    const p = m[1].split(',').map((x) => parseFloat(x));
    if (p.length >= 4 && p[3] === 0) return null;     // 투명
    return { r: p[0], g: p[1], b: p[2], a: p.length >= 4 ? p[3] : 1 };
  }
  function lum({ r, g, b }) {
    const f = (c) => { c /= 255; return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); };
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
  }
  function ratio(a, b) {
    const l1 = lum(a), l2 = lum(b);
    return px((Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05));
  }
  /** 배경을 위로 올라가며 찾되, gradient·이미지를 만나면 **측정을 포기하고 그 사실을 남긴다.**
   *  backgroundColor 만 읽으면 gradient 위 텍스트를 페이지 배경과 비교해 오탐이 대량 발생한다. */
  function effectiveBg(el) {
    let cur = el;
    while (cur && cur !== document.documentElement) {
      const cs = getComputedStyle(cur);
      if (cs.backgroundImage && cs.backgroundImage !== 'none') {
        return { unmeasurable: true, reason: 'background-image/gradient', at: shortSelector(cur) };
      }
      const c = parseRGB(cs.backgroundColor);
      if (c && c.a === 1) return { color: c };
      if (c && c.a > 0) return { unmeasurable: true, reason: '반투명 배경 합성', at: shortSelector(cur) };
      cur = cur.parentElement;
    }
    const c = parseRGB(getComputedStyle(document.documentElement).backgroundColor);
    return c ? { color: c } : { unmeasurable: true, reason: '배경 미상', at: 'html' };
  }
  function contrast(rootEl) {
    const fails = [], unmeasured = [];
    const els = cap(Array.from(rootEl.querySelectorAll('*')), 1500, '요소 표본(대비 검사)');
    for (const el of els) {
      const cs = getComputedStyle(el);
      if (!isVisible(el, cs)) continue;
      const t = firstTextNode(el);
      if (!t) continue;
      const fg = parseRGB(cs.color);
      if (!fg) continue;
      const bg = effectiveBg(el);
      if (bg.unmeasurable) {
        unmeasured.push({ selector: shortSelector(el), reason: bg.reason, at: bg.at });
        continue;
      }
      const fs = parseFloat(cs.fontSize);
      const bold = parseInt(cs.fontWeight, 10) >= 700;
      const large = fs >= 24 || (bold && fs >= 18.66);
      const need = large ? 3 : 4.5;
      const r = ratio(fg, bg.color);
      if (r < need) {
        fails.push({ selector: shortSelector(el), ratio: r, need, fontSize: px(fs), large });
      }
    }
    return { fails: cap(fails, 25, '대비 미달'), unmeasured: cap(unmeasured, 25, '대비 측정 불가') };
  }

  // ── 9. 미디어쿼리 컨텍스트 — 지금 폭이 어떤 쿼리에 걸리는가 ─────────────────
  function mediaContext() {
    const hits = [], unreadable = [];
    for (const sheet of Array.from(document.styleSheets)) {
      let rules;
      try { rules = sheet.cssRules; } catch (e) { unreadable.push(sheet.href || '(inline)'); continue; }
      if (!rules) continue;
      for (const rule of Array.from(rules)) {
        if (rule.type === 4 /* MEDIA */) {
          const txt = rule.conditionText || rule.media.mediaText;
          if (window.matchMedia(txt).matches) hits.push(txt);
        }
      }
    }
    return {
      // 인쇄(A4 794px)가 max-width 쿼리에 걸리는 사고가 반복됐다. 화면 전용이면 `screen and` 로 묶는다.
      activeQueries: cap(Array.from(new Set(hits)), 30, '활성 미디어쿼리'),
      unreadableStylesheets: unreadable,
      hint: 'max-width 만 쓴 쿼리는 인쇄(≈794px)와 좁은 데스크톱 창에도 걸린다. 화면 전용이면 screen and (max-width: ...) 로 묶는다.',
    };
  }

  // ── 10. 사각지대 — 못 본 것을 "깨끗함"으로 읽지 않게 ───────────────────────
  function blindSpots() {
    const out = [];
    document.querySelectorAll('iframe').forEach((f) => {
      let ok = false;
      try { ok = !!f.contentDocument; } catch (e) { ok = false; }
      if (!ok) out.push({ kind: 'cross-origin iframe', selector: shortSelector(f), effect: '내부를 측정하지 못했다' });
    });
    let shadowCount = 0;
    document.querySelectorAll('*').forEach((el) => { if (el.shadowRoot) shadowCount++; });
    if (shadowCount) out.push({ kind: 'shadow root', count: shadowCount, effect: '이 계측기는 shadow DOM 내부를 재지 않는다' });
    const lazy = Array.from(document.images).filter((i) => !i.complete || i.naturalWidth === 0);
    if (lazy.length) out.push({ kind: '미로드 이미지', count: lazy.length, effect: '빈 상자로 보이는 것이 결함이 아니라 로딩 미완일 수 있다' });
    const anim = document.getAnimations ? document.getAnimations().filter((a) => a.playState === 'running') : [];
    if (anim.length) out.push({ kind: '진행 중 애니메이션', count: anim.length, effect: '정지 계측값이 프레임마다 달라질 수 있다' });
    return out;
  }

  // ── 유틸 ────────────────────────────────────────────────────────────────
  function shortSelector(el) {
    if (!el || !el.tagName) return '(unknown)';
    const id = el.id ? '#' + el.id : '';
    const cls = (el.className && typeof el.className === 'string')
      ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '';
    return el.tagName.toLowerCase() + id + cls;
  }

  function run(opts) {
    _trunc.length = 0;
    const o = Object.assign({}, DEFAULTS, opts || {});
    const rootEl = o.root ? document.querySelector(o.root) : document.body;
    if (!rootEl) throw new Error('root 를 찾지 못했다: ' + o.root);

    const result = {
      identity: identity(),
      scrollTruth: scrollTruth(rootEl),
      glyphVsBoxGaps: verticalGaps(rootEl),
      overflow: overflow(rootEl),
      scaleOutliers: scaleOutliers(rootEl, o.scale),
      typography: typography(rootEl, o.minFont),
      touchTargets: touchTargets(rootEl),
      contrast: contrast(rootEl),
      mediaContext: mediaContext(),
      blindSpots: blindSpots(),
    };
    result.truncated = _trunc.slice();
    result.unmeasured = []
      .concat(result.contrast.unmeasured.map((u) => `대비: ${u.selector} (${u.reason})`))
      .concat(result.mediaContext.unreadableStylesheets.map((s) => `미디어쿼리: 읽을 수 없는 스타일시트 ${s}`))
      .concat(result.blindSpots.map((b) => `${b.kind}: ${b.effect}`))
      .concat(_trunc.map((c) => `절단: ${c.what} ${c.found}건 중 ${c.shown}건만 반환 — 나머지는 확인 못함`));
    const notes = [];
    if (_trunc.length) notes.push('⚠ 목록이 잘렸다(truncated 참조). 상한에 걸린 항목은 "이게 전부"가 아니다.');
    if (result.unmeasured.length) notes.push('⚠ unmeasured 항목은 "문제 없음"이 아니라 "확인 못함"이다 — 보고에 그대로 옮길 것.');
    notes.push('이 계측기는 시각 판단(조화·인상)을 대체하지 않는다.');
    result.readMe = notes.join(' ');
    return result;
  }

  if (typeof window !== 'undefined') {
    window.__uiProbe = run;
    // 콘솔에 붙여넣었을 때 바로 결과가 보이게 한다.
    try {
      const r = run();
      window.__uiProbeLast = r;
      if (typeof console !== 'undefined') console.log(JSON.stringify(r, null, 2));
    } catch (e) {
      if (typeof console !== 'undefined') console.error('ui_probe 실패:', e);
    }
  }
})();
