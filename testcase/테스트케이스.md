# 테스트케이스_통합.md - 소스 분석기 통합 테스트 케이스 및 샘플 소스

본 문서는 소스 분석 에이전트의 핵심 기능 및 개선 사항을 검증하기 위한 통합 테스트 케이스와 샘플 소스 코드를 정의합니다. 기존 `prd_v4.md` 및 개발 리뷰 문서들의 요구사항을 종합하고, 테스트 시나리오를 추가하여 분석기의 정확성, 성능, 안정성 및 확장성을 대폭 향상시키기 위한 기반을 마련합니다.

## 1. 통합 샘플 소스 코드 개요

기존 `PROJECT` 폴더 하위의 여러 테스트케이스 및 샘플 소스들을 `PROJECT/IntegratedSource` 폴더로 통합하였습니다. 이 통합 소스는 다양한 Java, MyBatis XML, JSP 패턴을 포함하며, 새로운 테스트 요구사항을 반영합니다.

### 1.1. `IntegratedService.java`

기존 `Example1`, `Example3`, `DynamicMyBatis`, `MixedTechLegacy` 프로젝트의 Java 코드들을 통합하고, 새로운 테스트 케이스를 위한 메서드들을 추가하였습니다. 주요 특징은 다음과 같습니다.

* **기본 Java 로직**: `startProcess`, `doWork` 등 간단한 메서드 호출 관계.
* **정적/동적 SQL 호출**: `getStaticUserData`, `getDynamicUserData` 메서드를 통해 정적 SQL과 동적 SQL 문자열을 생성하고 매퍼를 호출하는 패턴.
* **리플렉션 처리**: `processWithReflection` 메서드를 통해 리플렉션 사용 및 예외 처리.
* **동적 MyBatis 연동**: `getFilteredDynamicData`, `updateDynamicStatuses` 메서드를 통해 동적 SQL을 포함하는 MyBatis 매퍼 호출.
* **레거시 데이터 처리**: `retrieveLegacyData`, `generateComplexReport` 메서드를 통해 레거시 시스템 데이터 조회 및 보고서 생성.
* **주석 표준화**: `calculateOrderTotal` 메서드는 표준화된 주석(`@MethodName`, `@Description`, `@Parameters`, `@Return`, `@Throws`)을 포함하여 메타정보 생성 시 지능적으로 코멘트를 만들어내는지 테스트합니다. `getFormattedId` 메서드는 부실한 주석의 예시입니다.
* **복잡 SQL 호출**: `getMonthlySalesAndTopCustomers` 등 5개의 메서드가 10개 테이블 조인, 서브쿼리, 스칼라 함수 호출 등을 포함하는 복잡한 SQL 쿼리를 매퍼를 통해 호출합니다.
* **대규모 파일 시뮬레이션**: `largeMethod1`부터 `largeMethod100`까지 100개의 더미 메서드를 포함하여 대규모 Java 파일 분석 성능을 테스트합니다.

**소스 위치**: `PROJECT/IntegratedSource/src/main/java/com/example/integrated/IntegratedService.java`

### 1.2. `IntegratedMapper.java`

`IntegratedService.java`에서 호출하는 모든 MyBatis 매퍼 메서드들을 정의한 인터페이스입니다. 기존 매퍼들의 메서드를 통합하고, 새로운 복잡 SQL 쿼리 및 일반 테스트 케이스를 위한 메서드들을 추가하였습니다.

**소스 위치**: `PROJECT/IntegratedSource/src/main/java/com/example/integrated/IntegratedMapper.java`

### 1.3. `IntegratedMapper.xml`

`IntegratedMapper.java` 인터페이스에 정의된 모든 SQL 쿼리들을 구현한 MyBatis XML 파일입니다. 기존 XML 파일들의 SQL을 통합하고, 새로운 테스트 요구사항을 반영한 SQL 쿼리들을 추가하였습니다. 주요 특징은 다음과 같습니다.

