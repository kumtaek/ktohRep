개발내역 06 — 러너 정비 및 2차 LLM 보강(조인키/요약/게이팅)
=======================================================

목표
----
- 테스트 러너 정비: 엔진 관련 import를 `from src...`로 통일하고, 신규 kind 추가
- 2차 LLM 보강: 조인키 추론/요약 고도화/게이팅 조건 강화의 기반 마련

변경 사항
--------
- 러너(`tests/spec_runner.py`)
  - `sys.path`에 `phase1`, `phase1/src` 동시 추가 (패키지 혼용 안정화)
  - 엔진 import를 `from src...`로 통일
  - 신규 kind 추가:
    - `engine_llm_db_enrich`: 테이블/컬럼 코멘트 보강 + 조인키 추론(dry_run) 검증
  - 스펙 추가: `phase1/testcase/llm_db_enrich.spec.yaml`

- LLM 보강(2차)
  - `MetadataEngine`
    - `llm_infer_join_keys(max_items)`: 조인키 추론(드라이런 시 휴리스틱, 추후 LLM 출력 파싱 확장)
    - `llm_suggest_edge_hints_for_unresolved_calls(max_items)`: 미해소 호출 Edge에 EdgeHint 생성(초기 버전)
    - `llm_summarize_sql_units(...)`: 파일 원문 스니펫을 포함하도록 보강
  - 설정(`config/config.yaml > llm_assist.enrich`)
    - `join_infer.enabled/max_items`, `edge_hint.enabled/max_items` 추가

테스트 결과 요약
---------------
- Phase1 엔진 스펙: 통과 (보강/저장/드라이런 경로 포함)
- Visualize 일부 스펙: 기존 레거시 이슈(필수 `--out`, 내부 모델 필드 변경)로 실패 — 별도 이슈로 분리 권장

다음 단계 제안
-------------
- LLM 기반 조인키 추론 고도화: DB PK/FK 메타 + SQL 원문/샘플을 LLM에 제공 → `Join.inferred_pkfk/confidence` 정교화
- EdgeHint 고도화: 메소드/컴포넌트 연관관계 제안 생성(클래스/패키지 맥락 포함) 후 build 단계에서 해소
- 게이팅 강화: 신뢰 낮음·요약 미존재·조인 불명확 케이스에서만 LLM 호출 (현재 일부 조건 반영, 확대 예정)

