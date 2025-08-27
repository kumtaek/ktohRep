<%@ page contentType="text/html;charset=UTF-8" %>
<%@ include file="/WEB-INF/jsp/_fragments/header.jspf" %>
<html><body>
  <h1>Order Detail</h1>
  <div>ID: ${order.id}</div>
  <div>Status: ${order.status}</div>
  <form method="post" action="/orders/${order.id}/status">
    <input type="text" name="status" placeholder="new status"/>
    <button type="submit">Change</button>
  </form>
  <a href="/orders">Back</a>
</body></html>
