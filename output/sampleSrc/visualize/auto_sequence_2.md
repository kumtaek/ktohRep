# Artificial Flow: OrderMapper

**Entry Point**: com.example.mapper.OrderMapper.selectOrderById

**Category**: artificial

**Statistics**:
- Participants: 7
- Interactions: 6
- Unresolved calls: 0

```mermaid
sequenceDiagram
    participant method_23 as OrderMapper.selectOrderById()
    participant method_24 as OrderMapper.calculateOrderAmount()
    participant method_25 as OrderMapper.selectOrdersByStatus()
    participant method_26 as OrderMapper.getOrdersWithCustomerImplicitJoin()
    participant method_27 as OrderMapper.getComplexOrderReport()
    participant method_28 as OrderMapper.searchOrdersWithCriteria()
    participant method_29 as OrderMapper.executeDynamicQuery()

    method_23->>+method_24: calls calculateOrderAmount()
    method_24->>+method_25: calls selectOrdersByStatus()
    method_25->>+method_26: calls getOrdersWithCustomerImplicitJoin()
    method_26->>+method_27: calls getComplexOrderReport()
    method_27->>+method_28: calls searchOrdersWithCriteria()
    method_28->>+method_29: calls executeDynamicQuery()
```
