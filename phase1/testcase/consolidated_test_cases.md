# 통합 테스트 케이스 - 소스 분석기 및 시각화 모듈

본 문서는 소스 분석 에이전트의 핵심 기능 및 개선 사항, 그리고 시각화 모듈의 기능을 검증하기 위한 통합 테스트 케이스와 샘플 소스 코드를 정의합니다. 기존 `prd_v4.md` 및 개발 리뷰 문서들의 요구사항을 종합하고, 테스트 시나리오를 추가하여 분석기의 정확성, 성능, 안정성 및 확장성을 대폭 향상시키기 위한 기반을 마련합니다.

---

## 1. 통합 샘플 소스 코드 개요 (From phase1/testcase/test_cases.md)

기존 `PROJECT` 폴더 하위의 여러 테스트케이스 및 샘플 소스들을 `PROJECT/IntegratedSource` 폴더로 통합하였습니다. 이 통합 소스는 다양한 Java, MyBatis XML, JSP 패턴을 포함하며, 새로운 테스트 요구사항을 반영합니다.

### 1.1. `IntegratedService.java`

기존 `Example1`, `Example3`, `DynamicMyBatis`, `MixedTechLegacy` 프로젝트의 Java 코드들을 통합하고, 새로운 테스트 케이스를 위한 메서드들을 추가하였습니다. 주요 특징은 다음과 같습니다.

*   **기본 Java 로직**: `startProcess`, `doWork` 등 간단한 메서드 호출 관계.
*   **정적/동적 SQL 호출**: `getStaticUserData`, `getDynamicUserData` 메서드를 통해 정적 SQL과 동적 SQL 문자열을 생성하고 매퍼를 호출하는 패턴.
*   **리플렉션 처리**: `processWithReflection` 메서드를 통해 리플렉션 사용 및 예외 처리.
*   **동적 MyBatis 연동**: `getFilteredDynamicData`, `updateDynamicStatuses` 메서드를 통해 동적 SQL을 포함하는 MyBatis 매퍼 호출.
*   **레거시 데이터 처리**: `retrieveLegacyData`, `generateComplexReport` 메서드를 통해 레거시 시스템 데이터 조회 및 보고서 생성.
*   **주석 표준화**: `calculateOrderTotal` 메서드는 표준화된 주석(`@MethodName`, `@Description`, `@Parameters`, `@Return`, `@Throws`)을 포함하여 메타정보 생성 시 지능적으로 코멘트를 만들어내는지 테스트합니다. `getFormattedId` 메서드는 부실한 주석의 예시입니다.
*   **복잡 SQL 호출**: `getMonthlySalesAndTopCustomers` 등 5개의 메서드가 10개 테이블 조인, 서브쿼리, 스칼라 함수 호출 등을 포함하는 복잡한 SQL 쿼리를 매퍼를 통해 호출합니다.
*   **대규모 파일 시뮬레이션**: `largeMethod1`부터 `largeMethod100`까지 100개의 더미 메서드를 포함하여 대규모 Java 파일 분석 성능을 테스트합니다.

**소스 위치**: `PROJECT/IntegratedSource/src/main/java/com/example/integrated/IntegratedService.java`

### 1.2. `IntegratedMapper.java`

`IntegratedService.java`에서 호출하는 모든 MyBatis 매퍼 메서드들을 정의한 인터페이스입니다. 기존 매퍼들의 메서드를 통합하고, 새로운 복잡 SQL 쿼리 및 일반 테스트 케이스를 위한 메서드들을 추가하였습니다.

**소스 위치**: `PROJECT/IntegratedSource/src/main/java/com/example/integrated/IntegratedMapper.java`

### 1.3. `IntegratedMapper.xml`

`IntegratedMapper.java` 인터페이스에 정의된 모든 SQL 쿼리들을 구현한 MyBatis XML 파일입니다. 기존 XML 파일들의 SQL을 통합하고, 새로운 테스트 요구사항을 반영한 SQL 쿼리들을 추가하였습니다. 주요 특징은 다음과 같습니다.

