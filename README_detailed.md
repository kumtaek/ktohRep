# Source Analyzer - 상세 문서 (README_detailed)

본 문서는 Source Analyzer의 내부 구조, 데이터 모델, 상세 운영 방법, 오프라인 설치 절차 및 트러블슈팅을 자세히 설명합니다. 프로젝트의 간략한 개요 및 빠른 시작 가이드는 `README.md`를 참고하세요.

## 1) 개요

Source Analyzer는 Java, JSP, MyBatis, SQL 코드베이스를 대상으로 정적 분석을 수행하여 다양한 메타데이터를 추출하고 시각화하는 도구입니다. 폐쇄망(오프라인) 환경을 최우선으로 고려하여 설계되었으며, 다음과 같은 특징을 가집니다.

*   **대상 언어**: Java, JSP, MyBatis XML, SQL
*   **산출물**: 의존성 그래프, ERD, 컴포넌트 다이어그램, 클래스 다이어그램, 시퀀스 다이어그램. 이들은 HTML, JSON, CSV, Markdown(Mermaid) 형식으로 내보내기 가능합니다.
*   **운영 환경**: 모든 외부 네트워크 의존성을 제거하여 오프라인 환경에서 완벽하게 동작합니다.
*   **보안 분석**: 내장된 OWASP Top 10 및 CWE 취약점 문서를 활용하여 코드 내 잠재적 보안 취약점을 탐지하고 수정 가이드를 제공합니다.
*   **확장성**: 플러그인 가능한 파서 구조와 유연한 설정(`config.yaml`)을 통해 새로운 언어 및 분석 규칙 추가가 용이합니다.

## 2) 디렉터리 구조

프로젝트의 주요 디렉터리 구조는 다음과 같습니다.

```
E:\SourceAnalyzer.git\
├───phase1\
│   └───src\
│       ├───main.py                 # 메인 실행 스크립트, 분석 파이프라인 조정
│       ├───core\                   # 핵심 로직 (병렬 처리 등)
│       │   ├───db_comment_loader.py
│       │   └───parallel_processor.py
│       ├───database\               # 데이터베이스 관련 로직
│       │   ├───metadata_engine.py          # 메타데이터 저장 및 관계 구축 엔진
│       │   ├───metadata_engine_cleanup.py  # 삭제된 파일 메타데이터 정리
│       │   └───metadata_enhancement_engine.py # LLM 기반 메타데이터 보강 (선택)
│       ├───models\                 # SQLAlchemy ORM 모델 정의
│       │   └───database.py
│       ├───parsers\                # 언어별 파서
│       │   ├───java_parser.py              # Java 코드 파싱 (javalang/tree-sitter)
│       │   ├───jsp_mybatis_parser.py       # JSP/MyBatis XML 파싱
│       │   └───sql_parser.py               # 일반 SQL 구문 파싱
│       ├───security\               # 보안 취약점 탐지
│       │   └───vulnerability_detector.py   # SQL Injection, XSS 등 탐지
│       └───utils\                  # 공통 유틸리티
│           ├───confidence_calculator.py    # 분석 신뢰도 계산
│           ├───confidence_validator.py     # 신뢰도 검증 및 캘리브레이션
│           ├───csv_loader.py               # CSV 파일 로드
│           ├───large_file_processor.py     # 대용량 파일 처리
│           └───logger.py                   # 로깅 설정
├───visualize\
│   ├───cli.py                      # 시각화 CLI 엔트리 포인트
│   ├───data_access.py              # 시각화 데이터 접근 계층
│   ├───schema.py                   # 시각화 데이터 스키마
│   ├───builders\                   # 다이어그램별 데이터 빌더
│   │   ├───class_diagram.py
│   │   ├───component_diagram.py
│   │   ├───dependency_graph.py
│   │   ├───erd.py
│   │   └───sequence_diagram.py
│   ├───config\                     # 시각화 설정
│   │   └───visualization_config.yaml
│   ├───exporters\                  # 다양한 형식으로 내보내기
│   │   └───mermaid_exporter.py
│   └───templates\                  # HTML 템플릿
│       ├───class_view.html
│       ├───cyto_base.html
│       ├───erd_view.html
│       ├───graph_view.html
│       └───render.py
├───web-dashboard\
│   ├───backend\                    # FastAPI 기반 백엔드 API
│   │   └───app.py
│   └───frontend\                   # Vue.js 기반 프런트엔드 (사전 빌드 권장)
├───doc\                            # 오프라인 취약점 문서 (OWASP, CWE)
│   ├───cwe\
│   └───owasp\
├───config\
│   └───config.yaml                 # 전역 설정 파일
├───data\
│   └───metadata.db                 # SQLite 데이터베이스 파일
├───tests\                          # 테스트 코드
├───requirements.txt                # Python 의존성 목록
└───...
```

