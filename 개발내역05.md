개발내역 05 — LLM 기반 메타데이터 보강(코멘트/요약) 1차 적용
=====================================================

목표
----
- LLM을 이용해 다음 항목을 보강:
  - 테이블/컬럼 코멘트 보정(부정확/결측 시)
  - SQL 단위 요약(Summary 레코드 생성)
  - 메소드 요약(Summary 레코드 생성)
- 성능 고려: 드라이런/폴백/최대 처리 건수/임계값 등 설정화

주요 변경점
----------
- `phase1/src/llm/enricher.py`
  - 일반 텍스트 생성용 래퍼(`generate_text`) 추가
- `phase1/src/database/metadata_engine.py`
  - LLM 보강 메서드 추가:
    - `llm_enrich_table_and_column_comments(max_tables, max_columns, lang)`
    - `llm_summarize_sql_units(max_items, lang)`
    - `llm_summarize_methods(max_items, lang)`
  - `llm.enricher.generate_text` 사용 (드라이런/온도/토큰/프로바이더 반영)
- `config/config.yaml`
  - `llm_assist.enrich` 섹션 추가(기능별 on/off 및 최대 처리 개수 지정)

설정 예시
--------
llm_assist:
  enabled: true
  provider: auto
  dry_run: true           # 오프라인/CI
  temperature: 0.0
  max_tokens: 512
  enrich:
    table_comments:
      enabled: true
      max_tables: 25
    column_comments:
      enabled: true
      max_columns: 50
    sql_summary:
      enabled: true
      max_items: 30
    method_summary:
      enabled: true
      max_items: 30

테스트
-----
- 스펙 러너 보강 중(레거시 import 정리 과제 분리). 본 커밋에서는 단위 경로 추가와 드라이런 경로 회귀 기반으로 수동 확인.
- 후속으로 `engine_llm_db_enrich` kind 스펙 추가 예정(드라이런으로 테이블/컬럼 코멘트 자동 채움 검증).

한계/다음 단계
-------------
- SQL 원문이 없는 경우가 있어 구조 기반 요약으로 제한. 원문 보존/샘플링 도입 검토.
- 조인키 추론/구성요소 연관관계 LLM 보강은 2차에 추가(EdgeHint 생성/Join 보강 규칙 포함).
- 러너 import 경로 통일(`from src...`)로 엔진 계열 스펙 전반 안정화 예정.

