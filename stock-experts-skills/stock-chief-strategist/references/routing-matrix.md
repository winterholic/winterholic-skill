# 레퍼런스 — 전문가 20인 라우팅 매트릭스

> 각 전문가의 정체성·시간축·대표 트리거·상호 호출. 라우팅 판단의 빠른 참조표.
> 설계 근거: vault `wiki/stock-investing/주식 전문가 스킬 설계.md`.

## 펀더멘털 (A)

| 스킬 | 시간축 | 한 줄 정체성 | 대표 트리거 | 자주 함께 |
|---|---|---|---|---|
| stock-deepvalue | 장기 | 청산가치·안전마진(Graham) | 싸게/NCAV/PBR바닥 | behavioral, special-situations |
| stock-quality | 초장기 | 해자·고ROIC 복리(Buffett) | 해자/오래 보유 | garp |
| stock-garp | 중장기 | 성장 대비 가격 PEG(Lynch) | PEG/텐배거 | quality |
| stock-growth | 장기 | 15 Points·혁신(Fisher/ARK) | 고성장/혁신/TAM | behavioral, tail-risk |
| stock-special-situations | 이벤트 | 분사·M&A·마법공식(Greenblatt) | 스핀오프/특수상황 | deepvalue |
| stock-dividend | 장기 | 배당수익률 밴드(Weiss) | 배당/인컴 | quality |

## 기술적/타이밍 (B)

| 스킬 | 시간축 | 정체성 | 트리거 | 함께 |
|---|---|---|---|---|
| stock-trend | 수주~수개월 | 4단계·30주MA(Weinstein) | 추세/돌파 | swing |
| stock-swing | 수일~수주 | CAN SLIM(O'Neil) | 캔슬림/컵앤핸들 | trend |
| stock-intraday | 분~시간 | 프라이스액션(Brooks) | 단타/분봉 | execution |
| stock-pattern-theory | 가변 | Elliott·Wyckoff | 파동/국면 | trend |

## 퀀트/시스템 (C)

| 스킬 | 역할 | 정체성 | 트리거 | 함께 |
|---|---|---|---|---|
| stock-factor-quant | 장기 시그널 | 팩터(Fama-French) | 팩터/스마트베타 | portfolio-risk |
| stock-statarb | 단기 시그널 | 평균회귀 차익(Chan) | 페어/공적분 | execution |
| stock-execution | 실행 | 마이크로스트럭처(Harris/Kissell) | VWAP/슬리피지 | (모든 시그널) |
| stock-ml-alt-data | 알파 R&D | 금융ML(López de Prado) | ML/과적합 | factor-quant |

## 거시/탑다운 (D)

| 스킬 | 역할 | 정체성 | 트리거 | 함께 |
|---|---|---|---|---|
| stock-macro | 자산배분 | 부채사이클·All Weather(Dalio) | 매크로/금리/배분 | sector-rotation |
| stock-sector-rotation | 섹터 | 경기국면 4분기(Stovall) | 섹터/경기민감 | macro |

## 리스크/심리 (E) — 거부권급 가중

| 스킬 | 역할 | 정체성 | 트리거 | 함께 |
|---|---|---|---|---|
| stock-portfolio-risk | 사이징 | MPT·Kelly·VaR | 비중/사이징/VaR | tail-risk |
| stock-tail-risk | 꼬리 헤지 | 바벨·블랙스완(Taleb/Spitznagel) | 폭락대비/꼬리헤지 | portfolio-risk |
| stock-behavioral | 메타 검수 | 편향·사이클(Kahneman/Shiller/Marks) | 심리/과열/역발상 | (대상 학파) |

## 오케스트레이터 (F)

| 스킬 | 역할 |
|---|---|
| stock-chief-strategist | 라우팅·종합·충돌 조율·파이프라인 조립 |

## 메타 (G)

| 스킬 | 역할 | 트리거 |
|---|---|---|
| stock-scorecard | 사후 채점·트랙레코드·캘리브레이션·스킬 환류 | 복기/채점/지난 분석/점검일 도래/무효화 터치 |

## 라우팅 원칙 (요약)

1. 시간축·목적·스타일 먼저 분해.
2. 1~3명만 호출(과다 금지).
3. 시간축 다르면 충돌 아님 — 분리 제시.
4. 리스크/심리(E)는 가중치 높게(veto 성격).
5. 합의 없으면 억지 결론 금지 — 이견+확인 데이터로.

## 라우팅 평가표 (eval — 모호 질문 10선)

라우터 점검용. 아래 질문에 대해 기대 라우팅과 다르게 판단했다면 라우팅 표·원칙을 재독한다.

| # | 질문 | 기대 라우팅 | 포인트 |
|---|---|---|---|
| 1 | "삼성전자 지금 사도 돼?" | 시간축·목적 1회 되묻기 → 보통 가치 1 + 기술 1 + behavioral | 막연 질문은 즉답 금지 |
| 2 | "PER 5배인데 왜 안 오르지?" | deepvalue(+behavioral) | value trap 점검이 핵심 |
| 3 | "한 달 안에 먹고 나올 건데 차트 어때?" | swing | 수일~수주 = swing (trend 아님) |
| 4 | "금리 내리면 뭘 사야 해?" | macro → sector-rotation | 종목 아닌 자산군·섹터 질문 |
| 5 | "물렸는데 물타기 할까?" | behavioral(처분효과) + portfolio-risk(사이징) | 심리+사이징, 종목 분석 아님 |
| 6 | "인적분할 발표 났는데 기회야?" | special-situations | 이벤트가 촉매 |
| 7 | "배당 6%면 안전한 거지?" | dividend | yield trap 검증 포함 |
| 8 | "백테스트 샤프 1.5 나왔어, 돌려도 돼?" | ml-alt-data(과적합 검증, +factor-quant) | 실전 투입 전 CPCV/DSR |
| 9 | "폭락 올 것 같아서 무서워" | tail-risk + portfolio-risk(+behavioral) | 예측 아닌 대비·헤지로 |
| 10 | "엘리어트로 보면 지금 3파 맞아?" | pattern-theory 직행(라우터 스킵) | 방법 특정 시 라우터 안 거침 |
| 11 | "두 달 전에 분석했던 그 종목 어떻게 됐지?" | stock-scorecard | 새 분석 아님 — 채점·복기. 결과에 따라 전문가 재호출 |