* **정적/동적 SQL**: `executeStaticQuery`, `executeDynamicQuery`를 통해 서비스에서 전달된 SQL을 직접 실행하는 패턴 (분석기 테스트용).
* **동적 MyBatis**: `<if>`, `<choose>`, `<foreach>` 등 동적 태그를 활용한 복잡한 쿼리 (`findDynamicData`, `updateDynamicStatus`). `DEL_YN = 'N'`과 같은 필수 필터 포함.
* **레거시 데이터**: 동적 WHERE 절을 포함하는 레거시 데이터 조회 쿼리 (`selectLegacyRecords`). `ACTIVE_FLAG = 'Y'`와 같은 필수 필터 포함.
* **복합 보고서**: CTE, 서브쿼리, 조인을 활용한 복합 보고서 쿼리 (`getComplexReport`).
* **일반 테스트 케이스**: `getActiveUsers`, `getOrdersByStatus`, `getProductDetails` 등 일반적인 CRUD 및 조회 쿼리.
* **ANSI JOIN**: `getOrdersWithCustomerAnsiJoin` 쿼리를 통해 ANSI SQL 표준 JOIN 문법 사용.
* **Oracle Implicit JOIN**: `getOrdersWithCustomerImplicitJoin` 쿼리를 통해 Oracle Implicit JOIN 방식 사용.
* **복잡 쿼리 5개**: 10개 테이블 조인, 서브쿼리, 스칼라 쿼리, SF 함수 호출을 포함하는 5개의 복잡한 SQL 쿼리 (`getSalesPerformanceReport`, `getCustomerActivitySummary`, `getProjectResourceUtilization`, `getFinancialTransactionAudit`, `getSupplyChainOptimization`).
* **주석 표준화**: 각 SQL 쿼리 상단에 `@TableName`, `@ColumnName`, `@Description` 등의 주석을 포함하여 메타정보 생성 시 지능적으로 코멘트를 만들어내는지 테스트합니다. 부실한 주석의 예시도 포함합니다.

**소스 위치**: `PROJECT/IntegratedSource/src/main/resources/mybatis/IntegratedMapper.xml`

### 1.4. `IntegratedView.jsp`

기존 `ProductQuery.jsp`, `CustomerQuery.jsp`, `dynamicSqlView.jsp`, `legacyView.jsp`의 JSP 로직들을 통합하고, 새로운 테스트 케이스를 위한 섹션들을 추가하였습니다. 주요 특징은 다음과 같습니다.

* **동적 SQL 생성**: 요청 파라미터에 따라 `PRODUCT` 및 `CUSTOMER` 테이블에 대한 동적 SQL 쿼리를 생성하는 스크립틀릿 예제. SQL Injection 취약점 패턴 포함.
* **JSTL & Scriptlet 동적 SQL**: JSTL 변수와 스크립틀릿을 조합하여 동적 SQL을 생성하는 예제.
* **백엔드 데이터 출력**: 백엔드에서 전달된 `legacyDataList` 및 `generatedReportContent`를 JSTL을 사용하여 테이블 및 `pre` 태그로 출력하는 예제.
* **주석 표준화**: `User Greeting Logic` 섹션은 표준화된 주석을 포함하고, `Poorly Commented Section`은 부실한 주석의 예시를 포함합니다.
* **대규모 파일 시뮬레이션**: 50개의 반복되는 섹션을 포함하여 대규모 JSP 파일 분석 성능을 테스트합니다.

**소스 위치**: `PROJECT/IntegratedSource/src/main/webapp/WEB-INF/jsp/IntegratedView.jsp`

### 1.5. `integratedHeader.jspf`

`IntegratedView.jsp`에 포함되는 헤더 프래그먼트 파일입니다.

**소스 위치**: `PROJECT/IntegratedSource/src/main/webapp/WEB-INF/jsp/_fragments/integratedHeader.jspf`

## 2. 통합 테스트 케이스 목록

