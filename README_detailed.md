# Source Analyzer (소스 분석기) - 상세 버전

## 1. 프로젝트 개요

Source Analyzer는 소스 코드의 메타정보를 추출하고 분석하여 시스템의 구조와 의존성을 이해하는 데 도움을 주는 다단계 분석 시스템입니다. 현재 1단계는 소스 코드로부터 핵심 메타정보를 생성하는 데 중점을 두고 있으며, 향후 LLM(Large Language Model)을 활용하여 분석 결과의 정확성과 깊이를 개선하는 것을 목표로 합니다.

### 주요 목표
*   소스 코드로부터 클래스, 메서드, SQL 구문, 파일 간 의존성 등 핵심 메타정보를 자동으로 추출합니다.
*   추출된 메타정보를 기반으로 시스템의 구조와 흐름을 시각적으로 표현합니다.
*   분석 결과의 신뢰도를 측정하고, 낮은 신뢰도의 경우 LLM을 활용하여 정확성을 개선하는 방안을 모색합니다.
*   증분 분석을 통해 대규모 프로젝트의 분석 효율성을 극대화합니다.

### 현재 단계 (Phase 1) 주요 기능 요약
*   **메타정보 생성**: Java, JSP/MyBatis, SQL 소스 코드로부터 구조적 메타정보 추출.
*   **다국어 파싱**: 다양한 언어 및 프레임워크에 대한 파싱 지원.
*   **신뢰도 계산**: 분석 결과에 대한 신뢰도 점수 부여.
*   **증분 분석**: 변경된 파일만 재분석하여 시간 단축.
*   **병렬 처리**: 다수의 파일을 동시에 분석하여 성능 향상.
*   **시각화**: 분석된 메타데이터를 다양한 다이어그램으로 시각화.

### 향후 계획 (Phase 2)
*   LLM 기반 메타데이터 및 분석 결과 강화.
*   벡터 스토어를 활용한 코드 검색 및 유사성 분석.
*   분석 결과를 제공하는 API 및 웹 UI 개발.

## 2. 주요 기능

### 2.1. 강력한 메타정보 추출 (Robust Metadata Extraction)
Source Analyzer의 핵심 기능은 다양한 소스 코드로부터 심층적인 메타정보를 추출하여 데이터베이스에 저장하는 것입니다. 이 메타정보는 시스템의 구조, 동작 방식, 그리고 잠재적 문제점을 파악하는 데 필수적인 기반이 됩니다.

*   **Java 코드 분석**: `javalang` (또는 `Tree-sitter`)를 통해 Java 소스 코드의 AST를 분석하여 다음 정보를 추출합니다.
    *   **클래스**: FQCN(Fully Qualified Class Name), 클래스명, 정의된 라인 범위, `public`, `private`, `static`, `abstract` 등의 **수식어**, `@Service`, `@Autowired`, `@Override` 등 **어노테이션** 정보. Java 파서는 `javalang.tree.ClassDeclaration` 노드를 분석하여 이 정보를 추출합니다.
    *   **메서드**: 메서드명, 상세 시그니처(파라미터 포함), 반환 타입, 정의된 라인 범위, **어노테이션** 정보. `javalang.tree.MethodDeclaration` 노드에서 추출됩니다.
    *   **관계**: 클래스 간 **상속(`extends`) 및 인터페이스 구현(`implements`) 관계**, 메서드 간 **호출 관계**.
*   **JSP/MyBatis XML 분석**: JSP 페이지 및 MyBatis XML 파일에서 SQL 구문과 관련된 정보를 추출합니다.
    *   **SQL 구문**: 원본 SQL 내용, 정규화된 **구조적 지문(`normalized_fingerprint`)** (동적 요소 및 리터럴을 플레이스홀더로 대체하여 생성), 라인 범위, `SELECT`, `INSERT`, `UPDATE`, `DELETE` 등의 **SQL 유형**, MyBatis 매퍼 네임스페이스 및 Statement ID.
    *   **조인 조건**: SQL 구문 내에서 발견된 **조인(`JOIN`) 조건** (좌/우 테이블 및 컬럼, 연산자), **추론된 PK-FK 관계(`inferred_pkfk`)** (빈번한 조인 패턴을 통해 추론).
    *   **필터 조건**: `WHERE` 절에서 사용되는 **필수 필터 조건** (테이블, 컬럼, 값, 연산자), **항상 적용되는 필터(`always_applied`)** 여부.
    *   **의존성**: JSP 파일 간의 `<jsp:include>` 및 `<%@ include %>` **포함 관계**, MyBatis XML 파일 내 `<include>` **SQL Fragment 참조 관계**.
    *   **취약점**: SQL Injection, XSS(Cross-Site Scripting) 등 **잠재적 보안 취약점** 패턴 탐지.