*   **정적/동적 SQL**: `executeStaticQuery`, `executeDynamicQuery`를 통해 서비스에서 전달된 SQL을 직접 실행하는 패턴 (분석기 테스트용).
*   **동적 MyBatis**: `<if>`, `<choose>`, `<foreach>` 등 동적 태그를 활용한 복잡한 쿼리 (`findDynamicData`, `updateDynamicStatus`). `DEL_YN = 'N'`과 같은 필수 필터 포함.
*   **레거시 데이터**: 동적 WHERE 절을 포함하는 레거시 데이터 조회 쿼리 (`selectLegacyRecords`). `ACTIVE_FLAG = 'Y'`와 같은 필수 필터 포함.
*   **복합 보고서**: CTE, 서브쿼리, 조인을 활용한 복합 보고서 쿼리 (`getComplexReport`).
*   **일반 테스트 케이스**: `getActiveUsers`, `getOrdersByStatus`, `getProductDetails` 등 일반적인 CRUD 및 조회 쿼리.
*   **ANSI JOIN**: `getOrdersWithCustomerAnsiJoin` 쿼리를 통해 ANSI SQL 표준 JOIN 문법 사용.
*   **Oracle Implicit JOIN**: `getOrdersWithCustomerImplicitJoin` 쿼리를 통해 Oracle Implicit JOIN 방식 사용.
*   **복잡 쿼리 5개**: 10개 테이블 조인, 서브쿼리, 스칼라 쿼리, SF 함수 호출을 포함하는 5개의 복잡한 SQL 쿼리 (`getSalesPerformanceReport`, `getCustomerActivitySummary`, `getProjectResourceUtilization`, `getFinancialTransactionAudit`, `getSupplyChainOptimization`).
*   **주석 표준화**: 각 SQL 쿼리 상단에 `@TableName`, `@ColumnName`, `@Description` 등의 주석을 포함하여 메타정보 생성 시 지능적으로 코멘트를 만들어내는지 테스트합니다. 부실한 주석의 예시도 포함합니다.

**소스 위치**: `PROJECT/IntegratedSource/src/main/resources/mybatis/IntegratedMapper.xml`

### 1.4. `IntegratedView.jsp`

기존 `ProductQuery.jsp`, `CustomerQuery.jsp`, `dynamicSqlView.jsp`, `legacyView.jsp`의 JSP 로직들을 통합하고, 새로운 테스트 케이스를 위한 섹션들을 추가하였습니다. 주요 특징은 다음과 같습니다.

*   **동적 SQL 생성**: 요청 파라미터에 따라 `PRODUCT` 및 `CUSTOMER` 테이블에 대한 동적 SQL 쿼리를 생성하는 스크립틀릿 예제. SQL Injection 취약점 패턴 포함.
*   **JSTL & Scriptlet 동적 SQL**: JSTL 변수와 스크립틀릿을 조합하여 동적 SQL을 생성하는 예제.
*   **백엔드 데이터 출력**: 백엔드에서 전달된 `legacyDataList` 및 `generatedReportContent`를 JSTL을 사용하여 테이블 및 `pre` 태그로 출력하는 예제.
*   **주석 표준화**: `User Greeting Logic` 섹션은 표준화된 주석을 포함하고, `Poorly Commented Section`은 부실한 주석의 예시를 포함합니다.
*   **대규모 파일 시뮬레이션**: 50개의 반복되는 섹션을 포함하여 대규모 JSP 파일 분석 성능을 테스트합니다.

**소스 위치**: `PROJECT/IntegratedSource/src/main/webapp/WEB-INF/jsp/IntegratedView.jsp`

### 1.5. `integratedHeader.jspf`

`IntegratedView.jsp`에 포함되는 헤더 프래그먼트 파일입니다.

**소스 위치**: `PROJECT/IntegratedSource/src/main/webapp/WEB-INF/jsp/_fragments/integratedHeader.jspf`

---

## 2. 통합 테스트 케이스 목록 (From phase1/testcase/test_cases.md)

아래 테스트 케이스들은 `PROJECT/IntegratedSource`에 통합된 샘플 소스 코드를 기반으로, 소스 분석기의 다양한 기능을 검증하기 위해 설계되었습니다. 각 테스트 케이스는 `테스트케이스_통합.md` 파일 내에서 어떤 소스 파일의 어떤 부분이 해당하는지 명확히 정리되어 있습니다.

### 2.1. TC_INTEGRATED_001_BasicJavaParsing: 기본 Java 코드 파싱 및 메타데이터 추출

*   **Description**: `IntegratedService.java`의 `startProcess`, `doWork` 메서드와 `getStaticUserData` 등 기본 Java 메서드들이 정확히 파싱되고 메타데이터(클래스, 메서드)가 추출되는지 확인합니다.
*   **Associated Source**: `IntegratedService.java` (`startProcess`, `doWork`, `getStaticUserData` 메서드)

### 2.2. TC_INTEGRATED_002_DynamicSQLGeneration: JSP 동적 SQL 생성 및 SQL Injection 탐지

*   **Description**: `IntegratedView.jsp`에서 요청 파라미터에 따라 동적으로 생성되는 `PRODUCT` 및 `CUSTOMER` SQL 쿼리 문자열이 정확히 식별되고, SQL Injection 취약점 패턴 (`id = '...'`)이 탐지되는지 확인합니다.
*   **Associated Source**: `IntegratedView.jsp` (Product 및 Customer SQL 생성 스크립틀릿)

