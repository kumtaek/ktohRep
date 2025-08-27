<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core"%>
<%@ taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt"%>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Legacy Data View</title>
</head>
<body>
    <h1>Legacy Data List</h1>
    
    <c:if test="${not empty dataList}">
        <table border="1">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Value</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <c:forEach var="item" items="${dataList}">
                    <tr>
                        <td><c:out value="${item.ID}"/></td>
                        <td><c:out value="${item.NAME}"/></td>
                        <td><c:out value="${item.VALUE}"/></td>
                        <td><c:out value="${item.STATUS}"/></td>
                    </tr>
                </c:forEach>
            </tbody>
        </table>
    </c:if>
    <c:if test="${empty dataList}">
        <p>No legacy data found.</p>
    </c:if>

    <p>Generated Report: <c:out value="${reportContent}"/></p>

    <%-- Example of a scriptlet calling a Java method --%>
    <% 
        com.example.legacy.LegacyService legacyService = (com.example.legacy.LegacyService) application.getAttribute("legacyService");
        if (legacyService != null) {
            // This part is conceptual, as direct service calls in JSP are discouraged in modern Spring apps
            // For analysis, we assume 'legacyService.getLegacyData' might be called here or via a controller
            // String dynamicStatus = request.getParameter("status");
            // List<Map<String, Object>> dynamicData = legacyService.getLegacyData("TYPE_X", dynamicStatus);
            // request.setAttribute("dynamicData", dynamicData);
        }
    %>
</body>
</html>