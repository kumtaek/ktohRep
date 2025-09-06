# 샘풀소스명세서 - sampleSrc 프로젝트 (Part 1)

## 1. 프로젝트 개요

### 1.1 프로젝트 정보
- **프로젝트명**: sampleSrc
- **분석일시**: 2025-09-06 00:40:00
- **프로젝트 유형**: Spring MVC + MyBatis + JSP 웹 애플리케이션
- **주요 기능**: 사용자/상품 목록 및 검색, 동적 쿼리, 고급 조건 검색, 재고 업데이트

### 1.2 기술 스택
- **Backend**: Java, Spring MVC (Annotation 기반)
- **Persistence**: MyBatis (XML + Annotation Mapper 혼합)
- **Frontend**: JSP, JSTL, JavaScript
- **Database**: Oracle 유사 스키마(CSV 제공)
- **Build Tool**: Maven/Gradle (추정)

### 1.3 프로젝트 구조
```
sampleSrc/
├── src/main/java/com/example/
│   ├── controller/                 # 웹 컨트롤러 (정상 + 오류 유도 포함)
│   ├── service/                    # 서비스 레이어 (정상 + 오류 유도 포함)
│   ├── mapper/                     # MyBatis 매퍼 인터페이스 (XML/어노테이션)
│   └── model/                      # 도메인 모델 (User, Product)
├── src/main/resources/mybatis/mapper/   # MyBatis XML 매퍼 (정상 + 오류 유도)
├── src/main/webapp/                # JSP 뷰 (정상 + 오류 유도)
├── db_schema/                      # DB 스키마 덤프(CSV: ALL_TABLES, COLUMNS, PK, VIEWS)
└── config/                         # 필터/설정 (filter_config.yaml)
```

- **총 소스 파일(핵심)**: Controller 5, Service 4, Mapper 3, Model 2, XML Mapper 4, JSP 9
- **의도적 오류 포함 파일**: `ErrorController.java`, `MixedErrorController.java`, `MixedErrorService.java`, `MixedErrorMapper.xml`, `mixed/partialError.jsp`, `user/searchResult.jsp` 일부 블록

## 2. 데이터베이스 스키마 분석 (db_schema)

CSV 스키마 덤프 기반으로 주요 테이블과 컬럼을 요약합니다.

### 2.1 주요 테이블 (SAMPLE 스키마)

#### USERS
- **목적**: 사용자 정보 관리
- **PK**: `ID`
- **주요 컬럼**: `USERNAME(uniqe)`, `EMAIL`, `PASSWORD`, `NAME`, `AGE`, `STATUS`, `USER_TYPE`, `PHONE`, `ADDRESS`, `CREATED_DATE`, `UPDATED_DATE`

#### USER_TYPES
- **목적**: 사용자 유형 코드 관리
- **PK**: `TYPE_CODE`
- **주요 컬럼**: `TYPE_NAME`, `DESCRIPTION`

#### PRODUCTS
- **목적**: 상품 정보 관리
- **PK**: `PRODUCT_ID`
- **주요 컬럼**: `PRODUCT_NAME`, `DESCRIPTION(CLOB)`, `PRICE`, `STOCK_QUANTITY`, `STATUS`, `CATEGORY_ID`, `BRAND_ID`, `SUPPLIER_ID`, `WAREHOUSE_ID`, `CREATED_DATE`, `UPDATED_DATE`, `DEL_YN`

#### CATEGORIES / BRANDS / SUPPLIERS / WAREHOUSES
- **목적**: 기준정보 코드/마스터
- **PK**: 각 ID 컬럼(`CATEGORY_ID`, `BRAND_ID`, `SUPPLIER_ID`, `WAREHOUSE_ID`)
- **공통 컬럼**: `..._NAME`, `DEL_YN` 등

#### INVENTORIES
- **목적**: 상품 재고 현황
- **PK**: `INVENTORY_ID`
- **주요 컬럼**: `PRODUCT_ID`, `CURRENT_STOCK`, `UPDATED_DATE`

#### PRODUCT_REVIEWS / DISCOUNTS
- **목적**: 상품 리뷰/할인 정보
- **PK**: `REVIEW_ID`, `DISCOUNT_ID`
- **관계**: `PRODUCT_ID` 참조

### 2.2 기타 스키마
- **PUBLIC.USER_ROLE**: 복합 PK (`USER_ID`, `ROLE_ID`)
- **SCOTT.DYNAMIC_DATA / RELATED_DATA**: 테스트/참조성 데이터

### 2.3 뷰(views)
- `ACTIVE_USERS`, `USER_TYPE_SUMMARY`, `ORDER_SUMMARY`, `PRODUCT_INVENTORY` 등 집계/조인 뷰 존재

## 3. 도메인 모델

### 3.1 com.example.model.User
- **필드**: `id, username, email, password, name, age, status, userType, phone, address, createdDate, updatedDate`
- **역할**: 사용자 엔티티, MyBatis 결과 매핑 대상

