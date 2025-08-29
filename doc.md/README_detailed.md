# Source Analyzer - 상세 문서 (README_detailed)

본 문서는 내부 구조와 운영 방법, 오프라인 설치 절차를 자세히 설명합니다. 요약은 `README.md`를 참고하세요.

## 1) 개요

- 대상: Java/JSP/MyBatis/SQL 코드베이스 분석 및 시각화
- 산출물: 의존 그래프, ERD, 컴포넌트, 클래스/시퀀스 다이어그램, CSV/JSON/Markdown(mermaid)
- 운영 환경: 폐쇄망(오프라인) 우선 설계, 온라인 환경에서도 동작

## 2) 디렉터리 구조

- `phase1/src`: 메타데이터 추출 파이프라인(파서/DB/유틸/메인)
- `visualize`: 시각화 CLI와 템플릿, 데이터 접근 계층
- `web-dashboard/backend`: FastAPI 기반 백엔드 API (선택)
- `tests`: 최소 샘플과 실행 스크립트
- `doc`: 오프라인 취약점 문서(OWASP, CWE)
- `config/config.yaml`: 전역 설정(파일 패턴/DB/로깅 등)

## 3) 데이터 모델(핵심 테이블)

- `projects(project_id, name, root_path, created_at, updated_at)`
- `files(file_id, project_id, path, language, hash, loc, mtime)`
- `classes(class_id, file_id, fqn, name, start_line, end_line, modifiers, annotations)`
- `methods(method_id, class_id, name, signature, return_type, start_line, end_line, annotations, parameters, modifiers)`
- `sql_units(sql_id, file_id, origin, mapper_ns, stmt_id, stmt_kind, start_line, end_line, normalized_fingerprint)`
- `joins(join_id, sql_id, left_table/column, right_table/column, join_type, condition_text)`
- `required_filters(filter_id, sql_id, table, column, op, value_repr, always_applied, confidence)`
- `edges(edge_id, src_type/src_id, dst_type/dst_id, edge_kind, confidence)`
- `vulnerability_fixes(fix_id, target_type, target_id, owasp_category, cwe_id, description, fix_description, code, lines, confidence)`
- (지표/요약/임베딩 등 보조 테이블 다수)

## 4) 동작 흐름

1. 설정 로드: `phase1/src/main.py`가 `config/config.yaml` 로드 (환경변수 치환 지원)
2. 파싱: Java/JSP/MyBatis/SQL 파서가 파일별 메타데이터/관계/SQL 요소 추출
3. 저장: `models.database.DatabaseManager` + `database.metadata_engine`가 DB에 저장 및 그래프 구축
4. 시각화: `visualize/cli.py`가 그래프/ERD/컴포넌트/클래스/시퀀스 데이터를 생성, HTML/CSV/MD로 내보냄
5. API(선택): `web-dashboard/backend/app.py`가 조회/내보내기/오프라인 문서 제공

## 4-1) 내부 주요 로직 개요

- Java/JSP/MyBatis 파서
  - Java: `javalang`으로 AST 구성 → 클래스/메소드/주석/어노테이션/상속·구현 관계 추출
  - JSP/MyBatis: 태그/속성 파싱 및 SQL 추출 → JOIN/WHERE 필수 필터 추정, include/fragment 연결
  - SQL: 문 유형/테이블/컬럼 참조/조건 추출 → 정규화 지문(normalized_fingerprint) 생성으로 비교 용이
- 메타데이터 엔진(`metadata_engine`)
  - 신규/변경 파일만 저장(해시/mtime 기반) → 관계(엣지) 생성 → 성능 인덱스 자동 생성
  - 엣지 예: include/call/extends/implements/use_table 등
- 시각화 Exporter
  - 노드/엣지 수 배수 제한, 라벨 길이 제한, 신뢰도 임계치 필터 → Mermaid/CSV/JSON 출력
  - 전략(full/balanced/minimal)로 가독성과 정보량 균형 조정

## 5) 설정(config)

