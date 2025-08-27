<%@ page language="java" contentType="text/html; charset=UTF-8" %>
<%
String query = "SELECT ID, NAME, STATUS FROM CUSTOMER WHERE 1=1";
String id = request.getParameter("id");
String status = request.getParameter("status");
if (id != null && !id.isEmpty()) {
    query += " AND ID = '" + id + "'";
} else if (status != null && !status.isEmpty()) {
    query += " AND STATUS = '" + status + "'";
}
%>
