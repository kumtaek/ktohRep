<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%@ include file="/WEB-INF/jsp/_fragments/header.jspf" %>

<html>
<head>
    <title>상품 검색</title>
</head>
<body>
    <h1>상품 검색 및 관리</h1>
    
    <%--
        상품 검색 폼
        @FormName: productSearchForm  
        @Description: 카테고리, 가격 범위, 브랜드별 상품 검색 기능 제공
        @Fields: category, minPrice, maxPrice, brand
    --%>
    <form method="post" action="productSearch.jsp">
        <div class="search-form">
            <label for="category">카테고리:</label>
            <select name="category" id="category">
                <option value="">전체</option>
                <option value="electronics">전자제품</option>
                <option value="clothing">의류</option>
                <option value="books">도서</option>
            </select>
            
            <label for="minPrice">최소가격:</label>
            <input type="number" name="minPrice" id="minPrice" placeholder="0"/>
            
            <label for="maxPrice">최대가격:</label>
            <input type="number" name="maxPrice" id="maxPrice" placeholder="999999"/>
            
            <label for="brand">브랜드:</label>
            <input type="text" name="brand" id="brand" placeholder="브랜드명"/>
            
            <input type="submit" value="검색"/>
        </div>
    </form>
    
    <%
        // 복잡한 검색 조건 처리 - 동적 SQL 생성
        String category = request.getParameter("category");
        String minPrice = request.getParameter("minPrice");
        String maxPrice = request.getParameter("maxPrice");
        String brand = request.getParameter("brand");
        
        if (category != null || minPrice != null || maxPrice != null || brand != null) {
            StringBuilder sql = new StringBuilder();
            sql.append("SELECT p.*, c.category_name, b.brand_name ");
            sql.append("FROM products p ");
            sql.append("LEFT JOIN categories c ON p.category_id = c.id ");
            sql.append("LEFT JOIN brands b ON p.brand_id = b.id ");
            sql.append("WHERE p.del_yn = 'N' ");
            
            // 동적 조건 추가 - SQL Injection 취약점
            if (category != null && !category.isEmpty()) {
                sql.append("AND c.category_code = '").append(category).append("' ");
            }
            if (minPrice != null && !minPrice.isEmpty()) {
                sql.append("AND p.price >= ").append(minPrice).append(" ");
            }
            if (maxPrice != null && !maxPrice.isEmpty()) {
                sql.append("AND p.price <= ").append(maxPrice).append(" ");
            }
            if (brand != null && !brand.isEmpty()) {
                sql.append("AND b.brand_name LIKE '%").append(brand).append("%' ");
            }
            
            sql.append("ORDER BY p.created_date DESC");
            
            // 생성된 SQL 출력 (개발용)
            out.println("<!-- 생성된 검색 SQL: " + sql.toString() + " -->");
        }
    %>
    
    <%-- 검색 결과 표시 --%>
    <div class="search-results">
        <c:if test="${not empty productList}">
            <h2>검색 결과 (${productList.size()}개)</h2>
            
            <div class="product-grid">
                <c:forEach var="product" items="${productList}" varStatus="status">
                    <div class="product-item">
                        <h3><c:out value="${product.name}"/></h3>
                        <p>카테고리: ${product.categoryName}</p>
                        <p>브랜드: ${product.brandName}</p>
                        <p class="price">${product.price}원</p>
                        <p class="description">${product.description}</p>
                        
                        <%-- XSS 취약점 예제 --%>
                        <div class="user-review">
                            사용자 리뷰: ${product.userReview}
                        </div>
                    </div>
                    
                    <%-- 10개마다 구분선 --%>
                    <c:if test="${status.count % 10 == 0}">
                        <hr class="section-divider"/>
                    </c:if>
                </c:forEach>
            </div>
        </c:if>
        
        <c:if test="${empty productList}">
            <p class="no-results">검색 결과가 없습니다.</p>
        </c:if>
    </div>
    
    <script type="text/javascript">
        // 가격 범위 유효성 검사
        function validatePriceRange() {
            var minPrice = document.getElementById('minPrice').value;
            var maxPrice = document.getElementById('maxPrice').value;
            
            if (minPrice && maxPrice && parseInt(minPrice) > parseInt(maxPrice)) {
                alert('최소가격이 최대가격보다 클 수 없습니다.');
                return false;
            }
            return true;
        }
        
        // 폼 제출 시 검증
        document.addEventListener('DOMContentLoaded', function() {
            var form = document.querySelector('form');
            form.onsubmit = validatePriceRange;
        });
    </script>
    
    <%-- 단순 반복 섹션 --%>
    <div class="promotional-section">
        <% for (int i = 1; i <= 15; i++) { %>
            <div class="promo-item-<%=i%>">
                <h4>프로모션 <%=i%></h4>
                <p>특가 상품 <%=i%> - 할인 혜택을 놓치지 마세요!</p>
            </div>
        <% } %>
    </div>
    
</body>
</html>