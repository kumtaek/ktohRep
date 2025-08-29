Phase1 LLM 보강 설계/개발 내역
================================

목표
----
- Phase1 분석에서 파싱 실패 또는 신뢰도(Confidence)가 임계값 이하인 경우 로컬 Ollama(gemma3:1b) 또는 운영 vLLM(Qwen2.5)로 보강 질의를 수행해 정확도를 높인다.
- 보강 결과를 구조적으로 수집해 DB(Schema에 포함된 EnrichmentLog 등)에 기록하고, ConfidenceCalculator.update_confidence_with_enrichment 로 최종 신뢰도를 갱신한다.

적용 범위
---------
- 대상 파일: `.java`, `.jsp`, `.xml`(MyBatis) 우선.
- 대상 단계: `phase1/src/database/metadata_engine.py` 의 `_analyze_single_file_sync` 내 파일 단위 처리 완료 직후(혹은 실패 시 예외 처리 지점)에 LLM 보강을 훅(hook)으로 추가.

트리거 조건(초기 설정)
-----------------------
- 파싱 실패(Exception) 발생 시 → 보강 시도.
- 파싱 성공이나 계산된 `confidence < low_conf_threshold` 일 때 → 보강 시도.
- 기본 임계값 제안: `low_conf_threshold = 0.6` (config로 조정 가능)

구성 요소
--------
- LLM 클라이언트: `phase1/src/llm/client.py`
  - `OllamaClient`: 로컬 개발에서 `gemma3:1b`
  - `VLLMClient`: 운영 vLLM(OpenAI 호환)로 `Qwen2.5`
  - `get_client()`: `LLM_PROVIDER` 로 분기(`ollama` 기본)
- 보강 로깅/저장: `EnrichmentLog`(이미 모델 존재). 필요 시 파일 캐시 추가(sha256 기반).
- 신뢰도 갱신: `ConfidenceCalculator.update_confidence_with_enrichment()` 활용.

환경 변수/설정
--------------
- `.env` 또는 시스템 환경 변수
  - `LLM_PROVIDER=ollama|vllm|openai`(기본: `ollama`)
  - `OLLAMA_HOST`(기본: `http://localhost:11434`), `OLLAMA_MODEL`(기본: `gemma3:1b`)
  - `VLLM_BASE_URL`, `VLLM_API_KEY`, `VLLM_MODEL`(예: `Qwen2.5`)
- `config.yaml` 확장 예시

  processing:
    confidence_threshold: 0.5  # 기존
  llm_assist:
    enabled: true
    provider: auto           # auto|ollama|vllm
    low_conf_threshold: 0.6
    max_calls_per_run: 50
    file_max_lines: 1200     # 프롬프트에 실을 최대 라인
    temperature: 0.0
    max_tokens: 512
    strict_json: true        # LLM 응답 JSON 강제
    cache: true
    cache_dir: ./out/llm_cache
    log_prompt: false        # 민감정보 보호를 위해 기본 off
    dry_run: false

동작 흐름(파일 단위)
--------------------
1) 기존 파서 수행 → `parse_result_data` 생성 → `calculate_parsing_confidence()` 계산.
2) 실패 또는 `confidence < low_conf_threshold` 이면 LLM 보강 루틴 실행.
3) 프롬프트 구성: 파일의 앞/중간/끝 샘플링(최대 `file_max_lines`), 언어/파일 유형 메타.
4) LLM 호출(`get_client().chat`)은 비스트리밍, `temperature=0`, `max_tokens` 제한, 엄격 JSON 요청.
5) JSON 파싱 및 검증(스키마 최소 검증):
   - Java: classes[{name,fqn,start_line,end_line,methods[{name,signature,return_type,start_line,end_line}]}], edges(옵션)
   - JSP/MyBatis: sql_units[{stmt_kind, tables[], joins[], filters[]}]
6) 파싱된 구조를 현재 파이프라인에 맞도록 최소 변환 → 누락 보정(예: 라인 범위 추정) → 저장.
7) `update_confidence_with_enrichment(original_confidence, enrichment_result)`로 신뢰도 보정.
8) `EnrichmentLog` 에 pre/post confidence, 모델, prompt_id, 파라미터 저장. 캐시 활성화 시 sha256(file_content) 키로 파일 캐시에도 저장.

프롬프트 템플릿(초안)
--------------------
- 공통 시스템 메시지(요지):
  - "너는 정적 분석 보조 AI다. 지시된 스키마에 맞춘 JSON만 출력해라. 자연어 설명 금지."