## 3) 데이터 모델 (핵심 테이블) 

분석된 메타데이터는 SQLite 데이터베이스(`data/metadata.db`)에 저장됩니다. 주요 엔티티는 다음과 같습니다.

*   `projects`: 분석된 프로젝트의 기본 정보 (`project_id`, `name`, `root_path`, `created_at`, `updated_at`)
*   `files`: 소스 파일 정보 (`file_id`, `project_id`, `path`, `language`, `hash`, `loc`, `mtime`)
*   `classes`: Java 클래스/인터페이스/Enum 정보 (`class_id`, `file_id`, `fqn`, `name`, `start_line`, `end_line`, `modifiers`, `annotations`)
*   `methods`: Java 메서드/생성자 정보 (`method_id`, `class_id`, `name`, `signature`, `return_type`, `start_line`, `end_line`, `annotations`, `parameters`, `modifiers`)
*   `sql_units`: SQL 구문 단위 (`sql_id`, `file_id`, `origin`, `mapper_ns`, `stmt_id`, `stmt_kind`, `start_line`, `end_line`, `normalized_fingerprint`)
*   `joins`: SQL 조인 조건 (`join_id`, `sql_id`, `l_table`, `l_col`, `r_table`, `r_col`, `join_type`, `condition_text`, `inferred_pkfk`, `confidence`)
*   `required_filters`: SQL 필수 필터 조건 (`filter_id`, `sql_id`, `table`, `column`, `op`, `value_repr`, `always_applied`, `confidence`)
*   `edges`: 파일/클래스/메서드/SQL 단위 간의 의존성 관계 (`edge_id`, `src_type`, `src_id`, `dst_type`, `dst_id`, `edge_kind`, `confidence`, `meta`)
*   `vulnerability_fixes`: 탐지된 취약점 및 수정 제안 (`fix_id`, `target_type`, `target_id`, `vulnerability_type`, `severity`, `owasp_category`, `cwe_id`, `description`, `original_code`, `start_line`, `confidence`)
*   `db_tables`, `db_columns`, `db_pks`, `db_views`: 외부 DB 스키마 정보 (CSV 로드)
*   `enrichment_logs`: LLM 기반 보강 작업 로그
*   `summaries`: 프로젝트 요약 통계

## 4) 동작 흐름 및 내부 주요 로직

Source Analyzer의 핵심 동작은 `phase1/src/main.py`에서 시작되며, 다음 단계를 거쳐 메타데이터를 추출하고 저장합니다.

