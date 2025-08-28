# 소스 분석기 테스트 케이스 (Gemini 제안)

## 1. 개요

본 문서는 `prd_v4.md`, `1단계_002차_개발내역.md`, `1단계_002차_개발후_1_리뷰.md`, 그리고 `2차개발_개선안_gemini.md`의 내용을 종합하여 소스 분석 에이전트의 핵심 기능 및 개선 사항을 검증하기 위한 테스트 케이스를 정의합니다. 각 테스트 케이스는 `PROJECT` 폴더 하위에 생성될 샘플 소스 코드와 필요한 DB 스키마 CSV 파일을 포함합니다.

## 2. 테스트 케이스 목록

### 2.1. TC_001_JavaBasicParsing: 기본 Java 코드 파싱 및 메타데이터 추출

*   **Feature/Requirement**: Java 클래스, 메서드, 필드, 어노테이션 등 기본 구조 메타데이터 추출 (`prd_v4.md` 3.2.2.1)
*   **Description**: 간단한 Java 클래스 및 메서드를 포함하는 파일을 분석하여 정확한 클래스, 메서드 메타데이터가 추출되는지 확인합니다.
*   **Preconditions**: 분석기 시스템이 정상 작동 상태여야 합니다.
*   **Test Steps**:
    1.  `PROJECT/TC_001_JavaBasicParsing` 폴더를 분석 대상으로 지정하여 분석기를 실행합니다.
    2.  생성된 메타데이터를 조회합니다.
*   **Expected Result**:
    *   `MySimpleClass` 클래스 및 `myMethod`, `anotherMethod` 메서드가 정확히 추출됩니다.
    *   각 엔티티의 `start_line`, `end_line`, `name` 등의 정보가 올바르게 저장됩니다.
*   **Associated Files**:
    *   `PROJECT/TC_001_JavaBasicParsing/src/main/java/com/example/simple/MySimpleClass.java`

### 2.2. TC_002_SpringDIParsing: Spring DI 및 어노테이션 기반 의존성 분석

*   **Feature/Requirement**: Spring `@Service`, `@Autowired`, `@RestController`, `@GetMapping` 등 어노테이션 기반 DI 관계 및 HTTP API 엔드포인트 추출 (`prd_v4.md` 3.2.2.1, `2차개발_개선안_gemini.md` 3.1.2)
*   **Description**: Spring 어노테이션이 적용된 서비스, 컨트롤러 클래스 간의 의존성 주입 관계 및 HTTP API 엔드포인트 정보가 정확히 추출되는지 확인합니다.
*   **Preconditions**: 분석기 시스템이 정상 작동 상태여야 합니다.
*   **Test Steps**:
    1.  `PROJECT/TC_002_SpringDIParsing` 폴더를 분석 대상으로 지정하여 분석기를 실행합니다.
    2.  생성된 `edges` 테이블 및 클래스/메서드 메타데이터를 조회합니다.
*   **Expected Result**:
    *   `MyController`와 `MyService` 간의 `depends_on_di` 관계가 `edges` 테이블에 저장됩니다.
    *   `MyController`의 `getHello` 메서드에 `@GetMapping` 어노테이션 정보가 포함되고, `/hello` 엔드포인트 정보가 추출됩니다.
*   **Associated Files**:
    *   `PROJECT/TC_002_SpringDIParsing/src/main/java/com/example/spring/MyService.java`
    *   `PROJECT/TC_002_SpringDIParsing/src/main/java/com/example/spring/MyController.java`

### 2.3. TC_003_MyBatisDynamicSQL: 동적 SQL 및 필수 필터 추출

*   **Feature/Requirement**: MyBatis 동적 SQL (`<if>`, `<choose>`, `<foreach>`) 처리 및 실제 조인 조건/필수 필터 추출 (`prd_v4.md` 3.2.7, `2차개발_개선안_gemini.md` 3.1.1, 3.1.3)
*   **Description**: 복잡한 동적 SQL 구문을 포함하는 MyBatis XML 파일을 분석하여, 가능한 SQL 패턴을 정확히 파싱하고 `DEL_YN = 'N'`과 같은 필수 필터가 `required_filters` 테이블에 저장되는지 확인합니다.
*   **Preconditions**: 분석기 시스템이 정상 작동 상태여야 합니다.
*   **Test Steps**:
    1.  `PROJECT/TC_003_MyBatisDynamicSQL` 폴더를 분석 대상으로 지정하여 분석기를 실행합니다.
    2.  생성된 `sql_units`, `joins`, `required_filters` 테이블을 조회합니다.