### 2.3. TC_INTEGRATED_003_MyBatisDynamicSQL: MyBatis 동적 SQL 및 필수 필터 추출

*   **Description**: `IntegratedMapper.xml`의 `findDynamicData` 쿼리에서 `<if>`, `<choose>`, `<foreach>` 등 동적 태그가 정확히 처리되고, `DEL_YN = 'N'`과 같은 필수 필터가 `required_filters` 테이블에 저장되는지 확인합니다.
*   **Associated Source**: `IntegratedMapper.xml` (`findDynamicData` 쿼리)

### 2.4. TC_INTEGRATED_004_ComplexSQLParsing: 복잡 SQL (CTE, Subquery, ANSI/Implicit JOIN) 파싱

*   **Description**: `IntegratedMapper.xml`의 `getComplexReport` 쿼리 (CTE, 서브쿼리, 조인) 및 `getOrdersWithCustomerAnsiJoin` (ANSI JOIN), `getOrdersWithCustomerImplicitJoin` (Oracle Implicit JOIN) 쿼리들이 정확히 파싱되고 조인 조건, 필터 등이 추출되는지 확인합니다.
*   **Associated Source**: `IntegratedMapper.xml` (`getComplexReport`, `getOrdersWithCustomerAnsiJoin`, `getOrdersWithCustomerImplicitJoin` 쿼리)

### 2.5. TC_INTEGRATED_005_LLMCommentGeneration: LLM 기반 주석 생성 및 표준화

*   **Description**: `IntegratedService.java`의 `calculateOrderTotal` 메서드 (표준 주석) 및 `IntegratedMapper.xml`의 `findDynamicData` 쿼리 (표준 주석)에 대해 LLM 기반으로 고품질 코멘트가 생성되는지, `getFormattedId` 메서드 (부실 주석)와 같은 케이스도 처리되는지 확인합니다.
*   **Associated Source**: `IntegratedService.java` (`calculateOrderTotal`, `getFormattedId` 메서드), `IntegratedMapper.xml` (`findDynamicData` 쿼리 상단 주석)

### 2.6. TC_INTEGRATED_006_LargeFilePerformance: 대규모 파일 분석 성능

*   **Description**: `IntegratedService.java` (100개 더미 메서드) 및 `IntegratedView.jsp` (50개 반복 섹션)와 같은 대규모 파일을 분석할 때, 분석기가 멀티스레드 방식으로 효율적으로 처리하여 성능 목표를 달성하는지 확인합니다.
*   **Associated Source**: `IntegratedService.java` (`largeMethod1` ~ `largeMethod100`), `IntegratedView.jsp` (50개 반복 섹션)

### 2.7. TC_INTEGRATED_007_ComplexSQLQueries: 10개 테이블 조인 복잡 쿼리 5종

*   **Description**: `IntegratedMapper.xml`에 새로 추가된 5개의 복잡한 SQL 쿼리 (`getSalesPerformanceReport`, `getCustomerActivitySummary`, `getProjectResourceUtilization`, `getFinancialTransactionAudit`, `getSupplyChainOptimization`)가 10개 테이블 조인, 서브쿼리, 스칼라 쿼리, SF 함수 호출 등을 포함하여 정확히 파싱되고 메타데이터가 추출되는지 확인합니다.
*   **Associated Source**: `IntegratedMapper.xml` (5개 복잡 SQL 쿼리)

### 2.8. TC_INTEGRATED_008_ReflectionAndDynamicSQL: 리플렉션 및 동적 SQL 신뢰도

*   **Description**: `IntegratedService.java`의 `processWithReflection` 메서드 (리플렉션 사용) 및 `getDynamicUserData` 메서드 (동적 SQL 사용)와 같이 신뢰도 감점 요인이 있는 코드에 대해 CONFIDENCE 점수가 낮게 측정되는지 확인합니다.
*   **Associated Source**: `IntegratedService.java` (`processWithReflection`, `getDynamicUserData` 메서드)

### 2.9. TC_INTEGRATED_009_VulnerabilityDetection: 보안 취약점 탐지 및 저장

*   **Description**: `VulnerabilityTestService.java`에 포함된 다양한 보안 취약점 (SQL Injection, XSS, Path Traversal, 하드코딩된 자격증명, 약한 암호화 등)이 정확히 탐지되고 `vulnerability_fixes` 테이블에 저장되는지 확인합니다.
*   **Associated Source**: `VulnerabilityTestService.java` (모든 취약점 메서드)

### 2.10. TC_INTEGRATED_010_IncrementalAnalysis: 증분 분석 기능

