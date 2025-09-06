# 샘풀소스명세서 - sampleSrc 프로젝트 (Part 2)

## 1. 컨트롤러 상세 명세

### 1.1 UserController (`/user`)
- **GET `/list`**: 이름/이메일/상태 조건으로 목록 조회. `params: name(email LIKE), email(LIKE), status(=)` → `user/list.jsp`
- **POST `/search`**: 고급 검색. `params: userType, minAge, maxAge, startDate, endDate` → `user/searchResult.jsp`
- **GET `/dynamic/{type}`**: 유형별 목록. PathVariable `type`

### 1.2 ProductController (`/product`)
- **GET `/list`**: 이름/카테고리/상태 조건 목록 → `product/list.jsp`
- **POST `/search`**: 고급 검색. `categoryId, minPrice, maxPrice, minStock, maxStock` → `product/searchResult.jsp`
- **GET `/category/{categoryId}`**: 카테고리별 목록 → `product/categoryList`(JSP 미제공)
- **POST `/updateStock`**: 수량 증감 업데이트 → `product/updateResult`(JSP 미제공)

### 1.3 SyntaxErrorController (`/syntax-fixed`)
- **GET `/test1`**: 문자열 응답
- **GET `/test2`**: 분기 후 문자열 응답
- **GET `/users`**: 전체 사용자 목록(JSON)
- **GET `/user`**: 단건 조회(JSON, `id`)
- **POST `/user`**: 생성(try-catch 예외처리)

### 1.4 MixedErrorController (`/mixed-error`) [오류 혼합]
- 정상: `GET /users`, 삭제: `DELETE /user/{id}`
- 주의/오류:
  - `GET /user/{id}` 및 `PUT /user/{id}`에서 `@RequestParam` 사용(원래 `@PathVariable` 필요)
  - `createUser`에 세미콜론 누락(`new User()`), `Date` 미 import → 컴파일 오류
  - `updateUser`에서 `new Date()` 사용 시 import 누락 → 컴파일 오류

### 1.5 ErrorController (`/error`) [의도적 오류 집합]
- 메소드 내부 `@GetMapping`, `import` 선언, 잘못된 타입 대입, 중괄호 불일치, 무한루프, 미정의 변수(`params`), 잘못된 캐스팅 등 다수 문제 포함.
- 런타임 위험: `Integer.parseInt(param)`, 배열 인덱스 초과, `switch` fall-through, `NullPointerException` 유발 코드 등.

## 2. 서비스/매퍼 상세

### 2.1 UserService(+Impl)
- **getUsersByCondition(Map)** → `UserMapper.selectUsersByCondition`
- **getUsersByAdvancedCondition(Map)** → `...AdvancedCondition`
- **getUsersByType(String)** → `selectUsersByType`
- **getUserById(Long)** → `selectUserById`
- **updateUserDynamic(User)**, **deleteUsersByCondition(Map)**

### 2.2 ProductService(+Impl)
- **getProductsByCondition/AdvancedCondition/ByCategory**
- **getProductById**, **updateProductStock**, **updateProductDynamic**, **deleteProductsByCondition**

### 2.3 LogicErrorService [정상화 예시]
- 널/경계값 검증, 예외 래핑, 자원 사용 루프 예시 등 모범 패턴 포함

### 2.4 MixedErrorService [오류 혼합]
- `new Date()` import 누락,
- 존재하지 않는 매퍼 메소드 호출(`userMapper.searchByName`) → 컴파일 오류

### 2.5 Mapper 인터페이스
- `UserMapper`, `ProductMapper`: XML 기반 메소드 시그니처 일치
- `BrokenMapper`: 어노테이션 기반 정상 CRUD/조회 세트(네이밍은 'Broken'이지만 내용은 정상)

## 3. MyBatis XML 상세

### 3.1 UserMapper.xml
- `<where>`/`<if>`/`<set>`/`<trim>`/`<foreach>`/`JOIN`/날짜 변환(`TO_DATE`) 등 동적 패턴 풍부
- 예: `selectUsersByAdvancedCondition`는 `statusList`를 `<foreach>`로 IN 처리, `user_types` LEFT JOIN

### 3.2 ProductMapper.xml
- 조건/범위/조인/ResultMap/CRUD 전형 패턴 포함
- `updateProductStock` 수량 증감(구현은 매퍼 XML/인터페이스 합치며 실제 SQL은 단순화 예시 다수)