*   **일반 SQL 파일 분석**: 순수 SQL 파일에서 SQL 구문 유형, 조인 조건, 필터 조건, 사용 테이블 및 컬럼 정보를 추출합니다. Oracle PL/SQL의 경우 **프로시저, 함수, 패키지, 트리거, 커서** 등의 요소도 정규식 패턴을 통해 감지합니다.

### 2.2. 다국어 파싱 지원 (Multi-language Parsing Support)
Source Analyzer는 다양한 프로그래밍 언어 및 프레임워크의 소스 코드를 분석하기 위한 유연하고 확장 가능한 파싱 메커니즘을 제공합니다.

*   **Java 파싱**: `javalang` 라이브러리를 활용하여 Java 소스 코드의 **AST(Abstract Syntax Tree)**를 생성하고 분석합니다. **AST는 소스 코드의 구문 구조를 트리 형태로 표현한 것으로, 단순 텍스트 분석을 넘어 코드의 의미론적 관계를 파악하는 데 사용됩니다.** `javalang`은 Java 소스 코드를 토큰화하고 문법 규칙에 따라 `javalang.tree.CompilationUnit`, `ClassDeclaration`, `MethodDeclaration` 등의 노드로 구성된 AST를 생성합니다. 향후 `Tree-sitter`를 통합하여 파싱 성능과 정확도를 더욱 높이고 다양한 Java 버전을 지원할 예정입니다.
*   **JSP/MyBatis XML 파싱**: JSP 페이지의 HTML, CSS, JavaScript, 그리고 스크립틀릿(`<%...%>`) 구조를 `ANTLR` 기반의 문법 규칙에 따라 토큰화하고 파싱하여 구조적 요소를 식별합니다. MyBatis XML 파일의 경우 `lxml`을 사용하여 XML 구조를 견고하게 파싱하며, 내부에 포함된 SQL 구문은 `JSQLParser`를 활용하여 정밀하게 분석합니다. 특히 `AdvancedSqlExtractor` 모듈은 JSP 스크립틀릿 내의 Java 코드를 `Tree-sitter` Java 파서로 분석하여 SQL로 의심되는 문자열 리터럴이나 `StringBuilder.append()`와 같은 동적 SQL 구성 패턴을 AST 기반으로 식별합니다. 동적 SQL에 대해서는 **DFA(Deterministic Finite Automaton) 기반 최적화**를 수행합니다. 이는 `<if>`, `<choose>`, `<foreach>`와 같은 MyBatis 동적 태그가 포함된 SQL에서 발생할 수 있는 **조합 폭발(Combinatorial Explosion)** 문제를 해결하기 위해, 가능한 모든 SQL 실행 경로를 효율적으로 모델링하고 분석하여 실제 실행될 수 있는 SQL 패턴을 추론합니다.
*   **SQL 파싱**: 순수 SQL 파일 및 추출된 SQL 구문을 `JSQLParser` (Python 바인딩)가 분석하여 SQL의 주요 절(SELECT, FROM, WHERE, JOIN)을 정확하게 식별하고, 테이블, 컬럼, 조인 조건, 필터 조건 등을 추출합니다. `JSQLParser`는 SQL 구문을 구조화된 객체 모델로 변환하여, 단순 정규식으로는 어려운 복잡한 SQL 구문 분석을 가능하게 합니다. Oracle Dialect를 지원하여 `ROWNUM`, `DUAL` 테이블, PL/SQL 블록 등 복잡한 Oracle SQL 구문도 처리할 수 있습니다.