1.  **설정 로드**: `phase1/src/main.py`는 `config/config.yaml` 파일을 로드합니다. 이 설정 파일은 파일 패턴, 데이터베이스 연결, 로깅 수준, 병렬 처리 설정, 신뢰도 계산 가중치 등을 정의하며, `${VAR}` 형태의 환경변수 치환을 지원합니다.
2.  **초기화**: `SourceAnalyzer` 클래스는 `DatabaseManager`, 언어별 파서(`JavaParser`, `JspMybatisParser`, `SqlParser`), `MetadataEngine`, `ConfidenceCalculator`, `ConfidenceValidator` 등을 초기화합니다. 시스템 시작 시 `Confidence formula`의 유효성을 검증하고 필요시 자동 캘리브레이션을 시도합니다.
3.  **소스 파일 수집**: `_collect_source_files` 메서드는 `config.yaml`에 정의된 `file_patterns.include` 및 `exclude` 규칙에 따라 프로젝트 루트 디렉토리에서 분석 대상 소스 파일들을 재귀적으로 수집합니다.
4.  **증분 분석 (선택)**: `--incremental` 플래그가 주어지면, `_filter_changed_files` 메서드는 파일의 해시 및 수정 시간(mtime)을 기반으로 변경되거나 새로 추가된 파일만 선별하여 분석 효율을 높입니다. 삭제된 파일의 메타데이터는 `metadata_engine.cleanup_deleted_files`를 통해 정리됩니다.
5.  **파일 분석 (병렬 처리)**: `_analyze_files` 메서드는 수집된 소스 파일들을 `asyncio.Semaphore`와 `concurrent.futures.ThreadPoolExecutor`를 활용하여 병렬로 분석합니다. 각 파일은 해당 언어 파서에 의해 처리됩니다.
    *   **Java 파서 (`phase1/src/parsers/java_parser.py`)**:
        *   `javalang` 또는 `tree-sitter` 라이브러리를 사용하여 Java 소스 코드를 AST(Abstract Syntax Tree)로 파싱합니다.
        *   클래스, 인터페이스, Enum 선언을 추출하고, 각 선언의 FQN(Fully Qualified Name), 이름, 라인 번호, 수식어, 어노테이션 정보를 `classes` 테이블에 저장합니다.
        *   각 클래스/인터페이스 내의 메서드 및 생성자를 추출하여 이름, 시그니처, 반환 타입, 라인 번호, 어노테이션 정보를 `methods` 테이블에 저장합니다.
        *   클래스 상속(`extends`), 인터페이스 구현(`implements`) 관계를 `edges` 테이블에 저장합니다.
        *   메서드 본문 내에서 다른 메서드 호출을 탐지하여 `call` 타입의 엣지를 생성합니다. 호출 대상 메서드는 `MetadataEngine`에서 후처리로 해결됩니다.
    *   **JSP/MyBatis 파서 (`phase1/src/parsers/jsp_mybatis_parser.py`)**:
        *   JSP 파일에서 `<% ... %>`, `<%= ... %>`, `${ ... }` 등의 스크립틀릿 및 EL 표현식을 파싱합니다.
        *   MyBatis XML 파일에서 `<select>`, `<insert>`, `<update>`, `<delete>` 등의 SQL 매퍼 구문을 추출합니다.
        *   추출된 SQL 구문에서 사용되는 테이블, 컬럼, 조인 조건, 필수 필터 등을 분석하여 `sql_units`, `joins`, `required_filters` 테이블에 저장합니다.
        *   파일 간의 `include` 관계 및 SQL 구문과 테이블 간의 `use_table` 관계를 `edges` 테이블에 저장합니다.
        *   `phase1/src/security/vulnerability_detector.py`를 사용하여 SQL Injection 및 XSS 취약점을 탐지하고 `vulnerability_fixes` 테이블에 저장합니다.
6.  **메타데이터 저장 및 그래프 구축 (`phase1/src/database/metadata_engine.py`)**:
    *   `MetadataEngine`은 파서로부터 전달받은 `File`, `Class`, `Method`, `SqlUnit`, `Join`, `RequiredFilter`, `Edge`, `VulnerabilityFix` 객체들을 데이터베이스에 저장합니다.
    *   **의존성 그래프 구축**: `build_dependency_graph` 메서드는 다음을 수행합니다.
        *   **메서드 호출 관계 해결**: `_resolve_method_calls`는 파싱 단계에서 `dst_id`가 `None`으로 저장된 `call` 엣지들을 대상으로, 동일 클래스 또는 프로젝트 내의 다른 클래스/메서드를 검색하여 호출 대상 메서드를 찾아 `dst_id`를 업데이트합니다. 해결된 엣지의 신뢰도는 증가하고, 미해결 엣지는 감소합니다.
        *   **테이블 사용 관계 해결**: `_resolve_table_usage`는 SQL 구문에서 추출된 테이블 이름과 외부 DB 스키마 정보(`db_tables`)를 매칭하여 `sql_unit`과 `table` 간의 `use_table` 엣지를 생성합니다. `config.yaml`의 `database.default_schema`를 활용한 스키마 우선 검색 및 전역 검색 로직을 포함합니다.
        *   **PK-FK 관계 추론**: `_infer_pk_fk_relationships`는 SQL 조인 조건의 패턴을 분석하여 빈번하게 나타나는 조인 패턴을 PK-FK 관계로 추론하고 `joins` 테이블의 `inferred_pkfk` 플래그를 설정합니다.
