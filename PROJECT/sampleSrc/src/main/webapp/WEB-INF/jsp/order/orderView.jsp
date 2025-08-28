<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%@ include file="/WEB-INF/jsp/_fragments/header.jspf" %>

<html>
<head>
    <title>주문 조회</title>
</head>
<body>
    <h1>주문 상세 정보</h1>
    
    <%-- JSTL과 스크립틀릿을 조합한 동적 처리 --%>
    <c:set var="orderStatus" value="${param.status}"/>
    
    <%
        // 주문 상태에 따른 동적 SQL 생성 예제
        String status = (String) pageContext.getAttribute("orderStatus");
        if (status != null && !status.isEmpty()) {
            String orderQuery = "SELECT o.*, c.name as customer_name " +
                              "FROM orders o JOIN customers c ON o.customer_id = c.id " +
                              "WHERE o.status = '" + status + "' AND o.del_yn = 'N'";
            
            // 이것은 SQL Injection에 취약한 패턴입니다
            out.println("<!-- 실행될 쿼리: " + orderQuery + " -->");
        }
    %>
    
    <%-- 조건부 주문 정보 표시 --%>
    <c:choose>
        <c:when test="${not empty orderInfo}">
            <div class="order-details">
                <h2>주문 번호: ${orderInfo.orderId}</h2>
                <p>고객명: <c:out value="${orderInfo.customerName}"/></p>
                <p>주문일: ${orderInfo.orderDate}</p>
                <p>상태: ${orderInfo.status}</p>
                <p>총액: ${orderInfo.totalAmount}원</p>
            </div>
            
            <%-- 주문 상품 목록 --%>
            <table border="1">
                <thead>
                    <tr><th>상품명</th><th>수량</th><th>단가</th><th>소계</th></tr>
                </thead>
                <tbody>
                    <c:forEach var="item" items="${orderInfo.items}">
                        <tr>
                            <td><c:out value="${item.productName}"/></td>
                            <td>${item.quantity}</td>
                            <td>${item.unitPrice}원</td>
                            <td>${item.subtotal}원</td>
                        </tr>
                    </c:forEach>
                </tbody>
            </table>
        </c:when>
        <c:otherwise>
            <p>주문 정보가 없습니다.</p>
        </c:otherwise>
    </c:choose>
    
    <script type="text/javascript">
        // 클라이언트 사이드 XSS 취약점 패턴
        function displayMessage() {
            var message = '${param.message}';  // XSS 취약점
            document.getElementById('messageArea').innerHTML = message;
        }
        
        function validateOrder() {
            console.log("주문 검증 로직 실행");
            return true;
        }
    </script>
    
    <div id="messageArea"></div>
    
    <!-- 부실한 주석의 예 -->
    <!-- 뭔가 처리 -->
    <div class="footer">
        <p>주문 처리 완료</p>
    </div>
    
</body>
</html>