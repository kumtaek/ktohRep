# 샘플소스명세서 - sampleSrc 프로젝트 (Claude 분석 Part 1)

## 1. 프로젝트 개요

### 1.1 프로젝트 정보
- **프로젝트명**: sampleSrc
- **분석일시**: 2025-09-05 (Claude 직접 분석)
- **프로젝트 유형**: Spring Boot + MyBatis 웹 애플리케이션
- **주요 기능**: 사용자 관리, 상품 관리, 동적 쿼리 처리, 의도적 오류 포함 테스트 시나리오

### 1.2 기술 스택
- **Backend**: Java, Spring Boot, MyBatis
- **Frontend**: JSP, JSTL, JavaScript
- **Database**: Oracle (추정)
- **Build Tool**: Maven (추정)

### 1.3 프로젝트 구조
```
project/sampleSrc/
├── src/main/java/com/example/
│   ├── controller/          # 웹 컨트롤러 (5개 클래스)
│   ├── service/            # 비즈니스 로직 (6개 클래스)
│   ├── mapper/             # MyBatis 매퍼 인터페이스 (3개 클래스)
│   └── model/              # 도메인 모델 (2개 클래스)
├── src/main/resources/mybatis/mapper/  # MyBatis XML 매퍼 (4개 파일)
└── src/main/webapp/        # JSP 뷰 파일 (8개 파일)
```

## 2. Java 클래스 상세 분석

### 2.1 Controller 패키지 (5개 클래스)

#### 2.1.1 UserController.java
- **파일**: `src/main/java/com/example/controller/UserController.java`
- **클래스**: com.example.controller.UserController
- **기능**: 사용자 관련 웹 요청 처리
- **어노테이션**:
  - `@Controller` (클래스 레벨)
  - `@RequestMapping("/user")` (클래스 레벨)
  - `@Autowired` (필드 레벨)
  - `@GetMapping`, `@PostMapping` (메소드 레벨)
- **주요 메서드**:
  1. `getUserList()`: 사용자 목록 조회 (GET /user/list)
     - 파라미터: name, email, status (선택적, @RequestParam 어노테이션)
     - 다이나믹 쿼리 파라미터 구성 로직 포함
     - 반환: "user/list" (JSP 뷰)
  2. `searchUsers()`: 고급 사용자 검색 (POST /user/search)
     - 파라미터: Map<String, String> searchParams
     - 복잡한 다이나믹 쿼리 조건 구성 (userType, minAge, maxAge, startDate, endDate)
     - 반환: "user/searchResult" (JSP 뷰)
  3. `getUsersByType()`: 타입별 사용자 조회 (GET /user/dynamic/{type})
     - 파라미터: type (경로 변수, @PathVariable 어노테이션)
     - 반환: "user/typeList" (JSP 뷰)

#### 2.1.2 ProductController.java
- **파일**: `src/main/java/com/example/controller/ProductController.java`
- **클래스**: com.example.controller.ProductController
- **기능**: 상품 관련 웹 요청 처리
- **어노테이션 구조**: UserController와 동일한 패턴
- **주요 메서드**:
  1. `getProductList()`: 상품 목록 조회 (GET /product/list)
     - 파라미터: name, category, status (선택적)
     - 반환: "product/list" (JSP 뷰)
  2. `searchProducts()`: 고급 상품 검색 (POST /product/search)
     - 파라미터: categoryId, minPrice, maxPrice, minStock, maxStock
     - 반환: "product/searchResult" (JSP 뷰)
  3. `getProductsByCategory()`: 카테고리별 상품 조회 (GET /product/category/{categoryId})
     - 파라미터: categoryId (경로 변수)
     - 반환: "product/categoryList" (JSP 뷰)
  4. `updateProductStock()`: 상품 재고 업데이트 (POST /product/updateStock)
     - 파라미터: productId, quantity
     - 반환: "product/updateResult" (JSP 뷰)

