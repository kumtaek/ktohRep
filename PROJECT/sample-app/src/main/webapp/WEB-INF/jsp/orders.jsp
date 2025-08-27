<%@ page contentType="text/html;charset=UTF-8" %>
<%@ taglib uri="http://java.sun.com/jsp/jstl/core" prefix="c" %>
<%@ include file="/WEB-INF/jsp/_fragments/header.jspf" %>
<html><body>
  <h1>Orders</h1>
  <form method="get" action="/orders">
    <input type="text" name="status" placeholder="status"/>
    <button type="submit">Filter</button>
  </form>
  <a href="/orders">Refresh</a>
  <ul>
    <c:forEach items="${items}" var="o">
      <li><a href="/orders/${o.id}">Order ${o.id}</a> - ${o.status}</li>
    </c:forEach>
  </ul>
  ${param.status}
</body></html>