### 2.3. 분석 결과 신뢰도 측정 (Analysis Confidence Measurement)
`utils/confidence_calculator.py` 모듈은 각 분석 결과(파싱 성공 여부, 추출된 메타정보의 정확성, 관계 해결 여부 등)에 대해 0.0 ~ 1.0 범위의 신뢰도 점수를 계산합니다. 이 점수는 분석 결과의 품질을 나타내며, 낮은 신뢰도의 경우 LLM 기반의 추가 보강 프로세스를 트리거하는 기준으로 활용됩니다.

*   **`ParseResult` 데이터 클래스**: 파싱 성공 여부, 파서 유형, 파싱 시간, AST 완성도, 추출된 요소 수(클래스, 메서드, SQL 유닛), 매칭된 패턴, 참조된 DB 테이블 등 파싱 과정의 모든 상세 정보를 담아 신뢰도 계산의 입력으로 사용됩니다.
*   **AST 분석 품질 점수**: AST가 얼마나 완전하게 생성되었는지, 파싱 중 오류가 없었는지, 폴백 파서가 사용되었는지 등을 평가합니다. 예를 들어, 파싱된 `ClassDeclaration`이나 `MethodDeclaration` 노드의 수와 완전성, 그리고 파싱 중 발생한 오류 여부가 점수에 직접 반영됩니다. 완전한 AST는 높은 점수를, 부분적인 AST나 오류 발생 시에는 낮은 점수를 부여합니다.
*   **정적 규칙 매칭 점수**: 미리 정의된 코드 패턴(예: 특정 프레임워크 사용 패턴) 또는 정적 분석 규칙과의 일치율을 기반으로 점수를 부여합니다. 매칭률이 높을수록 신뢰도가 상승합니다.
*   **DB 스키마 매칭 점수**: 추출된 SQL 구문에서 참조하는 테이블이나 컬럼명이 `db_tables`, `db_columns` 테이블에 실제로 존재하는지 확인하여 신뢰도를 부여합니다. 예를 들어, `SELECT * FROM USERS`와 같은 SQL에서 `USERS` 테이블이 로드된 DB 스키마에 존재하면 해당 SQL 구문 분석의 신뢰도가 높아집니다.
*   **휴리스틱 점수**: 파일 확장자(예: `.java` 파일에서 Java 클래스가 발견되면 보너스), 사용된 파서의 종류(예: `Tree-sitter`는 `regex`보다 높은 점수), 코드 내 특정 키워드 존재 여부 등 경험적 규칙을 기반으로 점수를 보정합니다.
*   **복잡도 패널티**: 코드의 복잡도가 높을수록 분석의 불확실성이 증가하므로 감점 요인으로 작용합니다. 예를 들어, Java 코드에서 `Class.forName()`과 같은 **리플렉션** 사용이나 SQL에서 문자열 연결을 통한 **동적 SQL 구성**이 많을수록 분석의 불확실성이 커져 신뢰도 점수가 낮아집니다.

### 2.4. 증분 분석 및 효율성 (Incremental Analysis & Efficiency)
대규모 프로젝트의 분석 시간을 획기적으로 단축하고 리소스 사용을 최적화하기 위해 증분 분석 모드를 지원합니다.

*   **변경 감지 전략**: 데이터베이스의 `files` 테이블에 저장된 `hash` (SHA-256) 및 `mtime` (최종 수정 시간) 정보를 활용하여 파일 변경 여부를 판단하며, 파일 크기에 따라 가장 효율적인 변경 감지 전략을 동적으로 적용합니다.
    *   **소형 파일 (예: 50KB 미만)**: 파일 내용의 **SHA-256 해시**를 계산하여 데이터베이스에 저장된 이전 해시값과 비교합니다. 내용의 변경 여부를 가장 정확하게 판단할 수 있어 코드 무결성 검증에 적합합니다.
    *   **중대형 파일 (예: 10MB 미만)**: 파일의 최종 **수정 시간(mtime)**을 먼저 비교하여 변경 가능성이 있는 파일을 빠르게 식별합니다. mtime이 변경된 경우에만 SHA-256 해시를 재계산하여 정확성을 확보하면서도 불필요한 해시 계산 오버헤드를 줄입니다.
    *   **대형 파일 (예: 10MB 이상)**: 파일의 **mtime만을 기준**으로 변경 여부를 판단합니다. 대용량 파일의 해시 계산은 상당한 시간이 소요되므로, 분석 성능을 최우선으로 고려하여 mtime 기반의 빠른 판단을 수행합니다.
