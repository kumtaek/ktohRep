# 샘플소스명세서 - sampleSrc 분석 (Part 1)

## 1. 프로젝트 개요

### 1.1 프로젝트 정보
- **프로젝트명**: sampleSrc
- **분석일시**: 2025-09-06
- **프로젝트 유형**: Spring Boot + MyBatis 기반 웹 애플리케이션
- **주요 기능**: 사용자 및 상품 관리, 동적 SQL을 활용한 검색, 의도적인 오류를 포함한 테스트 케이스

### 1.2 기술 스택
- **Backend**: Java, Spring Boot, MyBatis
- **Frontend**: JSP, JSTL, JavaScript
- **Database**: Oracle (db_schema의 DDL로 추정)
- **Build Tool**: Maven (pom.xml 부재하나 표준 구조로 추정)

### 1.3 프로젝트 구조
```
sampleSrc/
├── config/
│   └── filter_config.yaml      # 분석 대상/제외 패턴 설정
├── db_schema/                  # DB 스키마 CSV 파일
│   ├── ALL_TABLES.csv
│   ├── ALL_TAB_COLUMNS.csv
│   ├── ALL_VIEWS.csv
│   └── PK_INFO.csv
└── src/main/
    ├── java/com/example/
    │   ├── controller/         # 웹 요청 처리 컨트롤러
    │   ├── service/            # 비즈니스 로직 서비스
    │   ├── mapper/             # MyBatis 매퍼 인터페이스
    │   └── model/              # 데이터 모델 (DTO)
    ├── resources/mybatis/mapper/ # MyBatis XML 매퍼
    └── webapp/                   # JSP 뷰 및 웹 리소스
        ├── error/
        ├── mixed/
        ├── product/
        └── user/
```

## 2. 데이터베이스 스키마 분석 (db_schema/*.csv 기반)

### 2.1 주요 테이블

#### USERS
- **설명**: 사용자 정보를 저장합니다.
- **주요 컬럼**: `ID`(PK), `USERNAME`, `EMAIL`, `PASSWORD`, `NAME`, `AGE`, `STATUS`, `USER_TYPE`

#### PRODUCTS
- **설명**: 상품 정보를 관리합니다.
- **주요 컬럼**: `PRODUCT_ID`(PK), `PRODUCT_NAME`, `DESCRIPTION`, `PRICE`, `STOCK_QUANTITY`, `STATUS`

#### ORDERS
- **설명**: 고객의 주문 정보를 저장합니다.
- **주요 컬럼**: `ORDER_ID`(PK), `CUSTOMER_ID`, `ORDER_DATE`, `STATUS`, `TOTAL_AMOUNT`

#### CATEGORIES
- **설명**: 상품 분류 정보를 관리합니다.
- **주요 컬럼**: `CATEGORY_ID`(PK), `CATEGORY_CODE`, `CATEGORY_NAME`

### 2.2 주요 뷰

#### ACTIVE_USERS
- **설명**: `STATUS`가 'ACTIVE'인 사용자만 조회합니다.

#### ORDER_SUMMARY
- **설명**: 주문 정보와 고객 이름을 조인하여 요약 정보를 제공합니다.

#### PRODUCT_INVENTORY
- **설명**: 상품, 재고, 창고 정보를 조인하여 상품별 현재 재고를 보여줍니다.

### 2.3 테이블 관계 (PK/FK 추정)
- `USERS.USER_TYPE` → `USER_TYPES.TYPE_CODE`
- `PRODUCTS.CATEGORY_ID` → `CATEGORIES.CATEGORY_ID`
- `ORDERS.CUSTOMER_ID` → `CUSTOMERS.CUSTOMER_ID`
- `ORDER_ITEMS.ORDER_ID` → `ORDERS.ORDER_ID`
- `ORDER_ITEMS.PRODUCT_ID` → `PRODUCTS.PRODUCT_ID`

## 3. Java 클래스 분석

### 3.1 Controller 패키지