*   **Description**: `--incremental` 플래그를 사용하여 파일 해시 기반으로 변경된 파일만 분석하는 증분 분석 기능이 올바르게 동작하는지 확인합니다. 파일 변경 전후로 분석을 수행하여 변경된 파일만 처리되는지 검증합니다.
*   **Test Steps**:
    1.  전체 프로젝트 분석 수행
    2.  특정 파일 수정 (예: IntegratedService.java의 메서드 하나 수정)
    3.  `--incremental` 플래그로 재분석 수행
    4.  변경된 파일만 처리되는지 로그 확인

### 2.11. TC_INTEGRATED_011_MethodCallResolution: 메서드 호출 관계 해결

*   **Description**: `IntegratedService.java`에서 `integratedMapper`의 메서드를 호출하는 관계가 올바르게 해결되어 `edges` 테이블에 저장되고, 신뢰도 점수가 적절히 계산되는지 확인합니다.
*   **Associated Source**: `IntegratedService.java`의 매퍼 메서드 호출 (`integratedMapper.executeStaticQuery()` 등)

### 2.12. TC_INTEGRATED_012_ConfidenceThresholding: 신뢰도 임계값 필터링

*   **Description**: `config.yaml`에서 `confidence_threshold` 값을 설정하고, 설정값보다 낮은 신뢰도를 가진 엣지나 분석 결과가 필터링되어 저장되지 않는지 확인합니다.
*   **Test Steps**:
    1.  `confidence_threshold: 0.7`로 설정
    2.  프로젝트 분석 수행
    3.  저장된 `edges` 테이블에서 모든 레코드의 `confidence` 값이 0.7 이상인지 확인

### 2.13. TC_INTEGRATED_013_DatabaseSchemaFlexibility: DB 스키마 소유자 유연화

*   **Description**: `config.yaml`에서 `database.default_schema` 설정을 통해 하드코딩된 'SAMPLE' 소유자 대신 설정 파일의 값을 사용하여 테이블을 매칭하는지 확인합니다.
*   **Test Steps**:
    1.  `config.yaml`에서 `database.default_schema: PUBLIC` 설정
    2.  프로젝트 분석 수행
    3.  PUBLIC 스키마의 테이블들이 올바르게 매칭되는지 확인

### 2.14. TC_INTEGRATED_014_ComplexityAnalysis: 코드 복잡도 분석

*   **Description**: `VulnerabilityTestService.java`의 `processComplexBusiness` 메서드와 같이 중첩된 조건문, 복잡한 표현식을 포함한 메서드의 복잡도가 올바르게 계산되고 신뢰도에 반영되는지 확인합니다.
*   **Associated Source**: `VulnerabilityTestService.java` (`processComplexBusiness` 메서드)

---

## 3. DB 스키마 통합 (From phase1/testcase/test_cases.md)

기존 `DB_SCHEMA` 폴더 하위의 여러 `ALL_TABLES.csv`, `ALL_TAB_COLUMNS.csv`, `ALL_TAB_COMMENTS.csv`, `PK_INFO.csv` 파일들을 `E:\SourceAnalyzer.git\DB_SCHEMA` 경로로 통합하였습니다. 이 파일들은 통합 샘플 소스에서 참조하는 모든 테이블 및 컬럼 정보를 포함합니다.

**통합된 DB 스키마 파일 위치**:

*   `E:\SourceAnalyzer.git\DB_SCHEMA\ALL_TABLES.csv`
*   `E:\SourceAnalyzer.git\DB_SCHEMA\ALL_TAB_COLUMNS.csv`
*   `E:\SourceAnalyzer.git\DB_SCHEMA\ALL_TAB_COMMENTS.csv`
*   `E:\SourceAnalyzer.git\DB_SCHEMA\PK_INFO.csv`

---

## 4. 향후 테스트 시 도움될 정리 (From phase1/testcase/test_cases.md)

