<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>
<%@ taglib uri="http://java.sun.com/jsp/jstl/sql" prefix="sql" %>
<%@ include file="_fragments/integratedHeader.jspf" %>
<html>
<body>
<h3>IntegratedView</h3>

<%
    // Scriptlet building a SQL string (for parser extraction / vuln detector)
    String productId = request.getParameter("id");
    String sql = "SELECT * FROM PRODUCTS WHERE DEL_YN = 'N'";
    if (productId != null) {
        sql = sql + " AND PRODUCT_ID = '" + productId + "'"; // potential SQLi if unchecked
    }
%>

<p>Inline SQL (scriptlet) should be detected.</p>

<sql:query var="custQuery">
  SELECT CUSTOMER_ID, CUSTOMER_NAME
  FROM CUSTOMERS
  WHERE STATUS = 'ACTIVE'
</sql:query>

<c:forEach var="row" items="${custQuery.rows}">
  <div>Customer: ${row.CUSTOMER_NAME}</div>
  <br/>
</c:forEach>

</body>
</html>