*   **삭제된 파일 처리**: 파일 시스템에서 더 이상 존재하지 않는 파일들의 메타데이터를 데이터베이스에서 자동으로 식별하고 정리하여 데이터의 일관성을 유지합니다.
*   **병렬 처리**: Python의 `asyncio`를 활용한 **비동기 I/O**와 **`asyncio.Semaphore`**를 사용하여 동시 실행되는 파일 파싱 태스크의 수를 제한합니다. 또한 `concurrent.futures.ThreadPoolExecutor`를 통해 CPU 바운드 작업(예: 파싱)을 병렬로 처리하여 전체 분석 시간을 단축합니다. `MetadataEngine`은 파일들을 배치(Batch) 단위로 나누어 병렬 워커에 할당함으로써 I/O 바운드 및 CPU 바운드 작업을 효율적으로 관리합니다.

### 2.5. 데이터베이스 스키마 연동 (Database Schema Integration)
Source Analyzer는 외부 데이터베이스의 스키마 정보를 분석 과정에 통합하여 코드 분석의 정확성과 깊이를 향상시킵니다. `DB_SCHEMA` 디렉토리에 위치한 CSV 파일들로부터 스키마 정보를 로드합니다.

*   **필수 파일**: `config.yaml`에 정의된 다음 CSV 파일들이 `DB_SCHEMA` 디렉토리에 존재해야 합니다.
    *   `ALL_TABLES.csv`: 테이블명, 소유자, 상태, 테이블 주석(`TABLE_COMMENT`) 등 DB 내 모든 테이블의 기본 정보를 제공하며, SQL 구문 분석 시 테이블명의 유효성 검증에 사용됩니다.
    *   `ALL_TAB_COLUMNS.csv`: 각 테이블의 컬럼명, 데이터 타입, Null 허용 여부 등 상세 컬럼 정보를 제공하며, SQL 구문 분석 시 컬럼명의 유효성 검증 및 ERD 생성에 활용됩니다.
    *   `ALL_TAB_COMMENTS.csv`: 테이블에 대한 상세 주석(`COMMENTS`)을 정의합니다.
    *   `ALL_COL_COMMENTS.csv`: 컬럼에 대한 상세 주석(`COMMENTS`)을 정의합니다.
    *   `PK_INFO.csv`: 각 테이블의 기본 키(Primary Key)를 구성하는 컬럼 정보와 해당 컬럼의 위치(`POSITION`)를 정의하며, 조인 관계 추론 및 ERD 생성 시 PK 컬럼 강조에 사용됩니다.
*   **활용**: SQL 구문 분석 시 추출된 테이블 및 컬럼명의 유효성을 로드된 스키마 정보와 비교하여 검증합니다. 이를 통해 SQL 구문 분석의 신뢰도를 높이고, ERD(Entity-Relationship Diagram) 생성 시 정확하고 상세한 스키마 정보를 기반으로 관계를 시각화합니다.

### 2.6. 시각화 기능 (Visualization Capabilities)
`visualize` 모듈은 `main.py`를 통해 분석된 메타데이터를 활용하여 다양한 형태의 다이어그램을 생성하고, 이를 웹 페이지 또는 Markdown 형식으로 내보냅니다. 생성된 다이어그램은 **노드 선택 시 상세 정보 패널 표시, 필터링, 다양한 레이아웃 옵션, 검색 기능 등 대화형 사용자 경험**을 제공합니다.

