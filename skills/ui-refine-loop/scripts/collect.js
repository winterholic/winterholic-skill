/**
 * 1b 결정론적 측정 — 브라우저 컨텍스트에서 실행된다(page.evaluate).
 *
 * 이 파일이 매 실행마다 재작성되면 라운드 간 점수 비교가 무의미해진다.
 * 판정 정의를 바꿀 때는 SKILL.md §1b 표와 함께 바꾼다.
 */

/**
 * 전량 수집 1패스. DOM 을 변경하지 않는다.
 *
 * getBoundingClientRect 는 동기 레이아웃 플러시를 강제하므로 DOM 변경과 번갈아
 * 호출하면 레이아웃 스래싱이 난다. 읽기만 모아서 하면 수천 건도 싸다.
 */
/**
 * 측정 대상 문서 목록 — 최상위 document + **같은 출처 iframe 문서**.
 *
 * ⚠️ 이전 판은 최상위 document 만 봤다. iframe 으로 임베드한 위젯이 **통째로 미측정**이라
 *    (실측 p20: DOM 12 / 요소 6) 안에 심어 둔 미정의 변수도 토큰 밖 18px 도 하나도 안 잡혔다.
 *    Shadow DOM 과 같은 「측정이 눈머는」 계열이고, 조용히 "깨끗함"으로 나오는 게 더 위험하다.
 * ⚠️ **교차 출처 iframe 은 원리적으로 접근할 수 없다**(same-origin policy). 빠지는 것 자체는
 *    막을 수 없으므로 `blocked` 로 돌려 **감사 사각지대로 보고**한다 — 조용히 빼면 안 된다.
 *
 * 좌표계: iframe 안의 `getBoundingClientRect()` 는 **그 iframe 의 뷰포트 기준**이다. 그대로 쓰면
 * 임베드 요소가 전부 페이지 좌상단에 있는 것처럼 잡혀 정렬·겹침·죽은 띠 판정이 통째로 어긋난다.
 * → 콘텐츠 원점(iframe 박스 + 테두리 + 패딩)만큼 밀어 **부모 좌표계로 통일**한다.
 */
function frameDocs() {
  const docs = [{ doc: document, view: window, dx: 0, dy: 0 }];
  const blocked = [];
  const scan = (entry) => {
    const frames = [];
    // iframe 은 shadow root 안에도 있다(위젯 컴포넌트가 흔히 그렇게 감싼다).
    const walk = (node) => {
      for (const el of node.querySelectorAll('iframe,frame')) frames.push(el);
      for (const el of node.querySelectorAll('*')) if (el.shadowRoot) walk(el.shadowRoot);
    };
    walk(entry.doc);
    for (const f of frames) {
      let d = null;
      try { d = f.contentDocument; } catch { d = null; }
      if (!d || !d.documentElement) {
        blocked.push(f.getAttribute('src') || f.src || '(src 없음)');
        continue;
      }
      const r = f.getBoundingClientRect();
      const cs = (f.ownerDocument.defaultView || window).getComputedStyle(f);
      const num = (v) => (Number.isFinite(parseFloat(v)) ? parseFloat(v) : 0);
      const child = {
        doc: d,
        view: f.contentWindow || d.defaultView,
        dx: entry.dx + r.left + num(cs.borderLeftWidth) + num(cs.paddingLeft),
        dy: entry.dy + r.top + num(cs.borderTopWidth) + num(cs.paddingTop),
      };
      docs.push(child);
      scan(child);   // 중첩 iframe
    }
  };
  scan(docs[0]);
  return { docs, blocked };
}

/**
 * 한 문서의 모든 스타일 규칙을 재귀로 훑는다.
 *
 * ⚠️ 이전 판은 `sheet.cssRules` 의 **최상위만** 봤다. 그래서 `@layer`·`@media`·`@supports`
 *    로 감싼 CSS 가 통째로 안 보였고, **Tailwind v4 는 전부를 `@layer` 안에 넣기 때문에
 *    스페이싱 변수도 hover 규칙도 하나도 발견되지 않았다.** 라이브러리마다 감싸는 방식이
 *    다르므로(@layer·@media·@supports·@container) 중첩을 따라 내려가야 한다.
 */
/**
 * 읽을 수 없는 스타일시트 목록 — **교차 출처 CSS**.
 *
 * ⚠️ 교차 출처 iframe 은 사각지대로 보고하면서 **교차 출처 시트는 조용히 건너뛰고 있었다.**
 *    그런데 이쪽이 훨씬 흔하다(CDN 의 디자인 토큰·컴포넌트 CSS 는 `crossorigin` 없이 링크된다).
 *    시트를 못 읽으면 선언 목록이 비어 **정상 토큰이 전부 「미정의 변수」로, 정상 포커스 링이
 *    전부 「focus 없음」으로 뒤집힌다**(실측 p29: 깨끗한 화면에서 16건 오탐).
 *    조용한 오탐 공장이라 iframe 과 같은 대칭 장치가 필요하다.
 */
function blockedSheets(docs) {
  const out = [];
  for (const ctx of docs) {
    for (const sheet of Array.from(ctx.doc.styleSheets || [])) {
      try { void sheet.cssRules; } catch { out.push(sheet.href || '(inline?)'); }
    }
  }
  return out;
}

function eachStyleRuleIn(ctx, visit) {
  const { doc, view } = ctx;
  // ⚠️ **지금 적용되는 규칙만** 본다. 라이브러리는 같은 토큰을 브레이크포인트마다 다시
  //    정의하므로(Pico 의 `--pico-typography-spacing-top` 은 값이 6종이다), 조건을 안 보면
  //    **지금 뷰포트가 아닌 값까지 스케일에 섞인다.**
  // ⚠️ 미디어 조건은 **그 문서의 window** 로 평가한다. iframe 은 폭이 부모와 다르므로
  //    부모의 matchMedia 로 재면 적용되지도 않는 브레이크포인트 값이 섞인다.
  const applies = (rule) => {
    if (rule.media && rule.conditionText) {
      try { return view.matchMedia(rule.conditionText).matches; } catch { return true; }
    }
    if (rule.conditionText && view.CSS && view.CSS.supports) {
      try { return view.CSS.supports(rule.conditionText); } catch { return true; }
    }
    return true;
  };
  const walk = (rules) => {
    for (const rule of Array.from(rules || [])) {
      if (rule.style) visit(rule);                 // 셀렉터 없는 :root·@property 도 포함
      if (rule.cssRules && applies(rule)) walk(rule.cssRules); // @layer·@media·@supports·@container
    }
  };
  const sheetsOf = (root) => [
    ...Array.from(root.styleSheets || []),
    ...Array.from(root.adoptedStyleSheets || []),   // 컴포넌트는 대개 이쪽으로 스타일을 붙인다
  ];
  const seenSheets = new Set();
  const visitSheets = (root) => {
    for (const sheet of sheetsOf(root)) {
      if (seenSheets.has(sheet)) continue;
      seenSheets.add(sheet);
      let rules;
      try { rules = sheet.cssRules; } catch { continue; } // cross-origin 시트는 건너뛴다
      walk(rules);
    }
  };
  visitSheets(doc);
  // ⚠️ **shadow root 안의 시트도 봐야 한다.** 안 보면 컴포넌트가 선언한 토큰이 안 잡혀
  //    스케일이 통째로 폴백하고, 컴포넌트 CSS 의 미정의 변수·hover 규칙도 못 읽는다.
  const walkShadow = (node) => {
    for (const el of node.querySelectorAll('*')) {
      if (!el.shadowRoot) continue;
      visitSheets(el.shadowRoot);
      walkShadow(el.shadowRoot);
    }
  };
  walkShadow(doc);
}

/** 모든 문서(부모 + 같은 출처 iframe)의 규칙을 훑는다. */
function eachStyleRule(visit, docs) {
  for (const ctx of (docs || frameDocs().docs)) eachStyleRuleIn(ctx, visit);
}