*   **소스-테스트케이스 매핑**: 각 통합 테스트 케이스(`TC_INTEGRATED_XXX`)는 `PROJECT/IntegratedSource` 폴더 내의 특정 파일 및 코드 섹션과 직접적으로 연결됩니다. 테스트 수행 시 해당 소스 코드를 참조하여 분석 결과의 정확성을 검증할 수 있습니다.
*   **DB 스키마 활용**: `IntegratedMapper.xml`에 정의된 SQL 쿼리들은 통합된 `DB_SCHEMA` 파일들을 참조합니다. 분석기가 SQL 내 테이블 및 컬럼을 DB 스키마와 정확히 매칭하는지 확인하는 데 활용됩니다.
*   **주석 기반 메타정보**: `IntegratedService.java` 및 `IntegratedMapper.xml`에 포함된 표준화된 주석(`@MethodName`, `@TableName` 등)은 LLM 기반 코멘트 생성 및 메타정보 추출의 정확도를 테스트하는 데 중요한 역할을 합니다.
*   **성능 측정**: 대규모 파일 (`IntegratedService.java`, `IntegratedView.jsp`) 분석 시 `config.yaml`의 `processing.max_workers` 설정을 변경하며 분석 시간을 측정하여 병렬 처리 성능을 검증할 수 있습니다.
*   **CONFIDENCE 검증**: `IntegratedService.java`의 리플렉션 및 동적 SQL 사용, `IntegratedMapper.xml`의 동적 태그 사용 등은 CONFIDENCE 점수 감점 요인으로 작용합니다. 분석 후 생성된 메타데이터의 `confidence` 필드를 확인하여 산식의 정확성을 검증할 수 있습니다.

---

## 5. Phase1 Analyzer Testcases (From phase1/testcase/testcase.md)

본 문서는 phase1 분석 파이프라인(파서/메타DB 저장/그래프 빌드)의 수동 테스트 시나리오입니다. PROJECT의 샘플 소스는 본 테스트를 위해 일부 추가되었습니다.

### 5.0. 사전 준비

-   Python 3.10+, `pip install -r requirements.txt`
-   설정: `config/config.yaml` (기본 사용)
-   분석 대상: `PROJECT/sampleSrc`

### 5.1. 실행

```bash
python phase1/src/main.py PROJECT/sampleSrc --project-name sample --config config/config.yaml
```

기대 결과:
-   `data/metadata.db` 생성
-   콘솔/로그에 분석 요약 출력

### 5.2. MyBatis 조인 추출 검증 (v1.4 확장)

대상 파일: `PROJECT/sampleSrc/src/main/resources/mybatis/TestJoinMapper.xml`

체크 포인트:
-   `sql_units`에 `selectUserOrders`, `selectUserOrdersWithInclude`, `selectCompositeJoin` 등록
-   **v1.4 신규**: 동적 SQL 처리 검증
    -   `selectDynamicChoose`: `<bind>`, `<choose>/<when>/<otherwise>` 처리
    -   `selectWithForeach`: `<foreach>` IN 표현으로 요약
    -   `selectWithNestedInclude`: 중첩된 `<include>`과 `<where>/<if>` 처리
-   `joins`에 다음 패턴 존재:
    -   `SAMPLE.USERS.USER_ID = SAMPLE.ORDERS.USER_ID`
    -   `SAMPLE.ORDER_ITEMS.ORDER_ID = SAMPLE.ORDERS.ORDER_ID`
    -   `SAMPLE.ORDER_ITEMS.PRODUCT_ID = SAMPLE.PRODUCTS.PRODUCT_ID`

검증 방법(예: sqlite3):
```sql
.open data/metadata.db
select * from sql_units where stmt_id in ('selectUserOrders','selectUserOrdersWithInclude','selectCompositeJoin');
select l_table,l_col,r_table,r_col from joins;
```

### 5.3. JSP include / JSP SQL 검출 검증

대상 파일: `PROJECT/sampleSrc/src/main/webapp/WEB-INF/jsp/test/testPage.jsp`

체크 포인트:
-   JSP SQL 패턴 1건 이상 검출(`sql_units.origin='jsp'`)
-   include 후보(헤더/통합헤더) 추출 → 빌드 후 `edges.edge_kind='include'` 추가(보강 시)

예시 질의:
```sql
select origin, stmt_id from sql_units where file_id in (
  select file_id from files where path like '%/WEB-INF/jsp/test/testPage.jsp'
);
```

### 5.4. Java 호출/오버로드/정적 임포트 검증(보강 시)

대상 파일:
-   `PROJECT/sampleSrc/src/main/java/com/example/service/OverloadService.java`
-   `PROJECT/sampleSrc/src/main/java/com/example/util/Texts.java`
-   `PROJECT/sampleSrc/src/main/java/com/example/service/impl/ListServiceImpl1.java`

체크 포인트:
-   `classes/methods`에 OverloadService, find(int), find(String), process() 등록
-   call 힌트(edge_hints) 생성 → 그래프 빌드 후 `edges(edge_kind='call')`로 일부 해소
-   static import(`Texts.isEmpty`)는 낮은 confidence로 후보 연결 또는 보류

예시 질의:
```sql
select name, signature from methods m join classes c on m.class_id=c.class_id where c.name='OverloadService';
select count(*) from edges where edge_kind='call';
```

### 5.5. 테이블 사용(use_table) / PK-FK 추론 검증