*   **의존성 그래프 (`graph`)**: `edges`, `files`, `classes`, `methods`, `sql_units`, `db_tables` 테이블의 데이터를 활용하여 파일, 클래스, 메서드, SQL 구문, 데이터베이스 테이블 간의 호출 및 사용 관계를 시각화합니다. 시스템의 전반적인 흐름과 모듈 간의 상호작용을 파악하는 데 유용합니다.
*   **ERD (Entity-Relationship Diagram, `erd`)**: `db_tables`, `db_columns`, `db_pk` 테이블의 데이터를 기반으로 데이터베이스 테이블 간의 관계를 시각화합니다. `SQLERD` 모드에서는 특정 SQL 구문에서 참조하는 테이블과 필수 필터 컬럼을 강조하여 보여줍니다.
*   **컴포넌트 다이어그램 (`component`)**: 프로젝트의 파일, 클래스, 메서드, SQL 유닛 등을 미리 정의된 규칙(`visualize/config/visualization_config.yaml`)에 따라 'Controller', 'Service', 'Repository', 'DB' 등의 논리적 컴포넌트 그룹으로 분류하고, 컴포넌트 간의 상호작용을 시각화합니다. 시스템의 고수준 아키텍처를 이해하는 데 적합합니다.
*   **시퀀스 다이어그램 (`sequence`)**: `edges` 테이블의 호출 관계 데이터를 활용하여 특정 시작 메서드 또는 파일로부터의 호출 흐름을 시퀀스 다이어그램으로 추적하여 시각화합니다. 복잡한 비즈니스 로직의 실행 경로를 이해하는 데 유용합니다.
*   **클래스 다이어그램 (`class`)**: Python 소스 코드의 클래스 구조, 멤버(속성, 메서드), 상속 관계를 시각화합니다. `visualize/builders/class_diagram.py`에서 `ast.NodeVisitor`를 상속받은 `ClassAnalyzer`를 통해 Python AST를 분석하여 정보를 추출하며, 클래스 계층 구조를 명확하게 보여줍니다.

### 6.1. 시각화 CLI (`python -m visualize.cli` 권장)
`python -m visualize.cli`(권장) 또는 `visualize_cli.py`를 통해 다양한 다이어그램을 생성할 수 있습니다.

```bash
python -m visualize.cli [명령] --project-id [ID] --out [출력_HTML_경로] [옵션]
```

**지원 명령 및 주요 옵션 상세:**

*   **`graph`**: **의존성 그래프 생성**
    *   **설명**: `edges`, `files`, `classes`, `methods`, `sql_units`, `db_tables` 테이블의 데이터를 활용하여 파일, 클래스, 메서드, SQL 구문, 데이터베이스 테이블 간의 호출 및 사용 관계를 시각화합니다. 시스템의 전반적인 흐름과 모듈 간의 상호작용을 파악하는 데 유용하며, 노드 선택, 필터링, 레이아웃 변경 등 **대화형 기능**을 제공합니다.
    *   `--kinds [종류1,종류2,...]` (기본값: `use_table,include,extends,implements`): 그래프에 포함할 엣지(관계)의 종류를 콤마로 구분하여 지정합니다. 예: `call,use_table`.
    *   `--focus [노드_이름/경로/테이블]` (선택적): 특정 노드(예: `UserService.java`, `UserMapper.selectUser`, `users` 테이블)를 중심으로 그래프를 생성합니다.
    *   `--depth [깊이]` (기본값: `2`): `--focus` 옵션 사용 시, 중심 노드로부터의 최대 탐색 깊이를 지정합니다.
    *   **예시**:
        ```bash
        # 프로젝트 ID 1번의 모든 호출 및 테이블 사용 관계를 포함하는 의존성 그래프 생성
        python -m visualize.cli graph --project-id 1 --out output/full_dependency_graph.html --kinds "call,use_table"

        # 'UserService.java' 파일을 중심으로 1단계 깊이의 의존성 그래프 생성
        python -m visualize.cli graph --project-id 1 --out output/user_service_deps.html --focus "UserService.java" --depth 1
        ```