7.  **분석 결과 요약**: `_generate_analysis_summary` 메서드는 분석된 파일 수, 클래스/메서드/SQL 구문 수, 언어별 분포, 의존성 통계 등 프로젝트 전반에 대한 요약 정보를 생성합니다.

## 5) 시각화 (`visualize/cli.py`)

`visualize/cli.py`는 분석된 메타데이터를 기반으로 다양한 다이어그램을 생성하고 내보내는 CLI 도구입니다.

*   **다이어그램 종류**: `graph` (의존성 그래프), `erd` (ERD), `component` (컴포넌트 다이어그램), `sequence` (시퀀스 다이어그램), `class` (클래스 다이어그램).
*   **데이터 빌더**: `visualize/builders` 디렉토리의 모듈들이 각 다이어그램 유형에 맞는 데이터를 데이터베이스에서 조회하고 가공합니다.
*   **내보내기 형식**: HTML, JSON, CSV, Mermaid/Markdown을 지원합니다.
    *   `MermaidExporter` (`visualize/exporters/mermaid_exporter.py`)는 다이어그램 데이터를 Mermaid 문법으로 변환하여 Markdown 파일에 포함하거나 `.mmd` 파일로 직접 내보냅니다.
    *   `render_html` (`visualize/templates/render.py`)는 `visualize/templates`의 HTML 템플릿을 사용하여 대화형 시각화 HTML 파일을 생성합니다.
*   **옵션**: `project-id`, `min-confidence`, `max-nodes`, `export-strategy` (full/balanced/minimal), `mermaid-label-max`, `keep-edge-kinds` 등 다양한 필터링 및 출력 옵션을 제공합니다.

## 6) 보안 취약점 탐지 (`phase1/src/security/vulnerability_detector.py`)

이 모듈은 코드 내 잠재적 보안 취약점을 정적으로 탐지합니다.

*   **탐지 유형**: `SQL_INJECTION` (JSP, MyBatis XML), `XSS` (JSP).
*   **패턴 기반 탐지**: 정규 표현식(`re` 모듈)을 사용하여 JSP 및 MyBatis XML 코드에서 SQL Injection 및 XSS 패턴을 식별합니다.
    *   **SQL Injection**: `StringBuilder.append`, 문자열 직접 결합, EL 표현식, MyBatis `${}` 치환, `ORDER BY` 절의 동적 컬럼, 동적 테이블명 지정 등의 패턴을 탐지합니다.
    *   **XSS**: JSP 출력 표현식(`<%= %>`), EL 표현식(`${}`), JavaScript 내 서버 데이터 직접 삽입 등의 패턴을 탐지합니다.
*   **심각도 분류**: 탐지된 취약점에 대해 `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO` 등의 심각도를 부여합니다.
*   **수정 제안 및 참조**: 각 취약점에 대한 수정 제안(`fix_suggestion`)과 OWASP, CWE 등의 참조 URL을 제공합니다.
*   **보고서 생성**: 탐지된 취약점들을 요약하고 상세 정보를 포함하는 보고서를 생성하며, SARIF(Static Analysis Results Interchange Format) 형식으로 내보내기 기능을 지원합니다.
*   **중복 제거**: 동일 파일, 라인 번호, 취약점 유형을 기준으로 중복 취약점을 제거하여 보고서의 정확성을 높입니다.

## 7) 설정 (`config/config.yaml`)

`config.yaml`은 Source Analyzer의 전역 설정을 정의합니다. 환경변수 치환(`${VAR}`)을 지원하여 유연한 배포가 가능합니다.