- 환경변수 치환: `${VAR}` 형태를 `os.path.expandvars`로 치환 지원
- 주요 항목: `database`, `file_patterns`, `processing`, `logging`, `db_schema`, `llm`(선택)
- CORS/서버 포트: 백엔드는 `ALLOWED_ORIGINS`, `HOST`, `PORT`, `RELOAD` 환경변수 사용

## 6) 오프라인 설치 (상세)

오프라인 환경에서 설치가 가능하도록, 온라인 환경에서 준비 → 오프라인 설치 순으로 진행합니다.

- 사전 준비(온라인)
  
  - Python 3.10+ 설치
  - 의존성 휠 생성
    - `python -m venv .venv && .venv/Scripts/python -m pip install -U pip`
    - `.venv/Scripts/pip wheel -r requirements.txt -w wheelhouse/`
  - (선택) 백엔드 의존 포함 시: `fastapi`, `uvicorn`도 설치/휠 생성
  - (선택) 프런트엔드: 사전에 빌드한 정적 파일 패키지 준비(build 폴더)

- 오프라인 설치(운영)
  
  - `python -m venv .venv && .venv/Scripts/python -m pip install -U pip`
  - `.venv/Scripts/pip install --no-index --find-links wheelhouse -r requirements.txt`
  - (선택) 백엔드 실행: `HOST=0.0.0.0 PORT=8000 ALLOWED_ORIGINS=http://127.0.0.1:3000 .venv/Scripts/python web-dashboard/backend/app.py`
  - (선택) 프런트엔드: 사전 빌드된 정적 파일을 오프라인 웹서버(Nginx 등)에 배포하거나 백엔드로 프록시 설정

- DB 스키마 CSV(선택)
  
  - 경로: `PROJECT/<프로젝트명>/DB_SCHEMA/`
  - 최소 필요: `ALL_TABLES.csv`, `ALL_TAB_COLUMNS.csv`, `PK_INFO.csv`
  - `config.yaml`의 `db_schema.required_files`에 정의

- 오프라인 문서
  
  - `doc/owasp`, `doc/cwe` 내 Markdown 제공
  - 백엔드가 `/docs` 정적 서빙 및 `/api/docs/owasp/{code}`, `/api/docs/cwe/{code}`로 제공

## 7) 실행 방법

- CLI(시각화)
  - 의존 그래프: `python -m visualize.cli graph --project-id 1 --export-mermaid ./out/graph.md`
  - ERD: `python -m visualize.cli erd --project-id 1 --export-mermaid ./out/erd.md`
  - 컴포넌트/클래스/시퀀스도 동일 패턴의 옵션 제공
- 백엔드(API)
  - 실행: `python web-dashboard/backend/app.py`
  - 헬스체크: `GET /api/health`
  - 내보내기: `GET /api/export/classes.csv?project_id=1` 등
  - 파일 다운로드: `GET /api/file/download?path=/project/...`
  - 오프라인 문서: `GET /api/docs/owasp/A03`, `GET /api/docs/cwe/CWE-89`

## 8) 보안/폐쇄망 고려

- 외부 URL 고정 제거: CORS/서버/엔드포인트는 환경변수로 제어
- 문서 로컬 제공: 오프라인 취약점 문서 내장 및 API 제공
- 파일 경로: 리포 상대경로만 사용, 절대경로 하드코딩 금지

## 9) 트러블슈팅

- Python 인코딩/출력 깨짐
  - Windows: `chcp 65001`
  - POSIX: `export LANG=ko_KR.UTF-8`
- DB 파일 경로 권한 오류
  - `./data/` 쓰기 권한 확인, `config.yaml`의 SQLite 경로 점검
- 성능/메모리
  - `processing.max_workers`, `file_patterns` 조절로 입력량 관리

## 10) 부록: 환경변수 예시

- `HOST=0.0.0.0 PORT=8000 RELOAD=false ALLOWED_ORIGINS=http://127.0.0.1:3000`

---
