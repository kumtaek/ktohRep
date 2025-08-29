# Phase1 Analyzer Testcases

본 문서는 phase1 분석 파이프라인(파서/메타DB 저장/그래프 빌드)의 수동 테스트 시나리오입니다. PROJECT의 샘플 소스는 본 테스트를 위해 일부 추가되었습니다.

## 0. 사전 준비

-   Python 3.10+, `pip install -r requirements.txt`
-   설정: `config/config.yaml` (기본 사용)
-   분석 대상: `PROJECT/sampleSrc`

## 1. 실행

```bash
python phase1/src/main.py PROJECT/sampleSrc --project-name sample --config config/config.yaml
```

기대 결과:
-   `data/metadata.db` 생성
-   콘솔/로그에 분석 요약 출력

## 2. MyBatis 조인 추출 검증 (v1.4 확장)

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

## 3. JSP include / JSP SQL 검출 검증

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

## 4. Java 호출/오버로드/정적 임포트 검증(보강 시)

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

## 5. 테이블 사용(use_table) / PK-FK 추론 검증

체크 포인트:
-   `edges(edge_kind='use_table')`가 sql_unit→db_table로 생성
-   빈도/PK 교차검증(보강 시)로 `joins.inferred_pkfk=1` 및 confidence 보정

예시 질의:
```sql
select edge_kind,count(*) from edges group by edge_kind;
select inferred_pkfk, count(*) from joins group by inferred_pkfk;
```

## 6. 로그/에러 확인

-   파일: `logs/analyzer.log`
-   실패/예외 로그가 없는지 확인

## 7. v1.4 신규 기능 테스트

### 7.1 동적 SQL 해석 테스트
```bash
# 동적 SQL이 포함된 매퍼에서 조건/분기 보존 확인
python phase1/src/main.py PROJECT/sampleSrc --project-name sample --config config/config.yaml
```

검증 항목:
-   `<bind>` 변수가 정규화된 SQL에 적절히 치환
-   `<choose>/<when>` 분기가 대표 분기로 요약되고 주석 보존
-   `<foreach>` 블록이 `IN (:list[])` 형태로 요약

### 7.2 Mermaid 내보내기 개선 테스트
```bash
# 다양한 export strategy 테스트
python visualize_cli.py graph --project-id 1 --out test_full.html --export-strategy full
python visualize_cli.py graph --project-id 1 --out test_balanced.html --export-strategy balanced --min-confidence 0.4
python visualize_cli.py class --project-id 1 --out test_class.html --class-methods-max 5 --class-attrs-max 8
```

## 8. 주의/한계

-   javalang 미설치 시 Java 파싱 스킵될 수 있음(requirements 설치 필요)
-   DB_SCHEMA CSV가 충분하지 않으면 PK 교차검증 결과가 달라질 수 있음
-   v1.4에서 추가된 DynamicSqlResolver는 lxml이 필요함

## 9. 통합 테스트 케이스 목록

### 9.1. TC_INTEGRATED_001_BasicJavaParsing: 기본 Java 코드 파싱 및 메타데이터 추출

*   **Description**: `IntegratedService.java`의 `startProcess`, `doWork` 메서드와 `getStaticUserData` 등 기본 Java 메서드들이 정확히 파싱되고 메타데이터(클래스, 메서드)가 추출되는지 확인합니다.
*   **Associated Source**: `IntegratedService.java` (`startProcess`, `doWork`, `getStaticUserData` 메서드)

### 9.2. TC_INTEGRATED_002_DynamicSQLGeneration: JSP 동적 SQL 생성 및 SQL Injection 탐지

*   **Description**: `IntegratedView.jsp`에서 요청 파라미터에 따라 동적으로 생성되는 `PRODUCT` 및 `CUSTOMER` SQL 쿼리 문자열이 정확히 식별되고, SQL Injection 취약점 패턴 (`id = '...'`)이 탐지되는지 확인합니다.
*   **Associated Source**: `IntegratedView.jsp` (Product 및 Customer SQL 생성 스크립틀릿)

### 9.3. TC_INTEGRATED_003_MyBatisDynamicSQL: MyBatis 동적 SQL 및 필수 필터 추출

*   **Description**: `IntegratedMapper.xml`의 `findDynamicData` 쿼리에서 `<if>`, `<choose>`, `<foreach>` 등 동적 태그가 정확히 처리되고, `DEL_YN = 'N'`과 같은 필수 필터가 `required_filters` 테이블에 저장되는지 확인합니다.
*   **Associated Source**: `IntegratedMapper.xml` (`findDynamicData` 쿼리)

