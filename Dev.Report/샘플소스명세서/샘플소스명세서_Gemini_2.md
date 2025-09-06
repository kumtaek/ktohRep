# 샘플소스명세서 - sampleSrc 분석 (Part 2)

## 4. Mapper 분석 (Java 인터페이스 및 XML)

### 4.1 UserMapper (UserMapper.java, UserMapper.xml)
- **기능**: 사용자 데이터에 접근하기 위한 MyBatis 매퍼입니다.
- **주요 쿼리**:
  - `selectUsersByCondition`: 이름, 이메일, 상태 등 단순 조건으로 사용자를 검색합니다. (`<if>` 사용)
  - `selectUsersByAdvancedCondition`: 사용자 유형, 나이/가입일자 범위 등 복합 조건으로 검색합니다. (`<if>`, `<foreach>` 사용)
  - `updateUserDynamic`: 사용자 정보 중 변경이 필요한 필드만 동적으로 업데이트합니다. (`<set>`, `<if>` 사용)
  - `insertUserDynamic`: 사용자 정보 중 `null`이 아닌 필드만 동적으로 추가합니다. (`<trim>`, `<if>` 사용)
  - `deleteUsersByCondition`: 특정 상태, 유형, 가입일자 이전의 사용자를 삭제합니다.

### 4.2 ProductMapper (ProductMapper.java, ProductMapper.xml)
- **기능**: 상품 데이터에 접근하기 위한 MyBatis 매퍼입니다.
- **주요 쿼리**:
  - `selectProductsByAdvancedCondition`: 카테고리, 브랜드, 가격/재고 범위, 상태 목록 등 매우 복잡한 조건으로 상품을 검색합니다.
  - `updateProductStock`: 상품 재고를 증가/감소시킵니다.
  - `updateProductDynamic`: 상품 정보 중 변경이 필요한 필드만 동적으로 업데이트합니다.
  - `insertProductDynamic`: 상품 정보 중 `null`이 아닌 필드만 동적으로 추가합니다.

### 4.3 오류 및 수정된 매퍼

#### MixedErrorMapper.xml
- **기능**: **의도적인 SQL 오류**를 포함한 매퍼 XML입니다.
- **분석**:
  - `selectByName`: 존재하지 않는 `active_flag` 컬럼을 참조하여 DB 오류를 유발합니다.
  - `update`: 존재하지 않는 `user_profiles` 테이블을 서브쿼리에서 참조합니다.
  - `searchUsers`: 존재하지 않는 `dept_name` 컬럼을 동적 쿼리에서 참조합니다.
  - `getUserWithDetails`: 존재하지 않는 `user_preferences` 테이블을 조인합니다.

#### BrokenMapper.java / BrokenMapper.xml
- **기능**: `MixedErrorMapper.xml` 등에서 발견된 **오류들을 모두 수정한 정상** 매퍼입니다.
- **분석**: 잘못된 테이블/컬럼명을 수정하고, 동적 SQL을 안전하게 구성하여 모든 쿼리가 정상적으로 실행됩니다.

## 5. JSP (JavaServer Pages) 분석

### 5.1 정상적인 JSP 파일
- **user/list.jsp, user/searchResult.jsp, user/typeList.jsp**: JSTL의 `<c:forEach>`, `<c:if>`, `<c:choose>` 등을 활용하여 컨트롤러에서 전달된 사용자 목록 및 검색 결과를 동적으로 화면에 표시합니다. CSS와 간단한 JavaScript 유효성 검증 기능이 포함되어 있습니다.
- **product/list.jsp, product/searchResult.jsp**: 상품 목록과 검색 결과를 동적으로 표시합니다.
- **error/syntaxError.jsp**: `partialError.jsp`의 **오류를 수정한 정상** JSP 파일입니다. 모든 JSTL 태그와 스크립틀릿이 올바르게 사용되었습니다.

### 5.2 오류가 포함된 JSP 파일

