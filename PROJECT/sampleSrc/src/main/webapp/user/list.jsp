<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<%@ taglib prefix="fmt" uri="http://java.sun.com/jsp/jstl/fmt" %>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>사용자 목록</title>
    <style>
        .search-form { margin: 20px 0; padding: 15px; background: #f5f5f5; }
        .user-table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        .user-table th, .user-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .user-table th { background-color: #4CAF50; color: white; }
        .status-active { color: green; font-weight: bold; }
        .status-inactive { color: red; font-weight: bold; }
    </style>
</head>
<body>
    <h1>사용자 목록</h1>
    
    <!-- 검색 폼 -->
    <div class="search-form">
        <form method="get" action="<c:url value='/user/list'/>">
            <label>이름: <input type="text" name="name" value="${searchParams.name}" placeholder="이름으로 검색"></label>
            <label>이메일: <input type="text" name="email" value="${searchParams.email}" placeholder="이메일로 검색"></label>
            <label>상태: 
                <select name="status">
                    <option value="">전체</option>
                    <option value="ACTIVE" ${searchParams.status == 'ACTIVE' ? 'selected' : ''}>활성</option>
                    <option value="INACTIVE" ${searchParams.status == 'INACTIVE' ? 'selected' : ''}>비활성</option>
                </select>
            </label>
            <button type="submit">검색</button>
        </form>
    </div>
    
    <!-- 사용자 목록 테이블 -->
    <table class="user-table">
        <thead>
            <tr>
                <th>ID</th>
                <th>사용자명</th>
                <th>이메일</th>
                <th>이름</th>
                <th>나이</th>
                <th>상태</th>
                <th>사용자 유형</th>
                <th>전화번호</th>
                <th>주소</th>
                <th>생성일</th>
            </tr>
        </thead>
        <tbody>
            <c:choose>
                <c:when test="${empty users}">
                    <tr>
                        <td colspan="10" style="text-align: center;">검색 결과가 없습니다.</td>
                    </tr>
                </c:when>
                <c:otherwise>
                    <c:forEach var="user" items="${users}">
                        <tr>
                            <td>${user.id}</td>
                            <td>${user.username}</td>
                            <td>${user.email}</td>
                            <td>${user.name}</td>
                            <td>${user.age}</td>
                            <td>
                                <c:choose>
                                    <c:when test="${user.status == 'ACTIVE'}">
                                        <span class="status-active">활성</span>
                                    </c:when>
                                    <c:otherwise>
                                        <span class="status-inactive">비활성</span>
                                    </c:otherwise>
                                </c:choose>
                            </td>
                            <td>${user.userType}</td>
                            <td>${user.phone}</td>
                            <td>${user.address}</td>
                            <td><fmt:formatDate value="${user.createdDate}" pattern="yyyy-MM-dd HH:mm"/></td>
                        </tr>
                    </c:forEach>
                </c:otherwise>
            </c:choose>
        </tbody>
    </table>
    
    <!-- 고급 검색 링크 -->
    <div style="margin: 20px 0;">
        <a href="<c:url value='/user/advanced-search'/>">고급 검색</a>
    </div>
    
    <script>
        // 클라이언트 사이드 검증
        function validateSearch() {
            var name = document.querySelector('input[name="name"]').value;
            var email = document.querySelector('input[name="email"]').value;
            
            if (name.length > 0 && name.length < 2) {
                alert('이름은 2자 이상 입력해주세요.');
                return false;
            }
            
            if (email.length > 0 && !email.includes('@')) {
                alert('올바른 이메일 형식을 입력해주세요.');
                return false;
            }
            
            return true;
        }
        
        // 폼 제출 시 검증
        document.querySelector('form').addEventListener('submit', function(e) {
            if (!validateSearch()) {
                e.preventDefault();
            }
        });
    </script>
</body>
</html>