export function collectPage(config) {
  const { spacingScale = [], spacingBase = 0, fullPage = false,
          ignoreSelectors = [], intentionalHScroll = [] } = config || {};

  const MIN_SIZE = 8;
  const ALIGN_TOLERANCE = 1; // 서브픽셀 레이아웃에서 0.5px 차이는 상시 발생한다
  const OVERFLOW_TOLERANCE = 1;

  const ignoreSet = ignoreSelectors.length ? ignoreSelectors.join(',') : null;
  const hScrollSet = intentionalHScroll.length ? intentionalHScroll.join(',') : null;

  const matches = (el, sel) => {
    if (!sel) return false;
    try { return el.matches(sel) || el.closest(sel) !== null; } catch { return false; }
  };

  // ---------- 문서 경계 (부모 + 같은 출처 iframe) ----------

  const { docs: DOCS, blocked: blockedFrames } = frameDocs();
  const blockedCss = blockedSheets(DOCS);
  // 선언 목록을 못 읽으면 이 두 판정은 **오탐만 만든다.** 조용히 내보내지 말고 보류한다.
  const cssReadable = blockedCss.length === 0;
  const offsetOf = new Map(DOCS.map((d) => [d.doc, d]));
  const ctxOf = (el) => offsetOf.get(el.ownerDocument) || DOCS[0];

  /** 부모 좌표계로 맞춘 사각형. iframe 안 요소는 iframe 콘텐츠 원점만큼 밀린다. */
  const rectOf = (el) => {
    const r = el.getBoundingClientRect();
    const o = ctxOf(el);
    if (!o.dx && !o.dy) return r;
    return { x: r.x + o.dx, y: r.y + o.dy, width: r.width, height: r.height,
             top: r.top + o.dy, bottom: r.bottom + o.dy,
             left: r.left + o.dx, right: r.right + o.dx };
  };
  /** 계산 스타일은 **그 요소가 속한 window** 로 읽는다(문서마다 루트 폰트·미디어가 다르다). */
  const csOf = (el) => (el.ownerDocument.defaultView || window).getComputedStyle(el);
  /** 요소가 속한 문서의 뷰포트 높이 — iframe 은 부모와 다르다. */
  const vhOf = (el) => (el.ownerDocument.defaultView || window).innerHeight || vh;
  /** 문서 전체 질의 — iframe 문서까지 함께 훑는다. */
  const queryAll = (sel) => DOCS.flatMap((d) => Array.from(d.doc.querySelectorAll(sel)));
  /** 서브트리 질의 — 중첩 표(그리드 안 그리드)를 바깥 것에 섞지 않는다. */
  const queryIn = (root, sel) => Array.from(root.querySelectorAll(sel))
    .filter((el) => el.closest('[role="table"], [role="grid"], [role="treegrid"], table') === root);
  /** 조상 — 문서 최상단에서 멈추지 않고 자기를 담은 iframe 요소로 올라간다. */
  const ancestorOf = (el) => el.parentElement
    || (el.ownerDocument.defaultView && el.ownerDocument.defaultView.frameElement) || null;

  // ---------- 요소 수집 ----------

  const vw = window.innerWidth;
  const vh = window.innerHeight;

  /**
   * 후보 집합을 두 겹으로 나눈다.
   *
   * 이전 판은 "자체 텍스트 또는 배경/테두리"만 후보로 삼았는데, 그러면 ul·div 같은
   * 레이아웃 컨테이너가 전부 빠진다. 그런데 간격·위계·정렬 판정에 필요한 게 바로 그
   * 컨테이너들이라 측정이 반쪽이 됐다(위계 역전이 한 건도 안 잡혔다).
   *
   * measurable : 레이아웃에 참여하는 블록 전부 — 측정용
   * visible    : 사람이 화면에서 식별 가능한 것 — 배지를 그릴 대상
   * 번호는 measurable 전체에 매긴다. 1b finding 이 배지 없는 컨테이너를 가리켜도
   * 하네스는 셀렉터를 알고, 비평가는 애초에 1b finding 을 보지 않으므로 문제없다.
   */
  const isMeasurable = (el, rect, cs) => {
    if (rect.width < MIN_SIZE || rect.height < MIN_SIZE) return false;
    // ⚠️ 기본은 **첫 뷰포트만** 잰다 — 비평가가 보는 스크린샷과 범위를 맞추기 위해서다.
    //    그런데 긴 문서(보고서·런북)는 첫 화면이 전체의 5% 도 안 돼서 **나머지가 통째로
    //    미감사 상태로 남는다.** `fullPage` 를 켜면 문서 전체를 재고, 캡처도 전체 페이지로 찍어
    //    범위를 다시 맞춘다.
    if (!fullPage && (rect.bottom < 0 || rect.top > vh)) return false;
    if (rect.right < 0 || rect.left > vw) return false;
    if (cs.display === 'none' || cs.visibility === 'hidden' || cs.opacity === '0') return false;
    if (matches(el, ignoreSet)) return false;
    if (['SCRIPT', 'STYLE', 'HEAD', 'META', 'LINK', 'TITLE'].includes(el.tagName)) return false;
    // ⚠️ **SVG 내부는 통째로 뺀다.** Mermaid 다이어그램의 `rect`·`g`·`text` 는 우리가 감사할 수
    //    있는 CSS 레이아웃이 아니다 — 겹쳐 그리는 게 정상이고, `text` 의 scrollWidth 는 늘 넘치며,
    //    좌표는 뷰박스 변환을 거친다. 판정마다 따로 빼면 계속 새는 곳이 생기므로(실측: 겹침에서
    //    빼자 오버플로·정렬로 옮겨 나왔다) **측정 단계에서 한 번에 뺀다.**
    //    다이어그램이 컨테이너를 넘치는 것은 `<svg>` 루트와 `.mermaid-wrap` 이 여전히 잡는다.
    if (el.ownerSVGElement != null) return false;
    return true;
  };

  const isVisible = (el, cs) => {
    const hasOwnText = Array.from(el.childNodes)
      .some((n) => n.nodeType === Node.TEXT_NODE && n.textContent.trim().length > 0);
    const hasSurface =
      cs.backgroundColor !== 'rgba(0, 0, 0, 0)' ||
      cs.backgroundImage !== 'none' ||
      parseFloat(cs.borderTopWidth) > 0 ||
      parseFloat(cs.borderBottomWidth) > 0;
    return hasOwnText || hasSurface;
  };

  /**
   * shadow DOM 까지 뚫고 모든 요소를 훑는다.
   *
   * ⚠️ 이전 판은 `document.querySelectorAll('*')` 만 썼다. 그래서 **웹컴포넌트로 만든 화면이
   *    통째로 안 보였다** — 실측: light DOM 9개 / shadow 포함 31개인데 측정은 3개였고,
   *    shadow 안에 심어 둔 미정의 변수도 못 잡았다. 디자인 시스템·임베드 위젯이 대부분
   *    이 방식이라 "깨끗함"으로 오판할 위험이 크다.
   */
  const deepAll = () => {
    const out = [];
    const walk = (node) => {
      for (const el of node.querySelectorAll('*')) {
        out.push(el);
        if (el.shadowRoot) walk(el.shadowRoot);
      }
    };
    // DOCS 에 iframe 문서가 이미 평탄하게 들어 있으므로 여기서 다시 내려가지 않는다.
    for (const d of DOCS) walk(d.doc);
    return out;
  };

  const cssPath = (el) => {
    const parts = [];
    let cur = el;
    while (cur && cur.nodeType === Node.ELEMENT_NODE && parts.length < 6) {
      let part = cur.tagName.toLowerCase();
      if (cur.id) { parts.unshift(`#${CSS.escape(cur.id)}`); break; }
      const parent = cur.parentElement;
      if (parent) {
        const sameTag = Array.from(parent.children).filter((c) => c.tagName === cur.tagName);
        if (sameTag.length > 1) part += `:nth-of-type(${sameTag.indexOf(cur) + 1})`;
      }
      parts.unshift(part);
      // shadow·iframe 경계를 넘을 때는 표시한다 — 이 셀렉터는 querySelector 로 못 찾는다.
      // 4층이 소스를 grep 할 때 "컴포넌트 내부"·"임베드 문서"임을 알아야 엉뚱한 파일을 고치지 않는다.
      const frameEl = !cur.parentElement && cur.ownerDocument.defaultView
        ? cur.ownerDocument.defaultView.frameElement : null;
      if (!cur.parentElement && cur.parentNode && cur.parentNode.host) {
        parts.unshift('>>');
        cur = cur.parentNode.host;
      } else if (frameEl) {
        parts.unshift('>>iframe');   // 이 아래는 **다른 파일**이다
        cur = frameEl;
      } else {
        cur = cur.parentElement;
      }
    }
    return parts.join(' > ');
  };

  const px = (v) => {
    const n = parseFloat(v);
    return Number.isFinite(n) ? n : 0;
  };

  // ⚠️ `aria-labelledby` 는 라벨링의 표준 수단이고 axe(1a)도 이걸로 통과시킨다.
  //    안 보면 디자인시스템 폼(MUI·Radix 계열)의 정상 입력이 전부 "라벨 없음"으로 잡혀
  //    **1a 와 1b 가 같은 화면을 두고 정반대 답을 낸다**(실측 p27: 3건 오탐).
  function hasLabelledby(el) {
    const ids = (el.getAttribute('aria-labelledby') || '').trim().split(/\s+/).filter(Boolean);
    return ids.some((id) => {
      const t = el.ownerDocument.getElementById(id);
      return t && (t.textContent || '').trim().length > 0;
    });
  }

  const elements = [];
  const byNode = new Map();

  /**
   * ★ 요소 번호는 **DOM 순회 순서**로 매긴다 — 측정 대상 여부·뷰포트와 무관하게.
   *
   * ⚠️ 이전 판은 `elements.length + 1`, 즉 **측정 대상만 세어** 번호를 붙였다. 그런데 측정 대상은
   *    뷰포트마다 다르다(실측 p6-bigdom: 1440 에서 224개 / 360 에서 77개). 그래서 **같은 `#28` 이
   *    1440 에서는 종목코드 셀, 360 에서는 등락률 셀**이었다. 비평가는 여러 폭의 이미지를 함께 보고
   *    번호를 한 줄에 섞어 쓰는데 3층은 measure 한 개로 대조하므로, **조용히 엉뚱한 요소에 매칭**된다.
   *    → DOM 순서로 매기면 같은 DOM 인 한 폭이 달라도 번호가 같다.
   *    (한계: 반응형으로 **DOM 자체가 바뀌면** 여전히 어긋난다. 그건 번호로는 못 푼다.)
   */
  const ALL = deepAll();   // 한 번만 훑는다 — 번호 부여와 측정이 같은 순회를 공유한다
  const nOfNode = new Map();
  ALL.forEach((el, i) => nOfNode.set(el, i + 1));

  ALL.forEach((el) => {
    const cs = csOf(el);
    const rect = rectOf(el);
    if (!isMeasurable(el, rect, cs)) return;

    const rec = {
      visible: isVisible(el, cs),
      n: nOfNode.get(el),
      // 부모 번호 — 3층이 「1b 는 넘치는 컨테이너를 재고 비평가는 잘려 보이는 셀을 가리킨다」는
      // 어긋남을 조상 관계로 흡수하기 위해 필요하다(실측: overflow 가 HEADER·MAIN 에 붙었다).
      p: el.parentElement ? (nOfNode.get(el.parentElement) ?? null) : null,
      selector: cssPath(el),
      tag: el.tagName.toLowerCase(),
      text: (el.textContent || '').trim().slice(0, 60),
      rect: { x: rect.x, y: rect.y, w: rect.width, h: rect.height,
              top: rect.top, right: rect.right, bottom: rect.bottom, left: rect.left },
      style: {
        display: cs.display,
        position: cs.position,
        flexDirection: cs.flexDirection,
        zIndex: cs.zIndex,
        pointerEvents: cs.pointerEvents,
        overflowX: cs.overflowX,
        overflowY: cs.overflowY,
        fontSize: px(cs.fontSize),
        fontWeight: cs.fontWeight,
        color: cs.color,
        backgroundColor: cs.backgroundColor,
        borderBottomWidth: px(cs.borderBottomWidth),
        paddingTop: px(cs.paddingTop), paddingRight: px(cs.paddingRight),
        paddingBottom: px(cs.paddingBottom), paddingLeft: px(cs.paddingLeft),
        marginTop: px(cs.marginTop), marginBottom: px(cs.marginBottom),
        gap: px(cs.rowGap), columnGap: px(cs.columnGap),
        // 저자가 선언한 축약 — 오버플로 판정이 이걸 봐야 클램프·말줄임을 결함으로 안 센다
        lineClamp: (cs.webkitLineClamp && cs.webkitLineClamp !== 'none') ? cs.webkitLineClamp : '',
        textOverflow: cs.textOverflow || '',
      },
      scroll: { sw: el.scrollWidth, cw: el.clientWidth, sh: el.scrollHeight, ch: el.clientHeight },
    };
    elements.push(rec);
    byNode.set(el, rec);
    // 배지는 시각적으로 식별 가능한 것에만 그린다 — 컨테이너까지 그리면 화면이 배지로 덮인다
    if (rec.visible) el.setAttribute('data-uir', String(rec.n));
  });

  const findings = [];
  const add = (kind, targets, detail) => findings.push({ kind, targets, detail });

  const addGrouped = (kind, targets, detail) => {
    const hit = findings.find((f) => f.kind === kind && f.detail.startsWith(detail));
    if (!hit) { findings.push({ kind, targets: targets.slice(0, 8), detail, n: 1 }); return; }
    hit.n++;
    if (hit.targets.length < 8) hit.targets.push(...targets.slice(0, 8 - hit.targets.length));
    hit.detail = `${detail} (같은 규칙 ${hit.n}곳)`;
  };

  /**
   * ★ **무너진 요소** — `MIN_SIZE`(8px) 미만이라 측정 대상에서 빠지는 것들.
   *
   * ⚠️ 지금까지 "작아서 못 잰다"와 "작아서 결함이다"를 구분하지 않았다. 데이터가 안 와서
   *    높이 4px 로 접힌 카드, flex 계산 실수로 폭 3px 이 된 열은 **눈에 보이는 결함인데
   *    측정 대상에서 아예 빠져 어떤 판정에도 안 걸렸다**(실측 p30: 심어둔 2건이 통째로 미탐).
   *    더 나쁜 건 **요소가 사라지면 모든 지표가 좋아진다**는 점이다 — 5층이 그걸 개선으로 읽는다.
   * ⚠️ 판정 기준은 크기가 아니라 **"저자가 면을 그렸는가"** 다. 테두리·배경이 있는 상자가
   *    한쪽만 8px 미만이면 그건 그리려던 것이 무너진 것이다. 구분선(hr)·아이콘 장식은
   *    두 변이 다 작거나 면이 없으므로 걸리지 않는다.
   */
  const collapsedEls = [];
  ALL.forEach((el) => {
    const cs = csOf(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || cs.opacity === '0') return;
    if (el.ownerSVGElement != null || matches(el, ignoreSet)) return;
    if (['SCRIPT', 'STYLE', 'HEAD', 'META', 'LINK', 'TITLE', 'BR', 'HR'].includes(el.tagName)) return;
    const r = rectOf(el);
    const collapsed = (r.width < MIN_SIZE) !== (r.height < MIN_SIZE);   // 한쪽만 무너진 것
    if (!collapsed || r.width < 1 || r.height < 1) return;
    // 「무너졌다」의 근거는 두 가지다: **저자가 면을 그렸거나**(그리려던 상자가 접혔다)
    // **안에 내용이 있는데 자리가 없거나**(폭 3px 인 열에 텍스트가 들어 있다).
    // 후자를 빼면 배경 없는 flex 열이 통째로 미탐이 된다(실측 p30: `flex:0 0 3px` 열).
    const hasSurface = cs.backgroundColor !== 'rgba(0, 0, 0, 0)' ||
                       cs.backgroundImage !== 'none' ||
                       parseFloat(cs.borderTopWidth) > 0 || parseFloat(cs.borderLeftWidth) > 0;
    const hasContent = el.children.length > 0 || (el.textContent || '').trim().length > 0;
    if (!hasSurface && !hasContent) return;
    // 내용도 자식도 없는 순수 장식(구분선 대용 div 등)은 저자 의도일 수 있다
    if (!hasContent && (r.width < 2 || r.height < 2)) return;
    collapsedEls.push({ el, r });
  });
  // ⚠️ **가장 바깥만 보고한다.** 열이 3px 로 접히면 그 안 자식도 전부 3px 이라, 원인 하나가
  //    요소 수만큼 계수된다(실측: 3px 열 하나가 4건). 고칠 곳은 바깥 한 군데다.
  collapsedEls
    .filter(({ el }) => !collapsedEls.some((o) => o.el !== el && o.el.contains(el)))
    .forEach(({ el, r }) => {
      addGrouped('collapsed', [],
        `${el.tagName.toLowerCase()} 가 ${Math.round(r.width)}×${Math.round(r.height)}px 로 무너짐 — 면은 그려져 있는데 내용이 들어갈 자리가 없다`);
    });

  /**
   * 같은 판정이 문서 전체에서 반복될 때 **한 건으로 모은다.**
   * ⚠️ 전체 페이지를 재기 시작하면서 드러난 문제 — 템플릿의 간격 결정 하나가
   *    섹션마다 반복돼 39건으로 셌다. 고칠 곳은 한 군데인데 사전식 비교를 지배한다.
   */

  // ---------- 오버플로 ----------

  // 가로 넘침은 조상으로 그대로 전파돼 원인 1개가 html·body·div·main·section 5건으로
  // 셌다. 실제로 콘텐츠를 못 담는 것은 **가장 안쪽 요소**이므로 거기만 보고한다.
  const hOverflow = [];
  byNode.forEach((rec, el) => {
    const scrollable = /(auto|scroll)/.test(rec.style.overflowX + rec.style.overflowY);
    if (scrollable || matches(el, hScrollSet)) return;
    if (rec.scroll.sw <= rec.scroll.cw + OVERFLOW_TOLERANCE) return;
    // ⚠️ 세로와 대칭으로 맞춘다. `overflow-x:visible` 이면 **글자가 잘리지 않는다** —
    //    상자 밖에 그려질 뿐이다. 진짜 결함은 ①잘려서 못 읽거나 ②화면 밖으로 나가 못 볼 때다.
    //    실측: Tufte 사이드노트(`float:right` + 음수 마진)가 부모의 scrollWidth 를 부풀려
    //    본문 문단마다 "가로 983 > 702" 가 찍혔는데, 사이드노트는 화면 안에 멀쩡히 보인다.
    // ⚠️ **말줄임도 선언된 축약이다.** `text-overflow:ellipsis` 는 `overflow:hidden` +
    //    `white-space:nowrap` 과 함께 쓰이므로 클리핑 조건을 정의상 항상 만족한다.
    //    표·카드 UI 에서 보편적인 정상 처리라, 빼지 않으면 말줄임 셀 수만큼 오탐이 된다.
    if (rec.style.textOverflow && rec.style.textOverflow !== 'clip') return;
    const contentRight = rec.rect.left + rec.scroll.sw;
    // ①자기가 잘라내거나 ②**조상이 잘라내거나** ③화면 밖으로 나가면 못 읽는다.
    //   ②를 빼면 `.wrap{overflow:hidden}` 안에서 넘치는 자식이 통째로 안 잡힌다 —
    //   자기 overflow-x 는 visible 이라서 ①에 안 걸린다.
    let clipped = rec.style.overflowX === 'hidden';
    // ⚠️ **iframe 경계를 넘어 올라간다.** 임베드 문서의 요소는 부모 뷰포트 안에 있어도
    //    iframe 박스가 잘라내면 못 읽는다 — 경계에서 멈추면 그 결함이 통째로 빠진다.
    for (let a = ancestorOf(el); a && !clipped; a = ancestorOf(a)) {
      const isFrame = /^(iframe|frame)$/.test(a.tagName.toLowerCase());
      // iframe 은 computed overflow 와 무관하게 자기 박스로 콘텐츠를 잘라낸다.
      if (!isFrame && !/(hidden|clip)/.test(csOf(a).overflowX)) continue;
      if (contentRight > rectOf(a).right + OVERFLOW_TOLERANCE) clipped = true;
    }
    const offscreen = contentRight > vw + OVERFLOW_TOLERANCE;
    /**
     * ⚠️ **세 번째 경로: 잘리지도 화면 밖도 아닌데 옆 요소를 덮어쓰는 경우.**
     *    `overflow:visible` 인 좁은 상자에서 긴 금액·이름이 밖으로 그려지면 **글자가 겹쳐
     *    둘 다 못 읽는다.** 그런데 ①은 자기가 안 자르니 통과, ③은 화면 안이라 통과,
     *    겹침 판정은 rect(보더 박스) 기준이라 상자가 안 커져서 못 본다 —
     *    **두 판정의 사각지대에 정확히 들어간다**(실측 p30: 눈에 명백히 겹치는데 0건).
     *    콘텐츠가 실제로 뻗은 범위가 다음 형제의 상자를 침범하는지 본다.
     */
    let invades = false;
    if (!clipped && !offscreen && rec.style.overflowX === 'visible') {
      const p = el.parentElement;
      const sibs2 = p ? Array.from(p.children).filter((x) => x !== el && byNode.has(x)) : [];
      invades = sibs2.some((x) => {
        const r2 = byNode.get(x).rect;
        const vOverlap = Math.min(rec.rect.bottom, r2.bottom) - Math.max(rec.rect.top, r2.top);
        return vOverlap > 1 && r2.left >= rec.rect.right - 1 && r2.left < contentRight - OVERFLOW_TOLERANCE;
      });
    }
    if (!clipped && !offscreen && !invades) return;
    hOverflow.push({ rec, el });
  });
  // ⚠️ **규칙 단위로 묶는다.** 가상 스크롤 목록에서 같은 `.row` 규칙 하나가 **20건**으로 셌다
  //    (실측). 고칠 곳은 그리드 정의 한 군데인데 사전식 비교를 그 한 규칙이 지배한다.
  //    같은 부모 아래 같은 태그가 다 넘치면 그건 한 가지 레이아웃 문제다.
  hOverflow
    .filter(({ el }) => !hOverflow.some((o) => o.el !== el && el.contains(o.el)))
    .forEach(({ rec, el }) => {
      const p = el.parentElement;
      const key = `${p ? (byNode.get(p)?.n ?? p.tagName) : 'root'}|${el.tagName}`;
      // ⚠️ 넘침 **크기를 그룹 키에 넣으면 안 된다** — 행마다 내용 폭이 달라 383/389/414 처럼
      //    갈리면서 같은 규칙이 다시 쪼개진다(실측 20→7건에서 멈췄다). 크기는 대상에서 읽는다.
      addGrouped('overflow', [rec.n],
        `가로 넘침 (콘텐츠가 상자를 넘어 잘리거나 화면 밖·옆 요소를 덮음) [${key}]`);
    });

  byNode.forEach((rec, el) => {
    const scrollable = /(auto|scroll)/.test(rec.style.overflowX + rec.style.overflowY);
    if (scrollable || matches(el, hScrollSet)) return;
    // 세로 오버플로는 `overflow-y: hidden` 일 때만 결함이다(텍스트가 잘린다).
    // 그 외에는 페이지가 그냥 스크롤되는 정상 상태이고, body·main 이 전부 위반으로 잡힌다.
    // ⚠️ **줄 수 클램프는 저자가 선언한 축약이다.** `-webkit-line-clamp: 2` 는 정의상 항상
    //    `overflow:hidden` + `scrollHeight > clientHeight` 라, 이걸 안 빼면 **카드형 화면마다
    //    클램프한 요소 수만큼 오탐**이 쏟아진다(실측 p26: 한 샷에 10건, `overflow` 는 사전식
    //    1순위라 그 화면의 판정 전체를 오염시킨다). 배제 규칙을 더하는 게 아니라
    //    **선언된 것을 읽는 것**이다 — 저자가 "여기서 자른다"고 CSS 에 써 뒀다.
    if (rec.style.lineClamp) return;
    if (rec.style.overflowY === 'hidden' && rec.scroll.sh > rec.scroll.ch + OVERFLOW_TOLERANCE) {
      add('overflow', [rec.n], `세로 잘림 ${rec.scroll.sh} > ${rec.scroll.ch}`);
    }
  });

  // ---------- 미정의 CSS 변수 참조 ----------
  // ★ 실사용에서 드러난 구멍. `gap:var(--sm-6)` 처럼 **선언되지 않은 변수**를 참조하면
  //   그 속성이 통째로 무효가 돼 gap·padding 이 0 으로 무너지고 **글자가 서로 붙어 나온다**
  //   (실측: 헤더 메타가 "작성자확인 필요" 처럼 붙었다. 원인은 토큰 선언이 스킨 교체 블록
  //   안에 있어 스킨 적용 순간 사라진 것). 눈에는 띄지만 어떤 기하 판정에도 안 걸린다 —
  //   무너진 값이 0 이라 "이탈"도 "정렬 편차"도 아니기 때문이다.
  // 결정론적이고 오탐이 거의 없다: 참조는 있는데 선언이 어디에도 없으면 그건 그냥 오타·누락이다.
  // ⚠️ **문서 단위로 판정한다.** 커스텀 속성은 **iframe 경계를 넘어 상속되지 않는다** —
  //    부모가 `--space-4` 를 선언해도 임베드 문서 안에서는 미정의다. 선언 목록을 문서끼리
  //    합치면 그 결함이 통째로 사라진다(같은 이유로 루트 계산값도 그 문서의 루트를 본다).
  const missing = new Map();
  for (const ctx of DOCS) {
    const declared = new Set();
    eachStyleRuleIn(ctx, (rule) => {
      for (const prop of Array.from(rule.style)) if (prop.startsWith('--')) declared.add(prop);
      // @property 로 등록된 이름도 선언으로 본다
      if (rule.name && String(rule.name).startsWith('--')) declared.add(String(rule.name));
    });
    ctx.doc.querySelectorAll('[style]').forEach((el) => {
      const m = el.getAttribute('style').match(/--[\w-]+(?=\s*:)/g);
      if (m) m.forEach((x) => declared.add(x));
    });
    // 런타임에 JS 가 심는 경우까지 감안해 루트 계산값도 확인한다
    const rootCS = ctx.view.getComputedStyle(ctx.doc.documentElement);

    // ⚠️ **스페이싱 속성만 본다.** 미정의 var 을 **의도적인 선택적 오버라이드 훅**으로 쓰는 것은
    //    널리 쓰이는 관용구다 — Bootstrap 의 `body{text-align:var(--bs-body-text-align)}` 은
    //    "설정 안 하면 기본값"을 노린 것이라 결함이 아니다(실측: 이 필터가 없으면 3건 오탐).
    //    반면 `gap`·`padding`·`margin` 이 무효가 되면 **0 으로 무너져 글자가 붙는다** —
    //    눈에 보이는 결함이고, 그 값을 "설정 안 함"으로 두려는 저자는 없다.
    const SPACING_PROP = /^(gap|row-gap|column-gap|padding|margin|inset)(-|$)/;
    // ⚠️ **`rule.style` 로 읽으면 안 된다.** `gap:var(--x)` 처럼 **단축 속성에 var 이 들어가면
    //    CSSOM 이 직렬화하지 못해 `getPropertyValue('gap')` 가 빈 문자열을 돌려준다.**
    //    (실측: 이 방식으로 짰더니 양성 대조군이 조용히 죽었다.) 규칙 텍스트를 직접 파싱한다.
    eachStyleRuleIn(ctx, (rule) => {
      const text = rule.cssText || '';
      if (!text.includes('var(')) return;
      const block = text.slice(text.indexOf('{') + 1, text.lastIndexOf('}'));
      for (const decl of block.split(';')) {
        const i = decl.indexOf(':');
        if (i < 0) continue;
        const prop = decl.slice(0, i).trim().toLowerCase();
        const val = decl.slice(i + 1);
        if (!SPACING_PROP.test(prop)) continue;
        if (!val.includes('var(')) continue;
        // 폴백이 있는 참조(`var(--x, 8px)`)는 무너지지 않으므로 제외한다
        const re = /var\(\s*(--[\w-]+)\s*\)/g;
        let m;
        while ((m = re.exec(val))) {
          const name = m[1];
          if (declared.has(name)) continue;
          if (rootCS.getPropertyValue(name).trim() !== '') continue;
          missing.set(name, (missing.get(name) || 0) + 1);
        }
      }
    });
  }
  // 시트를 다 못 읽었으면 "선언되지 않았다"고 말할 근거가 없다 — 판정을 내보내지 않는다.
  if (cssReadable) {
    missing.forEach((n, name) => {
      add('undefined-var', [], `${name} 이 선언되지 않았는데 참조된다 (${n}곳) — 해당 속성이 무효가 된다`);
    });
  }

  // ---------- 겹침 (형제끼리만) ----------
  // 전체 조합은 O(n²)로 터지고, 부모-자식 겹침은 정상이라 형제로 한정한다.

  /**
   * ⚠️ **회전·기울임된 요소의 `getBoundingClientRect()` 는 실제 상자가 아니다.**
   *    축정렬 바운딩 박스라 실제보다 크고 모서리 좌표가 밀린다(scale 은 AABB 가 정확해서
   *    지금까지 문제가 안 됐다). 그래서 겹치지 않은 것이 겹침으로, 맞춰진 것이 어긋남으로 잡힌다
   *    — 실측 p33(네오브루탈리즘): `overlap` 13 · `alignment` 6 이 전부 회전 때문이었다.
   *    **측정 도구가 진실을 못 재는 경우이므로 재지 않는다**(엔진이 보장하는 축을 안 재는 것과 같은 이유).
   */
  const rotatedSelf = (el) => {
    const t = csOf(el).transform;
    if (!t || t === 'none') return false;
    const m = /^matrix\(([^,]+),\s*([^,]+),/.exec(t);
    if (!m) return /rotate|skew/.test(t);
    return Math.abs(parseFloat(m[2])) > 0.001;   // b 항이 0 이 아니면 회전·기울임이 섞여 있다
  };
  // ⚠️ **조상까지 봐야 한다.** 회전은 자식에게 상속되지 않지만(자식의 computed transform 은
  //    `none`) 자식의 rect 는 부모 회전만큼 함께 틀어진다. 자기 것만 보면 회전한 카드는
  //    빠지고 그 **안의 요소들**이 그대로 오탐으로 남는다(실측 p33: 제외해도 20건 잔존).
  const rotCache = new WeakMap();
  const rotated = (el) => {
    if (!el) return false;
    if (rotCache.has(el)) return rotCache.get(el);
    let cur = el, hit = false;
    for (let d = 0; cur && d < 12 && !hit; d++) {
      hit = rotatedSelf(cur);
      cur = ancestorOf(cur);
    }
    rotCache.set(el, hit);
    return hit;
  };

  const overlapExempt = (rec) =>
    ['fixed', 'sticky', 'absolute'].includes(rec.style.position) ||
    rec.style.zIndex !== 'auto' ||
    rec.style.pointerEvents === 'none' ||
    // ⚠️ **인라인 요소는 겹침 판정에서 뺀다.** 여러 줄로 접힌 인라인의 `getBoundingClientRect()` 는
    //    각 줄을 합친 하나의 상자라, 같은 줄에 나란히 있는 `<code>` 둘이 서로 겹친 것처럼 보인다
    //    (실측: 전체 페이지 측정에서 이 오탐만 수십 건).
    rec.style.display.startsWith('inline');
    // (SVG 내부는 isMeasurable 에서 이미 제외되므로 여기서 다시 보지 않는다)

  const nodeOfN0 = new Map();
  byNode.forEach((rec, el) => nodeOfN0.set(rec.n, el));

  const parents = new Map();
  byNode.forEach((rec, el) => {
    const p = el.parentElement;
    if (!p) return;
    if (!parents.has(p)) parents.set(p, []);
    parents.get(p).push(rec);
  });

  parents.forEach((sibs) => {
    for (let i = 0; i < sibs.length; i++) {
      for (let j = i + 1; j < sibs.length; j++) {
        const a = sibs[i].rect, b = sibs[j].rect;
        if (overlapExempt(sibs[i]) || overlapExempt(sibs[j])) continue;
        if (rotated(nodeOfN0.get(sibs[i].n)) || rotated(nodeOfN0.get(sibs[j].n))) continue;
        const ox = Math.min(a.right, b.right) - Math.max(a.left, b.left);
        const oy = Math.min(a.bottom, b.bottom) - Math.max(a.top, b.top);
        if (ox > 1 && oy > 1) {
          add('overlap', [sibs[i].n, sibs[j].n], `${Math.round(ox)}×${Math.round(oy)}px`);
        }
      }
    }
  });

  // ---------- 정렬 편차 ----------
  // ⚠️ 재작성(다스택 실측 후). 이전 판은 부모의 배치 맥락을 읽지 않아 정상 레이아웃을
  //    대량 오탐했다 — 6개 스택(Tailwind v3/v4·Bootstrap·CSS-in-JS·MUI·대량표)에서
  //    정렬 히트 73건 중 68건이 오탐이었고 원인이 4종이었다:
  //      1) flex-row + align-items:center 면 높이가 다를 때 top·bottom 이 달라야 정상인데 위반 처리
  //      2) table-row-group(tbody)의 자식 tr 은 세로 스택인데 가로로 오판 → 행마다 위반
  //      3) max-width + margin:auto 인 중앙정렬 컨테이너가 형제와 left 다른 것을 위반 처리
  //      4) flex-wrap 으로 두 줄이 된 것을 한 줄로 보고 2행 요소를 1행과 비교
  //
  // 원칙: **레이아웃 엔진이 정렬을 보장하는 축은 재지 않는다.** 보장하지 않는 축만 잰다.
  //   flex 는 교차축에서 마진 박스를 정렬해 주므로 start 계열이 아닌 정렬값에서는
  //   좌표 차이가 곧 의도다. 잴 수 있는 것은 "엔진이 안 맞춰 주는 곳"뿐이다.
  // 좌표는 전부 **마진 박스** 기준이다 — 엔진이 정렬하는 단위가 마진 박스라서,
  // 보더 박스로 재면 저자가 준 마진(MUI 의 음수 거터, 체크박스 mt-1 등)이 전부 위반이 된다.

  const nodeOfN = new Map();
  byNode.forEach((rec, el) => nodeOfN.set(rec.n, el));

  const marginBox = (rec, el) => {
    const cs = csOf(el);
    return { top: rec.rect.top - px(cs.marginTop), bottom: rec.rect.bottom + px(cs.marginBottom),
             left: rec.rect.left - px(cs.marginLeft), right: rec.rect.right + px(cs.marginRight) };
  };

  // 중앙정렬은 의도다. auto 마진이 해결된 값이거나 좌우 여백이 대칭이면 제외한다.
  const isCentered = (rec, el, pRect) => {
    const cs = csOf(el);
    if (cs.marginLeft === cs.marginRight && parseFloat(cs.marginLeft) > 0) return true;
    const l = rec.rect.left - pRect.left, r = pRect.right - rec.rect.right;
    return Math.abs(l - r) <= 1 && rec.rect.width < pRect.width - 2;
  };

  parents.forEach((sibs, p) => {
    if (sibs.length < 2) return;
    const pcs = csOf(p);
    const disp = pcs.display;

    // 자식이 "행"인 컨테이너는 세로 스택이다. 가로인 것은 table-row(자식이 셀) 뿐이다.
    const childrenAreRows =
      ['table', 'table-header-group', 'table-row-group', 'table-footer-group'].includes(disp);
    const isRow = !childrenAreRows &&
      ((disp.includes('flex') && pcs.flexDirection.startsWith('row')) ||
       disp.includes('grid') || disp === 'table-row');

    const usable = sibs.filter((s) => !['absolute', 'fixed'].includes(s.style.position) &&
                                      s.style.display !== 'inline');
    if (usable.length < 2) return;

    if (!isRow) {
      // 세로 스택 — **시작 모서리**만 본다. 폭이 다른 건 흔한 의도라 끝 모서리는 보지 않는다.
      // ⚠️ 시작 모서리는 `left` 가 아니다. **쓰기 방향에 따라 달라진다** —
      //    RTL 에서는 오른쪽이 시작이다. `left` 로만 보면 RTL 화면의 미정렬을 통째로 놓친다
      //    (실측: `margin-inline-start:37px` 을 심은 RTL 카드가 **0건**으로 통과했다.
      //     전체폭 블록이라 왼쪽 모서리는 그대로였기 때문이다).
      // ⚠️ **부모가 `text-align` 으로 인라인 축을 정하면 그건 엔진이 보장하는 정렬이다.**
      //    center/right/end 인데 left 를 재면 정상 중앙정렬이 전부 어긋남이 된다
      //    (실측 p34: 컴포넌트 견본 격자에서 16건 — 버튼은 중앙, 라벨은 전폭이라 left 가 다르다).
      //    `isCentered` 는 마진 기반이라 `text-align` 경로를 못 잡는다.
      if (!/^(start|left)$/.test(pcs.textAlign)) return;
      const startEdge = pcs.direction === 'rtl' ? 'right' : 'left';
      const pRect = rectOf(p);
      const cand = usable.filter((s) => !isCentered(s, nodeOfN.get(s.n), pRect));
      if (cand.length < 2) return;
      const boxes = cand.filter((s) => !rotated(nodeOfN.get(s.n)))
                        .map((s) => ({ s, b: marginBox(s, nodeOfN.get(s.n)) }));
      if (boxes.length < 2) return;
      const base = boxes[0].b[startEdge];
      const off = boxes.filter((x) => Math.abs(x.b[startEdge] - base) > ALIGN_TOLERANCE);
      if (off.length) {
        add('alignment', off.map((x) => x.s.n),
          `${startEdge} 기준 ${off.length}개 형제가 ${Math.round(Math.abs(off[0].b[startEdge] - base))}px 어긋남`);
      }
      return;
    }

    // 가로 배치 — flex-wrap·grid 는 여러 줄일 수 있다. 줄로 나눈 뒤 줄 안에서만 비교한다.
    const boxes = usable.filter((s) => !rotated(nodeOfN.get(s.n)))
                        .map((s) => ({ s, b: marginBox(s, nodeOfN.get(s.n)) }))
                        .sort((a, b) => a.b.top - b.b.top);
    const lines = [];
    for (const x of boxes) {
      const line = lines[lines.length - 1];
      const lineBottom = line ? Math.max(...line.map((y) => y.b.bottom)) : 0;
      if (line && x.b.top < lineBottom - 1) line.push(x); else lines.push([x]);
    }

    for (const line of lines) {
      if (line.length < 2) continue;
      // 교차축 정렬값을 확인한다. center·baseline·end·stretch 는 높이가 다르면
      // top/bottom 이 달라야 맞다 — 재면 정상 디자인이 전부 위반이 된다.
      const resolved = [...new Set(line.map((x) => {
        const self = csOf(nodeOfN.get(x.s.n)).alignSelf;
        return self && self !== 'auto' ? self : pcs.alignItems;
      }))];
      if (resolved.length !== 1) continue;   // 자식마다 정렬을 달리 준 것은 의도로 본다
      if (!/^(start|flex-start|self-start)$/.test(resolved[0])) continue;
      const base = line[0].b.top;
      const off = line.filter((x) => Math.abs(x.b.top - base) > ALIGN_TOLERANCE);
      if (off.length) {
        add('alignment', off.map((x) => x.s.n),
          `top 기준 ${off.length}개 형제가 ${Math.round(Math.abs(off[0].b.top - base))}px 어긋남`);
      }
    }
  });

  // ---------- 죽은 세로 띠 (한쪽 쏠림) ----------
  // ★ 실사용에서 드러난 구멍. 정렬 판정은 **형제끼리만** 비교하므로
  //   「부모 안에서 콘텐츠가 한쪽으로 쏠려 반대쪽이 통째로 비는」 경우를 구조적으로 못 잡는다.
  //   실측(html-report 산출물): 컨테이너 1132px 안에 콘텐츠 702px 이 왼쪽에 붙어
  //   **오른쪽 584px 이 죽어 있었는데 정렬 지적은 0건**이었다. 화면을 열었을 때 가장 먼저
  //   눈에 띄는 결함인데 측정이 통째로 놓친 것이다. 원인은 대개 하나 —
  //   `max-width` 를 걸고 `margin-inline: auto` 를 빼먹은 것.
  //
  // 판정: 같은 부모 아래 **폭과 좌측이 일치하는 블록 자식이 2개 이상**이고, 그 폭이 부모
  //       콘텐츠 폭보다 좁아서 한쪽에만 큰 여백이 남을 때. 좌우가 대칭이면(중앙정렬) 제외한다.
  // ⚠️ 아래 두 상수는 실측으로 정한 값이 아니라 **판단선**이다(SKILL.md 에 명시).
  //    비대칭 레이아웃은 의도일 수 있으므로 이 판정은 자동수정이 아니라 중재자 경유로 간다.
  const DEAD_SHARE = 0.25;  // 죽은 띠가 부모 콘텐츠 폭에서 차지하는 비율 하한
  const DEAD_RATIO = 2;     // 반대쪽 여백 대비 배수 하한 (중앙정렬 배제)

  parents.forEach((sibs, p) => {
    const prec = byNode.get(p);
    if (!prec) return;
    const blocks = sibs.filter((s) =>
      /^(block|flex|grid|flow-root|list-item)$/.test(s.style.display) &&
      !['absolute', 'fixed'].includes(s.style.position));
    if (blocks.length < 2) return;

    const cLeft = prec.rect.left + prec.style.paddingLeft;
    const cRight = prec.rect.right - prec.style.paddingRight;
    const cw = cRight - cLeft;
    if (cw <= 0) return;

    const w0 = blocks[0].rect.w, l0 = blocks[0].rect.left;
    const uniform = blocks.every((b) => Math.abs(b.rect.w - w0) <= 1 && Math.abs(b.rect.left - l0) <= 1);
    if (!uniform) return;
    if (w0 >= cw - 1) return;                       // 부모 폭을 채우면 죽은 띠가 없다

    const gapL = l0 - cLeft;
    const gapR = cRight - (l0 + w0);
    const dead = Math.max(gapL, gapR), other = Math.min(gapL, gapR);
    if (dead < cw * DEAD_SHARE) return;
    if (dead < other * DEAD_RATIO) return;          // 좌우 대칭 = 중앙정렬 = 의도

    // ★ **띠가 실제로 비어 있는지 확인한다.** 이게 없으면 의도된 여백을 결함으로 신고한다 —
    //   실측: Tufte 식 사이드노트 레이아웃(본문 62% + 우측 38% 사이드노트 마진)에서
    //   제목 블록 옆에는 사이드노트가 없다는 이유로 지적이 나갔는데, 같은 띠를 문서
    //   아래쪽 사이드노트들이 쓰고 있었다(실측: 띠 856~1286 안에 사이드노트 898~1137).
    //   ⚠️ 뷰포트 밖 요소는 `elements` 에 없으므로 **문서 전체를 직접 훑는다.**
    //      사이드노트는 대개 첫 화면 아래에 있어서, 뷰포트 안만 보면 여전히 오탐이 난다.
    const bandL = gapR > gapL ? l0 + w0 : cLeft;
    const bandR = gapR > gapL ? cRight : l0;
    const occupied = deepAll().some((el) => {
      const r = rectOf(el);
      if (r.width < MIN_SIZE || r.height < MIN_SIZE) return false;
      // 띠 **안에** 들어 있는 요소만 — 띠를 통째로 감싸는 조상은 제외한다
      if (!(r.left >= bandL - 1 && r.right <= bandR + 1)) return false;
      const cs = csOf(el);
      return cs.display !== 'none' && cs.visibility !== 'hidden' && cs.opacity !== '0';
    });
    if (occupied) return;

    add('dead-column', blocks.map((b) => b.n).slice(0, 8),
      `${gapR > gapL ? '오른쪽' : '왼쪽'} ${Math.round(dead)}px 가 비어 있음 ` +
      `(콘텐츠 ${Math.round(w0)}px / 컨테이너 ${Math.round(cw)}px, 반대쪽 ${Math.round(other)}px)`);
  });

  // ---------- 위계 역전 ----------
  // 그룹 = 같은 부모 아래 연속 형제 중 간격이 같은 묶음. 간격이 바뀌는 지점이 경계다.
  // 상대 비교만 하므로 스케일 추출(0-2)에 의존하지 않는다 — 순환하지 않는다.

  parents.forEach((sibs) => {
    const col = sibs
      .filter((s) => s.style.position !== 'absolute')
      .sort((a, b) => a.rect.top - b.rect.top);
    if (col.length < 3) return;

    const gaps = [];
    for (let i = 0; i + 1 < col.length; i++) {
      const g = col[i + 1].rect.top - col[i].rect.bottom;
      // 구분선·배경 변화가 있으면 그룹 경계가 이미 성립하므로 제외한다
      const divided =
        col[i].style.borderBottomWidth > 0 ||
        col[i].style.backgroundColor !== col[i + 1].style.backgroundColor;
      gaps.push({ g: Math.round(g), from: col[i].n, to: col[i + 1].n, divided });
    }
    const clean = gaps.filter((x) => !x.divided && x.g >= 0);
    if (clean.length < 2) return;

    // ⚠️ 이전 판은 `정렬·중복제거 배열의 uniq[0] >= uniq[1]` 을 조건으로 썼는데,
    //    그건 구조적으로 항상 거짓이라 위계 역전이 한 번도 검출되지 않는 죽은 코드였다.
    //
    // 체크리스트 1-3 의 형태 그대로 판정한다:
    // 선두 요소(제목처럼 뒤 형제보다 크거나 굵은 것)와 자기 그룹 사이 간격이,
    // 그 그룹 내부 간격보다 크거나 같으면 제목이 자기 덩어리에서 떨어진 것이다.
    const rest = clean.slice(1).map((x) => x.g);
    if (!rest.length) return;
    const innerMin = Math.min(...rest);
    const lead = col[0], next = col[1];
    const isLeader =
      lead.style.fontSize > next.style.fontSize ||
      parseInt(lead.style.fontWeight, 10) > parseInt(next.style.fontWeight, 10);

    if (isLeader && clean[0].g >= innerMin && clean[0].g > 0) {
      addGrouped('hierarchy', [clean[0].from, clean[0].to],
        `선두↔그룹 ${clean[0].g}px ≥ 그룹 내 ${innerMin}px`);
    }

    // 그룹 내부에서도 유독 한 칸만 벌어지면 그 지점이 잘못된 경계다
    const uniform = rest.filter((g) => g === innerMin).length;
    if (uniform >= 2) {
      clean.slice(1).forEach((x) => {
        if (x.g > innerMin * 2) {
          addGrouped('hierarchy', [x.from, x.to], `그룹 내 ${x.g}px ≫ 나머지 ${innerMin}px`);
        }
      });
    }
  });

  // ---------- 스케일 이탈 ----------

  // ★ 규칙 단위로 묶는다. CSS 규칙 1개가 40개 셀에 적용되면 이전 판은 40건으로 셌고,
  //   그 한 규칙이 사전식 비교 전체를 지배해 다른 축이 의미를 잃었다.
  // spacingBase 는 「기준 단위 × 정수배」로 스케일을 정의하는 방식(Tailwind v4 등)이다.
  // 값 목록이 없으므로 정수배 여부로 판정한다 — 스케일 값을 지어내지 않는다.
  if (spacingScale.length || spacingBase > 0) {
    const scale = new Set(spacingScale);
    const onScale = (v) => scale.has(v) || (spacingBase > 0 && v % spacingBase === 0);
    const props = ['paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft',
                   'marginTop', 'marginBottom', 'gap', 'columnGap'];
    const rules = new Map();
    elements.forEach((rec) => {
      props.forEach((p) => {
        const v = rec.style[p];
        // 정수가 아닌 값은 em·rem 파생(브라우저 기본 스타일 등)이라 저자 의도가 아닐 가능성이
        // 높다. 19.92px 같은 UA 기본 마진이 스케일 위반으로 잡히는 노이즈를 막는다.
        if (v <= 0 || !Number.isInteger(v) || onScale(v)) return;
        // ⚠️ **값 단위로 묶는다.** 이전 판은 `prop=value` 로 묶어서, 하나의 디자인 결정(예: 6px)이
        //    paddingTop·paddingBottom·gap·columnGap 으로 쪼개져 4~6건으로 셌다(실측).
        //    고칠 곳은 한 군데인데 지적이 여러 건이면 사전식 비교에서 그 값이 과대대표된다.
        if (!rules.has(v)) rules.set(v, { targets: [], props: new Set(), n: 0 });
        const r = rules.get(v);
        r.props.add(p.replace(/^(padding|margin)/, (x) => x[0]).replace(/Top|Right|Bottom|Left/, ''));
        r.n++;
        if (r.targets.length < 8) r.targets.push(rec.n);
      });
    });
    rules.forEach((r, v) => {
      add('scale', r.targets, `${v}px — ${[...r.props].join('·')} (${r.n}곳)`);
    });
  }

  // ---------- 축 1 추가 판정 ----------

  // 1-1 같은 종류의 반복 요소인데 내부 패딩이 다르다
  // 선택·강조 상태가 다른 형제는 의도된 강조일 수 있으므로 class 가 완전히 같은 것끼리만 본다
  parents.forEach((sibs) => {
    const groups = new Map();
    sibs.forEach((s) => {
      const el = [...byNode.entries()].find(([, r]) => r === s)?.[0];
      if (!el) return;
      const key = `${s.tag}.${el.className || ''}`;
      if (!groups.has(key)) groups.set(key, []);
      groups.get(key).push(s);
    });
    groups.forEach((g) => {
      if (g.length < 3) return; // 2개는 우연히 다를 수 있다. 3개 이상에서 하나만 튀는 것을 본다
      const sig = (s) => `${s.style.paddingTop}/${s.style.paddingRight}/${s.style.paddingBottom}/${s.style.paddingLeft}`;
      const counts = new Map();
      g.forEach((s) => counts.set(sig(s), (counts.get(sig(s)) || 0) + 1));
      if (counts.size < 2) return;
      const major = [...counts.entries()].sort((a, b) => b[1] - a[1])[0][0];
      const odd = g.filter((s) => sig(s) !== major);
      add('repeat-padding', odd.map((s) => s.n),
        `반복 ${g.length}개 중 ${odd.length}개만 패딩이 다름 (${odd.map(sig).join(' vs ')} ≠ ${major})`);
    });
  });

  // 1-14 컨테이너 패딩 + 유일 자식 패딩 = 이중 들여쓰기
  // main·body 같은 페이지 컨테이너는 정상이므로 제외한다
  //
  // ⚠️ 재작성(다스택 실측 후). 이전 판은 두 가지로 오탐했다:
  //   1) 셀 안의 배지·버튼을 잡았다 — `td{padding:0 12px}` 안의 `span.tag{padding:4px 8px}` 는
  //      정상 패턴이다. 들여쓰기가 겹치려면 자식이 **부모 폭을 채우는 블록 상자**여야 한다.
  //      알약형 자식(inline-block/inline-flex)은 폭을 안 채우므로 겹칠 수가 없다.
  //   2) 규칙 단위 집계가 없었다 — 600행 표에서 CSS 규칙 1개가 36건으로 셌다.
  {
    const hits = new Map();
    byNode.forEach((rec, el) => {
      if (['MAIN', 'BODY', 'HTML', 'SECTION', 'TD', 'TH'].includes(el.tagName)) return;
      if (el.children.length !== 1) return;
      const childEl = el.children[0];
      const child = byNode.get(childEl);
      if (!child) return;
      if (!(rec.style.paddingLeft > 0 && child.style.paddingLeft > 0)) return;
      // 자식이 블록 상자로 부모 콘텐츠 폭을 실제로 채울 때만 들여쓰기가 겹친다
      if (!/^(block|flex|grid|flow-root|list-item)$/.test(child.style.display)) return;
      const contentW = rec.rect.w - rec.style.paddingLeft - rec.style.paddingRight;
      if (child.rect.w < contentW - 1) return;

      const key = `${el.tagName}>${childEl.tagName}|${rec.style.paddingLeft}+${child.style.paddingLeft}`;
      if (!hits.has(key)) hits.set(key, { targets: [], n: 0, a: rec.style.paddingLeft, b: child.style.paddingLeft });
      const h = hits.get(key);
      h.n++;
      if (h.targets.length < 8) h.targets.push(rec.n, child.n);
    });
    hits.forEach((h) => {
      add('double-indent', h.targets,
        `${h.a}px + ${h.b}px 이중 들여쓰기` + (h.n > 1 ? ` (같은 규칙 ${h.n}곳)` : ''));
    });
  }

  // 1-12 행 간격과 열 간격이 다르다
  elements.forEach((rec) => {
    const { gap, columnGap } = rec.style;
    if (gap > 0 && columnGap > 0 && gap !== columnGap) {
      add('gap-asym', [rec.n], `row-gap ${gap}px ≠ column-gap ${columnGap}px`);
    }
  });

  // 1-6 컨테이너 상하 패딩 비대칭
  byNode.forEach((rec, el) => {
    if (!rec.visible || el.children.length < 2) return;
    const { paddingTop: t, paddingBottom: b } = rec.style;
    if (t > 0 && b > 0 && t !== b) add('pad-asym', [rec.n], `상 ${t}px ≠ 하 ${b}px`);
  });

  // 1-4 버튼·입력의 상하:좌우 패딩 비율 불일치
  // ⚠️ 컨트롤 **종류를 섞어서** 비교하면 안 된다. 버튼과 입력의 패딩 비율이 다른 것은
  //    정상이다(버튼은 좌우가 넓고, 입력은 상하가 상대적으로 크다). 실측에서 스택 6종이
  //    전부 "비율 2종"으로 발화했는데 전부 button vs input 이었다.
  //    → **같은 태그끼리만** 비교한다. 그래야 "버튼끼리 들쭉날쭉"이라는 원래 취지가 살아난다.
  const ratio = (r) => {
    const v = r.style.paddingTop + r.style.paddingBottom;
    const h = r.style.paddingLeft + r.style.paddingRight;
    return h > 0 ? Math.round((v / h) * 100) / 100 : null;
  };
  for (const tag of ['button', 'input', 'select', 'textarea']) {
    const controls = elements.filter((r) => r.tag === tag);
    if (controls.length < 2) continue;
    const rs = new Map();
    controls.forEach((r) => { const x = ratio(r); if (x != null) rs.set(x, [...(rs.get(x) || []), r.n]); });
    if (rs.size > 1) {
      add('control-ratio', [...rs.values()].flat().slice(0, 8),
        `상하:좌우 패딩 비율이 ${rs.size}종 (${[...rs.keys()].join(', ')})`);
    }
  }

  // ---------- 축 2 추가 판정 ----------

  // 2-4 폰트 굵기 종류 과다. 표 내부는 라벨/값/등락 3종이 금융에서 정상이라 제외한다
  const weights = new Set();
  byNode.forEach((rec, el) => {
    if (!rec.visible || el.closest('table')) return;
    if (rec.text) weights.add(parseInt(rec.style.fontWeight, 10));
  });
  // ⚠️ 종 수만 세면 안 된다. 400/500/600/700 은 **연속된 100 단위 램프**로, 정상적인
  //    타이포 스케일이지 "굵기가 제각각"이 아니다. 실측에서 스택 5종이 전부 이걸로 발화했다.
  //    문제는 종 수가 아니라 **체계 없이 튀는 것**이므로, 연속 램프면 몇 종이든 제외한다.
  const sortedW = [...weights].sort((a, b) => a - b);
  const isRamp = sortedW.length > 1 &&
    sortedW.every((w, i) => i === 0 || w - sortedW[i - 1] === 100);
  if (weights.size >= 4 && !isRamp) {
    add('weight-variety', [], `폰트 굵기 ${weights.size}종 (${sortedW.join(', ')})`);
  }

  // 2-10 클릭 가능 요소가 일반 텍스트와 구분되지 않는다
  byNode.forEach((rec, el) => {
    if (el.tagName !== 'A' || !rec.text) return;
    const cs = csOf(el);
    const sib = el.parentElement && byNode.get(el.parentElement);
    if (!sib) return;
    const sameColor = cs.color === sib.style.color;
    const noDeco = cs.textDecorationLine === 'none';
    const sameWeight = cs.fontWeight === sib.style.fontWeight;
    // ⚠️ **구분 수단이 색·밑줄·굵기만 있는 게 아니다.** 색은 상속되므로 링크에 별도 색을 안 주면
    //    부모와 같을 수밖에 없고, 그러면 **내비게이션 링크가 통째로 오탐**이 된다
    //    (실측 p27: nav 링크 5개 전부 발화 → 샷 합산 20건).
    //    화면에서 실제로 "누를 수 있어 보이게" 만드는 것은 자체 표면(배경·테두리)과
    //    버튼처럼 잡힌 여백이다. 그 둘이 있으면 이 항목의 취지에 해당하지 않는다.
    const hasSurface = cs.backgroundColor !== 'rgba(0, 0, 0, 0)' ||
                       cs.backgroundImage !== 'none' ||
                       parseFloat(cs.borderTopWidth) > 0 || parseFloat(cs.borderBottomWidth) > 0;
    const buttonLike = (px(cs.paddingLeft) >= 4 && px(cs.paddingTop) >= 4) ||
                       cs.display === 'block' || cs.display === 'inline-block' ||
                       cs.display === 'flex' || cs.display === 'inline-flex';
    if (hasSurface || buttonLike) return;
    if (sameColor && noDeco && sameWeight) {
      add('affordance', [rec.n], '링크가 색·밑줄·굵기 어느 것으로도 구분되지 않음');
    }
  });

  // 2-12 hover 만 있고 focus 스타일이 없다
  //
  // ⚠️ 재작성(다스택 실측 후). 이전 판은 **모든 스타일시트를 훑어 셀렉터 문자열만 비교**했다.
  //    Bootstrap 에서 37종을 지적했는데 거기엔 `.table-hover > tbody > tr` 처럼
  //    **애초에 포커스를 받을 수 없는 요소**가 섞여 있었다. 라이브러리가 자기 리셋 CSS 에
  //    쓴 규칙이 프로젝트 결함으로 둔갑한 것이라, CSS 라이브러리를 쓰면 반드시 터진다.
  //    → 화면에 **실제로 매칭되는 요소가 있고, 그 요소가 포커스 가능할 때만** 센다.
  {
    const FOCUSABLE = 'a[href],button,input,select,textarea,summary,[contenteditable],' +
                      '[tabindex]:not([tabindex="-1"])';
    const hovers = new Map(), focuses = new Set();
    // ⚠️ 셀렉터 **목록**을 쉼표로 쪼갠 뒤 각각 정규화한다. 통째로 자르면
    //    `.nav-link:hover, .nav-link:focus` 가 hover 쪽은 `.nav-link`,
    //    focus 쪽은 `.nav-link:hover, .nav-link` 로 달라져 매칭에 실패한다
    //    (실측: Bootstrap 이 focus 스타일을 갖고 있는데 없다고 지적됐다).
    eachStyleRule((r) => {
      if (!r.selectorText) return;
      for (const part of r.selectorText.split(',')) {
        const sel = part.trim();
        if (!sel) continue;
        // `:focus-visible` 도 `:focus` 로 시작하므로 같은 절단으로 정규화된다
        if (/:focus/.test(sel)) focuses.add(sel.replace(/:focus.*/, '').trim());
        else if (/:hover/.test(sel)) {
          const base = sel.replace(/:hover.*/, '').trim();
          if (base && !hovers.has(base)) hovers.set(base, null);
        }
      }
    });
    // ⚠️ 셀렉터 문자열끼리 비교하면 안 된다. **같은 요소가 다른 셀렉터로 focus 스타일을
    //    이미 받고 있는 경우**를 놓친다 — 실측: `.mantine-Button-filled:hover` 만 있고
    //    focus 는 `.mantine-Button-root:focus-visible` 에 있는데, 그 버튼은 두 클래스를
    //    함께 갖고 있어 실제로는 포커스 스타일이 있다. **요소 단위로 판정한다.**
    const focusSels = [...focuses];
    const covered = (el) => focusSels.some((s) => {
      try { return el.matches(s); } catch { return false; }
    });
    const missing = [];
    for (const [sel] of hovers) {
      let hit = null;
      // 셀렉터가 깨졌거나(벤더 문법) 매칭이 없으면 이 화면의 문제가 아니다
      // 문서마다 따로 찾는다 — 임베드 위젯의 hover 규칙은 그 문서 안에서만 매칭된다.
      try { hit = queryAll(sel)[0] || null; } catch { continue; }
      if (!hit || !hit.matches(FOCUSABLE)) continue;
      if (covered(hit)) continue;
      const rec = byNode.get(hit);
      missing.push({ sel, n: rec ? rec.n : null });
    }
    if (missing.length && cssReadable) {
      add('focus-missing', missing.map((m) => m.n).filter(Boolean).slice(0, 8),
        `hover 만 있고 focus 가 없는 셀렉터 ${missing.length}종: ${missing.slice(0, 3).map((m) => m.sel).join(', ')}`);
    }
  }

  // ---------- 축 3·6 표·폼 판정 ----------

  /**
   * ★ **표는 `<table>` 만이 아니다.** react-table·ag-grid·TanStack·CSS grid 로 그린 데이터
   *    그리드는 `div` 에 `role="table"` 을 붙인다. 이전 판은 진입점이 `queryAll('table')` 뿐이라
   *    **표 판정 8종(cell-padding·row-height·table-header·decimals·num-align·tabular-nums·
   *    empty-cell·표 가로넘침)이 통째로 침묵**했다 — 실측 p28: 소수 자릿수를 일부러 섞은
   *    div 그리드에서 `decimals` 0건. 대형 그리드일수록 이 스킬이 필요한데 거기서 눈이 멀었다.
   *
   * ⚠️ ARIA 표를 태그 표로 **변환하지 않는다.** 행·셀을 role 로 찾고, `<th>`/`cells` 같은
   *    HTML 전용 API 대신 공통 접근자를 쓴다. 헤더는 `role="columnheader"` 로 본다.
   */
  const ariaTables = queryAll('[role="table"], [role="grid"], [role="treegrid"]')
    .filter((el) => !/^(table)$/i.test(el.tagName));   // 태그 표에 role 을 붙인 것은 중복 제외

  /**
   * ⚠️ **`role="presentation"` 은 "이건 데이터 표가 아니다"라는 저자의 명시적 선언이다.**
   *    이메일 HTML 은 레이아웃을 전부 중첩 테이블로 짜고 거기에 이 role 을 붙인다.
   *    그걸 데이터 표로 재면 스페이서 셀·속성 패딩·레이아웃 행이 전부 위반이 된다
   *    (실측 p32: `cell-padding` 32 · `row-height` 38 · `tabular-nums` 24 — 한 화면 94건 오탐).
   *    선언을 읽으면 끝나는 문제라 배제 규칙이 아니다.
   */
  const isLayoutTable = (el) => /^(presentation|none)$/i.test(el.getAttribute('role') || '');

  [...queryAll('table'), ...ariaTables].filter((t) => !isLayoutTable(t)).forEach((table) => {
    const isAria = !/^table$/i.test(table.tagName);
    const rec = byNode.get(table);
    const nOf = (el) => byNode.get(el)?.n;
    // 행 = tbody tr (태그) 또는 role="row" 중 헤더 행이 아닌 것(ARIA)
    const cellsOf = (row) => (isAria
      ? Array.from(row.querySelectorAll('[role="cell"], [role="gridcell"]'))
      : Array.from(row.cells));
    const rows = isAria
      ? queryIn(table, '[role="row"]').filter((r) => cellsOf(r).length > 0)
      : Array.from(table.querySelectorAll('tbody tr'));
    if (!rows.length) return;

    // 6-7 셀 좌우 패딩이 사실상 없다
    const tight = rows.flatMap((tr) => cellsOf(tr))
      .filter((td) => { const c = csOf(td); return px(c.paddingLeft) < 4 || px(c.paddingRight) < 4; });
    if (tight.length) {
      add('cell-padding', tight.map(nOf).filter(Boolean).slice(0, 8),
        `셀 좌우 패딩 4px 미만 ${tight.length}개`);
    }

    // 6-10 행 높이가 행마다 다르다
    // ⚠️ 1px 차이는 서브픽셀 레이아웃에서 상시 발생한다(실측: 51 vs 52px 로 발화).
    //    정렬 판정과 같은 허용치를 쓴다 — 판정마다 허용치가 다르면 결과가 안 맞는다.
    //
    // ⚠️ **행 높이 차이의 대부분은 내용 차이다.** 한글 표에서 셀 텍스트가 행마다 다른 줄 수로
    //    접히면 높이는 당연히 달라진다 — 특히 좁은 뷰포트에서 전부 터진다
    //    (실측: 360 에서 (325,218,175px) 처럼 줄 수가 다른 행들이 무더기로 지적됐다).
    //    이 항목의 취지는 「같은 모양인데 높이가 들쭉날쭉하다 = 패딩 불일치」이므로,
    //    **줄 수가 같은 행끼리만** 비교한다. 줄 수가 다르면 높이가 다른 게 정상이다.
    const linesOf = (tr) => {
      let n = 1;
      for (const td of cellsOf(tr)) {
        const cs = csOf(td);
        const lh = parseFloat(cs.lineHeight) || (parseFloat(cs.fontSize) || 16) * 1.5;
        const inner = rectOf(td).height - px(cs.paddingTop) - px(cs.paddingBottom);
        if (lh > 0) n = Math.max(n, Math.max(1, Math.round(inner / lh)));
      }
      return n;
    };
    const byLines = new Map();
    rows.forEach((tr) => {
      const k = linesOf(tr);
      if (!byLines.has(k)) byLines.set(k, []);
      byLines.get(k).push(tr);
    });
    byLines.forEach((group, lines) => {
      if (group.length < 2) return;
      const gh = group.map((tr) => Math.round(rectOf(tr).height));
      if (Math.max(...gh) - Math.min(...gh) <= ALIGN_TOLERANCE) return;
      add('row-height', group.map(nOf).filter(Boolean).slice(0, 8),
        `${lines}줄짜리 행끼리 높이가 다름 (${[...new Set(gh)].join(', ')}px) — 셀 패딩 불일치`);
    });


    // 6-6 세로 스크롤 시 표 헤더가 사라진다
    // ⚠️ 행 수가 아니라 **표가 뷰포트보다 긴가**로 판정한다. sticky 헤더는 스크롤하는 동안
    //    헤더를 붙잡아 두는 장치이므로, 한 화면에 다 들어오는 표에는 이득이 없다.
    //    행 수 하한(5)만 보던 이전 판은 5행짜리 표에도 sticky 를 요구했다.
    const th = isAria
      ? table.querySelector('[role="columnheader"]')
      : table.querySelector('thead th');
    const tableH = rectOf(table).height;
    const tableVh = vhOf(table);   // 임베드 문서는 부모와 뷰포트 높이가 다르다
    if (th && tableH > tableVh && csOf(th).position !== 'sticky') {
      add('table-header', [nOf(th)].filter(Boolean),
        `표 높이 ${Math.round(tableH)}px 가 뷰포트 ${tableVh}px 보다 긴데 헤더가 sticky 가 아님`);
    }

    // 열 단위 판정 — 3-12 소수 자릿수 · 3-5 정렬 방향 · 6-9 결측 표시
    const colCount = Math.max(...rows.map((r) => cellsOf(r).length));
    for (let c = 0; c < colCount; c++) {
      const cells = rows.map((r) => cellsOf(r)[c]).filter(Boolean);
      const texts = cells.map((td) => td.textContent.trim());
      const nums = texts.filter((t) => /^-?[\d,]+(\.\d+)?%?$/.test(t) && t !== '');
      if (nums.length >= 2) {
        const decimals = new Set(nums.map((t) => (t.split('.')[1] || '').replace('%', '').length));
        if (decimals.size > 1) {
          add('decimals', cells.map(nOf).filter(Boolean).slice(0, 8),
            `${c + 1}열 소수 자릿수 ${[...decimals].sort().join('/')} 혼재`);
        }
        const aligns = new Set(cells.map((td) => csOf(td).textAlign));
        if (aligns.size > 1) {
          add('num-align', cells.map(nOf).filter(Boolean).slice(0, 8),
            `${c + 1}열 정렬 방향 혼재 (${[...aligns].join(', ')})`);
        }
        // 3-13 숫자 열에 등폭 숫자가 없다
        const tab = cells.every((td) => /tabular-nums|lining-nums/.test(csOf(td).fontVariantNumeric));
        if (!tab) {
          add('tabular-nums', cells.map(nOf).filter(Boolean).slice(0, 4), `${c + 1}열 숫자에 등폭 숫자 미적용`);
        }
      }
      const blanks = cells.filter((td, i) => texts[i] === '');
      if (blanks.length && nums.length) {
        add('empty-cell', blanks.map(nOf).filter(Boolean),
          `${c + 1}열에 빈 셀 ${blanks.length}개 — 결측인지 0 인지 구분 불가`);
      }
    }
    if (rec && rec.scroll.sw > rec.scroll.cw + 1) {
      add('overflow', [rec.n], `표 가로 넘침 ${rec.scroll.sw} > ${rec.scroll.cw}`);
    }
  });

  // 폼 판정
  {
    const inputs = queryAll('input, select, textarea')
      .filter((el) => byNode.has(el));
    const nOf = (el) => byNode.get(el)?.n;

    // 6-1 입력 폭이 예상 입력값과 무관하게 전부 같다
    //
    // ⚠️ 재작성(다스택 실측 후). 이전 판은 `input, select, textarea` 를 통째로 세서
    //    **체크박스 3개(16×16px)가 "폭이 전부 같다"로 발화**했다. 균일 자체는 결함이 아니다.
    //    이 항목의 취지는 "CVC 3자리 칸이 주소 칸과 같은 폭이면 어색하다" 이므로,
    //    **짧은 입력과 긴 입력이 함께 있는데 폭이 같을 때**만 성립한다.
    const textEntry = inputs.filter((el) => {
      if (el.tagName !== 'INPUT') return el.tagName === 'TEXTAREA' || el.tagName === 'SELECT';
      return !['checkbox', 'radio', 'range', 'color', 'file', 'hidden',
               'submit', 'button', 'image', 'reset'].includes(el.type);
    });
    const isShort = (el) => {
      const ml = Number(el.getAttribute('maxlength') || 0);
      return (ml > 0 && ml <= 8) || ['number', 'tel'].includes(el.type) ||
             /numeric|tel/.test(el.getAttribute('inputmode') || '');
    };
    if (textEntry.length >= 3 && textEntry.some(isShort) && textEntry.some((el) => !isShort(el))) {
      const ws = new Set(textEntry.map((el) => Math.round(rectOf(el).width)));
      // ⚠️ **전폭 폼은 폭이 같은 게 의도다.** 입력이 부모 콘텐츠 폭을 꽉 채우면 그건
      //    "값 길이와 무관하게 같다"가 아니라 반응형 레이아웃이다. 좁은 폭에서는 오히려
      //    폭을 다르게 두는 쪽이 잘못이다(실측 p27: 1440·360 양쪽에서 전폭 폼이 발화).
      const fullWidth = textEntry.every((el) => {
        const p = el.parentElement;
        if (!p) return false;
        const pcs2 = csOf(p);
        const inner = rectOf(p).width - px(pcs2.paddingLeft) - px(pcs2.paddingRight);
        return Math.abs(rectOf(el).width - inner) <= 2;
      });
      if (ws.size === 1 && !fullWidth) {
        add('input-width', textEntry.map(nOf).filter(Boolean).slice(0, 8),
          `짧은 입력과 긴 입력이 섞여 있는데 ${textEntry.length}개가 전부 같은 폭 ${[...ws][0]}px`);
      }
    }

    // 6-5 placeholder 가 라벨을 대신한다
    inputs.forEach((el) => {
      if (!el.placeholder) return;
      const labelled = el.labels?.length || hasLabelledby(el) || el.getAttribute('aria-label') ||
        el.closest('label') || el.previousElementSibling?.tagName === 'LABEL';
      if (!labelled) add('placeholder-label', [nOf(el)].filter(Boolean), `placeholder 만 있고 라벨이 없음`);
    });

    // 6-2 필수 표시 규칙이 섞인다
    const labels = queryAll('label').map((l) => l.textContent.trim());
    if (labels.length >= 2) {
      const marks = new Set();
      labels.forEach((t) => {
        if (/\*/.test(t)) marks.add('*');
        else if (/필수|required/i.test(t)) marks.add('필수');
        else if (/선택|optional/i.test(t)) marks.add('선택');
        else marks.add('없음');
      });
      if (marks.size >= 3) {
        add('required-mark', [], `필수 표시 규칙 ${marks.size}종 혼재 (${[...marks].join(', ')})`);
      }
    }
  }

  return {
    viewport: { w: vw, h: vh },
    elements,
    findings,
    counts: findings.reduce((acc, f) => ({ ...acc, [f.kind]: (acc[f.kind] || 0) + 1 }), {}),
    domNodeCount: ALL.length,
    // ⚠️ **교차 출처 iframe 은 원리적으로 못 읽는다.** 조용히 빠지면 그 화면이 "깨끗함"으로
    //    보고되므로 사각지대로 남긴다 — 판정이 아니라 경고다(점수에 넣지 않는다).
    blindSpots: (blockedFrames.length || blockedCss.length) ? {
      ...(blockedFrames.length
        ? { crossOriginFrames: blockedFrames.slice(0, 8), count: blockedFrames.length } : {}),
      ...(blockedCss.length ? {
        crossOriginStyleSheets: blockedCss.slice(0, 8),
        cssCount: blockedCss.length,
        suppressed: ['undefined-var', 'focus-missing'],   // 근거를 못 읽어 보류한 판정
      } : {}),
    } : null,
    frames: DOCS.length - 1,
    // ⚠️ iframe 문서의 텍스트도 넣는다 — 빼면 임베드 콘텐츠를 지워도 불변식이 통과한다.
    textHash: hashText(DOCS.map((d) => (d.doc.body ? d.doc.body.innerText : '')).join('\u0000')),
  };

  function hashText(s) {
    let h = 0;
    for (let i = 0; i < s.length; i++) { h = (h * 31 + s.charCodeAt(i)) | 0; }
    return String(h);
  }
}

/**
 * 배지 오버레이 — 비평가용 이미지에만 적용한다. 원본에 섞이면 픽셀 diff 가 오염된다.
 *
 * ⚠️ 이전 판은 요소 좌상단 안쪽에 배지를 찍어 **텍스트를 가렸다.** 비평가가 판단해야 할
 * 대상을 배지가 덮으면 이 오버레이는 목적을 배반한다. 실제로 제목 첫 글자와 금액 앞자리가
 * 잘려 보였다. 그래서 두 가지를 고친다:
 *   1) 배지를 요소 박스 **바깥 좌상단**으로 밀어낸다
 *   2) 잎 요소(자체 텍스트를 가진 말단)와 카드형 컨테이너에만 찍는다 —
 *      전부 찍으면 화면이 배지로 덮이고 번호가 너무 많아 지목이 오히려 어려워진다
 */
export function paintBadges() {
  const style = document.createElement('style');
  style.id = 'uir-badge-style';
  style.textContent = `
    .uir-badge{position:absolute;z-index:2147483647;font:9px/1.2 monospace;
      background:#ff00ff;color:#fff;padding:0 2px;border-radius:2px;
      pointer-events:none;opacity:.9}`;
  document.head.appendChild(style);

  const layer = document.createElement('div');
  layer.id = 'uir-badge-layer';
  layer.style.cssText = 'position:absolute;inset:0;pointer-events:none;z-index:2147483647';
  document.body.appendChild(layer);

  // ⚠️ 배지는 **부모 문서 한 곳**에 그린다. iframe 안 요소도 번호를 받았으므로
  //    (측정이 임베드 문서까지 들어간다) 그 좌표를 부모 좌표계로 밀어서 찍는다.
  //    임베드 문서 안에 레이어를 따로 만들면 스크린샷 합성 위치가 어긋난다.
  const { docs } = frameDocs();
  const all = docs.flatMap((d) =>
    Array.from(d.doc.querySelectorAll('[data-uir]')).map((el) => ({ el, off: d })));
  const worth = all.filter(({ el }) => {
    const hasBadgedDescendant = el.querySelector('[data-uir]') !== null;
    if (!hasBadgedDescendant) return true;                   // 말단 = 지목 대상
    const cs = (el.ownerDocument.defaultView || window).getComputedStyle(el);
    return parseFloat(cs.borderTopWidth) > 0 ||               // 카드·패널 같은 면 단위
           (cs.backgroundColor !== 'rgba(0, 0, 0, 0)' && el.children.length > 1);
  });

  worth.forEach(({ el, off }) => {
    const r = el.getBoundingClientRect();
    const b = document.createElement('span');
    b.className = 'uir-badge';
    b.textContent = el.getAttribute('data-uir');
    // 박스 바깥 좌상단. 화면 위쪽에서 잘리지 않게 클램프한다.
    const top = r.top + off.dy + window.scrollY - 11;
    b.style.left = `${Math.max(0, r.left + off.dx + window.scrollX - 2)}px`;
    b.style.top = `${Math.max(0, top)}px`;
    layer.appendChild(b);
  });
}

/** 스페이싱 스케일 추출 — CSS 변수 우선, 없으면 빈도 군집화. */
export function extractScale() {
  // 이름으로 스페이싱 변수를 가린다 (상세 근거는 아래 주석).
  const nameOk = (p) =>
    /^--(?:[a-z0-9]+-)*(space|spacing|spacer|gap|gutter|inset|pad|padding|margin)([-_\d]|$)/i.test(p) &&
    !/(font|radius|border|width|height|line|z-|opacity|duration)/i.test(p);

  const excluded = (p) =>
    /(font|radius|border|width|height|line|z-|opacity|duration|shadow|blur|ease|dur-)/i.test(p);

  // ⚠️ 임베드(iframe) 문서도 함께 읽는다. 안 읽으면 위젯이 선언한 토큰이 안 보여
  //    그 토큰으로 그린 정상 여백이 전부 「스케일 이탈」로 지적된다 — Shadow DOM 때와 같은 실패다.
  //    **문서마다 루트 폰트 크기(rem 기준)와 미디어 조건이 다르므로 문서별로 해석한다.**
  const DOCS = frameDocs().docs;
  const fromVars = [];
  const varNames = new Set();
  const allNames = new Set();
  const lengthVars = new Map();   // 이름 무관 · 길이 값을 가진 변수 전부
  const multipliers = new Set();
  for (const ctx of DOCS) {
    const remPx = parseFloat(ctx.view.getComputedStyle(ctx.doc.documentElement).fontSize) || 16;
    eachStyleRuleIn(ctx, (rule) => {
      // 기준 단위 방식(Tailwind v4)의 유틸리티는 `calc(var(--spacing) * N)` 으로 쓴다.
      // **선언된 배수를 그대로 모으면** 스케일 값을 지어내지 않고 읽어낼 수 있다.
      // (이게 없으면 `py-1.5`=6px 처럼 프레임워크가 정식으로 제공하는 반단계가 이탈로 잡힌다)
      // ⚠️ 배수는 토큰 정의가 아니라 **사용처**에 있는 경우가 더 흔하다.
      //    Pico 는 `padding: calc(var(--pico-block-spacing-vertical) * 1.25)` 처럼 쓴다 —
      //    16px 토큰으로 20px 을 그리는 것이라, 토큰 값만 모으면 20 이 이탈로 잡힌다(실측 22건).
      //    변수와 배수를 **쌍으로** 모아 그 변수만 그 배수로 확장한다(스케일을 지어내지 않는다).
      const t = rule.cssText || '';
      if (t.includes('calc(')) {
        const re = /calc\(\s*var\(\s*(--[a-z0-9-]+)\s*\)\s*\*\s*(\d+(?:\.\d+)?)\s*\)/gi;
        let mm;
        while ((mm = re.exec(t))) {
          multipliers.add(`${mm[1]}|${parseFloat(mm[2])}`);
        }
      }
      for (const prop of Array.from(rule.style)) {
        if (!prop.startsWith('--')) continue;
        if (nameOk(prop)) varNames.add(prop);
        allNames.add(prop);
        const raw = rule.style.getPropertyValue(prop).trim();
        // 선행 0 이 없는 형태(`.25rem`)도 받는다 — minified CSS 가 그렇게 쓴다.
        // 이걸 놓쳐서 Tailwind v4 의 `--spacing:.25rem` 이 통째로 무시됐다.
        const m = /^(-?(?:\d+(?:\.\d+)?|\.\d+))(px|rem)$/.exec(raw);
        if (!m) continue;
        // 이름으로 스페이싱 변수를 가린다. computed style 만으로는 radius·font-size 와 안 갈린다.
        // ⚠️ 이전 판은 부분일치 `size-` 를 넣어 `--font-size-sm: 13px` 을 스페이싱으로 잡았고,
        //    그 13 이 스케일에 들어가는 바람에 13px 패딩 결함이 정상으로 판정됐다.
        //    → 그래서 `^--` 앵커를 걸었는데, 이번엔 반대 방향으로 부러졌다:
        //    실무 라이브러리는 변수를 전부 네임스페이스로 접두한다(`--bs-card-spacer-x`,
        //    `--tw-*`, `--mui-*`). 다스택 실측에서 Tailwind v3/v4·Bootstrap·CSS-in-JS·MUI
        //    **5종 전부 `vars:[]` 로 폴백**했다 — 즉 이 경로는 손으로 쓴 CSS 전용이었다.
        //    → 접두 구간을 허용하되 **키워드 자체는 여전히 완전 일치**로 둔다.
        //      (`--font-size-sm` 은 `size` 가 키워드에 없어 계속 걸러진다)
        const vAll = parseFloat(m[1]) * (m[2] === 'rem' ? remPx : 1);
        // 이름과 무관하게 「길이 값을 가진 변수」를 전부 모아 둔다.
        // 약어로 된 스페이싱 토큰(`--s-1..--s-9`)은 키워드 매칭으로는 절대 안 잡히는데,
        // 실무 수제 디자인시스템에서 아주 흔하다(실측: html-report 산출물).
        if (vAll > 0 && !excluded(prop)) lengthVars.set(prop, Math.round(vAll));
        if (!nameOk(prop)) continue;
        // ⚠️ rem 은 **루트 폰트 크기** 기준이다. 16 으로 하드코딩하면 안 된다 —
        //    Pico 는 뷰포트에 따라 루트를 100%→125% 로 키우므로 1440 에서 `1rem` 은 20px 이다.
        //    16 으로 환산하면 스케일이 통째로 어긋나 정상 여백이 전부 이탈로 잡힌다(실측 22건).
        const v = parseFloat(m[1]) * (m[2] === 'rem' ? remPx : 1);
        if (v > 0) fromVars.push({ name: prop, px: Math.round(v) });
      }
    });

    // ★ 규칙 텍스트를 그대로 읽는 위 경로만으로는 부족하다 —
    //   라이브러리는 토큰을 **calc 로 파생**시킨다(`--pico-block-spacing-vertical:
    //   calc(var(--pico-spacing) * 1.25)`). 그런 토큰은 값 정규식에 안 걸려 통째로 누락되고,
    //   그러면 그 토큰으로 그려진 정상 여백이 전부 「스케일 이탈」로 지적된다(실측 Pico 22건).
    //   → 프로브 요소에 `width: var(--x)` 를 넣어 **현재 뷰포트에서 실제로 해석되는 px** 을 잰다.
    //     calc·중첩 var 이 전부 풀리고, 지금 적용되는 브레이크포인트 값만 나온다.
    //   ⚠️ 프로브는 :root 상속만 받으므로 컴포넌트 스코프 변수(Bootstrap 의 `.card{--bs-…}`)는
    //     못 읽는다. 그래서 위의 직접 파싱 경로를 **대체하지 않고 합집합**으로 쓴다.
    //   ⚠️ 프로브는 **그 문서 안에** 만든다. 다른 문서의 :root 변수는 해석되지 않는다.
    const probe = ctx.doc.createElement('div');
    probe.style.cssText = 'position:absolute;left:-9999px;top:0;visibility:hidden;pointer-events:none';
    ctx.doc.documentElement.appendChild(probe);
    const seen = new Set(fromVars.map((v) => v.name));
    for (const name of varNames) {
      if (seen.has(name)) continue;
      probe.style.width = '0px';
      probe.style.width = `var(${name})`;
      const w = parseFloat(ctx.view.getComputedStyle(probe).width);
      if (Number.isFinite(w) && w > 0 && w <= 256) fromVars.push({ name, px: Math.round(w) });
    }
    probe.remove();
  }
  // 선언된 (변수 × 배수) 쌍으로 스케일을 확장한다.
  const byName = new Map(fromVars.map((v) => [v.name, v.px]));
  const derived = [];
  for (const pair of multipliers) {
    const [name, m] = pair.split('|');
    const basePx = byName.get(name);
    if (basePx > 0) derived.push(Math.round(basePx * parseFloat(m)));
  }

  // ---------- 실제 사용 히스토그램 ----------
  // 후보 스케일을 **이름이 아니라 「이 화면의 여백을 얼마나 설명하는가」로 고른다.**
  // ⚠️ 표본과 판정의 속성 목록이 같아야 한다. 이전 판은 표본에 marginTop 만 담고
  //    판정은 marginBottom 도 봐서, marginBottom 으로만 쓰인 정품 토큰(실측 4px)이
  //    히스토그램에 아예 안 들어가 「스케일 이탈」로 지적됐다.
  const freq = new Map();
  DOCS.flatMap((d) => Array.from(d.doc.querySelectorAll('*'))).forEach((el) => {
    const cs = (el.ownerDocument.defaultView || window).getComputedStyle(el);
    ['paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft',
     'marginTop', 'marginBottom', 'rowGap', 'columnGap'].forEach((pr) => {
      const v = Math.round(parseFloat(cs[pr]));
      if (v > 0 && v <= 128) freq.set(v, (freq.get(v) || 0) + 1);
    });
  });
  const total = [...freq.values()].reduce((a, b) => a + b, 0) || 1;
  const coverage = (vals) => {
    const set = new Set(vals);
    let hit = 0;
    for (const [v, c] of freq) if (set.has(v)) hit += c;
    return hit / total;
  };
  const expand = (names, base) => {
    const out = [...base];
    for (const pair of multipliers) {
      const [nm, mul] = pair.split('|');
      if (!names.has(nm)) continue;
      const px = lengthVars.get(nm) ?? byName.get(nm);
      if (px > 0) out.push(Math.round(px * parseFloat(mul)));
    }
    return [...new Set(out)].sort((a, b) => a - b);
  };

  const candidates = [];

  if (fromVars.length >= 3) {
    const names = new Set(fromVars.map((v) => v.name));
    candidates.push({ source: 'css-vars', names, vars: fromVars,
                      scale: expand(names, [...fromVars.map((v) => v.px), ...derived]) });
  }

  // ★ 약어 토큰 계열 탐지 — `--s-1 … --s-9` 처럼 **이름 끝의 숫자만 다른 변수 가족**은
  //   스페이싱 스케일의 구조적 특징이다. 키워드 매칭으로는 절대 안 잡히는데 수제
  //   디자인시스템에 아주 흔하다. 이름을 추측하지 않고 **가족을 만들어 커버리지로 고른다** —
  //   라디우스 가족(`--r-1..`)도 후보로 올라오지만 여백을 설명하지 못해 자연히 진다.
  const families = new Map();
  for (const [nm, px] of lengthVars) {
    const m = /^(.*?)(\d+)$/.exec(nm);
    if (!m) continue;
    const key = m[1];
    if (!families.has(key)) families.set(key, []);
    families.get(key).push({ name: nm, px });
  }
  for (const [key, members] of families) {
    const vals = [...new Set(members.map((v) => v.px))].sort((a, b) => a - b);
    if (vals.length < 3) continue;                       // 가족이라 부를 최소 크기
    const names = new Set(members.map((v) => v.name));
    candidates.push({ source: 'var-family', family: key, names, vars: members,
                      scale: expand(names, vals) });
  }

  if (candidates.length) {
    for (const c of candidates) c.coverage = coverage(c.scale);
    candidates.sort((a, b) => b.coverage - a.coverage);

    // ★ **후보를 하나만 고르면 안 된다.** 디자인 시스템은 스케일을 여러 벌 두는 게 정상이다 —
    //   본 스페이싱(4·8·12…)과 별도로 알약형·헤어라인용 **마이크로 스케일**(1·2·3·5·6px)을
    //   두는 식이다. 하나만 고르면 나머지 벌의 정품 토큰이 전부 「이탈」로 지적된다(실측 8문서).
    //   → **커버리지에 실제로 기여하는 가족을 전부 합친다.** 기여가 0 이면 이 화면의 여백을
    //     설명하지 못하는 가족(라디우스 등)이므로 자연히 빠진다.
    const chosen = [];
    const merged = new Set();
    for (const c of candidates) {
      const before = coverage([...merged]);
      const after = coverage([...new Set([...merged, ...c.scale])]);
      if (chosen.length && after <= before) continue;   // 새로 설명하는 값이 없으면 버린다
      c.scale.forEach((v) => merged.add(v));
      chosen.push(c);
    }
    const scale = [...merged].sort((a, b) => a - b);
    return { source: chosen[0].source,
             families: chosen.map((c) => c.family || c.source),
             vars: chosen.flatMap((c) => c.vars),
             coverage: Math.round(coverage(scale) * 100) / 100,
             rejected: candidates.filter((c) => !chosen.includes(c)).slice(0, 3)
               .map((c) => ({ family: c.family || c.source, coverage: Math.round(c.coverage * 100) / 100 })),
             scale };
  }

  // 기준 단위 1개 + calc 곱셈으로 스케일을 만드는 방식(Tailwind v4 의 `--spacing:.25rem` +
  // `calc(var(--spacing) * N)`)은 변수가 하나뿐이라 위 하한(3개)에 안 걸려 폴백으로 떨어졌다.
  // 스케일 값을 지어내지 않는다 — **기준 단위의 정수배인가**로 판정하도록 base 만 넘긴다.
  if (fromVars.length && fromVars.length < 3) {
    const base = fromVars.find((v) => /^--(?:[a-z0-9]+-)*(spacing|space)$/i.test(v.name));
    if (base && base.px > 0) {
      // 스타일시트에 **선언된 배수**로 스케일을 만든다. 값을 지어내지 않고 읽어낸 것이다.
      // 배수를 못 찾았으면 정수배 판정으로 폴백한다(`spacingBase` 만 넘어간다).
      return { source: 'base-unit', vars: fromVars, base: base.px,
               scale: [...new Set(derived)].sort((a, b) => a - b) };
    }
  }

  // ⚠️ 이전 판의 「전체 출현의 1% 미만은 노이즈」 컷은 **정품 디자인 토큰을 죽였다.**
  //    실측: CSS-in-JS 프로젝트의 `theme.space[1] = 4px` 이 4번밖에 안 쓰여 1% 컷에 걸렸고,
  //    그 결과 명시적 토큰인 4px 이 「스케일 이탈」로 지적됐다.
  //    SKILL.md §0-2 의 정의는 「반복되는 값 = 의도, 일회성 = 노이즈」이므로 그대로 쓴다.
  // ⚠️ **「상위 12개」 컷을 제거했다.** SKILL.md §0-2 의 정의는 「반복되는 값 = 의도,
  //    일회성 = 노이즈」뿐인데, 상위 N 슬라이스는 그 정의에 없는 **지어낸 값**이었다.
  //    스페이싱 값 종류가 12개를 넘는 화면(토큰 없이 손으로 쓴 CSS·브루탈리즘 계열)에서는
  //    **반복해서 쓴 정품 값이 스케일 밖으로 밀려나 전부 이탈로 잡힌다**(실측 p33: 21건).
  //    일회성 이탈은 `c >= 2` 로 이미 걸러지므로 양성 검출력은 유지된다.
  const scale = [...freq.entries()]
    .filter(([, c]) => c >= 2)
    .map(([v]) => v)
    .sort((a, b) => a - b);
  return { source: 'frequency', scale, histogram: [...freq.entries()].sort((a, b) => b[1] - a[1]) };
}
