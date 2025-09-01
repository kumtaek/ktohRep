# 소스 분석 로직 및 LLM 활용 방안 상세 보고서

이 문서는 SourceAnalyzer 프로젝트의 핵심 기능인 소스 코드 분석 로직과 대규모 언어 모델(LLM) 활용 방안에 대해 상세히 설명합니다.

---

## 1. 파싱 방법 및 로직

SourceAnalyzer는 다양한 유형의 소스 코드를 분석하기 위해 여러 파서를 사용하며, 정규식 기반과 AST(추상 구문 트리) 기반의 접근 방식을 혼합하여 사용합니다. 특히, 복잡한 언어 구조와 동적 SQL 처리를 위해 AST 기반 파싱과 고급 정규식 패턴을 활용합니다.

### 1.1. JavaParser (Java 소스 코드)

*   **주요 기능**: Java 파일에서 클래스, 인터페이스, 열거형, 메서드, 생성자 및 이들 간의 상속/구현/호출 관계를 추출합니다.
*   **사용 라이브러리**:
    *   `javalang`: Java 소스 코드를 파싱하여 AST를 생성하는 데 사용됩니다.
    *   `tree-sitter` (옵션): `javalang`의 한계를 보완하기 위해 더 정확한 AST 파싱을 제공합니다. `tree-sitter-java`를 통해 Java 언어 문법을 지원합니다.
*   **파싱 로직**:
    *   파일 내용을 읽어 `javalang.parse.parse()` 또는 `tree-sitter` 파서를 통해 AST를 생성합니다.
    *   AST를 순회하며 `ClassDeclaration`, `InterfaceDeclaration`, `EnumDeclaration`, `MethodDeclaration`, `ConstructorDeclaration` 노드를 식별합니다.
    *   각 노드에서 이름, FQN(Fully Qualified Name), 시작/종료 라인, 수식어(modifiers), 어노테이션(annotations) 등의 메타데이터를 추출합니다.
    *   메서드 본문 내에서 다른 메서드 호출을 탐지하여 호출 관계(Edge)를 생성합니다. 이때 심볼 테이블을 활용하여 변수 타입과 호출 대상의 자격(qualifier)을 추론합니다.
    *   상속(`extends`) 및 구현(`implements`) 관계도 추출하여 Edge로 기록합니다.
*   **특징**: `javalang`은 라인 번호 추정에 한계가 있어 `tree-sitter`를 통해 더 정확한 위치 정보를 얻으려 시도합니다.

### 1.2. SqlParser (일반 SQL 구문)

*   **주요 기능**: SQL 구문에서 테이블, 컬럼, 조인 조건, WHERE 절의 필터 조건을 추출합니다. Oracle PL/SQL 특수 요소(프로시저, 함수, 패키지 등)도 감지합니다.
*   **사용 라이브러리**:
    *   `jsqlparser` (옵션): Python 바인딩이 있다면 더 정확한 SQL 파싱을 위해 우선적으로 사용됩니다.
    *   `re` (정규식): `jsqlparser`를 사용할 수 없거나 특정 패턴 추출에 더 효율적일 때 사용되는 폴백(fallback) 메커니즘입니다.
*   **파싱 로직**:
    *   SQL 구문을 정규화(주석 제거, 공백 통일, Oracle 힌트 제거 등)합니다.
    *   `FROM`, `JOIN`, `UPDATE`, `INSERT INTO` 절에서 테이블 이름을 추출합니다.
    *   `테이블명.컬럼명` 형태의 컬럼 참조를 추출합니다.
    *   `ON` 절이나 `WHERE` 절의 `테이블1.컬럼1 = 테이블2.컬럼2` 형태에서 조인 조건을 추출합니다.
    *   `WHERE` 절에서 `컬럼명 = 값` 형태의 필터 조건을 추출하고, 동적 조건 여부를 판단합니다.
    *   Oracle PL/SQL 키워드(PROCEDURE, FUNCTION 등)를 사용하여 PL/SQL 요소를 감지합니다.
*   **특징**: `jsqlparser`가 설치되어 있지 않거나 파싱에 실패할 경우, 정규식 기반의 견고한 폴백 로직을 통해 분석을 시도합니다.

### 1.3. JspMybatisParser (JSP 및 MyBatis XML)

