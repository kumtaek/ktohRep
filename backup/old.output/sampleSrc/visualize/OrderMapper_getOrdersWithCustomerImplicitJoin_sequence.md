# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:40:33
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_163 as getOrdersWithCust...
  participant n2_method_265 as getOrdersWithCust...
  participant n3_method_367 as getOrdersWithCust...
  participant n4_method_469 as getOrdersWithCust...
  participant n5_method_571 as getOrdersWithCust...
  participant n6_method_61 as getOrdersWithCust...

  n6_method_61->>n1_method_163: inferred_sequence (10%)
  n1_method_163->>n2_method_265: inferred_sequence (10%)
  n2_method_265->>n3_method_367: inferred_sequence (10%)
  n3_method_367->>n4_method_469: inferred_sequence (10%)
  n4_method_469->>n5_method_571: inferred_sequence (10%)
```

## 범례

### 시퀀스 범례
- 실선 화살표: 해석된 메소드 호출
- 점선 화살표: 미해석 호출
- 숫자: 호출 순서

## 원본 데이터

<details>
<summary>원본 데이터를 보려면 클릭</summary>

노드 목록 (6)
```json
  method:61: getOrdersWithCustomerImplicitJoin() (method)
  method:163: getOrdersWithCustomerImplicitJoin() (method)
  method:265: getOrdersWithCustomerImplicitJoin() (method)
  method:367: getOrdersWithCustomerImplicitJoin() (method)
  method:469: getOrdersWithCustomerImplicitJoin() (method)
  method:571: getOrdersWithCustomerImplicitJoin() (method)
```

엣지 목록 (5)
```json
  method:61 -> method:163 (inferred_sequence)
  method:163 -> method:265 (inferred_sequence)
  method:265 -> method:367 (inferred_sequence)
  method:367 -> method:469 (inferred_sequence)
  method:469 -> method:571 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:40:33*