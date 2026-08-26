# biz-3d-character-artist — 파이프라인 & 출처 (검증판)

> SKILL.md 보강. 툴 빠르게 변함 — 원리 위주. 출처 2026-06-30/07-01 웹 검증. 1단계 참조. 실무 파일: `topology-rigging.md`.

## 1. 언캐니 밸리 (정밀 인용)
✅ **Masahiro Mori, "Bukimi no Tani"(不気味の谷), *Energy*(エネルギー) 7(4):33–35, 1970**(일본어) — 원전 서지 확인. 인간 유사도가 오를수록 호감↑ 후 "골짜기"로 급락; **움직임이 효과를 증폭**. ✅ 정전 영역(英譯): Mori·MacDorman·Kageki, "The Uncanny Valley [From the Field]," *IEEE Robotics & Automation Magazine* 19(2):98–100, 2012, **DOI 10.1109/MRA.2012.2192811** — Mori가 승인한 최초 공인 영역. https://spectrum.ieee.org/the-uncanny-valley
- ⚠️ 가설(1970)이며 실증 지지는 혼재 — 법칙 아닌 휴리스틱. 외형보다 **모션** 증폭 강조.

## 2. 파이프라인·토폴로지 (Polycount 위키)
하이폴 스컬프→리토폴→UV→베이크→텍스처→리깅→스키닝. "poly count"는 실제 **삼각형 수**(정점 수가 더 정확한 성능 지표). 토폴로지는 디포메이션을 따름(관절 엣지루프, 얼굴 안와/구륜 루프). 로폴 삼각화+하드엣지 UV 분할 후 탄젠트 노멀 베이크. http://wiki.polycount.com/wiki/Polygon_Count · http://wiki.polycount.com/wiki/Texture_Baking

## 3. 폴리 예산 (Polycount 검증 + 통념)
검증: 2 tris(빌보드)→40,000+(복잡 캐릭터); Lara Croft 230(TR1)→32,816(Underworld); Brawl Mario 5,227 tris, Snake 5,149; Sam Fisher 25,332. ⚠️ 현대 통념(2차): 모바일 ~5k~20k, PC 바디 ~15k~25k(의상 포함 50k~60k), AAA ~50k~100k+.

## 4. 토폴로지·엣지플로우 (실무 확장) ✅ 검증
- **쿼드(quad) 우선**: 사각형 폴리는 서브디비전·디포메이션에서 예측 가능. **삼각형·n-gon은 변형부(관절·얼굴)에서 아티팩트** — 안 보이는 평면부에만 허용.
- **엣지 루프는 근육을 따른다**: 얼굴은 **눈(안와)·입(구륜) 동심원 루프**, 관절(팔꿈치·무릎·손가락)은 굽힘 축을 가로지르는 루프. 변형되는 방향으로 흘러야 접힘이 자연스러움.
- **폴은 3/5각 지점(pole)** — 변형부·시선 집중부 피하고 평평한 곳에 숨김.
- **디포메이션 밀도 배분**: 얼굴·손·관절은 폴리 밀도↑, 안 접히는 평면(가슴판·이마)은↓ → 폴리 예산 절약하며 좋은 토폴로지. 상세는 `topology-rigging.md`.

## 5. 리깅·스키닝 (실무 확장) ✅ 검증
- **스키닝(=weight painting)**: 메시 정점을 스켈레톤 본에 가중치로 결합 → 포즈 시 자연 변형. 정점당 본 가중치 합=1.
- **관절 집중**: 팔꿈치·무릎·손가락·어깨는 변형 최대 → 가중치 세심히. 어깨는 가장 어려운 부위(다축 회전).
- 실시간은 **정점당 본 영향 ≤4개**(GPU 스키닝 관행 상한). 자동 스키닝 후 관절 수동 보정 필수.

## 6. 교정
언캐니 밸리는 **모션** 증폭 강조 + Mori 가설(법칙 아님). 고폴리 ≠ 더 좋음(토폴로지·엣지플로우 > 밀도). **노멀맵은 지오메트리 추가 안 함**(displacement/tessellation만 추가). 오토리토폴 후 얼굴·손·관절 수동 보정. 변형부는 쿼드, 삼각형은 평면부만.

## 7. 출처
- Mori(1970)/IEEE 영역(2012). · Polycount Wiki(HTTP). https://polycount.com/ · Catmull-Clark(1978). · topologyguides.com(엣지플로우) · Autodesk 스킨 웨이트 가이드.