#### UserController.java
- **기능**: 사용자(User) 관련 CRUD 웹 요청을 처리합니다.
- **주요 메서드**:
  - `getUserList()`: 조건(이름, 이메일, 상태)에 따른 동적 쿼리로 사용자 목록을 조회합니다.
  - `searchUsers()`: 나이, 가입일자 등 고급 조건으로 사용자를 검색합니다.
  - `getUsersByType()`: 사용자 유형(일반, 관리자 등)에 따라 사용자를 필터링합니다.

#### ProductController.java
- **기능**: 상품(Product) 관련 CRUD 웹 요청을 처리합니다.
- **주요 메서드**:
  - `getProductList()`: 상품명, 카테고리, 상태 등으로 상품을 검색합니다.
  - `searchProducts()`: 가격 범위, 재고 범위 등 복합 조건으로 상품을 검색합니다.
  - `updateProductStock()`: 특정 상품의 재고를 업데이트합니다.

#### ErrorController.java
- **기능**: **의도적인 오류**를 다수 포함하고 있는 컨트롤러입니다.
- **분석**:
  - **컴파일 오류**: `int wrongType = name;` (String을 int에 할당), 존재하지 않는 클래스 import, 중복 변수 선언, 중괄호 누락 등.
  - **런타임 오류**: `name.toString()` (NullPointerException 가능성), `Integer.parseInt()` (NumberFormatException 가능성), `array[10]` (ArrayIndexOutOfBoundsException), `(String) user.getId()` (ClassCastException).
  - **논리 오류**: `while(true)` 무한 루프, `switch`문 `break` 누락.
  - **보안 취약점**: `SQL Injection` 위험이 있는 문자열 쿼리 생성.

#### MixedErrorController.java
- **기능**: **정상 코드와 오류 코드가 혼재**된 컨트롤러입니다.
- **분석**:
  - **오류**: 세미콜론 누락(`new User()`), `java.util.Date` 클래스 import 누락으로 인한 컴파일 오류.
  - **정상**: 사용자 조회, 삭제 및 입력값 검증 로직은 정상적으로 구현되어 있습니다.

#### SyntaxErrorController.java
- **기능**: `MixedErrorController`의 **오류를 수정한 정상** 컨트롤러입니다.
- **분석**: 누락되었던 세미콜론과 import문이 추가되어 모든 메서드가 정상적으로 작동합니다.

### 3.2 Service 패키지

#### UserServiceImpl.java / ProductServiceImpl.java
- **기능**: 컨트롤러에서 호출하는 비즈니스 로직을 구현합니다.
- **특징**: `@Transactional` 어노테이션을 통해 모든 메서드가 하나의 트랜잭션으로 관리됩니다. 내부적으로 `UserMapper` 또는 `ProductMapper`를 호출하여 DB와 상호작용합니다.

#### LogicErrorService.java
- **기능**: `MixedErrorService` 등에서 발생할 수 있는 **논리 오류를 수정한 정상** 서비스 클래스입니다.
- **분석**:
  - `null` 체크를 강화하여 NullPointerException을 방지합니다.
  - `IllegalArgumentException`을 통해 잘못된 파라미터 유입을 명시적으로 차단합니다.
  - `try-catch` 블록으로 DB 오류 발생 시 `RuntimeException`을 발생시켜 트랜잭션 롤백을 유도합니다.

#### MixedErrorService.java
- **기능**: **정상 코드와 오류 코드가 혼재**된 서비스입니다.
- **분석**:
  - **오류**: `Date` 클래스 import 누락, 존재하지 않는 `userMapper.searchByName()` 메서드 호출로 인한 컴파일 오류.
  - **정상**: 사용자 ID 유효성 검사, 사용자 존재 여부 확인 등은 정상적으로 수행됩니다.

### 3.3 Model 패키지

#### User.java
- **기능**: `USERS` 테이블의 데이터를 담는 DTO(Data Transfer Object)입니다.
- **속성**: `id`, `username`, `email`, `password`, `name`, `age`, `status`, `userType` 등 테이블 컬럼과 1:1로 매핑됩니다.

#### Product.java
- **기능**: `PRODUCTS` 테이블의 데이터를 담는 DTO입니다.
- **속성**: `productId`, `productName`, `description`, `price`, `stockQuantity`, `status` 등 테이블 컬럼과 1:1로 매핑됩니다.
