# 테스트 안내 (모든 주석/메시지 한글)

- 목적: 최근 개발된 파서/엔진/모델 변경 사항의 정확성과 회복탄력성(에러 대응)을 검증합니다.
- 특징: 의도적으로 문법 오류/비정상 샘플을 포함하여 예외 안전성과 폴백 경로를 검사합니다.
- 실행: `python tests/run_tests.py`
- 출력: 표준 출력에 한국어 결과 요약과 세부 로그를 제공합니다.

구성
- `tests/samples/java`: 자바 소스 샘플(정상/비정상)
- `tests/samples/jsp`: JSP 샘플(정상)
- `tests/samples/xml`: MyBatis XML 샘플(정상/비정상)
- `tests/run_tests.py`: 간단 테스트 러너(파서/엔진 경로별 동작 검증)