- Java 파일용(User 메시지 예):
  - 지시: "다음 Java 코드에서 클래스와 메서드를 추출해 JSON으로만 응답해라."
  - 스키마: `{ "classes": [ { "name": str, "fqn": str?, "start_line": int?, "end_line": int?, "methods": [ { "name": str, "signature": str?, "return_type": str?, "start_line": int?, "end_line": int? } ] } ] }`
  - 제약: "JSON 이외 출력 금지, 값 미상시는 null 또는 생략"

- JSP/XML(MyBatis) 파일용(User 메시지 예):
  - 지시: "다음 파일에서 SQL 문과 테이블/조인/필수필터를 추출해 JSON으로만 응답해라."
  - 스키마: `{ "sql_units": [ { "stmt_kind": "select|insert|update|delete", "tables": [str], "joins": [ {"l_table": str, "l_col": str, "op": str, "r_table": str, "r_col": str } ], "filters": [ {"table_name": str?, "column_name": str, "op": str, "value_repr": str, "always_applied": bool } ] } ] }`
  - 제약: 위와 동일

오류/안전 가이드
----------------
- 토큰/길이 제어: 큰 파일은 샘플링하여 전송, 프롬프트 분할은 2차 과제로.
- 결정성: `temperature=0`, `stop` 미지정(필요 시 `\n\n` 등 추가).
- JSON 파싱 실패 시 1회 재시도(간단한 `fix-json` 프롬프트 적용).
- 민감정보: `log_prompt=false` 기본, 운영 로그에는 해시/요약만 기록.
- 네트워크/모델 장애 시 즉시 폴백 중단(원래 결과 유지) 및 경고 로그.

캐싱 전략(초기)
---------------
- 파일 내용 sha256과 파일 경로를 키로 파일 캐시(`out/llm_cache/<sha>.json`) 사용.
- 캐시 히트 시 LLM 호출 생략. TTL은 설정(예: 7일). 캐시 무효화는 파일 해시 변경으로 자동 처리.
- 장기적으로 DB 캐시 테이블 추가 가능하나, 초기에는 파일 캐시로 단순화.

DB 반영 최소 단위
-----------------
- Java: 누락된 `Class/Method`만 보강 삽입(중복 방지 위해 FQN+name 기준 존재 확인).
- JSP/XML: `SqlUnit/Join/RequiredFilter`를 보강 삽입(존재 중복 체크 후 추가).
- `Edge`는 1차에선 생성 생략 혹은 `edge_hints`에 힌트 저장하여 후속 빌드 단계에서 해소.

로깅/모니터링
-------------
- `EnrichmentLog`에 pre/post confidence, 모델명, prompt_id, 파라미터 저장.
- LLM 호출 실패/재시도/캐시 히트 건수 집계하여 배치 요약 로그에 포함.

테스트 계획
----------
- 단위 테스트: JSON 파싱/검증, 캐시 키/입출력, 임계값 로직.
- 통합 테스트: 샘플 파일로 파싱 실패/저신뢰 시나리오 강제 → LLM Mock로 JSON 리턴 → DB 삽입/신뢰도 갱신 확인.
- 수동 테스트(로컬): Ollama `gemma3:1b`로 CLI 및 파이프라인 실행, UTF-8 출력 확인.

점진적 적용 계획
----------------
1) 보강 훅/설정 플래그 추가(기본 off) + 캐시/파서-유형별 프롬프트 템플릿 탑재.
2) JSON 파싱/검증 + 최소 삽입 경로(Java methods, MyBatis filters)부터 적용.
3) EdgeHint 보강 및 Confidence 갱신 적용.
4) 운영 vLLM 라우팅/모니터링 지표 반영.

예상 변경 파일(1차)
------------------
- `phase1/src/database/metadata_engine.py`:
  - `_analyze_single_file_sync` 후처리 구간에 `llm_assist` 훅 추가(성공/실패 케이스 분기).
  - 보강 결과 저장 및 `EnrichmentLog` 기록.
- `config/config.yaml`(예시): `llm_assist` 섹션 추가.
- `phase1/src/llm/prompt_templates.py`(신규): 템플릿/스키마 상수 분리.
- `phase1/src/llm/assist.py`(신규): 보강 엔진(캐시, 호출, 파싱, 매핑, 로깅) 모듈.

운영 연계
--------
- 운영에서는 `LLM_PROVIDER=vllm`, `VLLM_MODEL=Qwen2.5` 설정으로 자동 사용.
- 로컬 개발은 Ollama `gemma3:1b` 기본값으로 동작.

메모
----
- 콘솔 출력 인코딩 이슈(Windows cp949)는 CLI에서 UTF-8 출력으로 처리(`llm_cli.py`).
- LLM 호출 비용/지연을 고려하여 캐시/임계값/최대 호출 수를 보수적으로 시작 후 조정.