체크 포인트:
-   `edges(edge_kind='use_table')`가 sql_unit→db_table로 생성
-   빈도/PK 교차검증(보강 시)로 `joins.inferred_pkfk=1` 및 confidence 보정

예시 질의:
```sql
select edge_kind,count(*) from edges group by edge_kind;
select inferred_pkfk, count(*) from joins group by inferred_pkfk;
```

### 5.6. 로그/에러 확인

-   파일: `logs/analyzer.log`
-   실패/예외 로그가 없는지 확인

### 5.7. v1.4 신규 기능 테스트

#### 5.7.1 동적 SQL 해석 테스트
```bash
# 동적 SQL이 포함된 매퍼에서 조건/분기 보존 확인
python phase1/src/main.py PROJECT/sampleSrc --project-name sample --config config/config.yaml
```

검증 항목:
-   `<bind>` 변수가 정규화된 SQL에 적절히 치환
-   `<choose>/<when>` 분기가 대표 분기로 요약되고 주석 보존
-   `<foreach>` 블록이 `IN (:list[])` 형태로 요약

#### 5.7.2 Mermaid 내보내기 개선 테스트
```bash
# 다양한 export strategy 테스트
python visualize_cli.py graph --project-id 1 --out test_full.html --export-strategy full
python visualize_cli.py graph --project-id 1 --out test_balanced.html --export-strategy balanced --min-confidence 0.4
python visualize_cli.py class --project-id 1 --out test_class.html --class-methods-max 5 --class-attrs-max 8
```

### 5.8. 주의/한계

-   javalang 미설치 시 Java 파싱 스킵될 수 있음(requirements 설치 필요)
-   DB_SCHEMA CSV가 충분하지 않으면 PK 교차검증 결과가 달라질 수 있음
-   v1.4에서 추가된 DynamicSqlResolver는 lxml이 필요함

---

## 6. Source Analyzer Visualization Testcases (From visualize/testcase/testcase.md)

본 문서는 Visualize_Implementation_Plan_v001.md의 구현 완료 후 기능 검증을 위한 테스트 시나리오입니다. 개발자는 .md 설계를 숙지하고 있으며, 아래 케이스는 실제 실행 관점에서 작성되었습니다.

주의: 본 문서는 구현 완료 후 수행을 전제로 하며, `visualize` CLI와 빌더/템플릿이 동작한다는 가정하에 기술합니다.

### 6.0. 사전 준비

-   Python 3.10+, `pip install -r requirements.txt`
-   설정 파일: `config/config.yaml` (기본 그대로 사용)
-   메타DB 초기화용 분석 실행:
    -   명령: `python phase1/src/main.py PROJECT/sampleSrc --project-name sample --config config/config.yaml`
    -   기대: `data/metadata.db` 생성, 로그는 `logs/analyzer.log`
-   성공 기준(대략):
    -   프로젝트/파일/SQL 단위가 DB에 적재됨
    -   `joins`, `required_filters`, `db_tables`, `db_pk` 등이 존재

### 6.1. ERD 시나리오

TC-ERD-01 기본 ERD 생성
-   목적: 전체 테이블 기반 ERD 생성
-   명령: `python -m visualize erd --project-id 1 --out visualize/output/erd_all.html`
-   기대:
    -   HTML 파일 생성, 테이블 노드 다수 표시
    -   노드 라벨: `OWNER.TABLE` 형식(대문자)

TC-ERD-02 소유자/테이블 필터
-   목적: 특정 오너/테이블만 표현
-   명령: `python -m visualize erd --project-id 1 --owners SAMPLE --tables USERS,ORDERS --out visualize/output/erd_subset.html`
-   기대: `SAMPLE.USERS`, `SAMPLE.ORDERS` 노드만 존재, 기타 노드는 없음

TC-ERD-03 FK 추론 시각화
-   목적: 조인 패턴 기반 FK 추론 엣지 확인
-   명령: `python -m visualize erd --project-id 1 --out visualize/output/erd_fk.html`
-   기대:
    -   `fk_inferred` 엣지가 표시되고, confidence>0.85인 엣지는 진한 색/굵기
    -   동일 테이블 페어에 복수 컬럼 조인(복합키 후보) 시 confidence가 소폭 상향

TC-ERD-04 SQL 기반 부분 ERD
-   목적: 특정 쿼리가 참조하는 테이블만 부분 ERD 생성
-   명령 예: `python -m visualize erd --project-id 1 --from-sql UserMapper:selectUser --out visualize/output/erd_from_sql.html`
-   기대: 해당 SQL이 참조하는 테이블만 노드로 표시

### 6.2. 의존성 그래프 시나리오

TC-GRAPH-01 테이블 사용 그래프
-   목적: SQL→TABLE 의존 확인
-   명령: `python -m visualize graph --project-id 1 --kinds use_table --out visualize/output/graph_use_table.html`
-   기대: `sql` 타입 노드에서 `table` 노드로 향하는 엣지 존재