### 9.4. TC_INTEGRATED_004_ComplexSQLParsing: 복잡 SQL (CTE, Subquery, ANSI/Implicit JOIN) 파싱

*   **Description**: `IntegratedMapper.xml`의 `getComplexReport` 쿼리 (CTE, 서브쿼리, 조인) 및 `getOrdersWithCustomerAnsiJoin` (ANSI JOIN), `getOrdersWithCustomerImplicitJoin` (Oracle Implicit JOIN) 쿼리들이 정확히 파싱되고 조인 조건, 필터 등이 추출되는지 확인합니다.
*   **Associated Source**: `IntegratedMapper.xml` (`getComplexReport`, `getOrdersWithCustomerAnsiJoin`, `getOrdersWithCustomerImplicitJoin` 쿼리)

### 9.5. TC_INTEGRATED_005_LLMCommentGeneration: LLM 기반 주석 생성 및 표준화

*   **Description**: `IntegratedService.java`의 `calculateOrderTotal` 메서드 (표준 주석) 및 `IntegratedMapper.xml`의 `findDynamicData` 쿼리 (표준 주석)에 대해 LLM 기반으로 고품질 코멘트가 생성되는지, `getFormattedId` 메서드 (부실 주석)와 같은 케이스도 처리되는지 확인합니다.
*   **Associated Source**: `IntegratedService.java` (`calculateOrderTotal`, `getFormattedId` 메서드), `IntegratedMapper.xml` (`findDynamicData` 쿼리 상단 주석)

### 9.6. TC_INTEGRATED_006_LargeFilePerformance: 대규모 파일 분석 성능

*   **Description**: `IntegratedService.java` (100개 더미 메서드) 및 `IntegratedView.jsp` (50개 반복 섹션)와 같은 대규모 파일을 분석할 때, 분석기가 멀티스레드 방식으로 효율적으로 처리하여 성능 목표를 달성하는지 확인합니다.
*   **Associated Source**: `IntegratedService.java` (`largeMethod1` ~ `largeMethod100`), `IntegratedView.jsp` (50개 반복 섹션)

### 9.7. TC_INTEGRATED_007_ComplexSQLQueries: 10개 테이블 조인 복잡 쿼리 5종

*   **Description**: `IntegratedMapper.xml`에 새로 추가된 5개의 복잡한 SQL 쿼리 (`getSalesPerformanceReport`, `getCustomerActivitySummary`, `getProjectResourceUtilization`, `getFinancialTransactionAudit`, `getSupplyChainOptimization`)가 10개 테이블 조인, 서브쿼리, 스칼라 쿼리, SF 함수 호출 등을 포함하여 정확히 파싱되고 메타데이터가 추출되는지 확인합니다.
*   **Associated Source**: `IntegratedMapper.xml` (5개 복잡 SQL 쿼리)

### 9.8. TC_INTEGRATED_008_ReflectionAndDynamicSQL: 리플렉션 및 동적 SQL 신뢰도

*   **Description**: `IntegratedService.java`의 `processWithReflection` 메서드 (리플렉션 사용) 및 `getDynamicUserData` 메서드 (동적 SQL 사용)와 같이 신뢰도 감점 요인이 있는 코드에 대해 CONFIDENCE 점수가 낮게 측정되는지 확인합니다.
*   **Associated Source**: `IntegratedService.java` (`processWithReflection`, `getDynamicUserData` 메서드)

### 9.9. TC_INTEGRATED_009_VulnerabilityDetection: 보안 취약점 탐지 및 저장

*   **Description**: `VulnerabilityTestService.java`에 포함된 다양한 보안 취약점 (SQL Injection, XSS, Path Traversal, 하드코딩된 자격증명, 약한 암호화 등)이 정확히 탐지되고 `vulnerability_fixes` 테이블에 저장되는지 확인합니다.
*   **Associated Source**: `VulnerabilityTestService.java` (모든 취약점 메서드)

### 9.10. TC_INTEGRATED_010_IncrementalAnalysis: 증분 분석 기능

