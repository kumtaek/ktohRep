# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:35:53
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_141 as getOrdersWithCust...
  participant n2_method_243 as getOrdersWithCust...
  participant n3_method_345 as getOrdersWithCust...
  participant n4_method_39 as getOrdersWithCust...
  participant n5_method_447 as getOrdersWithCust...
  participant n6_method_549 as getOrdersWithCust...

  n4_method_39->>n1_method_141: inferred_sequence (10%)
  n1_method_141->>n2_method_243: inferred_sequence (10%)
  n2_method_243->>n3_method_345: inferred_sequence (10%)
  n3_method_345->>n5_method_447: inferred_sequence (10%)
  n5_method_447->>n6_method_549: inferred_sequence (10%)
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
  method:39: getOrdersWithCustomerImplicitJoin() (method)
  method:141: getOrdersWithCustomerImplicitJoin() (method)
  method:243: getOrdersWithCustomerImplicitJoin() (method)
  method:345: getOrdersWithCustomerImplicitJoin() (method)
  method:447: getOrdersWithCustomerImplicitJoin() (method)
  method:549: getOrdersWithCustomerImplicitJoin() (method)
```

엣지 목록 (5)
```json
  method:39 -> method:141 (inferred_sequence)
  method:141 -> method:243 (inferred_sequence)
  method:243 -> method:345 (inferred_sequence)
  method:345 -> method:447 (inferred_sequence)
  method:447 -> method:549 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:35:53*