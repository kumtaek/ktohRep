<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<!-- 정상 JSP 샘플: 간단한 SQL 문자열 포함 -->
<%
    String sql = "select u.id, u.name from users u where u.status = 'A'";
%>
<html>
<body>
정상 JSP 샘플
</body>
</html>
