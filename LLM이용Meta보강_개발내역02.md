개발내역 02 — Phase1 LLM 보강(Assist) 통합 및 테스트케이스 추가
==============================================================

목표
----
- Phase1 분석에서 파싱 실패 또는 신뢰도(Confidence)가 임계값 이하인 경우 로컬 Ollama(`gemma3:1b`) 또는 운영 vLLM(`Qwen2.5`)로 보강 질의를 수행해 정확도를 향상.
- 보강 결과에 따라 `ConfidenceCalculator.update_confidence_with_enrichment`로 신뢰도를 갱신하고, `EnrichmentLog` 테이블에 기록.

적용 범위 및 트리거
------------------
- 대상: `.java`, `.jsp`, `.xml`(MyBatis)
- 위치: `phase1/src/database/metadata_engine.py`의 `_analyze_single_file_sync` 내 저장 직후 훅(hook)
- 트리거: 파싱 실패 또는 계산된 `confidence < low_conf_threshold`(기본 0.6)

구성 요소
--------
- 보강 엔진: `phase1/src/llm/assist.py`
  - 임계값 로직, 캐시(`out/llm_cache`), 드라이런(`dry_run`), JSON 강제(coerce) 처리
  - 프롬프트 템플릿: `phase1/src/llm/prompt_templates.py`
  - LLM 라우팅: 기존 `phase1/src/llm/client.py` 재사용 (Ollama/vLLM)
- 신뢰도 갱신: `ConfidenceCalculator.update_confidence_with_enrichment`
- 로깅: `models.EnrichmentLog`에 pre/post confidence, 모델, prompt_id, params 저장

설정(기본치 주입)
----------------
- `phase1/src/main.py`의 `_set_default_config`에서 `llm_assist` 기본값 추가
  - `enabled=true`, `provider=auto`, `low_conf_threshold=0.6`
  - `max_calls_per_run=50`, `file_max_lines=1200`, `temperature=0.0`, `max_tokens=512`
  - `strict_json=true`, `cache=true`, `cache_dir=./out/llm_cache`, `log_prompt=false`, `dry_run=false`

메시지/스키마(요약)
------------------
- Java: 클래스/메서드 구조 JSON만 응답(자연어 금지)
- JSP/XML: SQL/tables/joins/filters JSON만 응답(자연어 금지)

변경 파일
--------
- 추가: `phase1/src/llm/assist.py`, `phase1/src/llm/prompt_templates.py`
- 수정: `phase1/src/database/metadata_engine.py` (보강 훅 연결), `phase1/src/main.py` (기본 설정 주입)
- 테스트: `tests/spec_runner.py`(새 kind 추가), `phase1/testcase/llm_assist.spec.yaml`(dry-run 검증)

테스트케이스 추가
----------------
- `phase1/testcase/llm_assist.spec.yaml`
  - kind: `engine_llm_assist`
  - input: `tests/samples/java/ValidSimple.java`
  - expected: `enrichment_logs_min: 1`
- `tests/spec_runner.py`
  - `engine_llm_assist` 실행 시 `llm_assist.dry_run=true`, `low_conf_threshold=1.0`로 강제 트리거 후 `EnrichmentLog` 적재 확인

검증/한계
--------
- 드라이런 모드에서 LLM 호출 없이도 파이프라인/로깅 경로를 검증
- 실제 모델 호출은 `.env`/환경변수 설정 후 동일 경로로 동작(Ollama 또는 vLLM)

추가 업데이트
------------
- DB 보강 삽입 로직 추가: LLM JSON을 이용해 누락된 Class/Method 및 SqlUnit/Join/Filter를 중복 방지 규칙으로 최소 삽입합니다.
- 테스트(dry_run=true)에서는 실제 DB 보강은 수행하지 않고 EnrichmentLog 기록만 수행합니다.

향후 과제(제안)
--------------
- 보강 JSON을 DB에 최소 삽입(중복 방지 규칙 포함) 및 EdgeHint 강화
- 파일 단위가 큰 경우 스니펫 분할/재조합 호출, JSON 재시도(fix-json) 루틴 고도화
- 운영 모니터링 지표(호출 수/캐시 히트/재시도/실패율) 대시보드 연계
