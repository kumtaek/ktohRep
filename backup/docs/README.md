# 보안 문서 (오프라인)

- 이 디렉터리는 폐쇄망 환경을 고려하여 OWASP Top 10 및 주요 CWE 문서를 오프라인으로 제공하기 위해 포함되었습니다.
- 백엔드에서 다음과 같이 서빙됩니다.
  - 정적 경로: `/docs` (이 폴더 전체)
  - API: `/api/docs/owasp/{code}`, `/api/docs/cwe/{code}`
  - 기존 호환: `/api/open/owasp/{code}`는 온라인 리다이렉트(로컬 문서 사용을 권하면 `/api/docs/...` 사용)

## 사용법
- 예: `http://<SERVER>:8000/api/docs/owasp/A03` → A03: Injection 설명
- 예: `http://<SERVER>:8000/api/docs/cwe/CWE-89` → SQL Injection (CWE-89) 설명

## 구성
- `owasp/` 폴더: A01~A10 (2021 기준) 요약, 위험, 사례, 대응 방법
- `cwe/` 폴더: CWE-89, CWE-79 등 빈도 높은 취약점 요약

본 문서는 내부 참고용 요약이며, 조직 표준에 맞춰 추가/보완 가능합니다.
