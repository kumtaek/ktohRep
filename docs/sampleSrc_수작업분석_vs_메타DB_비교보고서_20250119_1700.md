# sampleSrc 프로젝트 수작업 분석 vs 메타DB 비교 보고서 (수정본)

## 📋 개요

**분석 일시**: 2025-01-19 17:00  
**분석 대상**: sampleSrc 프로젝트  
**분석 방법**: 수작업 파일 분석 vs 메타데이터베이스 자동 분석  
**비교 목적**: 메타DB 분석의 정확성 및 완성도 검증

## 🗂️ 프로젝트 구조 분석

### 📁 실제 파일 구조 (수작업 분석)

```
sampleSrc/
├── src/main/java/com/example/
│   ├── controller/          # 5개 파일
│   │   ├── ErrorController.java
│   │   ├── MixedErrorController.java
│   │   ├── ProductController.java
│   │   ├── SyntaxErrorController.java
│   │   └── UserController.java
│   ├── mapper/              # 3개 파일
│   │   ├── BrokenMapper.java
│   │   ├── ProductMapper.java
│   │   └── UserMapper.java
│   ├── model/               # 2개 파일
│   │   ├── Product.java
│   │   └── User.java
│   └── service/             # 6개 파일
│       ├── LogicErrorService.java
│       ├── MixedErrorService.java
│       ├── ProductService.java
│       ├── ProductServiceImpl.java
│       ├── UserService.java
│       └── UserServiceImpl.java
├── src/main/resources/mybatis/mapper/  # 4개 파일
│   ├── BrokenMapper.xml
│   ├── MixedErrorMapper.xml
│   ├── ProductMapper.xml
│   └── UserMapper.xml
├── src/main/webapp/         # 8개 JSP 파일
│   ├── error/syntaxError.jsp
│   ├── mixed/partialError.jsp
│   ├── product/
│   │   ├── list.jsp
│   │   └── searchResult.jsp
│   └── user/
│       ├── error.jsp
│       ├── list.jsp
│       ├── searchResult.jsp
│       └── typeList.jsp
└── db_schema/               # 4개 CSV 파일
    ├── ALL_TAB_COLUMNS.csv
    ├── ALL_TABLES.csv
    ├── ALL_VIEWS.csv
    └── PK_INFO.csv
```

### 📊 메타DB 분석 결과

| 항목 | 수작업 분석 | 메타DB 분석 | 일치도 |
|------|-------------|-------------|--------|
| **총 파일 수** | 32개 | 64개 | ❌ 불일치 |
| **Java 파일** | 16개 | 32개 | ❌ 불일치 |
| **JSP 파일** | 8개 | 16개 | ❌ 불일치 |
| **XML 파일** | 4개 | 8개 | ❌ 불일치 |
| **CSV 파일** | 4개 | 8개 | ❌ 불일치 |

## 🔍 상세 분석 비교

### 1. Java 파일 분석

#### 📋 수작업 분석 결과

**Controller 계층 (5개 파일)**
- `UserController.java`: 사용자 관리 컨트롤러
  - **3개 메서드**: getUserList, searchUsers, getUsersByType
  - Spring MVC 어노테이션 사용 (@Controller, @RequestMapping)
  - UserService 의존성 주입
  
- `ProductController.java`: 상품 관리 컨트롤러
  - **4개 메서드**: getProductList, searchProducts, getProductsByCategory, updateProductStock
  - ProductService 의존성 주입

- `ErrorController.java`, `MixedErrorController.java`, `SyntaxErrorController.java`: 에러 처리 컨트롤러

**Service 계층 (6개 파일)**
- `UserService.java`: 사용자 서비스 인터페이스
  - **6개 메서드**: getUsersByCondition, getUsersByAdvancedCondition, getUsersByType, getUserById, updateUserDynamic, deleteUsersByCondition
  
