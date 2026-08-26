# biz-3d-designer — 파이프라인 & 출처 (검증판)

> SKILL.md 보강. 툴 빠르게 변함 — 원리 위주, 세부는 공식 문서. 출처 2026-06-30/07-01 웹 검증. 1단계 참조. 실무 파일: `pbr-pipeline.md`.

## 1. PBR (정전·표준)
- **Brent Burley, "Physically Based Shading at Disney"(SIGGRAPH 2012)** — Disney principled BRDF, metallic-roughness의 개념적 기원. https://media.disneyanimation.com/uploads/production/publication_asset/48/asset/s2012_pbs_disney_brdf_notes_v3.pdf
- **Khronos glTF 2.0** — metallic-roughness가 **코어 기본** 머티리얼. https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html · https://www.khronos.org/gltf/pbr
- ⚠️ metallic-roughness ≠ specular-glossiness(후자는 deprecated 확장).

## 2. 포맷
- **glTF 2.0** = 비준된 Khronos 개방 표준. ✅ **ISO/IEC 12113:2022** 확정 — 정식 명칭 "Information technology — Runtime 3D asset delivery format — Khronos glTF 2.0"(2022-08 발표, PAS 절차로 만장일치 승인). https://www.iso.org/standard/83990.html · https://www.khronos.org/news/press/khronos-gltf-2.0-released-as-an-iso-iec-international-standard
- **USDZ**(Pixar/OpenUSD) = **비압축·비암호 ZIP**(압축 아님). OpenUSD 2016 오픈소스, AOUSD 2023-08 출범. ✅ **AOUSD OpenUSD Core Specification 1.0**이 2025-12-17 개방 표준으로 발표됨(USDA/USDC/USDZ 포함; 1.1은 2026 애니메이션 기능 예정). https://aousd.org/news/core-spec-announcement/ · https://openusd.org/release/spec_usdz.html

## 3. 라이팅 (IBL)
**Paul Debevec, IBL** — 정전 *논문* "Rendering Synthetic Objects into Real Scenes…", SIGGRAPH **1998**. https://www.pauldebevec.com/Research/IBL/ (⚠️ "Rendering with Natural Light"는 데모 *필름*, 논문 아님). 3점 조명·HDRI. ACES 색관리(ACEScg 작업·OpenEXR).

## 4. 실시간 vs 오프라인
실시간=래스터화(+하이브리드 RT), 오프라인=패스트레이싱(몬테카를로 GI). 텍셀 밀도 일관. https://blog.chaos.com/real-time-ray-traced-and-rasterized-rendering-explained

## 5. 텍스처·색공간 (실무 확장) ✅ 검증
- **베이스컬러/알베도 = sRGB 인코딩**(감마), **나머지 맵(노멀·러프니스·메탈릭·AO·height)은 리니어/Non-Color** — 값을 셰이더 수식에 직접 투입하므로 감마 보정하면 안 됨. 이걸 틀리면 재질이 전부 어긋남(최빈 실수).
- **알베도 값 범위**: 비금속(dielectric) 실제 알베도는 대략 **sRGB 50~240**(숯 ~50, 신설 ~240). 순수 검정/흰색은 물리적으로 없음 — 벗어나면 비사실적.
- **ORM 패킹**(관행): R=AO, G=Roughness, B=Metallic 한 텍스처에 채널 패킹 → 메모리·드로우콜 절감(실시간).
- **텍셀 밀도(texel density)**: 표면 1단위당 픽셀 수. **에셋 간 일관** 유지해야 왜곡·흐림 없음(예: 512px/m 통일). UDIM으로 고해상 다중 타일.

## 6. 노멀맵·베이크 (실무)
- **노멀맵은 지오메트리를 추가하지 않음** — 빛 반사 각도만 속임(디테일 착시). 실제 굴곡은 displacement/tessellation.
- **하이폴→로폴 베이크**: 케이지(cage, 로폴을 살짝 부풀린 사본)에서 레이를 쏴 하이폴 표면 노멀 기록. 케이지가 너무 타이트→누락, 너무 느슨→왜곡. 로폴 UV·스무딩·케이지 품질이 베이크 품질을 좌우.
- 탄젠트 스페이스 노멀(대부분) vs 오브젝트 스페이스(변형 없는 것). 하드엣지는 UV 심(seam)으로 분리해 베이크.

## 7. 교정
PBR은 재질 응답을 지배(사실감엔 IBL+선형색공간+텍셀해상도 필요). USDZ 비압축. 패스트레이싱 ⊃ 실시간 "RT"(보통 제한적 하이브리드). 베이스컬러만 sRGB, 데이터맵은 리니어. 노멀맵≠지오메트리 추가.

## 8. 출처
- Burley(Disney, SIGGRAPH 2012). · Khronos glTF 2.0/USDZ. · Paul Debevec(IBL, SIGGRAPH 1998). · Catmull-Clark 서브디비전(1978). · Polycount Wiki(텍스처 베이킹).
