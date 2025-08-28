<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%@ include file="/WEB-INF/jsp/_fragments/header.jspf" %>

<html>
<head>
    <title>사용자 목록</title>
</head>
<body>
    <h1>사용자 관리</h1>
    
    <%-- 
        사용자 검색 폼
        표준화된 주석 예제
    --%>
    <form method="post" action="userSearch.jsp">
        <label for="searchType">검색 조건:</label>
        <select name="searchType" id="searchType">
            <option value="name">이름</option>
            <option value="email">이메일</option>
        </select>
        <input type="text" name="searchValue" placeholder="검색어를 입력하세요"/>
        <input type="submit" value="검색"/>
    </form>
    
    <%-- 동적 SQL 생성 - SQL Injection 취약점 패턴 --%>
    <%
        String searchType = request.getParameter("searchType");
        String searchValue = request.getParameter("searchValue");
        
        if (searchType != null && searchValue != null) {
            // 취약한 SQL 생성 패턴
            String dynamicSql = "SELECT * FROM users WHERE " + searchType + " = '" + searchValue + "'";
            out.println("<!-- 생성된 SQL: " + dynamicSql + " -->");
        }
    %>
    
    <%-- 사용자 목록 출력 --%>
    <table border="1">
        <thead>
            <tr>
                <th>ID</th>
                <th>이름</th>
                <th>이메일</th>
                <th>상태</th>
            </tr>
        </thead>
        <tbody>
            <c:forEach var="user" items="${userList}">
                <tr>
                    <td>${user.id}</td>
                    <td><c:out value="${user.name}"/></td>
                    <td><c:out value="${user.email}"/></td>
                    <td>${user.status}</td>
                </tr>
            </c:forEach>
        </tbody>
    </table>
    
    <%-- 대용량 파일 시뮬레이션을 위한 반복 섹션 --%>
    <% for (int i = 0; i < 20; i++) { %>
        <div class="section-<%=i%>">
            <h3>섹션 <%=i%></h3>
            <p>이것은 대용량 JSP 파일 처리를 테스트하기 위한 반복 섹션입니다.</p>
            <ul>
                <li>항목 1</li>
                <li>항목 2</li>
                <li>항목 3</li>
            </ul>
        </div>
    <% } %>
    
</body>
</html>