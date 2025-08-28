<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ include file="../_fragments/header.jspf" %>
<jsp:include page="../_fragments/integratedHeader.jspf" />
<html>
  <head><title>Test Page</title></head>
  <body>
    <h1>Test Page</h1>
    <%-- Scriptlet with SQL to trigger JSP SQL detection --%>
    <%
      String sql = "select * from USERS u join ORDERS o on u.USER_ID = o.USER_ID";
    %>
  </body>
</html>

