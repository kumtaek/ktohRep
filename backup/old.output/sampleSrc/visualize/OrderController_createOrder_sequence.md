# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:32:51
- 노드 수: 7
- 엣지 수: 6

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_125 as createOrder()
  participant n2_method_227 as createOrder()
  participant n3_method_23 as createOrder()
  participant n4_method_28 as OrderController.u...
  participant n5_method_329 as createOrder()
  participant n6_method_431 as createOrder()
  participant n7_method_533 as createOrder()

  n3_method_23->>n4_method_28: call (80%)
  n1_method_125->>n4_method_28: call (80%)
  n2_method_227->>n4_method_28: call (80%)
  n5_method_329->>n4_method_28: call (80%)
  n6_method_431->>n4_method_28: call (80%)
  n7_method_533->>n4_method_28: call (80%)
```

## 범례

### 시퀀스 범례
- 실선 화살표: 해석된 메소드 호출
- 점선 화살표: 미해석 호출
- 숫자: 호출 순서

## 원본 데이터

<details>
<summary>원본 데이터를 보려면 클릭</summary>

노드 목록 (7)
```json
  method:23: createOrder() (method)
  method:125: createOrder() (method)
  method:227: createOrder() (method)
  method:329: createOrder() (method)
  method:431: createOrder() (method)
  method:533: createOrder() (method)
  method:28: OrderController.updateInventory() (method)
```

엣지 목록 (6)
```json
  method:23 -> method:28 (call)
  method:125 -> method:28 (call)
  method:227 -> method:28 (call)
  method:329 -> method:28 (call)
  method:431 -> method:28 (call)
  method:533 -> method:28 (call)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:32:51*