### 3.2 com.example.model.Product
- **필드**: `productId, productName, description, price, stockQuantity, status, categoryId, brandId, supplierId, warehouseId, createdDate, updatedDate, delYn`
- **역할**: 상품 엔티티, MyBatis 결과 매핑 대상

## 4. 애플리케이션 기능 개요

### 4.1 사용자(User) 기능
- **목록/검색**: `/user/list` (이름/이메일/상태 조건, LIKE 지원)
- **고급검색**: `/user/search` (POST, 유형/나이범위/기간/상태목록 동적 조합)
- **유형별 목록**: `/user/dynamic/{type}`

### 4.2 상품(Product) 기능
- **목록/검색**: `/product/list` (이름/카테고리/상태)
- **고급검색**: `/product/search` (POST, 카테고리/가격범위/재고범위)
- **카테고리별**: `/product/category/{categoryId}`
- **재고변경**: `/product/updateStock` (POST, 수량 증감)

### 4.3 정상이자 테스트용 엔드포인트
- `SyntaxErrorController`(경로 `/syntax-fixed`): 간단 텍스트/목록 조회, 단정/예외처리 예시 포함
- `BrokenMapper`(어노테이션 매퍼): 정상 CRUD/조회 예시 집합

## 5. MyBatis 매퍼 요약

### 5.1 UserMapper.xml (핵심 동적 쿼리)
- **selectUsersByCondition(map)**: `<where> + <if>`로 name/email/status 조건
- **selectUsersByAdvancedCondition(map)**: users + user_types JOIN, 나이/기간/상태목록 `<foreach>` IN 처리
- **selectUsersByType(type)**: 단순 EQ + 정렬
- **updateUserDynamic(user)**: `<set>` 기반 부분 업데이트, `updated_date = SYSDATE`
- **insertUserDynamic(user)**: `<trim>`으로 컬럼/값 동적 구성, `useGeneratedKeys`
- **deleteUsersByCondition(map)** / **countUsersByCondition(map)**: 조건부 삭제/집계

### 5.2 ProductMapper.xml
- **selectProductsByCondition/AdvancedCondition**: 이름/카테고리/상태, 가격/재고 범위
- **selectProductsByCategory(categoryId)**: 카테고리별 필터
- **updateProductStock(productId, quantity)**: 수량 증감
- **update/insert/delete/count**: 기본 CRUD/집계, ResultMap 예시 포함

### 5.3 Annotation Mapper (BrokenMapper)
- `@Select/@Insert/@Update/@Delete` 기반 정상 쿼리 세트, 페이징/정렬/범위 예시 포함

## 6. JSP 명세 개요 (상세는 Part 2)

- `user/list.jsp`: 검색폼 + 목록표 + 상태 뱃지 + 클라이언트검증
- `user/searchResult.jsp`: 조건표시 + 결과테이블 + 에러 유도 섹션 포함(의도적)
- `product/list.jsp`, `product/searchResult.jsp`: 기본 목록/검색 결과
- `error/syntaxError.jsp`: 정상 JSP 예시
- `mixed/partialError.jsp`: 정상/오류 혼합(닫힘 태그 누락, 잘못된 EL 등)

## 7. 의도적 오류 및 리스크 개요

### 7.1 컨트롤러(Java)
- `ErrorController`: 타입불일치, 중첩 메소드 정의, 내부 `import`, 중괄호 불일치, 무한루프, 미정의 변수 사용, 캐스팅 오류 등 컴파일/런타임 오류 다수
- `MixedErrorController`: 세미콜론 누락, `Date` 미 import, PathVariable vs RequestParam 혼용, 업데이트 메소드 시그니처 부정확

### 7.2 서비스(Java)
- `MixedErrorService`: `Date` 미 import, 존재하지 않는 매퍼 메소드 호출(`searchByName`)

### 7.3 XML 매퍼
- `MixedErrorMapper.xml`: 잘못된 컬럼/테이블 참조(`active_flag`, `user_profiles`, `dept_name`) 포함

### 7.4 JSP
- `mixed/partialError.jsp`: `c:choose` 닫힘 누락, 정의되지 않은 변수 참조(`userList`), 잘못된 EL
- `user/searchResult.jsp`: 샘플 오류 블록 포함(잘못된 JSTL 닫기, JS 무한루프/널접근 등)

## 8. 보안/성능 메모
- **SQL Injection 위험**: 문자열 연결 쿼리 예시(`ErrorController.sql`)는 반패턴, 실제 사용 금지 권장
- **XSS**: JSP 출력 시 이스케이프 필요, 사용자 입력 표시부 점검
- **페이징/인덱스**: 대량 목록에 페이징/인덱스 전제 필요

---

**Part 2에서 파일별 상세 명세, 오류 패턴, 검증 체크리스트를 제공합니다.**