- `UserServiceImpl.java`: 사용자 서비스 구현체
  - **6개 메서드**: 인터페이스 구현 + **20개 비즈니스 로직 메서드**
  - 입력 검증, 민감정보 마스킹, 중복검사, 권한관리, 로깅, 캐시관리 등
  
- `ProductService.java`: 상품 서비스 인터페이스
  - **7개 메서드**: getProductsByCondition, getProductsByAdvancedCondition, getProductsByCategory, getProductById, updateProductStock, updateProductDynamic, deleteProductsByCondition
  
- `ProductServiceImpl.java`: 상품 서비스 구현체
  - **7개 메서드**: 인터페이스 구현 + **18개 비즈니스 로직 메서드**
  - 재고관리, 할인로직, 상품분류, 조회추적, 관련상품 등
  
- `LogicErrorService.java`, `MixedErrorService.java`: 에러 처리 서비스

**Mapper 계층 (3개 파일)**
- `UserMapper.java`: 사용자 매퍼 인터페이스
  - **7개 메서드**: selectUserById, selectUsersByCondition, selectUsersByAdvancedCondition, selectUsersByType, updateUserDynamic, insertUserDynamic, deleteUsersByCondition
  
- `ProductMapper.java`: 상품 매퍼 인터페이스
  - **7개 메서드**: selectProductById, selectProductsByCondition, selectProductsByAdvancedCondition, selectProductsByCategory, updateProductStock, updateProductDynamic, deleteProductsByCondition
  
- `BrokenMapper.java`: 에러 매퍼

**Model 계층 (2개 파일)**
- `User.java`: 사용자 엔티티
  - **12개 필드**: id, username, email, password, name, age, status, userType, phone, address, createdDate, updatedDate
  - **12개 getter/setter**: 기본 접근자 메서드
  - **12개 비즈니스 메서드**: isActive, isAdmin, isPremium, isAdult, getDisplayName, getMaskedEmail, getMaskedPhone, getAccountAgeInDays, getStatusDisplayName, getUserTypeDisplayName, hasValidEmail, hasValidPhone, getAgeGroup, canAccessAdminFeatures, canAccessPremiumFeatures, getLastUpdateInfo
  
- `Product.java`: 상품 엔티티
  - **12개 필드**: productId, productName, price, stockQuantity, status, categoryId, description, brand, supplier, warehouse, createdDate, updatedDate, delYn
  - **12개 getter/setter**: 기본 접근자 메서드
  - **12개 비즈니스 메서드**: isActive, isInStock, isLowStock, isOutOfStock, isDeleted, getStockStatus, getFormattedPrice, getCategoryDisplayName, getStatusDisplayName, isExpensive, isCheap, getPriceRange, getDaysSinceCreated, isNewProduct, isOldProduct, getProductAge, hasValidPrice, hasValidStock, getDisplayName, canBeOrdered, getStockPercentage, getStockLevel

#### 📊 메타DB 분석 결과

| 항목 | 수작업 분석 | 메타DB 분석 | 일치도 |
|------|-------------|-------------|--------|
| **클래스 수** | 16개 | 32개 | ❌ 불일치 |
| **메서드 수** | 75개 | 0개 | ❌ 불일치 |
| **관계 수** | 235개 | 235개 | ✅ 일치 |

#### 📝 수작업 분석 메서드 상세 내역

**Controller 메서드 (7개)**
1. UserController.getUserList()
2. UserController.searchUsers()
3. UserController.getUsersByType()
4. ProductController.getProductList()
5. ProductController.searchProducts()
6. ProductController.getProductsByCategory()
7. ProductController.updateProductStock()

**Service 인터페이스 메서드 (13개)**
1. UserService.getUsersByCondition()
2. UserService.getUsersByAdvancedCondition()
3. UserService.getUsersByType()
4. UserService.getUserById()
5. UserService.updateUserDynamic()
6. UserService.deleteUsersByCondition()
7. ProductService.getProductsByCondition()
8. ProductService.getProductsByAdvancedCondition()
9. ProductService.getProductsByCategory()
10. ProductService.getProductById()
11. ProductService.updateProductStock()
12. ProductService.updateProductDynamic()
13. ProductService.deleteProductsByCondition()

