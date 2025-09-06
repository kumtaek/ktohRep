# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:35:41
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_140 as getOrdersWithCust...
  participant n2_method_242 as getOrdersWithCust...
  participant n3_method_344 as getOrdersWithCust...
  participant n4_method_38 as getOrdersWithCust...
  participant n5_method_446 as getOrdersWithCust...
  participant n6_method_548 as getOrdersWithCust...

  n4_method_38->>n1_method_140: inferred_sequence (10%)
  n1_method_140->>n2_method_242: inferred_sequence (10%)
  n2_method_242->>n3_method_344: inferred_sequence (10%)
  n3_method_344->>n5_method_446: inferred_sequence (10%)
  n5_method_446->>n6_method_548: inferred_sequence (10%)
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
  method:38: getOrdersWithCustomerAnsiJoin() (method)
  method:140: getOrdersWithCustomerAnsiJoin() (method)
  method:242: getOrdersWithCustomerAnsiJoin() (method)
  method:344: getOrdersWithCustomerAnsiJoin() (method)
  method:446: getOrdersWithCustomerAnsiJoin() (method)
  method:548: getOrdersWithCustomerAnsiJoin() (method)
```

엣지 목록 (5)
```json
  method:38 -> method:140 (inferred_sequence)
  method:140 -> method:242 (inferred_sequence)
  method:242 -> method:344 (inferred_sequence)
  method:344 -> method:446 (inferred_sequence)
  method:446 -> method:548 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:35:41*