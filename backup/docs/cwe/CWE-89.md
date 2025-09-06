# CWE-89: SQL Injection

## 설명
신뢰할 수 없는 입력이 SQL 쿼리 문맥에 삽입되어 실행되는 취약점입니다.

## 영향
- 데이터 유출/변조/삭제, 인증 우회, RCE(조건에 따라)

## 방어
- Prepared Statement/ORM 사용, 파라미터 바인딩
- 입력 검증/정규화, 에러 메시지 최소화
- 최소 권한 DB 계정, 감사 로깅/모니터링

## 취약/안전 코드 예시
### JDBC (취약)
```java
String sql = "SELECT * FROM t WHERE id=" + request.getParameter("id");
```

### JDBC (안전)
```java
String sql = "SELECT * FROM t WHERE id=?";
PreparedStatement ps = conn.prepareStatement(sql);
ps.setInt(1, Integer.parseInt(request.getParameter("id")));
```

### MyBatis (취약: `${}`)
```xml
<select id="q" resultType="map">
  SELECT * FROM t WHERE name = ${name}
</select>
```

### MyBatis (안전: `#{}`)
```xml
<select id="q" resultType="map">
  SELECT * FROM t WHERE name = #{name}
</select>
```

## 탐지 포인트
- 문자열 연결로 쿼리 생성
- MyBatis `${}` 사용
- 사용자 입력이 직접 LIKE/ORDER/LIMIT 등에 삽입
