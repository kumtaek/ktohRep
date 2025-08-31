# Artificial Flow: OrderService

**Entry Point**: com.example.service.OrderService.calculateOrderTotal

**Category**: artificial

**Statistics**:
- Participants: 6
- Interactions: 5
- Unresolved calls: 0

```mermaid
sequenceDiagram
    participant method_42 as OrderService.calculateOrderTotal()
    participant method_43 as OrderService.getOrdersByStatus()
    participant method_44 as OrderService.generateOrderReport()
    participant method_45 as OrderService.largeOrderMethod1()
    participant method_46 as OrderService.largeOrderMethod2()
    participant method_47 as OrderService.largeOrderMethod3()

    method_42->>+method_43: calls getOrdersByStatus()
    method_43->>+method_44: calls generateOrderReport()
    method_44->>+method_45: calls largeOrderMethod1()
    method_45->>+method_46: calls largeOrderMethod2()
    method_46->>+method_47: calls largeOrderMethod3()
```
