# 샘플소스명세서 - sampleSrc 프로젝트 (Claude 분석 Part 2)

## 1. MyBatis XML 매퍼 상세 분석

### 1.1 UserMapper.xml 분석

#### 1.1.1 기본 정보
- **파일**: `src/main/resources/mybatis/mapper/UserMapper.xml`
- **네임스페이스**: com.example.mapper.UserMapper
- **총 쿼리 수**: 8개 (SELECT 4개, UPDATE 1개, INSERT 1개, DELETE 1개, COUNT 1개)
- **인코딩**: UTF-8

#### 1.1.2 쿼리별 상세 분석

##### 1.1.2.1 기본 조회 쿼리
**selectUserById**
- **타입**: SELECT
- **파라미터**: long (단일 파라미터)
- **리턴타입**: com.example.model.User
- **쿼리**: `SELECT * FROM users WHERE id = #{id}`
- **특징**: 단순 기본키 조회

##### 1.1.2.2 동적 조건부 조회 쿼리
**selectUsersByCondition**
- **타입**: SELECT
- **파라미터**: map
- **리턴타입**: com.example.model.User
- **동적 요소**:
  - `<where>` 태그 사용
  - 3개의 `<if>` 태그: name, email, status
- **SQL 패턴**:
  ```xml
  <if test="name != null and name != ''">
      AND name LIKE #{name}
  </if>
  ```
- **특징**: LIKE 검색 지원, null 및 빈 문자열 검사

##### 1.1.2.3 고급 동적 조회 쿼리
**selectUsersByAdvancedCondition**
- **타입**: SELECT (복잡한 JOIN 쿼리)
- **파라미터**: map
- **리턴타입**: com.example.model.User
- **JOIN**: users u LEFT JOIN user_types ut
- **동적 요소**:
  - 6개의 `<if>` 태그
  - 1개의 `<foreach>` 태그 (statusList 처리)
- **조건 분석**:
  - userType: 단순 등가 비교
  - minAge, maxAge: 숫자 범위 검색
  - startDate, endDate: 날짜 범위 검색 (TO_DATE 함수 사용)
  - statusList: IN 절 처리
- **Oracle 함수**: TO_DATE() 함수 사용으로 Oracle DB 확인

##### 1.1.2.4 동적 업데이트 쿼리
**updateUserDynamic**
- **타입**: UPDATE
- **파라미터**: com.example.model.User
- **동적 요소**: `<set>` 태그 + 7개의 `<if>` 태그
- **업데이트 대상 컬럼**: username, email, name, age, status, phone, address
- **고정 업데이트**: updated_date = SYSDATE (Oracle 함수)
- **조건**: WHERE id = #{id}

##### 1.1.2.5 동적 삽입 쿼리
**insertUserDynamic**
- **타입**: INSERT
- **파라미터**: com.example.model.User
- **특징**: useGeneratedKeys="true", keyProperty="id"
- **동적 요소**: 2개의 `<trim>` 태그 (컬럼명/값 각각)
- **처리 컬럼**: 9개 동적 컬럼 + 2개 고정 컬럼 (created_date, updated_date)
- **Oracle 함수**: SYSDATE 사용

##### 1.1.2.6 조건부 삭제 쿼리
**deleteUsersByCondition**
- **타입**: DELETE
- **파라미터**: map
- **동적 요소**: `<where>` 태그 + 3개의 `<if>` 태그
- **삭제 조건**: status, userType, beforeDate
- **날짜 처리**: TO_DATE() 함수 사용

##### 1.1.2.7 동적 카운트 쿼리
**countUsersByCondition**
- **타입**: SELECT COUNT(*)
- **파라미터**: map
- **리턴타입**: int
- **동적 요소**: 4개의 `<if>` 태그
- **카운트 조건**: userType, status, minAge, maxAge

### 1.2 ProductMapper.xml 분석

#### 1.2.1 기본 정보
- **파일**: `src/main/resources/mybatis/mapper/ProductMapper.xml`
- **네임스페이스**: com.example.mapper.ProductMapper
- **총 쿼리 수**: 8개 (SELECT 4개, UPDATE 2개, INSERT 1개, DELETE 1개)
- **인코딩**: UTF-8