*   **Expected Result**:
    *   `selectDynamicData` SQL 유닛이 파싱되고, 동적 태그에 따른 여러 SQL 패턴이 (최대 포함 변형으로) 처리됩니다.
    *   `DEL_YN = 'N'` 필터가 `always_applied=1`로 `required_filters` 테이블에 저장됩니다.
    *   `JOIN` 조건이 정확히 추출됩니다.
*   **Associated Files**:
    *   `PROJECT/TC_003_MyBatisDynamicSQL/src/main/java/com/example/mybatis/DynamicDataMapper.java`
    *   `PROJECT/TC_003_MyBatisDynamicSQL/src/main/resources/mybatis/DynamicDataMapper.xml`
*   **Data Files**:
    *   `PROJECT/TC_003_MyBatisDynamicSQL/DB_SCHEMA/ALL_TABLES.csv`
    *   `PROJECT/TC_003_MyBatisDynamicSQL/DB_SCHEMA/ALL_TAB_COLUMNS.csv`
    *   `PROJECT/TC_003_MyBatisDynamicSQL/DB_SCHEMA/PK_INFO.csv`

### 2.4. TC_004_JSPWithJSTLAndScriptlet: JSP JSTL 및 스크립틀릿 SQL 추적

*   **Feature/Requirement**: JSP JSTL 및 스크립틀릿 내 Java 코드의 SQL 생성 문맥 추적 (`prd_v4.md` 3.2.2.2, `2차개발_개선안_gemini.md` 3.1.1)
*   **Description**: JSTL 태그와 Java 스크립틀릿을 사용하여 동적으로 SQL 문자열을 생성하는 JSP 파일을 분석하여, 해당 SQL이 정확히 추적되고 메타데이터로 추출되는지 확인합니다.
*   **Preconditions**: 분석기 시스템이 정상 작동 상태여야 합니다.
*   **Test Steps**:
    1.  `PROJECT/TC_004_JSPWithJSTLAndScriptlet` 폴더를 분석 대상으로 지정하여 분석기를 실행합니다.
    2.  생성된 `sql_units` 테이블을 조회합니다.
*   **Expected Result**:
    *   JSP 파일 내에서 동적으로 생성된 SQL 문자열이 `sql_units` 테이블에 저장됩니다.
    *   SQL 유닛의 `origin`이 JSP 파일 경로를 가리킵니다.
*   **Associated Files**:
    *   `PROJECT/TC_004_JSPWithJSTLAndScriptlet/src/main/webapp/WEB-INF/jsp/dynamicSqlView.jsp`
    *   `PROJECT/TC_004_JSPWithJSTLAndScriptlet/src/main/java/com/example/jsp/JspController.java`

### 2.5. TC_005_IncrementalAnalysis: 증분 분석 및 변경 추적

*   **Feature/Requirement**: 파일 해시/mtime 비교를 통한 증분 분석 및 그래프 ‘국소’ 재계산 (`prd_v4.md` 3.4.2, 3.2.10)
*   **Description**: 초기 분석 후 파일 내용을 변경하고 다시 분석기를 실행하여, 변경된 파일만 재분석되고 메타데이터가 업데이트되는지 확인합니다. 암호학적 해시를 통한 변경 추적 기능을 검증합니다.
*   **Preconditions**: 분석기 시스템이 정상 작동 상태여야 합니다.
*   **Test Steps**:
    1.  `PROJECT/TC_005_IncrementalAnalysis` 폴더를 분석 대상으로 지정하여 분석기를 초기 실행합니다.
    2.  `MyIncrementalService.java` 파일의 메서드 내용을 일부 변경합니다.
    3.  동일 폴더를 대상으로 분석기를 다시 실행합니다.
    4.  생성된 `files` 테이블의 `hash` 및 `updated_at` 필드, 그리고 `methods` 테이블의 변경 사항을 조회합니다.
*   **Expected Result**:
    *   초기 분석 시 `MyIncrementalService.java`의 해시가 저장됩니다.
    *   파일 변경 후 재분석 시 `MyIncrementalService.java`의 `hash` 값이 변경되고, `updated_at` 타임스탬프가 업데이트됩니다.
    *   변경되지 않은 다른 파일들은 재분석되지 않고 기존 메타데이터가 유지됩니다.
    *   `MyIncrementalService.java`의 변경된 메서드 메타데이터가 정확히 반영됩니다.
*   **Associated Files**:
    *   `PROJECT/TC_005_IncrementalAnalysis/src/main/java/com/example/incremental/MyIncrementalService.java`

### 2.6. TC_006_SQLInjectionDetection: SQL Injection 취약점 탐지

