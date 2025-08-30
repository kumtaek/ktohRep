개발내역 04 — 자동 테스트케이스 보강(LLM Assist/증분보강/서버설정)
==========================================================

목표
----
- 최근 개발 항목(LLM 보강, DB 최소 삽입, 서버 설정 이관)에 대한 스펙 기반 자동 테스트를 추가하여 회귀 검증을 강화.

추가/수정된 테스트
-----------------
- 스펙 러너 보강(`tests/spec_runner.py`)
  - Python 경로 설정 개선: `phase1`와 `phase1/src` 모두 `sys.path`에 추가
  - 신규 kind 추가:
    - `engine_llm_assist`: LLM 보강 드라이런 경로 검증(EnrichmentLog 카운트 확인)
    - `engine_augment_unit`: LLM JSON → DB 최소 삽입 로직 단위 검증(클래스/메서드, SQL/Join/Filter)

- 신규 스펙 파일
  - `phase1/testcase/llm_assist.spec.yaml` (기존)
  - `phase1/testcase/llm_assist_jsp.spec.yaml`: JSP 대상 드라이런 보강 → EnrichmentLog ≥ 1 확인
  - `phase1/testcase/augment_java.spec.yaml`: `_augment_java_from_json` 경로 단위 검증
  - `phase1/testcase/augment_sql.spec.yaml`: `_augment_sql_from_json` 경로 단위 검증

현황/메모
--------
- 일부 스펙은 레거시 모듈 import 경로 이슈(상대/절대 혼용)로 실패할 수 있음. 현재 러너는 `phase1`와 `phase1/src`를 모두 path에 추가했으며, 점진적으로 import 기준을 통일할 예정.
- `visualize` 관련 스펙 일부는 CLI 인자 스키마 변경(필수 `--out`)과 내부 모델 필드 변경으로 실패. 본 과제 범위를 넘는 레거시 조정 이슈로 별도 작업 항목으로 분리 권장.

다음 단계(제안)
--------------
- `src` 하위 패키지의 import 정책 통일(`from src.xxx`), 레거시 절대경로(`from models.../from database...`) 제거
- 스펙 러너에 traceback 표시 옵션 추가(디버깅 편의)
- CI에서 드라이런(default)과 실모델(옵션) 두 프로파일로 테스트 구분 실행