*   **Description**: `--incremental` 플래그를 사용하여 파일 해시 기반으로 변경된 파일만 분석하는 증분 분석 기능이 올바르게 동작하는지 확인합니다. 파일 변경 전후로 분석을 수행하여 변경된 파일만 처리되는지 검증합니다.
*   **Test Steps**:
    1.  전체 프로젝트 분석 수행
    2.  특정 파일 수정 (예: IntegratedService.java의 메서드 하나 수정)
    3.  `--incremental` 플래그로 재분석 수행
    4.  변경된 파일만 처리되는지 로그 확인

### 9.11. TC_INTEGRATED_011_MethodCallResolution: 메서드 호출 관계 해결

*   **Description**: `IntegratedService.java`에서 `integratedMapper`의 메서드를 호출하는 관계가 올바르게 해결되어 `edges` 테이블에 저장되고, 신뢰도 점수가 적절히 계산되는지 확인합니다.
*   **Associated Source**: `IntegratedService.java`의 매퍼 메서드 호출 (`integratedMapper.executeStaticQuery()` 등)

### 9.12. TC_INTEGRATED_012_ConfidenceThresholding: 신뢰도 임계값 필터링

*   **Description**: `config.yaml`에서 `confidence_threshold` 값을 설정하고, 설정값보다 낮은 신뢰도를 가진 엣지나 분석 결과가 필터링되어 저장되지 않는지 확인합니다.
*   **Test Steps**:
    1.  `confidence_threshold: 0.7`로 설정
    2.  프로젝트 분석 수행
    3.  저장된 `edges` 테이블에서 모든 레코드의 `confidence` 값이 0.7 이상인지 확인

### 9.13. TC_INTEGRATED_013_DatabaseSchemaFlexibility: DB 스키마 소유자 유연화

*   **Description**: `config.yaml`에서 `database.default_schema` 설정을 통해 하드코딩된 'SAMPLE' 소유자 대신 설정 파일의 값을 사용하여 테이블을 매칭하는지 확인합니다.
*   **Test Steps**:
    1.  `config.yaml`에서 `database.default_schema: PUBLIC` 설정
    2.  프로젝트 분석 수행
    3.  PUBLIC 스키마의 테이블들이 올바르게 매칭되는지 확인

### 9.14. TC_INTEGRATED_014_ComplexityAnalysis: 코드 복잡도 분석

*   **Description**: `VulnerabilityTestService.java`의 `processComplexBusiness` 메서드와 같이 중첩된 조건문, 복잡한 표현식을 포함한 메서드의 복잡도가 올바르게 계산되고 신뢰도에 반영되는지 확인합니다.
*   **Associated Source**: `VulnerabilityTestService.java` (`processComplexBusiness` 메서드)

## 10. Web Dashboard Backend API 테스트

### 10.1. TC_API_001_HealthCheck: 헬스체크 테스트
- **목적**: API 서버가 정상적으로 동작하는지 확인
- **엔드포인트**: `GET /health`
- **기대 응답**: `{"status": "healthy", "timestamp": "..."}`

### 10.2. TC_API_002_ProjectList: 프로젝트 목록 조회
- **목적**: 분석된 프로젝트 목록을 정상적으로 반환하는지 확인
- **엔드포인트**: `GET /api/projects`
- **기대 응답**: 프로젝트 목록이 포함된 JSON 배열

### 10.3. TC_API_003_ProjectDetails: 프로젝트 상세 정보
- **목적**: 특정 프로젝트의 상세 정보를 정상적으로 반환하는지 확인
- **엔드포인트**: `GET /api/projects/{project_id}`
- **기대 응답**: 프로젝트 상세 정보 JSON

### 10.4. TC_VIS_001_ERDData: ERD 데이터 조회
- **목적**: ERD 생성을 위한 데이터를 정상적으로 반환하는지 확인
- **엔드포인트**: `GET /api/projects/{project_id}/erd-data`
- **기대 응답**: 테이블 및 관계 정보가 포함된 JSON

### 10.5. TC_VIS_002_GraphData: 그래프 데이터 조회
- **목적**: 의존성 그래프 생성을 위한 데이터를 정상적으로 반환하는지 확인
- **엔드포인트**: `GET /api/projects/{project_id}/graph-data`
- **매개변수**: `kinds`, `min_confidence`, `max_nodes`
- **기대 응답**: 노드와 엣지 정보가 포함된 JSON

### 10.6. TC_WS_001_Connection: WebSocket 연결
- **목적**: WebSocket 연결이 정상적으로 설정되는지 확인
- **엔드포인트**: `WS /ws/{client_id}`
- **기대 결과**: 연결 성공 및 초기 메시지 수신