*   **Feature/Requirement**: MyBatis 매퍼 파일에서 `${...}` 패턴을 통한 SQL Injection 취약점 탐지 (`prd_v4.md` 2.2.2, 3.2.3, `2차개발_개선안_gemini.md` 3.5.1)
*   **Description**: `${...}` 패턴을 사용하여 파라미터를 직접 삽입하는 MyBatis SQL 구문을 포함하는 파일을 분석하여, 해당 구문이 SQL Injection 취약점으로 정확히 탐지되고 `vulnerability_fixes` 테이블에 저장되는지 확인합니다.
*   **Preconditions**: 분석기 시스템이 정상 작동 상태여야 합니다.
*   **Test Steps**:
    1.  `PROJECT/TC_006_SQLInjectionDetection` 폴더를 분석 대상으로 지정하여 분석기를 실행합니다.
    2.  생성된 `vulnerability_fixes` 테이블을 조회합니다.
*   **Expected Result**:
    *   `findUserByDynamicColumn` SQL 유닛이 SQL Injection 취약점으로 탐지됩니다.
    *   `vulnerability_fixes` 테이블에 `sql_injection` 유형의 취약점 정보가 저장되고, `original_code` 및 `fixed_code` 제안이 포함됩니다.
*   **Associated Files**:
    *   `PROJECT/TC_006_SQLInjectionDetection/src/main/java/com/example/security/UserMapper.java`
    *   `PROJECT/TC_006_SQLInjectionDetection/src/main/resources/mybatis/UserMapper.xml`

### 2.7. TC_007_LLMDBCommentGeneration: LLM 기반 DB 컬럼 코멘트 생성

*   **Feature/Requirement**: 소스 코드 사용 맥락 기반 LLM을 통한 DB 컬럼 코멘트 생성 (`prd_v4.md` 1.4.2, 3.2.8, `2차개발_개선안_gemini.md` 3.4.1)
*   **Description**: 특정 DB 컬럼을 사용하는 SQL 및 Java 코드를 포함하는 프로젝트를 분석한 후, LLM이 해당 컬럼의 역할과 의미를 설명하는 고품질 한글 코멘트를 생성하여 `summaries` 테이블에 `db_comment_suggestion` 타입으로 저장하는지 확인합니다.
*   **Preconditions**: 분석기 시스템 및 LLM 연동이 정상 작동 상태여야 합니다.
*   **Test Steps**:
    1.  `PROJECT/TC_007_LLMDBCommentGeneration` 폴더를 분석 대상으로 지정하여 분석기를 실행합니다.
    2.  생성된 `summaries` 테이블을 조회하여 `db_comment_suggestion` 타입의 코멘트가 존재하는지 확인합니다.
*   **Expected Result**:
    *   `USER_INFO` 테이블의 `USER_STATUS` 컬럼에 대한 LLM 기반 한글 코멘트가 `summaries` 테이블에 저장됩니다.
    *   코멘트 내용은 `UserMapper.xml` 및 `UserService.java`에서 `USER_STATUS`가 사용되는 맥락을 반영합니다.
*   **Associated Files**:
    *   `PROJECT/TC_007_LLMDBCommentGeneration/src/main/java/com/example/llm/UserService.java`
    *   `PROJECT/TC_007_LLMDBCommentGeneration/src/main/java/com/example/llm/UserMapper.java`
    *   `PROJECT/TC_007_LLMDBCommentGeneration/src/main/resources/mybatis/UserMapper.xml`
*   **Data Files**:
    *   `PROJECT/TC_007_LLMDBCommentGeneration/DB_SCHEMA/ALL_TABLES.csv`
    *   `PROJECT/TC_007_LLMDBCommentGeneration/DB_SCHEMA/ALL_TAB_COLUMNS.csv`
    *   `PROJECT/TC_007_LLMDBCommentGeneration/DB_SCHEMA/ALL_TAB_COMMENTS.csv`

### 2.8. TC_008_ComplexSQLParsing: 복잡한 SQL 구문 (CTE, Subquery, ANSI JOIN) 파싱

*   **Feature/Requirement**: CTE, 서브쿼리, ANSI JOIN 등 복잡한 SQL 구문 파싱 및 메타데이터 추출 (`prd_v4.md` 3.1.2, 3.2.7, `2차개발_개선안_gemini.md` 3.1.3)
*   **Description**: CTE, 서브쿼리, ANSI JOIN을 포함하는 복잡한 SQL 구문을 분석하여, 테이블, 조인 조건, 필터 등이 정확히 추출되고 `sql_units`, `joins`, `required_filters` 테이블에 저장되는지 확인합니다.
*   **Preconditions**: 분석기 시스템이 정상 작동 상태여야 합니다.
*   **Test Steps**:
    1.  `PROJECT/TC_008_ComplexSQLParsing` 폴더를 분석 대상으로 지정하여 분석기를 실행합니다.
    2.  생성된 `sql_units`, `joins`, `required_filters` 테이블을 조회합니다.