#### 1.2.2 주요 쿼리 패턴 분석

##### 1.2.2.1 복잡한 JOIN 쿼리
**selectProductsByAdvancedCondition**
- **JOIN 구조**: products p LEFT JOIN categories c LEFT JOIN brands b
- **동적 조건**: 7개의 조건 처리
- **가격 범위**: minPrice, maxPrice (숫자 비교)
- **재고 범위**: minStock, maxStock (숫자 비교)
- **IN 절 처리**: statusList에 대한 `<foreach>` 태그

##### 1.2.2.2 재고 업데이트 쿼리
**updateProductStock**
- **특징**: 재고 수량 증감 처리 (`stock_quantity = stock_quantity + #{quantity}`)
- **파라미터**: productId, quantity
- **동시 업데이트**: updated_date = SYSDATE

##### 1.2.2.3 논리 삭제 처리
**deleteProductsByCondition**
- **특징**: 물리적 삭제가 아닌 논리적 삭제
- **처리 방식**: `UPDATE products SET del_yn = 'Y'`
- **동적 조건**: 3개의 조건 (status, categoryId, beforeDate)

### 1.3 오류 포함 매퍼 분석

#### 1.3.1 BrokenMapper.xml
- **파일**: `src/main/resources/mybatis/mapper/BrokenMapper.xml`
- **예상 오류 유형**:
  - XML 구문 오류 (태그 미스매치, 닫기 태그 누락)
  - 잘못된 parameterType, resultType
  - 존재하지 않는 테이블/컬럼 참조
  - MyBatis 태그 문법 오류

#### 1.3.2 MixedErrorMapper.xml
- **파일**: `src/main/resources/mybatis/mapper/MixedErrorMapper.xml`
- **특징**: 정상 쿼리와 오류 쿼리 혼재

### 1.4 MyBatis 동적 쿼리 패턴 통계

#### 1.4.1 사용된 동적 태그 분석
- **`<if>`**: 총 22개 사용
  - null 체크: `test="param != null"`
  - 빈 문자열 체크: `test="param != null and param != ''"`
  - 숫자 타입: `test="param != null"`
- **`<where>`**: 총 6개 사용 (자동 AND 제거 기능)
- **`<set>`**: 총 2개 사용 (자동 쉼표 제거 기능)
- **`<foreach>`**: 총 2개 사용 (IN 절 처리)
- **`<trim>`**: 총 4개 사용 (접두사/접미사 제거)

#### 1.4.2 데이터베이스 특화 함수
- **Oracle 함수**: TO_DATE(), SYSDATE 사용
- **날짜 포맷**: 'YYYY-MM-DD' 패턴 사용
- **문자열 처리**: LIKE 패턴 사용

## 2. JSP 페이지 상세 분석

### 2.1 정상 JSP 파일 분석

#### 2.1.1 user/list.jsp
- **파일**: `src/main/webapp/user/list.jsp`
- **기능**: 사용자 목록 표시 및 검색
- **인코딩**: UTF-8
- **JSTL 태그 사용** (총 9개):
  - `<%@ taglib prefix="c"`: core 태그 라이브러리
  - `<%@ taglib prefix="fmt"`: formatting 태그 라이브러리
  - `<c:url>`: URL 생성 (2개 사용)
  - `<c:choose>`, `<c:when>`, `<c:otherwise>`: 조건부 처리 (2세트)
  - `<c:forEach>`: 반복 처리 (1개)
  - `<fmt:formatDate>`: 날짜 포맷팅
- **HTML 구조 분석**:
  - DOCTYPE html 선언
  - meta charset="UTF-8"
  - CSS 스타일 정의 (4개 클래스)
  - JavaScript 함수 2개
- **CSS 클래스**:
  - `.search-form`: 검색 폼 스타일
  - `.user-table`: 테이블 스타일
  - `.status-active`: 활성 상태 스타일 (녹색)
  - `.status-inactive`: 비활성 상태 스타일 (빨간색)