아래 테스트 케이스들은 `PROJECT/IntegratedSource`에 통합된 샘플 소스 코드를 기반으로, 소스 분석기의 다양한 기능을 검증하기 위해 설계되었습니다. 각 테스트 케이스는 `테스트케이스_통합.md` 파일 내에서 어떤 소스 파일의 어떤 부분이 해당하는지 명확히 정리되어 있습니다.

### 2.1. TC_INTEGRATED_001_BasicJavaParsing: 기본 Java 코드 파싱 및 메타데이터 추출

* **Description**: `IntegratedService.java`의 `startProcess`, `doWork` 메서드와 `getStaticUserData` 등 기본 Java 메서드들이 정확히 파싱되고 메타데이터(클래스, 메서드)가 추출되는지 확인합니다.
* **Associated Source**: `IntegratedService.java` (`startProcess`, `doWork`, `getStaticUserData` 메서드)

### 2.2. TC_INTEGRATED_002_DynamicSQLGeneration: JSP 동적 SQL 생성 및 SQL Injection 탐지

* **Description**: `IntegratedView.jsp`에서 요청 파라미터에 따라 동적으로 생성되는 `PRODUCT` 및 `CUSTOMER` SQL 쿼리 문자열이 정확히 식별되고, SQL Injection 취약점 패턴 (`id = '...'`)이 탐지되는지 확인합니다.
* **Associated Source**: `IntegratedView.jsp` (Product 및 Customer SQL 생성 스크립틀릿)

### 2.3. TC_INTEGRATED_003_MyBatisDynamicSQL: MyBatis 동적 SQL 및 필수 필터 추출

* **Description**: `IntegratedMapper.xml`의 `findDynamicData` 쿼리에서 `<if>`, `<choose>`, `<foreach>` 등 동적 태그가 정확히 처리되고, `DEL_YN = 'N'`과 같은 필수 필터가 `required_filters` 테이블에 저장되는지 확인합니다.
* **Associated Source**: `IntegratedMapper.xml` (`findDynamicData` 쿼리)

### 2.4. TC_INTEGRATED_004_ComplexSQLParsing: 복잡 SQL (CTE, Subquery, ANSI/Implicit JOIN) 파싱

* **Description**: `IntegratedMapper.xml`의 `getComplexReport` 쿼리 (CTE, 서브쿼리, 조인) 및 `getOrdersWithCustomerAnsiJoin` (ANSI JOIN), `getOrdersWithCustomerImplicitJoin` (Oracle Implicit JOIN) 쿼리들이 정확히 파싱되고 조인 조건, 필터 등이 추출되는지 확인합니다.
* **Associated Source**: `IntegratedMapper.xml` (`getComplexReport`, `getOrdersWithCustomerAnsiJoin`, `getOrdersWithCustomerImplicitJoin` 쿼리)

### 2.5. TC_INTEGRATED_005_LLMCommentGeneration: LLM 기반 주석 생성 및 표준화

* **Description**: `IntegratedService.java`의 `calculateOrderTotal` 메서드 (표준 주석) 및 `IntegratedMapper.xml`의 `findDynamicData` 쿼리 (표준 주석)에 대해 LLM 기반으로 고품질 코멘트가 생성되는지, `getFormattedId` 메서드 (부실 주석)와 같은 케이스도 처리되는지 확인합니다.
* **Associated Source**: `IntegratedService.java` (`calculateOrderTotal`, `getFormattedId` 메서드), `IntegratedMapper.xml` (`findDynamicData` 쿼리 상단 주석)

### 2.6. TC_INTEGRATED_006_LargeFilePerformance: 대규모 파일 분석 성능

* **Description**: `IntegratedService.java` (100개 더미 메서드) 및 `IntegratedView.jsp` (50개 반복 섹션)와 같은 대규모 파일을 분석할 때, 분석기가 멀티스레드 방식으로 효율적으로 처리하여 성능 목표를 달성하는지 확인합니다.
* **Associated Source**: `IntegratedService.java` (`largeMethod1` ~ `largeMethod100`), `IntegratedView.jsp` (50개 반복 섹션)