*   **Expected Result**:
    *   `getComplexReport` SQL 유닛이 파싱되고, CTE, 서브쿼리 내 테이블 및 조인 관계가 정확히 식별됩니다.
    *   ANSI JOIN 조건이 `joins` 테이블에 올바르게 저장됩니다.
*   **Associated Files**:
    *   `PROJECT/TC_008_ComplexSQLParsing/src/main/java/com/example/complexsql/ReportMapper.java`
    *   `PROJECT/TC_008_ComplexSQLParsing/src/main/resources/mybatis/ReportMapper.xml`
*   **Data Files**:
    *   `PROJECT/TC_008_ComplexSQLParsing/DB_SCHEMA/ALL_TABLES.csv`
    *   `PROJECT/TC_008_ComplexSQLParsing/DB_SCHEMA/ALL_TAB_COLUMNS.csv`
    *   `PROJECT/TC_008_ComplexSQLParsing/DB_SCHEMA/PK_INFO.csv`

### 2.9. TC_009_ErrorHandlingAndLogging: 예외 처리 및 체계적 로깅

*   **Feature/Requirement**: 구체적 예외 타입별 처리, 체계적 오류 보고, 파싱 실패 파일 목록 제공 (`prd_v4.md` 3.3.1, `2차개발_개선안_gemini.md` 3.2.3)
*   **Description**: 의도적으로 구문 오류가 있는 파일을 포함시켜 분석기를 실행하고, `src/utils/logger.py`를 통해 오류가 정확히 기록되고, 파싱 실패 파일 목록이 보고서에 포함되는지 확인합니다.
*   **Preconditions**: 분석기 시스템이 정상 작동 상태여야 합니다.
*   **Test Steps**:
    1.  `PROJECT/TC_009_ErrorHandlingAndLogging` 폴더를 분석 대상으로 지정하여 분석기를 실행합니다.
    2.  `logs/analyzer.log` 파일을 확인하고, 분석 완료 보고서를 확인합니다.
*   **Expected Result**:
    *   `ErrorSyntax.java` 파일 파싱 시 `ERROR` 레벨의 로그가 기록되고, 예외 스택 트레이스가 포함됩니다.
    *   분석 완료 보고서에 `ErrorSyntax.java`가 파싱 실패 파일 목록에 포함됩니다.
*   **Associated Files**:
    *   `PROJECT/TC_009_ErrorHandlingAndLogging/src/main/java/com/example/error/ErrorSyntax.java`
    *   `PROJECT/TC_009_ErrorHandlingAndLogging/src/main/java/com/example/error/ValidClass.java`

### 2.10. TC_010_CyclomaticComplexity: 순환 복잡도 계산

*   **Feature/Requirement**: 순환 복잡도 등 코드 품질 지표 분석 및 `code_metrics` 테이블 저장 (`prd_v4.md` 3.2.4, `2차개발_개선안_gemini.md` 3.5.2)
*   **Description**: 다양한 제어 흐름 (if, for, while, switch)을 포함하는 Java 메서드의 순환 복잡도가 정확히 계산되고 `code_metrics` 테이블에 저장되는지 확인합니다.
*   **Preconditions**: 분석기 시스템이 정상 작동 상태여야 합니다.
*   **Test Steps**:
    1.  `PROJECT/TC_010_CyclomaticComplexity` 폴더를 분석 대상으로 지정하여 분석기를 실행합니다.
    2.  생성된 `code_metrics` 테이블을 조회하여 `metric_type='complexity'`인 항목을 확인합니다.
*   **Expected Result**:
    *   `ComplexMethod` 및 `SimpleMethod`의 순환 복잡도가 정확히 계산되어 `code_metrics` 테이블에 저장됩니다.
    *   `ComplexMethod`의 복잡도 값이 `SimpleMethod`보다 높게 측정됩니다.
*   **Associated Files**:
    *   `PROJECT/TC_010_CyclomaticComplexity/src/main/java/com/example/complexity/ComplexityService.java`

### 2.11. TC_011_StreamingHash: 스트리밍 해시 계산