- **JavaScript 기능**:
  - `validateSearch()`: 클라이언트 사이드 검증
  - 폼 제출 이벤트 리스너
- **폼 구조**:
  - GET 방식 검색 폼
  - 3개 입력 필드: name, email, status (select)
  - 검색 버튼
- **테이블 구조**:
  - 10개 컬럼 헤더
  - 동적 행 생성 (`<c:forEach>`)
  - 조건부 메시지 표시

#### 2.1.2 product/list.jsp
- **파일**: `src/main/webapp/product/list.jsp`
- **기능**: 상품 목록 표시

#### 2.1.3 user/searchResult.jsp
- **파일**: `src/main/webapp/user/searchResult.jsp`
- **기능**: 고급 검색 결과 표시

### 2.2 오류 포함 JSP 파일 분석

#### 2.2.1 mixed/partialError.jsp ⚠️
- **파일**: `src/main/webapp/mixed/partialError.jsp`
- **기능**: 정상 부분과 오류 부분이 혼재된 JSP
- **정상 부분 분석**:
  - 라인 1-3: 정상적인 페이지 디렉티브 및 taglib 선언
  - 라인 19-26: 정상적인 `<c:if>` 태그 사용
  - 라인 29-56: 정상적인 테이블 구조 및 `<c:forEach>` 태그
  - 라인 64-66: 정상적인 `<c:if>` 태그
  - 라인 79-83: 정상적인 HTML 링크
- **오류 부분 분석**:
  - 라인 59: 스코프 오류 (`${user.status}`에서 user 변수가 forEach 외부에서 사용)
  - 라인 74: 정의되지 않은 변수 참조 (`userList` 변수)
  - 라인 86-92: 태그 구조 오류 (`<c:choose>` 태그의 `</c:choose>` 닫기 태그 누락)
- **스크립틀릿 분석**:
  - 라인 69-77: 정상적인 스크립틀릿 사용
  - 현재 시간 출력 기능
  - 정의되지 않은 변수 참조 오류 포함

#### 2.2.2 error/syntaxError.jsp
- **파일**: `src/main/webapp/error/syntaxError.jsp`
- **기능**: 문법 오류가 수정된 정상 JSP 페이지

### 2.3 JSP 오류 유형별 분석

#### 2.3.1 JSTL 태그 오류
1. **태그 닫기 누락**: `<c:choose>` 태그의 `</c:choose>` 누락
2. **스코프 오류**: forEach 루프 외부에서 루프 변수 사용
3. **정의되지 않은 변수**: `userList` 변수 참조

#### 2.3.2 EL 표현식 오류
1. **잘못된 속성 참조**: 존재하지 않는 객체 속성 참조
2. **스코프 오류**: 잘못된 범위에서 변수 참조

#### 2.3.3 스크립틀릿 오류
1. **정의되지 않은 변수**: Java 코드에서 선언되지 않은 변수 사용

### 2.4 JSP 태그 사용 통계

#### 2.4.1 JSTL Core 태그
- **`<c:if>`**: 조건부 처리
- **`<c:choose>`, `<c:when>`, `<c:otherwise>`**: 다중 조건 분기
- **`<c:forEach>`**: 컬렉션 반복 처리
- **`<c:url>`**: URL 생성 및 인코딩

#### 2.4.2 JSTL Formatting 태그
- **`<fmt:formatDate>`**: 날짜 포맷팅
- **`<fmt:formatNumber>`**: 숫자 포맷팅 (추정)

## 3. 파서 검증 체크리스트

### 3.1 Java 파서 검증 항목

#### 3.1.1 클래스 레벨 검증
- [ ] 총 클래스 수: 16개 인식
  - Controller: 5개
  - Service: 6개 (인터페이스 2개, 구현체 4개)
  - Mapper: 3개
  - Model: 2개
- [ ] 패키지 구조 인식: com.example.* 패키지
- [ ] import 구문 인식
- [ ] 클래스 어노테이션 인식: @Controller, @Service, @Repository 등