*   **`database`**: SQLite 파일 경로, 기본 스키마 등 DB 관련 설정.
*   **`file_patterns`**: 분석 대상 파일의 `include` 및 `exclude` 패턴 (glob 형식).
*   **`processing`**: 병렬 처리 워커 수(`max_workers`), 배치 크기(`batch_size`), 파일 변경 감지 임계값(`size_threshold_hash`, `size_threshold_mtime`), 신뢰도 임계값(`confidence_threshold`).
*   **`logging`**: 로깅 레벨(`level`), 로그 파일 경로(`file`).
*   **`confidence`**: 신뢰도 계산 가중치 (`ast`, `static`, `db_match`, `heuristic`).
*   **`db_schema`**: 외부 DB 스키마 CSV 파일 경로 및 필수 파일 목록.
*   **`parsers`**: 각 파서의 활성화 여부 및 특정 파서 설정 (예: Java 파서의 `parser_type`으로 `javalang` 또는 `tree-sitter` 선택).
*   **`security`**: SQL Injection 및 XSS 탐지 활성화 여부.
*   **`llm` (선택)**: LLM 연동 관련 설정 (활성화 시).

웹 대시보드 백엔드는 `ALLOWED_ORIGINS`, `HOST`, `PORT`, `RELOAD` 환경변수를 통해 CORS, 서버 바인딩 주소, 포트, 자동 리로드 여부 등을 제어합니다.

## 8) 오프라인 설치 (상세)

`README.md`의 간략한 오프라인 설치 가이드에 더하여, 다음은 각 단계에 대한 상세 설명과 고려사항입니다.

### 8.1. 사전 준비 (온라인 환경)

1.  **Python 3.10+ 설치**: 운영체제에 맞는 Python 3.10 이상 버전을 설치합니다. `PATH` 환경변수에 Python이 추가되었는지 확인합니다.
2.  **가상 환경 생성 및 pip 업그레이드**: 프로젝트 루트 디렉토리에서 가상 환경을 생성하고 `pip`를 최신 버전으로 업데이트합니다. 이는 시스템 전역 Python 환경과의 충돌을 방지하고 의존성을 격리합니다.
    ```bash
    python -m venv .venv
    .venv/Scripts/python -m pip install -U pip
    ```
3.  **의존성 휠(Wheel) 파일 생성**: `requirements.txt`에 명시된 모든 Python 패키지의 휠 파일을 다운로드하여 오프라인 설치를 위한 로컬 저장소(`wheelhouse/`)를 만듭니다. 이 과정에서 모든 전이 의존성(transitive dependencies)까지 함께 다운로드됩니다.
    ```bash
    .venv/Scripts/pip wheel -r requirements.txt -w wheelhouse/
    ```
    *   **주의**: `requirements.txt`에는 `fastapi`와 `uvicorn` 등 웹 대시보드 관련 의존성도 포함되어 있어야 합니다. 만약 `tree-sitter` 기반 파서를 사용한다면 `tree_sitter_java`와 같은 언어 바인딩 패키지도 포함되어야 합니다.
4.  **(선택) 웹 대시보드 프런트엔드 빌드**: `web-dashboard/frontend` 디렉토리로 이동하여 Node.js 및 npm/yarn을 사용하여 프런트엔드 애플리케이션을 빌드합니다. 빌드 결과물(`dist` 폴더)은 오프라인 환경에서 정적 파일로 서빙됩니다.
    ```bash
    cd web-dashboard/frontend
    npm install # 또는 yarn install
    npm run build # 또는 yarn build
    cd ../..
    ```
    *   빌드된 `dist` 폴더를 오프라인 환경으로 전송할 준비를 합니다.

### 8.2. 오프라인 설치 (운영 환경)

1.  **파일 전송**: 온라인 환경에서 준비한 `SourceAnalyzer.git` 프로젝트 폴더 전체, `wheelhouse/` 디렉토리, 그리고 선택적으로 `web-dashboard/frontend/dist` 폴더를 오프라인 서버 또는 PC로 전송합니다.
2.  **가상 환경 생성 및 pip 업그레이드**: 오프라인 환경에서 프로젝트 루트 디렉토리로 이동하여 가상 환경을 생성하고 `pip`를 업그레이드합니다.
    ```bash
    python -m venv .venv
    .venv/Scripts/python -m pip install -U pip
    ```