*   **Feature/Requirement**: 파일 해시 계산 시 스트리밍 방식 적용 (`2차개발_개선안_gemini.md` 3.2.2)
*   **Description**: 대용량 파일을 시뮬레이션하는 파일을 생성하고, 분석기가 해당 파일의 해시를 스트리밍 방식으로 계산하여 메모리 효율성을 유지하는지 (직접적인 메모리 사용량 측정은 어려우나, 기능적 검증) 확인합니다.
*   **Preconditions**: 분석기 시스템이 정상 작동 상태여야 합니다.
*   **Test Steps**:
    1.  `PROJECT/TC_011_StreamingHash` 폴더를 분석 대상으로 지정하여 분석기를 실행합니다.
    2.  생성된 `files` 테이블의 `hash` 필드를 조회합니다.
*   **Expected Result**:
    *   `LargeFile.txt`의 해시 값이 정확히 계산되어 `files` 테이블에 저장됩니다.
    *   (간접적으로) 대용량 파일 처리 시 시스템 메모리 사용량이 급증하지 않습니다.
*   **Associated Files**:
    *   `PROJECT/TC_011_StreamingHash/LargeFile.txt` (대용량 더미 파일)

### 2.12. TC_012_GenericTypeParsing: 제네릭 타입 정보 추출

*   **Feature/Requirement**: 서비스/매퍼 인터페이스의 제네릭 반환 타입 및 매개변수 정보 추출 (`2차개발_개선안_gemini.md` 3.3.1)
*   **Description**: 제네릭 타입을 사용하는 Java 인터페이스 및 클래스를 분석하여, `List<Customer>`, `Optional<Order>`와 같은 제네릭 타입 정보가 `return_type` 필드에 정확히 저장되는지 확인합니다.
*   **Preconditions**: 분석기 시스템이 정상 작동 상태여야 합니다.
*   **Test Steps**:
    1.  `PROJECT/TC_012_GenericTypeParsing` 폴더를 분석 대상으로 지정하여 분석기를 실행합니다.
    2.  생성된 `methods` 테이블을 조회하여 `return_type` 필드를 확인합니다.
*   **Expected Result**:
    *   `CustomerService`의 `getCustomers` 메서드 `return_type`이 `List<Customer>`로, `getCustomerById` 메서드 `return_type`이 `Optional<Customer>`로 정확히 추출됩니다.
*   **Associated Files**:
    *   `PROJECT/TC_012_GenericTypeParsing/src/main/java/com/example/generics/Customer.java`
    *   `PROJECT/TC_012_GenericTypeParsing/src/main/java/com/example/generics/CustomerService.java`

### 2.13. TC_013_MethodReferenceAndLambda: 메서드 참조 및 람다식 호출 추적

*   **Feature/Requirement**: 람다식 및 메서드 참조 내부 호출 추적 (`prd_v4.md` 3.2.6, `2차개발_개선안_gemini.md` 3.3.2)
*   **Description**: Java 8+의 람다식 및 메서드 참조를 사용하여 다른 메서드를 호출하는 코드를 분석하여, 이러한 간접 호출 관계가 `edges` 테이블에 정확히 저장되는지 확인합니다.
*   **Preconditions**: 분석기 시스템이 정상 작동 상태여야 합니다.
*   **Test Steps**:
    1.  `PROJECT/TC_013_MethodReferenceAndLambda` 폴더를 분석 대상으로 지정하여 분석기를 실행합니다.
    2.  생성된 `edges` 테이블을 조회하여 람다/메서드 참조를 통한 `call` 관계가 존재하는지 확인합니다.
*   **Expected Result**:
    *   `ProcessorService`의 `processList` 메서드에서 `MyUtil.transform` 및 `item.toUpperCase` 호출에 대한 `call` 엣지가 `edges` 테이블에 저장됩니다.
*   **Associated Files**:
    *   `PROJECT/TC_013_MethodReferenceAndLambda/src/main/java/com/example/lambda/MyUtil.java`
    *   `PROJECT/TC_013_MethodReferenceAndLambda/src/main/java/com/example/lambda/ProcessorService.java`

### 2.14. TC_014_JSPIncludeAndJavaLinkage: JSP 포함 관계 및 Java 연동 분석

*   **Feature/Requirement**: JSP 페이지 간 포함 관계 (`<jsp:include>`) 및 백엔드 Java 코드(Servlet, Spring Controller)와의 연동 관계 분석 (`prd_v4.md` 3.2.2.2, `2차개발_개선안_gemini.md` 3.3.2)
*   **Description**: `<jsp:include>`를 사용하여 다른 JSP 파일을 포함하고, 백엔드 Java 컨트롤러와 연동되는 JSP 페이지를 분석하여, 이들 간의 `edges` 관계가 정확히 추출되는지 확인합니다.
*   **Preconditions**: 분석기 시스템이 정상 작동 상태여야 합니다.
*   **Test Steps**:
    1.  `PROJECT/TC_014_JSPIncludeAndJavaLinkage` 폴더를 분석 대상으로 지정하여 분석기를 실행합니다.
    2.  생성된 `edges` 테이블을 조회하여 JSP-JSP 포함 관계 및 JSP-Java 연동 관계를 확인합니다.