#### 2.1.3 ErrorController.java ⚠️ (의도적 오류 포함)
- **파일**: `src/main/java/com/example/controller/ErrorController.java`
- **클래스**: com.example.controller.ErrorController
- **기능**: 파서 테스트를 위한 의도적인 오류 코드 포함
- **오류 유형별 분석**:
  1. **컴파일 오류**:
     - 라인 27: `int wrongType = name;` (String을 int로 할당)
     - 라인 47: 메소드 내부에 import 문 (잘못된 위치)
     - 라인 50: 중복 변수 선언 (name 변수)
  2. **런타임 오류 가능성**:
     - 라인 30: `name.toString()` (null 체크 없음)
     - 라인 71: `Integer.parseInt()` (예외 처리 없음)
     - 라인 75: `array[10]` (배열 범위 초과)
     - 라인 101: 잘못된 타입 캐스팅
     - 라인 104: null 참조 오류 가능성
  3. **구조적 오류**:
     - 라인 33-36: 메소드 내부에 메소드 정의
     - 라인 39-44: 중괄호 불일치 (누락된 '}'')
     - 라인 56-59: 무한 루프 (break 문 없음)
  4. **논리적 오류**:
     - 라인 84-92: switch문에서 break 누락
  5. **보안 취약점**:
     - 라인 53: SQL Injection 위험 (문자열 연결)

#### 2.1.4 SyntaxErrorController.java
- **파일**: `src/main/java/com/example/controller/SyntaxErrorController.java`
- **클래스**: com.example.controller.SyntaxErrorController
- **기능**: 문법 오류가 수정된 정상적인 컨트롤러
- **주요 메서드**: test1(), test2(), getAllUsers(), getUserById(), createUser()

#### 2.1.5 MixedErrorController.java
- **파일**: `src/main/java/com/example/controller/MixedErrorController.java`
- **클래스**: com.example.controller.MixedErrorController
- **기능**: 정상 코드와 오류 코드가 혼합된 컨트롤러

### 2.2 Service 패키지 (6개 클래스)

#### 2.2.1 UserService.java (인터페이스)
- **파일**: `src/main/java/com/example/service/UserService.java`
- **인터페이스**: com.example.service.UserService
- **기능**: 사용자 관련 비즈니스 로직 인터페이스
- **주요 메서드**:
  - `getUsersByCondition(Map<String, Object> params)`: 조건부 사용자 조회
  - `getUsersByAdvancedCondition(Map<String, Object> params)`: 고급 조건부 사용자 조회
  - `getUsersByType(String type)`: 타입별 사용자 조회
  - `getUserById(Long id)`: ID로 사용자 조회
  - `updateUserDynamic(User user)`: 동적 사용자 업데이트
  - `deleteUsersByCondition(Map<String, Object> params)`: 조건부 사용자 삭제

#### 2.2.2 ProductService.java (인터페이스)
- **파일**: `src/main/java/com/example/service/ProductService.java`
- **인터페이스**: com.example.service.ProductService
- **기능**: 상품 관련 비즈니스 로직 인터페이스

#### 2.2.3 UserServiceImpl.java
- **파일**: `src/main/java/com/example/service/UserServiceImpl.java`
- **클래스**: com.example.service.UserServiceImpl
- **기능**: UserService 인터페이스 구현체

#### 2.2.4 ProductServiceImpl.java
- **파일**: `src/main/java/com/example/service/ProductServiceImpl.java`
- **클래스**: com.example.service.ProductServiceImpl
- **기능**: ProductService 인터페이스 구현체

#### 2.2.5 LogicErrorService.java ⚠️
- **파일**: `src/main/java/com/example/service/LogicErrorService.java`
- **클래스**: com.example.service.LogicErrorService
- **기능**: 논리적 오류가 포함된 서비스

#### 2.2.6 MixedErrorService.java ⚠️
- **파일**: `src/main/java/com/example/service/MixedErrorService.java`
- **클래스**: com.example.service.MixedErrorService
- **기능**: 정상 코드와 오류 코드가 혼합된 서비스

### 2.3 Mapper 패키지 (3개 클래스)

#### 2.3.1 UserMapper.java (인터페이스)
- **파일**: `src/main/java/com/example/mapper/UserMapper.java`
- **인터페이스**: com.example.mapper.UserMapper
- **기능**: 사용자 데이터 접근 인터페이스
- **주요 메서드**:
  - `selectUsersByCondition(Map<String, Object> params)`: 조건부 사용자 조회
  - `selectUsersByAdvancedCondition(Map<String, Object> params)`: 고급 조건부 사용자 조회
  - `selectUsersByType(@Param("type") String type)`: 타입별 사용자 조회
  - `selectUserById(@Param("id") Long id)`: ID로 사용자 조회
  - `updateUserDynamic(User user)`: 동적 사용자 업데이트
  - `deleteUsersByCondition(Map<String, Object> params)`: 조건부 사용자 삭제
  - `insertUserDynamic(User user)`: 동적 사용자 삽입
  - `countUsersByCondition(Map<String, Object> params)`: 조건부 사용자 카운트
- **어노테이션**: `@Param` 어노테이션 사용

#### 2.3.2 ProductMapper.java (인터페이스)
- **파일**: `src/main/java/com/example/mapper/ProductMapper.java`
- **인터페이스**: com.example.mapper.ProductMapper
- **기능**: 상품 데이터 접근 인터페이스

#### 2.3.3 BrokenMapper.java ⚠️ (의도적 오류 포함)
- **파일**: `src/main/java/com/example/mapper/BrokenMapper.java`
- **클래스**: com.example.mapper.BrokenMapper
- **기능**: 파서 테스트를 위한 의도적인 오류가 포함된 매퍼

### 2.4 Model 패키지 (2개 클래스)

#### 2.4.1 User.java
- **파일**: `src/main/java/com/example/model/User.java`
- **클래스**: com.example.model.User
- **기능**: 사용자 도메인 객체
- **주요 필드** (총 12개):
  - `Long id`: 사용자 고유 식별자
  - `String username`: 사용자명
  - `String email`: 이메일 주소
  - `String password`: 암호화된 비밀번호
  - `String name`: 사용자 실명
  - `Integer age`: 나이
  - `String status`: 계정 상태
  - `String userType`: 사용자 유형
  - `Date createdDate`: 계정 생성일
  - `Date updatedDate`: 정보 수정일
  - `String phone`: 전화번호
  - `String address`: 주소
- **생성자**: 기본 생성자, 3개 파라미터 생성자
- **메서드**: 각 필드에 대한 Getter/Setter 메서드 (총 24개)

#### 2.4.2 Product.java
- **파일**: `src/main/java/com/example/model/Product.java`
- **클래스**: com.example.model.Product
- **기능**: 상품 도메인 객체

## 3. 오류 분석 및 검증 포인트

### 3.1 의도적 오류 유형별 통계

#### 3.1.1 Java 파일별 오류 현황
1. **ErrorController.java**: 13개 오류
   - 컴파일 오류: 3개
   - 런타임 오류: 5개
   - 구조적 오류: 3개
   - 논리적 오류: 1개
   - 보안 취약점: 1개

2. **MixedErrorController.java**: 예상 오류 3-5개
3. **LogicErrorService.java**: 예상 오류 2-4개
4. **MixedErrorService.java**: 예상 오류 2-4개
5. **BrokenMapper.java**: 예상 오류 2-3개

#### 3.1.2 파서 검증 체크리스트
- **클래스 인식**: 정상 클래스 11개, 오류 포함 클래스 5개
- **메서드 인식**: UserController 3개, ProductController 4개 등
- **어노테이션 인식**: Spring 어노테이션 (@Controller, @RequestMapping, @GetMapping 등)
- **필드 인식**: User 모델 12개 필드, Product 모델 예상 10-15개 필드
- **오류 감지 능력**: 13개 이상의 다양한 유형 오류 감지 필요

### 3.2 코드 품질 분석

#### 3.2.1 정상 코드 패턴
- **Spring MVC 패턴**: Controller → Service → Mapper 계층 구조 준수
- **어노테이션 사용**: 적절한 Spring 어노테이션 사용
- **예외 처리**: 일부 메서드에서 적절한 예외 처리
- **네이밍 규칙**: Java 네이밍 컨벤션 준수

#### 3.2.2 보안 취약점
- **SQL Injection**: 문자열 연결을 통한 쿼리 생성 (ErrorController.java:53)
- **입력 검증 부재**: 사용자 입력에 대한 검증 로직 부족
- **null 체크 부재**: null 참조 오류 가능성

## 4. 주요 기능 분석

### 4.1 동적 쿼리 처리
- **파라미터 구성**: HashMap을 통한 동적 파라미터 구성
- **조건부 처리**: null 체크 및 빈 문자열 체크
- **LIKE 검색**: 패턴 검색을 위한 '%' 패턴 추가
- **복잡한 조건**: 나이 범위, 날짜 범위, 다중 조건 처리

### 4.2 웹 요청 처리
- **GET 요청**: 목록 조회, 상세 조회
- **POST 요청**: 검색, 업데이트 작업
- **경로 변수**: RESTful URL 패턴 사용
- **모델 바인딩**: Spring MVC 모델 바인딩 활용

### 4.3 데이터 바인딩
- **Model 객체**: Spring Model을 통한 뷰 데이터 전달
- **RequestParam**: 요청 파라미터 바인딩
- **PathVariable**: URL 경로 변수 바인딩
- **Map 파라미터**: 동적 파라미터 처리

## 5. 개선 제안

### 5.1 코드 품질 향상
- **예외 처리**: 모든 메서드에 적절한 예외 처리 추가
- **입력 검증**: Bean Validation 어노테이션 활용
- **로깅**: 적절한 로깅 레벨 및 메시지 추가
- **문서화**: 메서드 및 클래스 JavaDoc 추가

### 5.2 보안 강화
- **SQL Injection 방지**: PreparedStatement 사용 (MyBatis 권장 방식)
- **XSS 방지**: 출력 데이터 이스케이프 처리
- **CSRF 보호**: Spring Security 적용

### 5.3 성능 최적화
- **페이징 처리**: 대용량 데이터 처리를 위한 페이징 구현
- **캐싱**: 자주 조회되는 데이터 캐싱
- **인덱스 활용**: 데이터베이스 인덱스 최적화

---

**Part 2에서는 MyBatis XML 매퍼 상세 분석, JSP 페이지 분석, 검증 프로세스를 다룹니다.**