3.  **오프라인 의존성 설치**: `wheelhouse/` 디렉토리를 `pip`의 로컬 패키지 소스로 지정하여 의존성을 설치합니다. `--no-index` 옵션은 PyPI와 같은 외부 인덱스 서버에 접근하지 않도록 합니다.
    ```bash
    .venv/Scripts/pip install --no-index --find-links wheelhouse -r requirements.txt
    ```
4.  **(선택) 웹 대시보드 백엔드 실행**: 백엔드 서버를 실행합니다. `HOST`, `PORT`, `ALLOWED_ORIGINS`, `RELOAD` 환경변수를 적절히 설정해야 합니다. `ALLOWED_ORIGINS`는 프런트엔드가 배포될 도메인을 지정합니다.
    ```bash
    # 예시: 모든 IP에서 8000번 포트로 서비스, 로컬 프런트엔드 허용
    HOST=0.0.0.0 PORT=8000 ALLOWED_ORIGINS=http://127.0.0.1:3000 .venv/Scripts/python web-dashboard/backend/app.py
    ```
5.  **(선택) 웹 대시보드 프런트엔드 배포**: 사전 빌드된 `dist` 폴더의 정적 파일들을 오프라인 웹 서버(예: Nginx, Apache)에 배포하거나, 백엔드 `app.py`에서 정적 파일을 서빙하도록 설정합니다. (현재 `app.py`는 정적 파일 서빙 기능을 포함하고 있지 않으므로, 별도의 웹 서버 사용을 권장합니다.)

### 8.3. DB 스키마 CSV (선택)

외부 데이터베이스의 스키마 정보를 활용하여 ERD 생성 및 SQL 구문 분석의 정확도를 높일 수 있습니다. `PROJECT/<프로젝트명>/DB_SCHEMA/` 경로에 다음 CSV 파일들을 배치합니다.

*   `ALL_TABLES.csv`: 모든 테이블 목록 (필수)
*   `ALL_TAB_COLUMNS.csv`: 모든 테이블의 컬럼 목록 (필수)
*   `PK_INFO.csv`: 기본 키(Primary Key) 정보 (필수)

이 파일들은 `config.yaml`의 `db_schema.required_files`에 정의되어 있으며, `phase1/src/main.py`의 `_load_db_schema` 메서드에 의해 로드됩니다.

### 8.4. 오프라인 문서

`doc/owasp` 및 `doc/cwe` 디렉토리에는 OWASP Top 10 및 CWE 취약점에 대한 Markdown 문서가 내장되어 있으며, 웹 대시보드 백엔드를 통해 `/docs` 경로로 정적 서빙됩니다. 또한 `/api/docs/owasp/{code}` 및 `/api/docs/cwe/{code}` API 엔드포인트를 통해 프로그램적으로 접근할 수 있습니다.

## 9) 실행 방법

### 9.1. CLI (분석 및 시각화)

*   **프로젝트 분석**: `phase1/src/main.py`를 실행하여 소스 코드를 분석하고 메타데이터를 데이터베이스에 저장합니다.
    ```bash
    # 기본 분석
    python phase1/src/main.py PROJECT/sampleSrc
    # 프로젝트 이름 지정
    python phase1/src/main.py PROJECT/sampleSrc --project-name "My Application"
    # 증분 분석 (변경된 파일만)
    python phase1/src/main.py PROJECT/sampleSrc --incremental
    # 특정 확장자만 포함
    python phase1/src/main.py PROJECT/sampleSrc --include-ext .java,.jsp
    # 특정 디렉토리만 포함
    python phase1/src/main.py PROJECT/sampleSrc --include-dirs src/main/java
    # 상세 로그 출력
    python phase1/src/main.py PROJECT/sampleSrc -v
    ```
*   **시각화 생성**: `visualize/cli.py`를 실행하여 다양한 다이어그램을 생성하고 내보냅니다.
    ```bash
    # 의존성 그래프 (Mermaid Markdown)
    python visualize/cli.py graph --project-name sampleSrc --export-mermaid ./out/dependency_graph.md
    # ERD (HTML)
    python visualize/cli.py erd --project-name sampleSrc --export-html ./out/erd.html
    # 클래스 다이어그램 (JSON)
    python visualize/cli.py class --project-name sampleSrc --modules com.example.MyClass --export-json ./out/my_class_diagram.json
    # 시퀀스 다이어그램 (특정 파일/메서드 시작, 깊이 2)
    python visualize/cli.py sequence --project-name sampleSrc --start-file src/main/java/com/example/Service.java --start-method processRequest --depth 2 --export-html ./out/sequence.html
    ```