*   **주요 기능**: JSP 파일에서 SQL 구문 및 `include` 의존성을, MyBatis XML 파일에서 SQL 유닛, 조인, 필터, 동적 SQL 구조를 추출합니다. SQL Injection 및 XSS 취약점 탐지 기능도 포함합니다.
*   **사용 라이브러리**:
    *   `lxml`: XML 파싱 및 XPath 쿼리를 통해 MyBatis XML 구조를 정확하게 탐색하고 위치 정보를 추출합니다.
    *   `sqlparse`: SQL 구문을 토큰화하고 구조화하여 조인 및 필터 조건을 더 정확하게 추출합니다.
    *   `re` (정규식): JSP 스크립틀릿 내 SQL 패턴, JSTL 태그, 동적 SQL 패턴 등을 탐지하는 데 사용됩니다.
    *   `tree-sitter` (옵션): JSP 스크립틀릿 내 Java 코드에서 SQL을 추출하거나 XML 구조를 파싱하는 데 활용됩니다. `tree-sitter-java`, `tree-sitter-xml`을 사용합니다.
*   **파싱 로직**:
    *   **JSP 파싱**:
        *   JSP 스크립틀릿(`<%...%>`), 표현식(`<%=...%>`), 선언(`<%!...%>`), JSTL SQL 태그(`sql:query`, `sql:update`)에서 SQL 구문을 추출합니다.
        *   `tree-sitter` Java 파서를 사용하여 스크립틀릿 내 Java 코드에서 SQL 문자열 리터럴이나 동적 SQL 빌딩 패턴을 탐지합니다.
        *   `<jsp:include>` 태그 및 `<%@ include%>` 지시어를 분석하여 JSP 파일 간의 의존성(Edge)을 추적합니다.
    *   **MyBatis XML 파싱**:
        *   `lxml`을 사용하여 XML 파일을 파싱하고 `namespace`를 추출합니다.
        *   `<select>`, `<insert>`, `<update>`, `<delete>`, `<sql>` 태그 내의 SQL 유닛을 식별합니다.
        *   `DynamicSqlResolver`를 사용하여 `<include>`, `<bind>`, `<choose>`, `<foreach>`, `<if>`, `<trim>`, `<where>`, `<set>`과 같은 MyBatis 동적 태그를 해석하고 SQL 내용을 정규화합니다. 특히 `DFA 기반 동적 SQL 최적화`를 통해 조합 폭발 문제를 해결하고 대표 분기만 전개하여 분석합니다.
        *   `sqlparse`를 활용하여 정규화된 SQL에서 조인 및 필터 조건을 추출합니다.
        *   `<include>` 태그를 통해 SQL 프래그먼트 간의 의존성(Edge)을 추적합니다.
    *   **보안 취약점 탐지**: `SqlInjectionDetector`와 `XssDetector`를 사용하여 JSP 및 MyBatis XML 파일에서 잠재적인 SQL Injection 및 XSS 취약점을 탐지합니다.
*   **대용량 파일 최적화**: `LargeFileOptimizer`를 통해 대용량 파일을 청크 단위로 나누어 처리하거나 `mtime` 기반으로 변경 여부를 빠르게 체크하여 파싱 성능을 최적화합니다.
*   **신뢰도 계산**: 추출된 SQL 유닛, 조인, 필터 등에 대해 신뢰도(confidence)를 계산하고, 특정 임계값 이하의 결과는 `_SUSPECT`로 마킹하거나 필터링합니다.

---

## 2. 사용 라이브러리

`requirements.txt`에 명시된 주요 라이브러리 및 그 역할은 다음과 같습니다.