### 3.3 BrokenMapper.xml (정상)
- `selectById/selectAll/selectByName/selectByPriceRange/insert/update/delete/count/selectRecentProducts`
- 가독성 높은 예시 쿼리, 컬럼 명시적 선택 및 정렬/범위 사용

### 3.4 MixedErrorMapper.xml (오류 유도)
- 잘못된 컬럼/테이블 참조 포함: `active_flag`, `user_profiles`, `dept_name` 등
- 일부 `<if>` 조건은 정상, WHERE/ORDER BY와 혼재하여 파서의 부분 추출/오류 복구 검증 목적

## 4. JSP 상세 명세

### 4.1 user/list.jsp [정상]
- 검색폼(name/email/status) + 목록 테이블(10열)
- 상태 뱃지(`ACTIVE/INACTIVE`)를 `c:choose`로 표시
- 클라이언트 검증(JS) 포함

### 4.2 user/searchResult.jsp [테스트용 에러 블록 포함]
- 상단: 검색 조건 echo 영역 및 결과 테이블(제품/사용자 혼합 예시 섹션 포함)
- 하단 오류 유도 섹션(샘플):
  - 잘못된 JSTL 닫기(</c:if> 위치 오류),
  - 잘못된 EL(`users.size()` 직접 호출),
  - `fmt:formatDate` 잘못된 패턴,
  - JavaScript: 선언 전 참조, 존재하지 않는 함수 호출, `null` 접근, 무한 루프
  - CSS: invalid 색상/hex, border 스타일 누락
  - HTML: 닫히지 않은 `<tr>`
  - 폼: 문자열을 숫자로 변환 없이 연산 시도

### 4.3 product/*.jsp [정상]
- `product/list.jsp`: 기본 검색 + 목록
- `product/searchResult.jsp`: 조건 echo + 상세 결과

### 4.4 error/syntaxError.jsp [정상]
- 사용자 정보 출력, 날짜 포맷, 목록 테이블, 링크 모음

### 4.5 mixed/partialError.jsp [혼합]
- 정상 메시지/목록 + 오류:
  - 잘못된 EL: `user` 스코프 객체 전제,
  - 스크립틀릿에서 미정의 변수 `userList` 참조,
  - `c:choose` 닫힘 태그 누락

## 5. 오류 요약 체크리스트

- **컴파일 오류(Java)**: 세미콜론 누락, 잘못된 import 위치, 미 import 타입(Date), 존재하지 않는 메소드 호출
- **런타임 오류(Java/JS)**: NPE, NumberFormatException, ArrayIndexOutOfBounds, 무한루프, null 접근
- **템플릿 오류(JSP/JSTL/EL)**: 잘못된 닫힘 태그, 미정의 변수, 잘못된 EL 메소드 호출
- **SQL/매퍼 오류(MyBatis)**: 존재하지 않는 컬럼/테이블, WHERE 절 조건/JOIN 대상 불일치
- **보안**: 문자열 연결 SQL 예시로 SQL Injection 위험 시나리오 존재

## 6. 검증 가이드(예시)

- **파일 파싱**: Java/JSP/XML 각각 파싱 → 클래스/메소드/매핑/태그 추출
- **오류 감지**: 구문/의미 오류, 미정의 참조, 태그 구조 위반 검출
- **동적 쿼리 처리**: `<if>/<where>/<set>/<foreach>` 등 안전 처리 및 토큰 보존
- **스키마 대조**: `db_schema/*.csv` 기준으로 컬럼/테이블/뷰 매칭 및 불일치 리포트
- **보안 점검**: 문자열 연결 SQL, JSP 출력 이스케이프 여부, 입력 검증

## 7. 개선 제안

### 7.1 코드 품질
- 전역 예외 처리기, 로깅 수준 일관화, 입력값 검증(@Valid), 컨벤션/포맷팅 도입

### 7.2 파서/분석기 개선
- Java: 람다/스트림/제네릭/중첩 어노테이션 처리 강화
- JSP: 커스텀 태그/복잡 EL/인라인 JS·CSS 분석 확장
- SQL: 중첩 동적 쿼리/서브쿼리/윈도우/CTE 토큰화·정규화

### 7.3 보안·성능
- SQL 파라미터 바인딩 강제, XSS 이스케이프, CSRF 토큰
- 페이징/캐시/인덱스 튜닝 포인트 명시

## 8. 결론

- 본 Part 2는 파일별 상세와 오류 패턴, 검증 포인트를 정리했습니다.
- Part 1과 함께 사용하여 파서 정확도와 복원력(오류 내성)을 종합 검증할 수 있습니다.