*   **Expected Result**:
    *   `main.jsp`와 `header.jspf` 간의 `include` 엣지가 `edges` 테이블에 저장됩니다.
    *   `JspController`와 `main.jsp` 간의 `render` 또는 `use_view`와 같은 연동 엣지가 저장됩니다.
*   **Associated Files**:
    *   `PROJECT/TC_014_JSPIncludeAndJavaLinkage/src/main/java/com/example/jspinclude/JspController.java`
    *   `PROJECT/TC_014_JSPIncludeAndJavaLinkage/src/main/webapp/WEB-INF/jsp/main.jsp`
    *   `PROJECT/TC_014_JSPIncludeAndJavaLinkage/src/main/webapp/WEB-INF/jsp/_fragments/header.jspf`

### 2.15. TC_015_MyBatisIncludeAndSQLRef: MyBatis `<include>` 및 `<sql>` 참조 관계

*   **Feature/Requirement**: MyBatis SQL 유닛 간 `<include>` 및 `<sql>` 참조 관계 추출 (`prd_v4.md` 3.2.6, `2차개발_개선안_gemini.md` 3.3.2)
*   **Description**: `<sql>` 태그로 정의된 SQL 조각을 `<include>` 태그로 참조하는 MyBatis XML 파일을 분석하여, 이들 간의 참조 관계가 `edges` 테이블에 정확히 저장되는지 확인합니다.
*   **Preconditions**: 분석기 시스템이 정상 작동 상태여야 합니다.
*   **Test Steps**:
    1.  `PROJECT/TC_015_MyBatisIncludeAndSQLRef` 폴더를 분석 대상으로 지정하여 분석기를 실행합니다.
    2.  생성된 `edges` 테이블을 조회하여 `<include>`-`<sql>` 참조 관계를 확인합니다.
*   **Expected Result**:
    *   `selectUser` SQL 유닛과 `userColumns` SQL 조각 간의 `include_sql` 엣지가 `edges` 테이블에 저장됩니다.
*   **Associated Files**:
    *   `PROJECT/TC_015_MyBatisIncludeAndSQLRef/src/main/java/com/example/mybatisinclude/UserQueryMapper.java`
    *   `PROJECT/TC_015_MyBatisIncludeAndSQLRef/src/main/resources/mybatis/UserQueryMapper.xml`

### 2.16. TC_016_TargetedAnalysis: 특정 폴더/파일 대상 분석

*   **Feature/Requirement**: 메타정보 생성 작업의 선택적 실행 및 대상 지정 기능 확장 (`prd_v4.md` 3.2.9)
*   **Description**: 프로젝트 내 특정 폴더 또는 특정 파일만 지정하여 분석기를 실행하고, 지정된 대상에 대해서만 메타데이터가 생성되는지 확인합니다.
*   **Preconditions**: 분석기 시스템이 정상 작동 상태여야 합니다.
*   **Test Steps**:
    1.  `PROJECT/TC_016_TargetedAnalysis` 폴더를 생성하고, `TargetService.java`와 `OtherService.java`를 생성합니다.
    2.  `TargetService.java` 파일만 분석 대상으로 지정하여 분석기를 실행합니다.
    3.  생성된 `classes` 및 `methods` 테이블을 조회합니다.
*   **Expected Result**:
    *   `TargetService` 클래스 및 메서드에 대한 메타데이터만 생성되고, `OtherService`에 대한 메타데이터는 생성되지 않습니다.
*   **Associated Files**:
    *   `PROJECT/TC_016_TargetedAnalysis/src/main/java/com/example/targeted/TargetService.java`
    *   `PROJECT/TC_016_TargetedAnalysis/src/main/java/com/example/targeted/OtherService.java`

### 2.17. TC_017_ConfidenceCalculation: CONFIDENCE 산식 검증

*   **Feature/Requirement**: CONFIDENCE 산식 적용 및 동적 SQL/리플렉션 복잡도에 따른 감점 (`prd_v4.md` 5.3, `2차개발_개선안_gemini.md` 3.4.2)
*   **Description**: 일반적인 SQL과 동적 SQL을 포함하는 파일을 분석하여, 동적 SQL이 포함된 SQL 유닛의 CONFIDENCE 점수가 감점되어 낮게 측정되는지 확인합니다.
*   **Preconditions**: 분석기 시스템이 정상 작동 상태여야 합니다.
*   **Test Steps**:
    1.  `PROJECT/TC_017_ConfidenceCalculation` 폴더를 분석 대상으로 지정하여 분석기를 실행합니다.
    2.  생성된 `sql_units` 테이블을 조회하여 `confidence` 필드를 확인합니다.
