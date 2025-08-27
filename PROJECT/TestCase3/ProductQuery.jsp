<%@ page language="java" contentType="text/html; charset=UTF-8" %>
<%
String query = "SELECT ID, NAME, PRICE FROM PRODUCT WHERE 1=1";
String id = request.getParameter("id");
String category = request.getParameter("category");
if (id != null && !id.isEmpty()) {
    query += " AND ID = '" + id + "'";
}
if (category != null && !category.isEmpty()) {
    query += " AND CATEGORY = '" + category + "'";
}
%>