### 9.2. 백엔드 (API)

`web-dashboard/backend/app.py`를 실행하여 웹 대시보드 백엔드 API를 시작합니다.

```bash
python web-dashboard/backend/app.py
```

주요 API 엔드포인트:

*   **헬스체크**: `GET /api/health`
*   **데이터 내보내기**: `GET /api/export/classes.csv?project_id=1`, `GET /api/export/sql_units.json?project_id=1` 등
*   **파일 다운로드**: `GET /api/file/download?path=/project/...
*   **오프라인 문서**: `GET /api/docs/owasp/A03`, `GET /api/docs/cwe/CWE-89`

## 10) 보안/폐쇄망 고려사항

*   **외부 URL 고정 제거**: 모든 외부 URL 및 서비스 엔드포인트는 `config.yaml` 또는 환경변수를 통해 제어됩니다. CORS 설정(`ALLOWED_ORIGINS`)도 환경변수로 관리됩니다.
*   **문서 로컬 제공**: OWASP 및 CWE 취약점 문서는 프로젝트 내부에 내장되어 있으며, 웹 대시보드 백엔드를 통해 오프라인으로 제공됩니다.
*   **파일 경로 관리**: 코드 내에서 절대 경로 하드코딩을 지양하고, 프로젝트 루트를 기준으로 한 상대 경로만 사용합니다. 이는 다양한 환경에서의 이식성을 보장합니다.
*   **민감 정보 처리**: 데이터베이스 연결 정보 등 민감한 설정은 환경변수(`os.path.expandvars`)를 통해 관리하며, 코드에 직접 노출되지 않도록 합니다.

## 11) 트러블슈팅

*   **Python 인코딩/출력 깨짐**: 터미널에서 한글이 깨져 보일 경우 다음 명령을 실행합니다.
    *   Windows: `chcp 65001`
    *   Linux/macOS: `export LANG=ko_KR.UTF-8`
*   **DB 파일 경로 권한 오류**: `data/metadata.db` 파일에 대한 쓰기 권한이 없거나, `config.yaml`에 지정된 SQLite 데이터베이스 경로가 올바르지 않을 수 있습니다. 권한을 확인하고 경로를 점검하세요.
*   **성능/메모리 문제**: 대규모 프로젝트 분석 시 성능 저하 또는 메모리 부족이 발생할 수 있습니다.
    *   `config.yaml`의 `processing.max_workers` (병렬 처리 워커 수)를 조절하여 시스템 리소스에 맞게 최적화합니다.
    *   `file_patterns` 설정을 통해 분석 대상 파일의 범위를 좁히거나, `phase1/src/main.py`의 `--incremental` 옵션을 사용하여 증분 분석을 수행합니다.
*   **파싱 오류**: 특정 소스 파일에서 파싱 오류가 발생할 경우, 해당 파일의 문법 오류를 확인하거나 `config.yaml`에서 해당 파서의 설정을 점검합니다. `phase1/src/main.py` 실행 시 `-v` 옵션을 사용하여 상세 로그를 확인하면 문제 해결에 도움이 됩니다.
*   **시각화 결과 누락/불완전**: `visualize/cli.py` 실행 시 `--min-confidence` (최소 신뢰도 임계값) 또는 `--max-nodes` (최대 노드 수) 옵션이 너무 제한적으로 설정되었을 수 있습니다. 이 값들을 조정하여 더 많은 데이터를 포함하도록 시도해 보세요.

## 12) 부록: 환경변수 예시

```bash
# 웹 대시보드 백엔드 실행 시 사용되는 환경변수 예시
HOST=0.0.0.0
PORT=8000
RELOAD=false
ALLOWED_ORIGINS=http://127.0.0.1:3000,http://localhost:3000

# 데이터베이스 경로를 환경변수로 지정하는 예시 (config.yaml에서 ${DB_PATH}로 참조)
DB_PATH=/app/data/analyzer.db
```