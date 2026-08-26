# Effect 결정 트리·cleanup·ref 경계 (SKILL.md 비중복)

## "useEffect가 맞나" 결정 트리

```
이 코드는 왜 실행돼야 하는가?
├─ 다른 상태/props에서 계산 가능 → 렌더 중 계산 (비싸면 useMemo) - Effect 아님
├─ 사용자가 무언가를 해서 → 이벤트 핸들러 - Effect 아님
├─ 부모/자식에게 알리려고 → 핸들러에서 콜백 호출 / 상태 끌어올리기 - Effect 아님
├─ 서버 데이터가 필요해서 → 데이터 라이브러리 / 프레임워크 로더 - 직접 Effect는 최후
└─ "이 컴포넌트가 화면에 있는 동안" 외부 시스템과 동기화
   (구독·타이머·차트 인스턴스·document title) → ✅ useEffect가 맞는 유일한 경우
```

## cleanup 규칙 (Effect를 쓰기로 했다면)

- **set과 unset은 쌍** — 구독했으면 해지, 타이머 걸었으면 clear, 연결했으면 끊기. cleanup 없는 구독은 StrictMode에서 2중 구독으로 즉시 드러난다(고마운 일이다).
- fetch 직접 구현 시 경쟁 차단 표준형:
  ```jsx
  useEffect(() => {
    let ignore = false;
    load(code).then((d) => { if (!ignore) setData(d); });
    return () => { ignore = true; };   // 이전 요청의 늦은 응답 무시
  }, [code]);
  ```
- cleanup은 "다음 실행 직전 + 언마운트 시" 양쪽에서 돈다 — 의존성 변경마다 [정리→재설정]이 한 사이클.

## ref의 정당한 용도 / 오용

| 정당 | 오용 |
|---|---|
| DOM 접근(포커스·스크롤·측정) | 상태 대신 ref에 값 저장 후 화면 갱신 기대(렌더 안 됨) |
| 외부 인스턴스 보관(차트·소켓) | 렌더 중 ref.current 읽고 분기(렌더 비결정성) |
| 렌더와 무관한 값(타이머 id·이전 값) | props를 ref에 복사(이미 클로저가 잡는다) |

- "값이 바뀌어도 다시 그릴 필요 없다"가 ref의 자격 조건. 그릴 필요 있으면 상태다.
- ref 콜백(`ref={(el) => ...}`)은 인스턴스 연결을 Effect 없이 해결하는 경우가 많다 — 차트 라이브러리 마운트의 1순위 패턴.

## StrictMode 이중 실행과 화해하기

- 개발 전용·마운트 Effect만 2회 — "두 번 fetch돼요"는 버그 신고가 아니라 **멱등 아님 신고**다.
- 대응: cleanup 정합(위) 또는 데이터 라이브러리(자체 dedupe). `useRef(didRun)` 가드로 1회 강제는 문제를 숨기는 것 — 진짜 1회 보장이 필요한 앱 초기화는 컴포넌트 밖(모듈 레벨·엔트리)으로.

## useLayoutEffect / useSyncExternalStore (드문 도구)

- useLayoutEffect: 그리기 전에 DOM 측정→동기 반영이 필요할 때만(툴팁 위치 등) — 기본은 useEffect, 깜빡임이 보이면 승격.
- useSyncExternalStore: 외부 스토어(브라우저 API·전역 객체) 구독의 정석 — `window.matchMedia`·온라인 상태 등을 Effect+setState로 짜고 있다면 이것으로.