#### user/error.jsp
- **기능**: **다양한 유형의 프론트엔드 오류**를 의도적으로 포함한 JSP입니다.
- **분석**:
  - **JSTL 오류**: `<c:forEach>`가 `<c:if>`로 잘못 닫혔습니다. `${users.size()}`와 같이 EL에서 메서드를 직접 호출할 수 없습니다.
  - **JavaScript 오류**: 선언되지 않은 변수(`undefinedVariable`) 사용, 존재하지 않는 함수(`nonExistentFunction`) 호출, `null` 객체 속성 접근 등 런타임 오류가 발생합니다.
  - **HTML/CSS 오류**: `<tr>` 태그가 닫히지 않았고, 유효하지 않은 CSS 속성값(`invalid-color`)이 사용되었습니다.
  - **논리 오류**: 숫자형으로 변환되지 않은 문자열 파라미터에 덧셈 연산을 수행하여 예상치 못한 결과를 초래합니다.

#### mixed/partialError.jsp
- **기능**: **정상 코드와 오류 코드가 혼재**된 JSP입니다.
- **분석**:
  - **JSTL 오류**: `<c:choose>` 태그가 닫히지 않았습니다.
  - **EL 오류**: `forEach` 외부에서 아이템 변수(`user`)에 접근하여 오류가 발생합니다.
  - **스크립틀릿 오류**: 선언되지 않은 `userList` 변수를 참조하여 `NullPointerException`이 발생합니다.

## 6. 분석 요약 및 개선 제안

### 6.1 종합 분석
- `sampleSrc` 프로젝트는 Spring Boot와 MyBatis를 사용한 웹 애플리케이션의 표준적인 구조를 가지고 있습니다.
- 동적 SQL을 적극적으로 활용하여 유연한 데이터 조회가 가능하도록 설계되었습니다.
- `ErrorController`, `MixedErrorMapper` 등 의도적으로 오류를 포함시킨 파일들은 시스템의 오류 처리 능력과 개발자의 디버깅 능력을 테스트하기 위한 좋은 예시입니다.
- 전반적으로 백엔드 로직은 체계적이나, 프론트엔드(JSP)와 일부 Java 코드에서 기본적인 문법 및 런타임 오류가 다수 발견되었습니다.

### 6.2 발견된 오류 유형
1.  **Java 컴파일 오류**: 타입 불일치, import 누락, 세미콜론 누락, 중복 변수 선언.
2.  **Java 런타임 오류**: NullPointerException, ArrayIndexOutOfBoundsException, ClassCastException, NumberFormatException.
3.  **SQL 오류**: 존재하지 않는 테이블/컬럼 참조.
4.  **JSP/JSTL 오류**: 태그 불일치, 태그 미닫힘, 잘못된 EL 사용, 스크립틀릿 변수 참조 오류.
5.  **보안 취약점**: SQL Injection (ErrorController.java).

### 6.3 개선 제안
1.  **오류 수정**: 명세서에 기술된 모든 오류를 수정하여 애플리케이션이 정상적으로 동작하도록 해야 합니다.
2.  **예외 처리 강화**: 전역 예외 처리기(`@ControllerAdvice`)를 도입하여 중복된 `try-catch` 블록을 제거하고 일관된 오류 응답을 제공해야 합니다.
3.  **보안 강화**: MyBatis의 `#` 파라미터 바인딩을 일관되게 사용하여 SQL Injection을 원천적으로 차단해야 합니다. `ErrorController`의 예시는 실제 코드에 적용되어서는 안 됩니다.
4.  **정적 분석 도구 도입**: SonarQube, Checkstyle과 같은 정적 분석 도구를 CI/CD 파이프라인에 통합하여 잠재적인 버그와 코드 스멜을 조기에 발견해야 합니다.
5.  **단위 테스트 작성**: JUnit, Mockito 등을 사용하여 서비스 및 컨트롤러 계층에 대한 단위 테스트를 작성하여 코드의 안정성과 신뢰성을 높여야 합니다.