TC-GRAPH-02 include 그래프
-   목적: JSP/JSP 및 MyBatis include 엣지 표시
-   명령: `python -m visualize graph --project-id 1 --kinds include --out visualize/output/graph_include.html`
-   기대: 파일 간 include 엣지 존재(뷰어 클릭 시 대상 경로 표시)

TC-GRAPH-03 confidence 필터
-   목적: `--min-confidence` 적용 확인
-   명령: `python -m visualize graph --project-id 1 --kinds use_table,include --min-confidence 0.9 --out visualize/output/graph_conf90.html`
-   기대: 낮은 신뢰도의 엣지는 제외되어 그래프가 간결해짐

TC-GRAPH-04 포커스/깊이 제한
-   목적: 특정 노드를 기준으로 BFS 제한 적용
-   명령: `python -m visualize graph --project-id 1 --kinds use_table --focus SAMPLE.USERS --depth 1 --out visualize/output/graph_focus_users.html`
-   기대: `SAMPLE.USERS`와 1단계 이웃만 표시

TC-GRAPH-05 노드 상한(max_nodes)
-   목적: 대규모 그래프 상한 적용 확인
-   명령: `python -m visualize graph --project-id 1 --kinds use_table,include --max-nodes 200 --out visualize/output/graph_cap200.html`
-   기대: 200개 내 노드로 잘림(툴바/경고 표시)

### 6.3. 컴포넌트 다이어그램 시나리오

TC-COMP-01 기본 컴포넌트 표시
-   목적: 규칙 기반 그룹핑 확인
-   명령: `python -m visualize component --project-id 1 --out visualize/output/components.html`
-   기대:
    -   컨트롤러/서비스/레포지토리/매퍼/JSP/DB 그룹 노드 색 구분
    -   교차 컴포넌트 엣지(집계) 표시, 툴팁에 집계 수/평균 confidence

TC-COMP-02 규칙 튜닝
-   목적: 규칙 변경 시 그룹핑 변화 확인
-   절차: `config/config.yaml`에 `visualize.component_rules` 추가/수정 → 재실행
-   기대: 해당 규칙에 따라 그룹 배정이 달라짐

### 6.4. 시퀀스(흐름) 다이어그램 시나리오

TC-SEQ-01 JSP 중심 흐름
-   목적: JSP→SQL→TABLE 흐름 표시
-   명령: `python -m visualize sequence --project-id 1 --start-file PROJECT/sampleSrc/src/main/webapp/WEB-INF/jsp/user/userList.jsp --out visualize/output/seq_jsp.html`
-   기대: 시작 JSP에서 관련 SQL, 그 SQL이 참조하는 TABLE로의 흐름이 레이어로 배치

TC-SEQ-02 메서드 호출 반영(보강 후)
-   목적: Java call 해소 후 Controller→Service→Repository/Mapper 흐름 포함
-   명령: `python -m visualize sequence --project-id 1 --start-method com.example.service.UserService.listUsers --depth 3 --out visualize/output/seq_java.html`
-   기대: 메서드 간 call 체인이 시간축 유사 계층으로 표현(미해소 호출은 낮은 confidence 또는 점선 스타일)

### 6.5. 메타 보강 기능 시나리오

TC-META-01 edge_hints 생성/소비(메서드 호출)
-   목적: 파서→edge_hints→edges(call) 파이프라인 검증
-   절차:
    1)  분석 실행 전 `data/metadata.db` 삭제(신규 분석)
    2)  분석 실행 후 DB 확인: `edge_hints(hint_type='method_call')` 존재
    3)  `build_dependency_graph()` 수행(분석 과정에서 자동)
    4)  DB 확인: `edges(edge_kind='call', dst_id not null)` 증가, 해당 `edge_hints`는 삭제됨
-   기대: call 엣지가 생성되고 hints는 소비됨

TC-META-02 include 힌트 해소
-   목적: JSP include 힌트→include 엣지 검증
-   절차: 위와 동일 플로우로 `edge_hints('jsp_include')`가 `edges('include')`로 전환되는지 확인

### 6.6. SQL 조인키 도출 강화 시나리오

TC-JOIN-01 별칭(alias) 해소
-   목적: `a.id=b.user_id` 형태에서 a,b→OWNER.TABLE 치환 확인
-   방법: MyBatis XML이나 JSP에 다음과 유사한 테스트 쿼리를 임시 추가 후 분석:
    ```sql
    SELECT * FROM USERS u JOIN ORDERS o ON u.USER_ID = o.USER_ID
    ```