*   **Expected Result**:
    *   `getStaticData` SQL 유닛은 높은 CONFIDENCE 점수를 가집니다.
    *   `getDynamicData` SQL 유닛은 동적 SQL 사용으로 인해 감점되어 `getStaticData`보다 낮은 CONFIDENCE 점수를 가집니다.
*   **Associated Files**:
    *   `PROJECT/TC_017_ConfidenceCalculation/src/main/java/com/example/confidence/DataMapper.java`
    *   `PROJECT/TC_017_ConfidenceCalculation/src/main/resources/mybatis/DataMapper.xml`

### 2.18. TC_018_DataFlowAnalysis: 데이터 흐름 분석 (Source to Sink)

*   **Feature/Requirement**: 코드 내 데이터의 이동 경로 (Source to Sink) 추적 및 메타정보 저장 (`prd_v4.md` 3.2.5)
*   **Description**: 사용자 입력(Source)이 데이터베이스(Sink)로 흘러가는 간단한 데이터 흐름을 포함하는 Java 코드를 분석하여, 해당 데이터 흐름이 정확히 식별되고 메타정보에 저장되는지 확인합니다.
*   **Preconditions**: 분석기 시스템이 정상 작동 상태여야 합니다.
*   **Test Steps**:
    1.  `PROJECT/TC_018_DataFlowAnalysis` 폴더를 분석 대상으로 지정하여 분석기를 실행합니다.
    2.  생성된 `edges` 테이블 또는 별도의 데이터 흐름 관련 테이블을 조회합니다.
*   **Expected Result**:
    *   `UserController.createUser` 메서드의 `username` 파라미터가 `UserService.saveUser`를 거쳐 `UserMapper.insertUser`로 전달되는 데이터 흐름이 `edges` 테이블에 `data_flow`와 같은 `edge_kind`로 저장됩니다.
*   **Associated Files**:
    *   `PROJECT/TC_018_DataFlowAnalysis/src/main/java/com/example/dataflow/User.java`
    *   `PROJECT/TC_018_DataFlowAnalysis/src/main/java/com/example/dataflow/UserMapper.java`
    *   `PROJECT/TC_018_DataFlowAnalysis/src/main/java/com/example/dataflow/UserService.java`
    *   `PROJECT/TC_018_DataFlowAnalysis/src/main/java/com/example/dataflow/UserController.java`
    *   `PROJECT/TC_018_DataFlowAnalysis/src/main/resources/mybatis/UserMapper.xml`
*   **Data Files**:
    *   `PROJECT/TC_018_DataFlowAnalysis/DB_SCHEMA/ALL_TABLES.csv`
    *   `PROJECT/TC_018_DataFlowAnalysis/DB_SCHEMA/ALL_TAB_COLUMNS.csv`

### 2.19. TC_019_MultilingualParsing: 다국어 (한국어/영어) 인식 및 검색

*   **Feature/Requirement**: 다국어(한국어/영어) 인식 및 검색 (`prd_v4.md` 3.1.8)
*   **Description**: 한국어 및 영어 주석, 변수명, 문자열 리터럴을 포함하는 Java 파일을 분석하여, 메타데이터 추출 시 다국어 정보가 손실 없이 처리되고, 향후 RAG 기반 검색 시 다국어 질의에 올바르게 응답할 수 있는 기반을 마련하는지 확인합니다.
*   **Preconditions**: 분석기 시스템이 정상 작동 상태여야 합니다.
*   **Test Steps**:
    1.  `PROJECT/TC_019_MultilingualParsing` 폴더를 분석 대상으로 지정하여 분석기를 실행합니다.
    2.  생성된 `classes`, `methods`, `summaries` (LLM 기반 요약 시) 테이블을 조회합니다.
*   **Expected Result**:
    *   한국어 주석 및 변수명이 메타데이터에 올바르게 포함됩니다.
    *   (간접적으로) LLM 기반 요약 생성 시 한국어 텍스트가 정확히 처리됩니다.
*   **Associated Files**:
    *   `PROJECT/TC_019_MultilingualParsing/src/main/java/com/example/multilingual/MultilingualService.java`

### 2.20. TC_020_LargeProjectPerformance: 대규모 프로젝트 성능 및 병렬화

