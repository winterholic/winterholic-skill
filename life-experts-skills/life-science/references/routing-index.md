# 과학 스킬 라우팅 색인

이 파일은 후보를 좁히는 1차 지도다. 전체 166종의 정본은 원본 `docs/skills.md`이며, 여기 없는 도구명은 그 파일에서 검색한다.

| 요청 신호 | 1차 영역 | 대표 후보 | 선택 메모 |
|---|---|---|---|
| FASTA·VCF·BAM·유전자·RNA-seq·single-cell | 생물정보학·유전체 | `biopython`, `pysam`, `bulk-rnaseq`, `scanpy`, `scvi-tools`, `pydeseq2` | 파일 형식/분석 단계가 명시된 전용 스킬 우선 |
| 유전자 집합·경로·네트워크·계통 | 시스템생물학·진화 | `pathway-enrichment`, `networkx`, `phylogenetics`, `scikit-bio` | 단순 그래프 코드는 dev가 아니라 과학 해석이면 이쪽 |
| SMILES·SDF·RDKit·도킹·ADMET·QSAR | 화학·신약개발 | `rdkit`, `datamol`, `diffdock`, `deepchem`, `medchem`, `pytdc` | 포즈 예측과 결합 친화도 예측을 구분 |
| 단백질 구조·서열·설계 | 단백질공학 | `esm`, `glycoengineering`, `molecular-dynamics`, `tamarind` | 구조 조회와 새 서열 설계를 구분 |
| 질량분석·proteomics·스펙트럼 | 프로테오믹스 | `pyopenms`, `matchms` | 벤더 포맷과 공개 포맷 변환 조건 확인 |
| DICOM·MRI·CT·병리 슬라이드 | 의료영상·디지털병리 | `pydicom`, `histolab`, `imaging-data-commons` | 개인 진단이 아니라 연구 데이터 처리만 |
| EEG·spike·전기생리 | 신경과학 | `bids`, `neurokit2`, `neuropixels-analysis` | 임상 판정으로 넘어가면 중단 |
| PyTorch·Transformer·분류·예측 | 과학 ML | `scikit-learn`, `pytorch-lightning`, `transformers`, `hugging-science` | 일반 ML 앱 구현은 dev-experts |
| 재료·결정·양자화학·분자동역학 | 재료·화학·물리 | `pymatgen`, `molecular-dynamics`, `rdkit`, `rowan` | 계산 자원·외부 API·라이선스 확인 |
| 유체·수치해석·공학 시뮬레이션 | 공학·시뮬레이션 | `fluidsim`, `openpiv`, `matlab`, `simpy`, `sympy` | 사용자가 지정한 솔버가 있으면 그 도구 우선 |
| 통계·베이지안·시계열·인과·EDA | 분석·통계 | `statsmodels`, `pymc`, `aeon`, `exploratory-data-analysis` | 연구 질문과 데이터 생성 구조부터 확인 |
| 실험군·표본수·무작위화·가설 | 연구 방법론 | `experimental-design`, `statistical-analysis`, `hypothesis-generation` | 수집 전 설계와 수집 후 분석을 구분 |
| 논문 검색·체계적 문헌고찰·인용 | 과학 문헌 | `literature-review`, `citation-management`, `bgpt-paper-search` | 최신성 필요 시 원문·DOI를 웹으로 재확인 |
| 그래프·논문 그림·포스터·발표 | 과학 커뮤니케이션 | `scientific-visualization`, `scientific-schematics`, `latex-posters` | 일반 문서 파일 제작은 전용 artifact 스킬 우선 |
| Benchling·LIMS·ELN·프로토콜 | 연구 플랫폼 | `benchling-integration`, `labarchive-integration`, `protocolsio-integration` | 계정·권한·데이터 반출 확인 |
| Opentrons·액체취급·실험실 장비 | 실험실 자동화 | `opentrons-integration`, `pylabrobot` | 실제 장비 동작 전 시뮬레이션·사람 검토 필수 |
| Nextflow·nf-core·재현 파이프라인 | 연구 워크플로우 | `nextflow`, `datalad` | 일반 CI/CD와 구분하고 data provenance를 보존 |
| ISO·ICH·분석법 검증 | 규제·표준 준비 | `iso-standards-readiness`, `analytical-method-validation` | 인증·법적 판정이 아니라 증거 준비까지만 |
| 공개 과학 DB·온톨로지·현재 병원체 | 데이터 접근 | `database-lookup`, `ontology-term-resolution`, `pathogen-variant-surveillance` | 현재 상태는 라이브 API와 조회 시각 기록 |

## 조합 규칙

- 같은 단계의 대체 도구는 하나만 고른다. `scanpy`와 `scvi-tools`를 습관적으로 함께 읽지 않는다.
- 연속 단계가 명확할 때만 2개를 조합한다. 예: `bulk-rnaseq` → `pathway-enrichment`.
- 문서 출력 형식 스킬과 연구 내용 스킬이 겹치면 내용은 `life-science`, 파일 생성은 전용 artifact 스킬이 맡는다.