*   **`sqlalchemy`**: 데이터베이스 ORM(Object-Relational Mapping)으로, 파싱된 메타데이터를 SQLite 데이터베이스에 저장하고 관리하는 데 사용됩니다.
*   **`pyyaml`**: 설정 파일(`config.yaml`)을 로드하는 데 사용됩니다.
*   **`python-dotenv`**: 환경 변수를 관리하는 데 사용됩니다.
*   **`javalang`**: Java 소스 코드를 파싱하여 AST를 생성합니다.
*   **`requests`**: HTTP 요청을 보내는 데 사용되며, 특히 Ollama LLM 클라이언트와 통신하는 데 활용됩니다.
*   **`sqlparse`**: SQL 구문을 파싱하고 포맷팅하여 구조적인 분석을 돕습니다.
*   **`lxml`**: XML 및 HTML 파일을 효율적으로 파싱하고 XPath 쿼리를 지원하여 MyBatis XML 분석에 사용됩니다.
*   **`openai`**: LLM 통합을 위한 라이브러리로, vLLM/OpenAI 호환 LLM 클라이언트와 통신하는 데 사용됩니다.
*   **`networkx`**: 추출된 코드 요소 간의 관계(Edge)를 그래프 형태로 분석하고 시각화하는 데 활용될 수 있습니다.
*   **`psutil`**: 시스템 리소스 모니터링에 사용됩니다.
*   **`flask`, `flask-cors`, `werkzeug`, `jinja2`, `markdown`, `pygments`**: 웹 대시보드 구축 및 관련 기능(CORS, 템플릿 렌더링, 마크다운/코드 하이라이팅)에 사용됩니다.
*   **`httpx`**: 비동기 HTTP 클라이언트로, LLM 클라이언트 등에서 비동기 통신이 필요할 때 사용될 수 있습니다.
*   **`pydantic`**: 데이터 유효성 검사 및 설정 관리에 사용됩니다.
*   **`pandas`, `numpy`**: 데이터 처리 및 수치 계산에 사용됩니다.
*   **`pytest`, `pytest-asyncio`**: 테스트 프레임워크 및 비동기 테스트 지원에 사용됩니다.
*   **`tree_sitter`, `tree_sitter_java`, `tree_sitter_xml` (옵션)**: `javalang` 및 정규식 파싱의 한계를 보완하여 더 정확하고 견고한 AST 기반 파싱을 제공합니다.

---

## 3. LLM 활용 방안 특화

SourceAnalyzer는 대규모 언어 모델(LLM)을 적극적으로 활용하여 소스 코드 분석의 깊이와 유용성을 크게 향상시킵니다. `CodeSummarizer` 클래스가 이 모든 LLM 기반 기능을 총괄합니다.

### 3.1. LLM 클라이언트 연동 (`phase1/llm/client.py`)

*   **다중 LLM 제공자 지원**: `OllamaClient`와 `VLLMClient`를 통해 Ollama(로컬 모델) 및 vLLM/OpenAI 호환 API(원격 모델)를 지원합니다.
*   **설정 기반 선택**: `config.yaml` 파일의 `llm.provider` 설정에 따라 사용할 LLM 제공자를 동적으로 선택합니다.
*   **모델 가용성 확인**: Ollama의 경우, 설정된 기본 모델 및 폴백 모델의 가용성을 확인하여 LLM이 활성화되어 있는지 검증합니다.
*   **한국어 시스템 프롬프트**: 모든 LLM 요청에 "모든 응답을 한국어로 해주세요. 간결하고 명확하게 답변해주세요. 딱 필요한 답변만 하고 네, 알겠습니다 같은 군더더기 말은 하지 마세요. 만약 이해가 안되거나 답변이 불가한 경우 '-'를 답변주세요."와 같은 시스템 프롬프트를 추가하여 일관된 한국어 응답을 유도합니다.

### 3.2. 코드 요약 (`CodeSummarizer.summarize_file`, `summarize_method`, `summarize_sql_unit`)

LLM은 파일, 메서드, SQL 유닛의 목적과 기능을 자동으로 요약하여 코드 이해도를 높입니다.

*   **파일 요약**:
    *   Java, JSP 등 파일 확장자에 따라 맞춤형 프롬프트를 사용하여 파일의 목적, 주요 기능, 핵심 구성요소를 1~2문장으로 요약합니다.
    *   파일 내용을 최대 4KB까지 읽어 LLM에 전달합니다.
*   **메서드 요약**:
    *   메서드 이름, 소속 클래스, 매개변수, 반환 타입, 코드 스니펫을 바탕으로 메서드의 기능과 목적을 1문장으로 간결하게 요약합니다.
    *   메서드 코드가 없는 경우, 파일 내용에서 메서드 코드를 휴리스틱하게 추출하여 사용합니다.
*   **SQL 유닛 요약**:
    *   매퍼 네임스페이스, Statement ID, SQL 종류, SQL 내용을 바탕으로 SQL 문의 기능과 목적을 1문장으로 요약합니다.
    *   MyBatis XML에서 SQL 내용을 추출하거나 `normalized_fingerprint`를 사용하여 LLM에 전달합니다.
*   **요약 결과 저장**: 생성된 요약은 데이터베이스의 `llm_summary` 컬럼에 저장되며, 요약의 신뢰도(`llm_summary_confidence`)도 함께 기록됩니다.

### 3.3. 테이블 및 컬럼 주석 향상 (`CodeSummarizer.enhance_table_comment`, `enhance_column_comment`)

