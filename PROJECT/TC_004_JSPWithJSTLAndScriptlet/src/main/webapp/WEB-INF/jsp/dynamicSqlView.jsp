<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core"%>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Dynamic SQL View</title>
</head>
<body>
    <h1>Dynamic SQL Example</h1>
    
    <c:set var="tableName" value="MY_DATA_TABLE" />
    <c:set var="whereClause" value="" />
    <c:if test="${not empty searchStatus}">
        <c:set var="whereClause" value="WHERE STATUS = '${searchStatus}'" />
    </c:if>

    <%-- JSTL and scriptlet combined to form a dynamic SQL string --%>
    <% 
        String dynamicSql = "SELECT * FROM " + pageContext.getAttribute("tableName") + " " + pageContext.getAttribute("whereClause");
        // In a real scenario, this dynamicSql would be executed, e.g., via JDBC or a DAO
        // For testing purposes, we just need to ensure the parser can identify this string as SQL
        // System.out.println("Generated SQL: " + dynamicSql);
    %>

    <p>Generated SQL (conceptual): <%= dynamicSql %></p>

    <ul>
        <c:forEach var="item" items="${dataList}">
            <li><c:out value="${item}"/></li>
        </c:forEach>
    </ul>
</body>
</html>