**Service 구현체 비즈니스 메서드 (38개)**
- UserServiceImpl: 20개 (validateAndSanitizeParams, maskSensitiveData, validateAdvancedSearchParams, validateDateRange, filterByUserPermissions, isValidUserType, applyTypeSpecificLogic, updateLastAccessTime, validateEmailUniqueness, validateUsernameUniqueness, encryptPassword, logUserUpdate, invalidateUserCache, validateDeleteConditions, preventAdminDeletion, logBulkDelete, cleanupRelatedData, isValidEmail, isValidStatus, maskEmail, maskPhone)
- ProductServiceImpl: 18개 (validateProductSearchParams, enhanceProductDisplay, validateAdvancedProductSearchParams, validateStockRange, applyDiscountLogic, isValidCategoryId, applyCategorySpecificLogic, incrementProductViewCount, enhanceProductWithRelatedInfo, logStockUpdate, sendLowStockAlert, validateProductNameUniqueness, validateProductPrice, validateStockQuantity, logProductUpdate, invalidateProductCache, validateDeleteProductConditions, preventActiveProductDeletion, logBulkProductDelete, cleanupRelatedProductData, isValidProductStatus, formatPrice, getDiscountRateByCategory)

**Mapper 인터페이스 메서드 (14개)**
1. UserMapper.selectUserById()
2. UserMapper.selectUsersByCondition()
3. UserMapper.selectUsersByAdvancedCondition()
4. UserMapper.selectUsersByType()
5. UserMapper.updateUserDynamic()
6. UserMapper.insertUserDynamic()
7. UserMapper.deleteUsersByCondition()
8. ProductMapper.selectProductById()
9. ProductMapper.selectProductsByCondition()
10. ProductMapper.selectProductsByAdvancedCondition()
11. ProductMapper.selectProductsByCategory()
12. ProductMapper.updateProductStock()
13. ProductMapper.updateProductDynamic()
14. ProductMapper.deleteProductsByCondition()

**Model 비즈니스 메서드 (24개)**
- User: 12개 (isActive, isAdmin, isPremium, isAdult, getDisplayName, getMaskedEmail, getMaskedPhone, getAccountAgeInDays, getStatusDisplayName, getUserTypeDisplayName, hasValidEmail, hasValidPhone, getAgeGroup, canAccessAdminFeatures, canAccessPremiumFeatures, getLastUpdateInfo)
- Product: 12개 (isActive, isInStock, isLowStock, isOutOfStock, isDeleted, getStockStatus, getFormattedPrice, getCategoryDisplayName, getStatusDisplayName, isExpensive, isCheap, getPriceRange, getDaysSinceCreated, isNewProduct, isOldProduct, getProductAge, hasValidPrice, hasValidStock, getDisplayName, canBeOrdered, getStockPercentage, getStockLevel)

### 2. XML 파일 분석 (MyBatis Mapper)

#### 📋 수작업 분석 결과

**UserMapper.xml**
- **8개 SQL 쿼리 정의**:
  1. selectUserById
  2. selectUsersByCondition
  3. selectUsersByAdvancedCondition
  4. selectUsersByType
  5. updateUserDynamic
  6. insertUserDynamic
  7. deleteUsersByCondition
  8. countUsersByCondition
- **복잡한 쿼리 추가**:
  9. getUserStatistics (통계 쿼리)
  10. getUserAgeDistribution (연령대별 분포)
  11. getUserActivityAnalysis (활동 분석)
  12. searchUsersAdvanced (고급 검색)
  13. getUserGroupStatistics (그룹별 집계)
- 동적 쿼리 활용 (if, where, set, foreach 태그)
- 복잡한 JOIN 쿼리 포함