#### 3.1.2 메소드 레벨 검증
- [ ] 총 메소드 수: 약 50개+ 인식
- [ ] 메소드 어노테이션: @GetMapping, @PostMapping, @RequestParam, @PathVariable 등
- [ ] 메소드 시그니처 파싱
- [ ] 반환 타입 인식

#### 3.1.3 필드 레벨 검증
- [ ] User 모델: 12개 필드 인식
- [ ] Product 모델: 예상 10-15개 필드 인식
- [ ] 필드 어노테이션: @Autowired, @Param 등

#### 3.1.4 오류 감지 검증
- [ ] 컴파일 오류 감지: 타입 불일치, 중복 선언 등
- [ ] 구문 오류 감지: 중괄호 불일치, 세미콜론 누락 등
- [ ] 논리 오류 감지: 무한루프, break 누락 등

### 3.2 XML 파서 검증 항목

#### 3.2.1 MyBatis 매퍼 검증
- [ ] 총 XML 파일 수: 4개 인식
- [ ] 네임스페이스 인식: 4개 네임스페이스
- [ ] 쿼리 태그 수: SELECT, UPDATE, INSERT, DELETE 태그
- [ ] 동적 쿼리 태그: `<if>`, `<where>`, `<set>`, `<foreach>`, `<trim>` 태그

#### 3.2.2 동적 쿼리 요소 검증
- [ ] 총 동적 요소 수: 50개+ 인식
- [ ] `<if>` 태그: 22개+ 인식
- [ ] `<where>` 태그: 6개 인식
- [ ] `<foreach>` 태그: 2개 인식

### 3.3 JSP 파서 검증 항목

#### 3.3.1 JSP 파일 기본 검증
- [ ] 총 JSP 파일 수: 8개 인식
- [ ] 페이지 디렉티브 인식
- [ ] taglib 디렉티브 인식

#### 3.3.2 JSTL 태그 검증
- [ ] 총 JSTL 태그 수: 30개+ 인식
- [ ] Core 태그: `<c:if>`, `<c:choose>`, `<c:forEach>` 등
- [ ] Formatting 태그: `<fmt:formatDate>` 등

#### 3.3.3 JSP 오류 감지 검증
- [ ] 태그 닫기 누락 감지
- [ ] 정의되지 않은 변수 참조 감지
- [ ] 스코프 오류 감지

## 4. 검증 성공 기준

### 4.1 정확도 기준
- **과소추출**: 0% (누락 없음)
- **과다추출**: 10% 이내 허용
- **파일별 오차**: 10% 이내 허용
- **오류 감지**: 100% (모든 의도적 오류 감지)

### 4.2 성능 기준
- **파싱 시간**: 파일당 1초 이내
- **메모리 사용량**: 합리적 수준 유지
- **오류 복구**: 부분 오류 시 계속 진행

## 5. 종합 분석 결과

### 5.1 프로젝트 특성
1. **현실적 복잡성**: 실제 Spring MVC + MyBatis 프로젝트 수준
2. **다양한 패턴**: 기본 CRUD부터 복잡한 동적 쿼리까지
3. **의도적 오류**: 13개 이상의 다양한 오류 유형 포함
4. **포괄적 검증**: 전체 스택 검증 가능

### 5.2 파서 검증 포인트
1. **Java 파싱**: Spring 어노테이션, 복잡한 메소드 시그니처
2. **XML 파싱**: MyBatis 동적 쿼리, 복잡한 JOIN 쿼리
3. **JSP 파싱**: JSTL 태그, EL 표현식, 혼합 구조
4. **오류 감지**: 컴파일/런타임/논리/보안 오류

### 5.3 검증 가치
이 샘플 프로젝트는 파서의 **정확성**, **견고성**, **오류 감지 능력**을 종합적으로 검증할 수 있는 완전한 테스트베드 역할을 합니다.

---

**이 명세서는 Part 1과 함께 사용하여 완전한 파서 검증 프로세스를 수행할 수 있습니다.**