*   **`erd`**: **ERD (Entity-Relationship Diagram) 생성**
    *   **설명**: `db_tables`, `db_columns`, `db_pk` 테이블의 데이터를 기반으로 데이터베이스 테이블 간의 관계를 시각화합니다. `SQLERD` 모드에서는 특정 SQL 구문에서 참조하는 테이블과 필수 필터 컬럼을 강조하여 보여줍니다.
    *   `--tables [테이블명1,테이블명2,...]` (선택적): ERD에 포함할 특정 테이블 목록을 콤마로 구분하여 지정합니다.
    *   `--owners [스키마명1,스키마명2,...]` (선택적): 특정 스키마(Owner)에 속하는 테이블만 포함합니다.
    *   `--from-sql [mapper_ns:stmt_id]` (선택적): 특정 SQL 구문(예: `com.example.UserMapper:selectUser`)에서 참조하는 테이블과 해당 SQL에서 사용되는 필수 필터 컬럼을 강조하여 ERD를 생성합니다 (SQLERD 모드).
    *   **예시**:
        ```bash
        # 프로젝트 ID 1번의 전체 ERD 생성
        python -m visualize.cli erd --project-id 1 --out output/full_erd.html

        # 'USERS', 'PRODUCTS' 테이블만 포함하는 ERD 생성
        python -m visualize.cli erd --project-id 1 --out output/user_product_erd.html --tables "USERS,PRODUCTS"

        # 'com.example.OrderMapper:selectOrderList' SQL 구문에서 참조하는 테이블과 필터를 강조한 ERD 생성
        python -m visualize.cli erd --project-id 1 --out output/order_sql_erd.html --from-sql "com.example.OrderMapper:selectOrderList"
        ```

*   **`component`**: **컴포넌트 다이어그램 생성**
    *   **설명**: 프로젝트의 파일, 클래스, 메서드, SQL 유닛 등을 미리 정의된 규칙(`visualize/config/visualization_config.yaml`)에 따라 'Controller', 'Service', 'Repository', 'DB' 등의 논리적 컴포넌트 그룹으로 분류하고, 컴포넌트 간의 상호작용을 시각화합니다. 시스템의 고수준 아키텍처를 이해하는 데 적합합니다.
    *   **예시**:
        ```bash
        # 프로젝트 ID 1번의 컴포넌트 다이어그램 생성
        python -m visualize.cli component --project-id 1 --out output/component_diagram.html
        ```

*   **`sequence`**: **시퀀스 다이어그램 생성**
    *   **설명**: `edges` 테이블의 호출 관계 데이터를 활용하여 특정 시작 메서드 또는 파일로부터의 호출 흐름을 시퀀스 다이어그램으로 추적하여 시각화합니다. 복잡한 비즈니스 로직의 실행 경로를 이해하는 데 유용합니다.
    *   `--start-file [파일_경로]` (선택적): 시퀀스 추적을 시작할 파일의 경로(부분 일치 가능)를 지정합니다.
    *   `--start-method [메서드_이름]` (선택적): `--start-file`과 함께 사용하여 특정 메서드로부터 시퀀스를 시작합니다.
    *   `--depth [깊이]` (기본값: `3`): 시작 노드로부터의 최대 추적 깊이를 지정합니다.
    *   **예시**:
        ```bash
        # 'UserService.java' 파일 내의 'createUser' 메서드로부터 시퀀스 다이어그램 생성
        python -m visualize.cli sequence --project-id 1 --out output/create_user_sequence.html --start-file "UserService.java" --start-method "createUser"

        # 시작 파일/메서드 미지정 시, JSP -> SQL -> Table의 기본 흐름 시퀀스 생성
        python -m visualize.cli sequence --project-id 1 --out output/default_jsp_sql_sequence.html
        ```

*   **`class`**: **클래스 다이어그램 생성 (Python 코드 전용)**
    *   **설명**: Python 소스 코드의 클래스 구조, 멤버(속성, 메서드), 상속 관계를 시각화합니다. `visualize/builders/class_diagram.py`에서 `ast.NodeVisitor`를 상속받은 `ClassAnalyzer`를 통해 Python AST를 분석하여 정보를 추출하며, 클래스 계층 구조를 명확하게 보여줍니다.
    *   `--modules [모듈명1,모듈명2,...]` (선택적): 다이어그램에 포함할 특정 Python 모듈 또는 파일 목록을 콤마로 구분하여 지정합니다.
    *   `--include-private` (플래그): 클래스의 private 멤버(예: `_private_method`, `__private_attr`)도 다이어그램에 포함합니다.
    *   `--max-methods [수]` (기본값: `10`): 각 클래스에 표시할 최대 메서드 수를 제한합니다.
    *   **예시**:
        ```bash
        # 프로젝트 ID 1번의 'main.py' 및 'utils' 모듈에 대한 클래스 다이어그램 생성
        python -m visualize.cli class --project-id 1 --out output/python_class_diagram.html --modules "main.py,utils"

        # 모든 private 멤버를 포함하여 클래스 다이어그램 생성
        python -m visualize.cli class --project-id 1 --out output/python_class_diagram_private.html --modules "my_module.py" --include-private
        ```