-   기대: `joins`에 `SAMPLE.USERS.USER_ID = SAMPLE.ORDERS.USER_ID` 저장, ERD에 fk_inferred 후보 표시

TC-JOIN-02 스키마 정규화
-   목적: `owner.table`/`table` 혼재 시 OWNER 대문자/테이블 대문자로 정규화
-   기대: ERD/그래프의 테이블 라벨이 일관되게 `OWNER.TABLE`

TC-JOIN-03 PK 교차검증
-   목적: `DbPk` 기준으로 한쪽이 PK인 조인에서 inferred_pkfk=1 & confidence 상향
-   절차: `DB_SCHEMA/PK_INFO.csv`에 USERS.USER_ID가 PK임을 확인
-   기대: USERS(USER_ID)↔ORDERS(USER_ID) 조인 시 inferred_pkfk=1, confidence≥0.85

TC-JOIN-04 복합키 추론
-   목적: 동일 페어에서 두 컬럼 이상 조인 시 복합키 후보 상향
-   방법: 테스트 쿼리(예: ORDER_ITEMS(ORDER_ID, PRODUCT_ID)↔ORDERS(ORDER_ID) & PRODUCTS(PRODUCT_ID))를 포함한 매퍼를 임시 추가
-   기대: 동일 페어 빈도≥2 → confidence 소폭 상향, 스타일 반영

### 6.7. 정확성(오버로드/정적 임포트/동적 바인딩)

TC-CALL-01 오버로드 구분
-   목적: 동일 메서드명 다른 시그니처에서 arg_count 우선 매칭 동작 확인
-   방법: `UserService`에 `find(int id)`/`find(String id)` 존재 시, 호출 인자 유형에 따라 다른 대상 매칭 여부 확인
-   기대: 인자 수/유형이 맞는 메서드로 우선 연결(confidence 가중치 상향)

TC-CALL-02 정적 임포트
-   목적: qualifier 없는 호출이 static import된 유틸로 연결되는지 확인
-   방법: `import static com.example.util.Texts.isEmpty;` 후 `isEmpty(name)` 호출
-   기대: `Texts.isEmpty`로 resolve 또는 후보 다중 생성(낮은 confidence)

TC-CALL-03 동적 바인딩
-   목적: 인터페이스 타입 수신자의 구현 후보 분산 연결
-   방법: `ListService` 인터페이스와 `ListServiceImpl1/2` 구현, 호출 시 두 구현 중 후보 엣지 생성
-   기대: 복수 call 엣지 생성, confidence 분산(예: 0.5/개수)

### 6.8. Confidence/필터링/성능

TC-CF-01 min-confidence 필터링
-   목적: 낮은 신뢰도 엣지 제거 확인(그래프 간결화)
-   명령: `--min-confidence 0.9` vs `0.5` 비교
-   기대: 0.9에서 엣지 수가 현저히 감소

TC-CF-02 suspect 마킹 유지
-   목적: `_SUSPECT` stmt_id 포함 여부 및 시각화 라벨 확인
-   기대: 라벨에 `_SUSPECT` 접미사 표기 또는 다른 스타일 적용

TC-PERF-01 노드 cap 성능 확인
-   목적: 1000+ 노드 시 레이아웃 시간/상호작용 확인
-   명령: `--max-nodes 500`/`2000` 변경하여 반응성 비교
-   기대: cap이 낮을수록 렌더가 빨라짐

### 6.9. PNG Export

TC-PNG-01 PNG 내보내기
-   목적: 뷰어 버튼으로 PNG 저장 확인
-   절차: 임의 그래프 열기 → `Export PNG` 클릭 → 파일 저장 확인
-   기대: `graph.png` 다운로드, 해상도(scale=2) 적용됨

### 6.10. 예외/에지 케이스

TC-EX-01 DB 스키마 미존재
-   목적: DB_SCHEMA 누락 시 안전한 경고/동작 확인
-   절차: 임시로 DB_SCHEMA 경로를 비우고 분석
-   기대: 경고 로그 후 계속 진행, ERD는 비어 있거나 제한적으로 생성

TC-EX-02 잘못된 owners/tables 인자
-   목적: 존재하지 않는 테이블 필터 지정 시 빈 그래프 처리
-   기대: 빈 노드/엣지로 HTML 생성하되 오류 없이 로딩됨

---

## 7. 검증 레코딩 가이드 (From visualize/testcase/testcase.md)

-   각 케이스 수행 후 `visualize/output/*.html` 스냅샷 보관
-   필요 시 브라우저 콘솔에 `DATA.nodes.length`, `DATA.edges.length`로 개수 확인
-   DB 확인은 `sqlite3 data/metadata.db` 또는 DB 클라이언트 사용
