# Source Analyzer - 요약 README

Source Analyzer는 오프라인 환경에서도 동작하는 소스 분석/시각화 도구입니다. Java/JSP/MyBatis/SQL 메타데이터를 수집하여 의존 그래프, ERD, 컴포넌트, 클래스, 시퀀스 다이어그램을 생성하고 JSON/CSV/Markdown(mermaid)/HTML로 내보낼 수 있습니다.

## 빠른 시작
- 요구: Python 3.10+
- 설치: `pip install -r requirements.txt`
- 샘플 시각화:
  - `python -m visualize.cli graph --project-id 1 --export-mermaid ./out/graph.md`
  - `python -m visualize.cli erd --project-id 1 --export-mermaid ./out/erd.md`

## 주요 기능
- 정적 분석: 파일/클래스/메소드/SQL/관계 추출
- 다이어그램: 의존 그래프, ERD, 컴포넌트, 클래스, 시퀀스
- 내보내기: JSON/CSV/Markdown(Mermaid)
- 오프라인 문서: `doc/owasp`, `doc/cwe`에서 취약점 설명과 샘플/가이드 제공, API로 서빙

## 웹 대시보드 (선택)
- 백엔드 실행: `python web-dashboard/backend/app.py`
- 환경변수: `HOST`, `PORT`, `RELOAD`, `ALLOWED_ORIGINS`
- 오프라인 문서 API: `/api/docs/owasp/{code}`, `/api/docs/cwe/{code}`

## 오프라인 설치 개요
- 온라인 PC에서 휠 저장소 만들기:
  - `pip wheel -r requirements.txt -w wheelhouse/`
- 오프라인 설치:
  - `pip install --no-index --find-links wheelhouse -r requirements.txt`
- (선택) 프런트엔드는 사전 빌드 정적 파일을 전달해 운영 권장

자세한 구조/내부 로직/오프라인 설치 상세는 `README_detailed.md`를 참고하세요.