**공통 옵션:**
*   `--project-id [ID]` (필수): 분석된 프로젝트의 고유 ID. `main.py` 실행 후 출력되는 ID를 사용합니다.
*   `--out [경로]` (필수): 생성될 HTML 출력 파일의 경로. 예: `output/diagram.html`.
*   `--min-confidence [값]` (기본값: `0.5`): 그래프에 포함할 관계(엣지)의 최소 신뢰도 임계값. 이 값 미만의 신뢰도를 가진 엣지는 제외됩니다.
*   `--max-nodes [수]` (기본값: `2000`): 다이어그램에 표시할 최대 노드(파일, 클래스, 메서드 등) 수. 대규모 그래프의 성능 저하를 방지합니다.
*   `--export-json [경로]`: 생성된 다이어그램 데이터를 JSON 형식으로 지정된 파일 경로에 내보냅니다.
*   `--export-csv-dir [경로]`: 생성된 다이어그램의 노드 및 엣지 데이터를 CSV 형식으로 지정된 디렉토리에 내보냅니다 (`nodes.csv`, `edges.csv`).
*   `--export-mermaid [경로]`: 생성된 다이어그램을 Mermaid Markdown (`.md`) 또는 순수 Mermaid (`.mmd`) 형식으로 지정된 파일 경로에 내보냅니다.
    *   `--mermaid-label-max [길이]` (기본값: `20`): Mermaid 다이어그램에서 노드 라벨의 최대 길이를 제한합니다.
    *   `--mermaid-erd-max-cols [수]` (기본값: `10`): Mermaid ERD에서 각 테이블에 표시할 최대 컬럼 수를 제한합니다.
*   `--keep-edge-kinds [종류목록]` (기본값: `include,call,use_table`): 신뢰도 임계 미만이라도 반드시 유지할 엣지 종류.

> 주의: `PROJECT/` 폴더는 개발 소스가 아니라 테스트용 샘플 소스입니다. 실제 대상 소스 경로로 분석을 수행하세요.

### 6.3. DB 스키마 CSV 형식 (통합)
- `ALL_TABLES.csv`: OWNER, TABLE_NAME, COMMENTS (테이블 코멘트 통합)
- `ALL_TAB_COLUMNS.csv`: OWNER, TABLE_NAME, COLUMN_NAME, DATA_TYPE, NULLABLE, COLUMN_COMMENTS (컬럼 코멘트 통합)
- `PK_INFO.csv`: OWNER, TABLE_NAME, COLUMN_NAME, POSITION

별도의 `ALL_TAB_COMMENTS.csv`, `ALL_COL_COMMENTS.csv`는 필요 없습니다.
*   `-v`, `--verbose`, `-vv`: 로그 출력 상세도를 높입니다.
*   `-q`, `--quiet`: 로그 출력을 최소화합니다.
*   `--log-file [경로]`: 로그를 지정된 파일에 기록합니다.

### 6.2. 기술 스택
*   **프론트엔드 시각화**: Cytoscape.js (대화형 그래프 렌더링 라이브러리), Dagre (계층적 그래프 레이아웃 알고리즘).
*   **다이어그램 정의**: Mermaid (텍스트 기반 다이어그램 정의 언어, Markdown 내보내기용).
*   **템플릿 엔진**: Python 내장 기능 활용하여 HTML 템플릿(`visualize/templates/`)을 렌더링합니다.

## 7. 향후 계획 (Future Plans - Phase 2)

Source Analyzer는 지속적으로 발전할 예정이며, 다음 단계에서는 다음과 같은 기능들을 추가할 계획입니다.