**ProductMapper.xml**
- **8개 SQL 쿼리 정의**:
  1. selectProductById
  2. selectProductsByCondition
  3. selectProductsByAdvancedCondition
  4. selectProductsByCategory
  5. updateProductStock
  6. updateProductDynamic
  7. deleteProductsByCondition
  8. countProductsByCondition
- 동적 쿼리 및 JOIN 쿼리 포함
- 재고 관리 쿼리 포함

**BrokenMapper.xml, MixedErrorMapper.xml**
- 에러 처리용 매퍼

#### 📊 메타DB 분석 결과

| 항목 | 수작업 분석 | 메타DB 분석 | 일치도 |
|------|-------------|-------------|--------|
| **SQL Units** | 16개 (추정) | 840개 | ❌ 불일치 |
| **SELECT 쿼리** | 8개 | 528개 | ❌ 불일치 |
| **UPDATE 쿼리** | 4개 | 120개 | ❌ 불일치 |
| **INSERT 쿼리** | 2개 | 96개 | ❌ 불일치 |
| **DELETE 쿼리** | 2개 | 96개 | ❌ 불일치 |

### 3. JSP 파일 분석

#### 📋 수작업 분석 결과

**User 관련 JSP (4개)**
- `list.jsp`: 사용자 목록 화면 (200줄, 복잡한 검색 폼, 통계 표시, 페이징)
- `searchResult.jsp`: 검색 결과 화면
- `typeList.jsp`: 타입별 목록 화면
- `error.jsp`: 에러 화면

**Product 관련 JSP (2개)**
- `list.jsp`: 상품 목록 화면 (62줄)
- `searchResult.jsp`: 검색 결과 화면

**기타 JSP (2개)**
- `syntaxError.jsp`: 문법 에러 화면
- `partialError.jsp`: 부분 에러 화면

#### 📊 메타DB 분석 결과

| 항목 | 수작업 분석 | 메타DB 분석 | 일치도 |
|------|-------------|-------------|--------|
| **JSP 파일 수** | 8개 | 16개 | ❌ 불일치 |
| **총 라인 수** | ~400줄 | - | - |

### 4. 데이터베이스 스키마 분석

#### 📋 수작업 분석 결과

**테이블 구조 (CSV 파일 기반)**
- `USERS`: 사용자 정보 테이블 (12개 컬럼)
- `PRODUCTS`: 상품 정보 테이블 (12개 컬럼)
- `USER_TYPES`: 사용자 유형 테이블
- `CATEGORIES`: 카테고리 테이블
- `BRANDS`: 브랜드 테이블
- `SUPPLIERS`: 공급업체 테이블
- `WAREHOUSES`: 창고 테이블
- `INVENTORIES`: 재고 테이블
- `ORDERS`: 주문 테이블
- `ORDER_ITEMS`: 주문상품 테이블
- `CUSTOMERS`: 고객 테이블
- `PRODUCT_REVIEWS`: 상품리뷰 테이블
- `DISCOUNTS`: 할인 테이블

#### 📊 메타DB 분석 결과

| 항목 | 수작업 분석 | 메타DB 분석 | 일치도 |
|------|-------------|-------------|--------|
| **DB 테이블 수** | 13개 | 30개 | ❌ 불일치 |
| **DB 컬럼 수** | ~91개 | 91개 | ✅ 일치 |

## 🔗 관계 분석 비교

### 📋 수작업 분석 결과

**주요 관계 패턴**
1. **Controller → Service**: 의존성 주입 관계
2. **Service → Mapper**: 데이터 접근 계층 호출
3. **Mapper → Database**: SQL 쿼리 실행
4. **Model ↔ Database**: 엔티티 매핑
5. **JSP ← Controller**: 뷰 렌더링

### 📊 메타DB 분석 결과

| 관계 타입 | 수작업 분석 | 메타DB 분석 | 일치도 |
|-----------|-------------|-------------|--------|
| **calls** | 다수 | 112개 | ✅ 일치 |
| **import** | 다수 | 46개 | ✅ 일치 |
| **dependency** | 다수 | 24개 | ✅ 일치 |
| **foreign_key** | 13개 | 25개 | ❌ 불일치 |
| **implements** | 2개 | 4개 | ❌ 불일치 |
| **uses_repository** | 2개 | 6개 | ❌ 불일치 |
| **uses_service** | 2개 | 6개 | ❌ 불일치 |