*   **Feature/Requirement**: 100k LOC 프로젝트 전체 분석 ≤ 30분, 파일 단위 멀티스레드 파싱 (`prd_v4.md` 10.3, 3.4.1)
*   **Description**: 대규모 프로젝트를 시뮬레이션하기 위해 다수의 더미 Java 파일을 생성하고, 분석기가 이를 멀티스레드 방식으로 효율적으로 처리하여 지정된 성능 목표를 달성하는지 확인합니다.
*   **Preconditions**: 분석기 시스템이 정상 작동 상태여야 합니다. `config.yaml`에 `analysis.thread_count`가 적절히 설정되어 있어야 합니다.
*   **Test Steps**:
    1.  `PROJECT/TC_020_LargeProjectPerformance` 폴더에 1000개 이상의 더미 Java 파일을 생성합니다.
    2.  `PROJECT/TC_020_LargeProjectPerformance` 폴더를 분석 대상으로 지정하여 분석기를 실행하고, 총 분석 시간을 측정합니다.
*   **Expected Result**:
    *   분석 시간이 `prd_v4.md`에 명시된 성능 목표 (예: 100k LOC ≤ 30분)를 만족합니다.
    *   로그에서 멀티스레드 파싱이 활성화되고 여러 워커가 사용되었음을 확인합니다.
*   **Associated Files**:
    *   `PROJECT/TC_020_LargeProjectPerformance/src/main/java/com/example/largeproject/DummyService_001.java`
    *   ...
    *   `PROJECT/TC_020_LargeProjectPerformance/src/main/java/com/example/largeproject/DummyService_N.java` (N은 대규모 프로젝트 시뮬레이션을 위한 충분한 수)

### 2.21. TC_021_ComplexDependencies: 복합적인 파일 간 종속성 분석

*   **Feature/Requirement**: JSP-Java, Java-JSP, Java-SQL, SQL-Java 등 복합적인 파일 간 종속성 및 호출 관계 추적 (`prd_v4.md` 3.2.2.2, 3.2.6, `2차개발_개선안_gemini.md` 3.3.2)
*   **Description**: 하나의 JSP 파일이 여러 Java 서비스/컨트롤러를 호출하고, 하나의 Java 서비스가 여러 JSP 뷰를 렌더링하며 여러 MyBatis 쿼리를 사용하는 복합적인 시나리오를 분석합니다. 또한 하나의 MyBatis 쿼리가 여러 Java 메서드에 의해 호출되는 경우를 포함하여, 이 모든 종속성 관계가 `edges` 테이블에 정확히 저장되는지 확인합니다.
*   **Preconditions**: 분석기 시스템이 정상 작동 상태여야 합니다.
*   **Test Steps**:
    1.  `PROJECT/TC_021_ComplexDependencies` 폴더를 분석 대상으로 지정하여 분석기를 실행합니다.
    2.  생성된 `edges` 테이블을 조회하여 JSP-Java, Java-JSP, Java-SQL, SQL-Java 간의 다양한 `edge_kind` 관계를 확인합니다.
*   **Expected Result**:
    *   `complexView.jsp`에서 `ServiceA` 및 `ServiceB`의 메서드를 호출하는 `call` 엣지가 `edges` 테이블에 저장됩니다.
    *   `ComplexService.java`에서 `complexView.jsp`, `anotherView.jsp`를 렌더링하는 `render` 또는 `use_view` 엣지가 저장됩니다.
    *   `ComplexService.java`에서 `QueryMapper.selectQueryA` 및 `QueryMapper.selectQueryB`를 호출하는 `call_sql` 엣지가 저장됩니다.
    *   `QueryMapper.xml`의 `selectQueryC` 쿼리가 `ServiceA.getDataC` 및 `ServiceB.getDataC` 메서드에 의해 호출되는 `call_sql` (역방향) 엣지가 저장됩니다.
*   **Associated Files**:
    *   `PROJECT/TC_021_ComplexDependencies/src/main/java/com/example/complexdep/ServiceA.java`
    *   `PROJECT/TC_021_ComplexDependencies/src/main/java/com/example/complexdep/ServiceB.java`
    *   `PROJECT/TC_021_ComplexDependencies/src/main/java/com/example/complexdep/ComplexService.java`
    *   `PROJECT/TC_021_ComplexDependencies/src/main/java/com/example/complexdep/QueryMapper.java`
    *   `PROJECT/TC_021_ComplexDependencies/src/main/resources/mybatis/QueryMapper.xml`
    *   `PROJECT/TC_021_ComplexDependencies/src/main/webapp/WEB-INF/jsp/complexView.jsp`
    *   `PROJECT/TC_021_ComplexDependencies/src/main/webapp/WEB-INF/jsp/anotherView.jsp`

---