*   **LLM 기반 메타데이터 강화**:
    *   **코드 요약 및 설명**: LLM을 활용하여 복잡한 코드 블록, 클래스, 메서드에 대한 자연어 요약 및 설명을 자동으로 생성합니다.
    *   **컨텍스트 기반 분석**: 주석, 변수명, 함수명 등 비정형적인 코드 정보를 LLM이 이해하고, 이를 메타데이터에 반영하여 분석의 깊이를 더합니다.
    *   **신뢰도 낮은 결과 보강**: 현재 시스템에서 신뢰도 점수가 낮은 분석 결과(예: 모호한 SQL 구문, 불확실한 의존성)에 대해 LLM이 추가적인 추론과 설명을 제공하여 정확성을 높입니다.
    *   **취약점 설명 및 수정 제안**: 탐지된 취약점에 대해 LLM이 상세한 설명과 함께 구체적인 수정 방안을 코드 스니펫 형태로 제안합니다.
*   **벡터 스토어 활용**:
    *   `BAAI/bge-m3` (다국어) 및 `jhgan00/ko-sentence-transformers` (한국어)와 같은 임베딩 모델을 사용하여 코드 청크를 벡터 공간에 임베딩합니다.
    *   `FAISS`와 같은 벡터 스토어를 이용하여 코드의 의미론적 유사성을 분석하고, 다음과 같은 기능을 제공합니다.
        *   **시맨틱 코드 검색**: 자연어 쿼리 또는 코드 스니펫을 통해 의미적으로 유사한 코드를 검색합니다.
        *   **중복 코드 탐지**: 유사한 기능을 수행하는 중복 코드를 효율적으로 탐지합니다.
        *   **코드 추천**: 특정 컨텍스트에 맞는 코드 스니펫이나 API 사용법을 추천합니다.
*   **API 및 웹 UI 제공**:
    *   `FastAPI`를 기반으로 분석 결과를 조회하고 시각화 다이어그램을 동적으로 생성할 수 있는 RESTful API를 제공합니다.
    *   이를 통해 외부 시스템(IDE, CI/CD 파이프라인)과의 연동을 용이하게 하고, 사용자 친화적인 웹 인터페이스를 구축하여 분석 결과를 직관적으로 탐색할 수 있도록 합니다.
*   **다양한 언어 파싱 확장**:
    *   `Tree-sitter`를 도입하여 Python, JavaScript, TypeScript, C#, Go 등 더 많은 프로그래밍 언어에 대한 파싱을 지원하고, 언어별 특성을 고려한 메타데이터 추출을 강화합니다.
*   **고급 취약점 분석**:
    *   `security` 모듈을 강화하여 OWASP Top 10과 같은 일반적인 웹 취약점 패턴(예: SQL Injection, XSS, Broken Access Control)을 소스 코드에서 더욱 정밀하게 탐지하고, 상세한 보고서와 함께 수정 가이드를 제공합니다.

## 8. 웹 대시보드: Export / 원본 열기 / 재분석 (Phase1 트리거)

- 백엔드 기동: `cd web-dashboard/backend && uvicorn app:app --reload`
- 프론트엔드 기동: `cd web-dashboard/frontend && npm install && npm run dev`

### 8.1 Export (CSV/TXT)
- `/api/export/classes.csv?project_id=1`
- `/api/export/methods.csv?project_id=1`
- `/api/export/sql.csv?project_id=1`
- `/api/export/edges.csv`

### 8.2 원본 파일 열기
- 다운로드: `/api/file/download?path=/project/<상대경로>` 또는 절대경로
- 정적 마운트: 서버 초기화 시 `PROJECT/`, `DB_SCHEMA/` 폴더가 존재하면 `/project`, `/dbschema`로 서비스됨

### 8.3 OWASP / CWE 문서 열기
- `/api/open/owasp/A03`
- `/api/open/owasp/CWE-89`

### 8.4 Phase1 재분석 트리거(변경 동기화)
- API:
```json
{
  "project_path": "PROJECT/sampleSrc",
  "project_name": "샘플",
  "incremental": true,
  "include_ext": ".java,.jsp,.xml",
  "include_dirs": "src/main/java,src/main/webapp"
}
```
- CLI:
```bash
python phase1/src/main.py PROJECT/sampleSrc --project-name 샘플 \
  --include-ext .java,.jsp,.xml --include-dirs src/main/java,src/main/webapp
```