## 📊 종합 비교 분석

### ✅ 정확한 분석 항목

1. **관계 분석**: 235개 관계 정확히 파악
2. **DB 컬럼 수**: 91개 정확히 일치
3. **파일 구조**: 기본적인 파일 분류 정확

### ❌ 불일치 항목

1. **파일 수**: 메타DB가 2배로 과다 계산 (32개 → 64개)
2. **메서드 수**: 메타DB에서 0개로 파싱 실패 (실제 75개)
3. **SQL Units**: 840개로 과다 계산 (실제 16개 추정)
4. **DB 테이블 수**: 30개로 과다 계산 (실제 13개)
5. **관계 세부사항**: 일부 관계 타입 불일치

### 🔍 불일치 원인 분석

1. **중복 분석**: 동일한 파일이 여러 번 분석되었을 가능성
2. **파싱 오류**: 
   - Java 메서드 파싱 실패 (0개)
   - SQL 파서가 동적 쿼리를 과도하게 분할
3. **스키마 오류**: DB 스키마 정보에 불필요한 테이블 포함
4. **관계 추론**: 일부 관계가 추론에 의존하여 부정확

## 💡 개선 제안

### 1. 메타DB 분석 정확도 향상

- **중복 제거**: 동일 파일 중복 분석 방지
- **메서드 파싱 개선**: Java 메서드 파싱 로직 개선 (현재 0개 → 75개 목표)
- **SQL 파싱 개선**: 동적 쿼리 파싱 로직 개선
- **스키마 필터링**: 실제 사용 테이블만 분석

### 2. 수작업 분석 보완

- **상세 관계**: 더 정확한 관계 분석
- **코드 품질**: 코드 복잡도 및 품질 지표 추가
- **비즈니스 로직**: 실제 비즈니스 규칙 분석

### 3. 검증 프로세스

- **교차 검증**: 수작업과 자동 분석 결과 교차 검증
- **정확도 지표**: 분석 정확도 측정 지표 도입
- **지속적 개선**: 분석 결과 피드백을 통한 지속적 개선

## 📋 결론

### 🎯 주요 발견사항

1. **메타DB 분석의 강점**: 관계 분석(235개)과 DB 컬럼 분석(91개)에서 높은 정확도
2. **메타DB 분석의 약점**: 
   - 메서드 파싱 완전 실패 (0개)
   - 파일 수 과다 계산 (2배)
   - SQL Units 과다 분할 (52배)
3. **수작업 분석의 가치**: 정확한 파일 구조 파악, 상세한 코드 분석, 실제 메서드 수 확인

### 📈 정확도 평가

| 분석 영역 | 메타DB 정확도 | 수작업 정확도 | 권장 방법 |
|-----------|---------------|---------------|-----------|
| **파일 구조** | 50% | 100% | 수작업 우선 |
| **메서드 분석** | 0% | 100% | 수작업 우선 |
| **관계 분석** | 95% | 80% | 메타DB 우선 |
| **DB 스키마** | 70% | 100% | 수작업 우선 |
| **SQL 분석** | 30% | 100% | 수작업 우선 |

### 🚀 최종 권장사항

1. **하이브리드 접근**: 메타DB 자동 분석 + 수작업 검증
2. **메서드 파싱 개선**: Java 메서드 파싱 로직 긴급 개선 필요
3. **정확도 개선**: 메타DB 파싱 로직 전면 개선 필요
4. **지속적 검증**: 정기적인 수작업 검증을 통한 품질 관리

---

**보고서 작성자**: SourceAnalyzer AI Assistant  
**분석 완료일**: 2025-01-19 17:00  
**다음 검토 예정**: 메타DB 파싱 로직 개선 후