LLM은 데이터베이스 스키마의 이해도를 높이기 위해 테이블과 컬럼의 주석을 자동으로 생성하거나 향상시킵니다.

*   **테이블 주석 향상**:
    *   테이블명, 기존 코멘트, 그리고 해당 테이블을 참조하는 관련 SQL 쿼리 컨텍스트를 LLM에 제공합니다.
    *   LLM은 이를 바탕으로 테이블의 용도, 저장 데이터, 애플리케이션에서의 역할, 주요 관계 등을 포함하는 향상된 설명을 100자 이내의 한국어로 생성합니다.
*   **컬럼 주석 향상**:
    *   컬럼명, 데이터 타입, NULL 허용 여부, 기존 코멘트, 그리고 소속 테이블의 컨텍스트(테이블명, 테이블 주석)를 LLM에 제공합니다.
    *   LLM은 컬럼이 저장하는 데이터, 용도, 비즈니스 의미, 제약사항 등을 포함하는 향상된 설명을 30자 이내의 한국어로 생성합니다.
*   **향상된 주석 저장**: 생성된 주석은 데이터베이스의 `llm_comment` 컬럼에 저장되며, 신뢰도(`llm_comment_confidence`)도 함께 기록됩니다.

### 3.4. 조인 조건 분석 (`CodeSummarizer.analyze_joins_from_sql`, `process_missing_joins`)

LLM은 SQL 파서가 놓칠 수 있는 복잡한 조인 조건을 분석하여 데이터 관계를 명확히 합니다.

*   **SQL 조인 조건 추출**:
    *   SQL 정보(Mapper, Statement ID, SQL 종류)와 SQL 내용을 LLM에 제공합니다.
    *   LLM은 SQL 쿼리를 분석하여 `테이블1.컬럼1 = 테이블2.컬럼2`와 같은 형식으로 테이블 간의 조인 조건을 추출합니다.
    *   추출된 조인 조건은 데이터베이스의 `joins` 테이블에 `llm_generated=True`로 표시되어 저장됩니다.
*   **누락된 조인 처리**: 기존 파서가 조인 정보를 추출하지 못한 SQL 유닛들을 대상으로 LLM 기반 조인 분석을 수행하여 데이터베이스의 관계 정보를 보강합니다.

### 3.5. Primary Key 후보 분석 (`CodeSummarizer.analyze_primary_key_candidates`)

LLM은 테이블의 컬럼 정보를 바탕으로 실질적인 Primary Key 후보를 추천하여 데이터 모델링 이해를 돕습니다.

*   **PK 후보 추천**:
    *   테이블명, 테이블 설명, 컬럼 목록(컬럼명, 데이터 타입, NULL 허용 여부, 코멘트), 관련 코드 컨텍스트를 LLM에 제공합니다.
    *   LLM은 고유성, NOT NULL 제약, 비즈니스적 식별자 역할, 컬럼명 패턴 등을 기준으로 Primary Key로 적합한 컬럼명을 쉼표로 구분하여 추천합니다.
    *   추천된 Primary Key 후보는 테이블 명세서 생성 시 활용됩니다.

### 3.6. 명세서 생성 (`generate_source_specification_md`, `generate_table_specification_md`)

LLM이 생성한 요약 및 주석 정보를 활용하여 소스 코드 및 데이터베이스 테이블 명세서 Markdown 파일을 자동으로 생성합니다.

*   **소스 코드 명세서**: 파일, 클래스, 메서드, SQL 쿼리별 LLM 요약을 포함하여 소스 코드의 구조와 기능을 문서화합니다.
*   **데이터베이스 테이블 명세서**: 테이블 및 컬럼의 LLM 향상 주석, Primary Key 정보(LLM 추천 포함)를 포함하여 데이터베이스 스키마를 문서화합니다.

---

## 결론

SourceAnalyzer는 정교한 파싱 로직과 강력한 LLM 통합을 통해 소스 코드와 데이터베이스 스키마에 대한 심층적인 분석과 이해를 제공합니다. 특히 LLM은 코드 요약, 주석 향상, 관계 분석 등 다양한 영역에서 개발자의 생산성과 시스템 이해도를 크게 높이는 핵심적인 역할을 수행합니다. 향후 LLM의 활용 범위를 더욱 확장하여 코드 품질 분석, 취약점 패턴 학습, 리팩토링 제안 등 고도화된 기능을 제공할 계획입니다.