### 2.7. TC_INTEGRATED_007_ComplexSQLQueries: 10개 테이블 조인 복잡 쿼리 5종

* **Description**: `IntegratedMapper.xml`에 새로 추가된 5개의 복잡한 SQL 쿼리 (`getSalesPerformanceReport`, `getCustomerActivitySummary`, `getProjectResourceUtilization`, `getFinancialTransactionAudit`, `getSupplyChainOptimization`)가 10개 테이블 조인, 서브쿼리, 스칼라 쿼리, SF 함수 호출 등을 포함하여 정확히 파싱되고 메타데이터가 추출되는지 확인합니다.
* **Associated Source**: `IntegratedMapper.xml` (5개 복잡 SQL 쿼리)

### 2.8. TC_INTEGRATED_008_ReflectionAndDynamicSQL: 리플렉션 및 동적 SQL 신뢰도

* **Description**: `IntegratedService.java`의 `processWithReflection` 메서드 (리플렉션 사용) 및 `getDynamicUserData` 메서드 (동적 SQL 사용)와 같이 신뢰도 감점 요인이 있는 코드에 대해 CONFIDENCE 점수가 낮게 측정되는지 확인합니다.
* **Associated Source**: `IntegratedService.java` (`processWithReflection`, `getDynamicUserData` 메서드)

## 3. DB 스키마 통합

기존 `DB_SCHEMA` 폴더 하위의 여러 `ALL_TABLES.csv`, `ALL_TAB_COLUMNS.csv`, `ALL_TAB_COMMENTS.csv`, `PK_INFO.csv` 파일들을 `E:\SourceAnalyzer.git\DB_SCHEMA` 경로로 통합하였습니다. 이 파일들은 통합 샘플 소스에서 참조하는 모든 테이블 및 컬럼 정보를 포함합니다.

**통합된 DB 스키마 파일 위치**:

* `E:\SourceAnalyzer.git\DB_SCHEMA\ALL_TABLES.csv`
* `E:\SourceAnalyzer.git\DB_SCHEMA\ALL_TAB_COLUMNS.csv`
* `E:\SourceAnalyzer.git\DB_SCHEMA\ALL_TAB_COMMENTS.csv`
* `E:\SourceAnalyzer.git\DB_SCHEMA\PK_INFO.csv`

## 4. 향후 테스트 시 도움될 정리

* **소스-테스트케이스 매핑**: 각 통합 테스트 케이스(`TC_INTEGRATED_XXX`)는 `PROJECT/IntegratedSource` 폴더 내의 특정 파일 및 코드 섹션과 직접적으로 연결됩니다. 테스트 수행 시 해당 소스 코드를 참조하여 분석 결과의 정확성을 검증할 수 있습니다.
* **DB 스키마 활용**: `IntegratedMapper.xml`에 정의된 SQL 쿼리들은 통합된 `DB_SCHEMA` 파일들을 참조합니다. 분석기가 SQL 내 테이블 및 컬럼을 DB 스키마와 정확히 매칭하는지 확인하는 데 활용됩니다.
* **주석 기반 메타정보**: `IntegratedService.java` 및 `IntegratedMapper.xml`에 포함된 표준화된 주석(`@MethodName`, `@TableName` 등)은 LLM 기반 코멘트 생성 및 메타정보 추출의 정확도를 테스트하는 데 중요한 역할을 합니다.
* **성능 측정**: 대규모 파일 (`IntegratedService.java`, `IntegratedView.jsp`) 분석 시 `config.yaml`의 `processing.max_workers` 설정을 변경하며 분석 시간을 측정하여 병렬 처리 성능을 검증할 수 있습니다.
* **CONFIDENCE 검증**: `IntegratedService.java`의 리플렉션 및 동적 SQL 사용, `IntegratedMapper.xml`의 동적 태그 사용 등은 CONFIDENCE 점수 감점 요인으로 작용합니다. 분석 후 생성된 메타데이터의 `confidence` 필드를 확인하여 산식의 정확성을 검증할 수 있습니다.
