<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core"%>
<%@ taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt"%>
<%@ page import="java.sql.*"%>
<%@ page import="java.util.List"%>
<%@ page import="java.util.Map"%>
<%@ page import="com.example.integrated.IntegratedService"%>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Integrated Test View</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1, h2 { color: #333; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        pre { background-color: #eee; padding: 10px; border-radius: 5px; overflow-x: auto; }
        .section { margin-bottom: 30px; padding: 15px; border: 1px solid #ccc; border-radius: 8px; }
        .comment-good { color: green; font-style: italic; }
        .comment-bad { color: red; font-style: italic; }
    </style>
</head>
<body>
    <jsp:include page="_fragments/integratedHeader.jspf" />

    <h1>Integrated Test Cases View</h1>

    <!-- ==================================================================== -->
    <!-- From ProductQuery.jsp & CustomerQuery.jsp: Dynamic SQL Generation -->
    <!-- ==================================================================== -->
    <div class="section">
        <h2>Dynamic SQL Generation (Product & Customer)</h2>
        <%--
            @Description : 요청 파라미터에 따라 동적으로 SQL 쿼리를 생성하는 예제입니다.
                           SQL Injection에 취약한 패턴을 포함하고 있습니다.
            @Parameters : id (상품 ID 또는 고객 ID), category (상품 카테고리), status (고객 상태)
        --%>
        <% 
            String productId = request.getParameter("productId");
            String productCategory = request.getParameter("productCategory");
            String customerId = request.getParameter("customerId");
            String customerStatus = request.getParameter("customerStatus");

            StringBuilder productSql = new StringBuilder("SELECT ID, NAME, PRICE FROM PRODUCT WHERE 1=1");
            if (productId != null && !productId.isEmpty()) {
                productSql.append(" AND ID = '").append(productId).append("'");
            }
            if (productCategory != null && !productCategory.isEmpty()) {
                productSql.append(" AND CATEGORY = '").append(productCategory).append("'");
            }
            out.println("<p>Generated Product SQL: <pre>" + productSql.toString() + "</pre></p>");

            StringBuilder customerSql = new StringBuilder("SELECT ID, NAME, EMAIL, STATUS FROM CUSTOMER WHERE 1=1");
            if (customerId != null && !customerId.isEmpty()) {
                customerSql.append(" AND ID = '").append(customerId).append("'");
            } else if (customerStatus != null && !customerStatus.isEmpty()) {
                customerSql.append(" AND STATUS = '").append(customerStatus).append("'");
            }
            out.println("<p>Generated Customer SQL: <pre>" + customerSql.toString() + "</pre></p>");
        %>
    </div>

    <!-- ==================================================================== -->
    <!-- From dynamicSqlView.jsp: JSTL and Scriptlet Dynamic SQL -->
    <!-- ==================================================================== -->
    <div class="section">
        <h2>JSTL & Scriptlet Dynamic SQL</h2>
        <%--
            @Description : JSTL 변수와 스크립틀릿을 조합하여 동적 SQL을 생성하는 예제입니다.
                           분석기가 SQL 문자열을 정확히 식별하는지 확인합니다.
            @Parameters : searchStatus (검색할 상태)
        --%>
        <c:set var="tableName" value="MY_DYNAMIC_DATA_TABLE" />
        <c:set var="whereClause" value="" />
        <c:if test="${not empty param.searchStatus}">
            <c:set var="whereClause" value="WHERE STATUS = '${param.searchStatus}'" />
        </c:if>

        <% 
            String dynamicSqlFromJstl = "SELECT * FROM " + pageContext.getAttribute("tableName") + " " + pageContext.getAttribute("whereClause");
            out.println("<p>Generated SQL from JSTL/Scriptlet: <pre>" + dynamicSqlFromJstl + "</pre></p>");
        %>
    </div>

    <!-- ==================================================================== -->
    <!-- From legacyView.jsp: Displaying Data from Backend -->
    <!-- ==================================================================== -->
    <div class="section">
        <h2>Legacy Data Display</h2>
        <%--
            @Description : 백엔드에서 전달된 레거시 데이터를 JSTL을 사용하여 테이블 형태로 출력하는 예제입니다.
                           데이터가 없을 경우 메시지를 표시합니다.
            @DataModel : List<Map<String, Object>> legacyDataList, String generatedReportContent
        --%>
        <c:if test="${not empty legacyDataList}">
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
                    <c:forEach var="item" items="${legacyDataList}">
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
        <c:if test="${empty legacyDataList}">
            <p>No legacy data found.</p>
        </c:if>

        <h3>Generated Report Content</h3>
        <pre><c:out value="${generatedReportContent}"/></pre>
    </div>

    <!-- ==================================================================== -->
    <!-- New: Well-commented and poorly commented JSP sections -->
    <!-- ==================================================================== -->
    <div class="section">
        <h2>JSP Comment Examples</h2>
        <h3>Well-Commented Section</h3>
        <%--
            @SectionName : User Greeting Logic
            @Description : 현재 로그인한 사용자의 이름을 가져와 환영 메시지를 출력합니다.
                           세션에 'userName' 속성이 존재할 경우 사용하고, 없을 경우 'Guest'로 처리합니다.
            @DataModel : String sessionScope.userName
        --%>
        <p class="comment-good">
            <% 
                String userName = (String) session.getAttribute("userName");
                if (userName == null || userName.isEmpty()) {
                    userName = "Guest";
                }
                out.println("Welcome, " + userName + "!");
            %>
        </p>

        <h3>Poorly Commented Section</h3>
        <%-- Just some logic --%>
        <p class="comment-bad">
            <% 
                int a = 10;
                int b = 20;
                int sum = a + b;
                out.println("Sum: " + sum);
            %>
        </p>
    </div>

    <!-- ==================================================================== -->
    <!-- New: Large JSP file example (simulated with many sections) -->
    <!-- ==================================================================== -->
    <div class="section">
        <h2>Large JSP File Example (Simulated)</h2>
        <p>This section simulates a very large JSP file with many repeated content blocks.</p>
        <c:forEach begin="1" end="50">
            <div style="margin-bottom: 10px; padding: 5px; border: 1px dashed #ccc;">
                <h3>Section <c:out value="${pageScope.index}"/></h3>
                <p>Content block for section <c:out value="${pageScope.index}"/>. This could contain complex logic, data display, or other includes.</p>
                <%-- Example of dynamic content within a large file --%>
                <% 
                    String dynamicContent = "Dynamic content for section " + pageContext.getAttribute("index");
                    out.println("<p>" + dynamicContent + "</p>");
                %>
                <ul>
                    <li>Item 1</li>
                    <li>Item 2</li>
                </ul>
            </div>
        </c:forEach>
    </div>

</body>
</html>
