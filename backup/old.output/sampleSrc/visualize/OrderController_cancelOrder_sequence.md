# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:32:38
- 노드 수: 7
- 엣지 수: 6

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_129 as cancelOrder()
  participant n2_method_231 as cancelOrder()
  participant n3_method_27 as cancelOrder()
  participant n4_method_29 as OrderController.r...
  participant n5_method_333 as cancelOrder()
  participant n6_method_435 as cancelOrder()
  participant n7_method_537 as cancelOrder()

  n3_method_27->>n4_method_29: call (80%)
  n1_method_129->>n4_method_29: call (80%)
  n2_method_231->>n4_method_29: call (80%)
  n5_method_333->>n4_method_29: call (80%)
  n6_method_435->>n4_method_29: call (80%)
  n7_method_537->>n4_method_29: call (80%)
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
  method:27: cancelOrder() (method)
  method:129: cancelOrder() (method)
  method:231: cancelOrder() (method)
  method:333: cancelOrder() (method)
  method:435: cancelOrder() (method)
  method:537: cancelOrder() (method)
  method:29: OrderController.restoreInventory() (method)
```

엣지 목록 (6)
```json
  method:27 -> method:29 (call)
  method:129 -> method:29 (call)
  method:231 -> method:29 (call)
  method:333 -> method:29 (call)
  method:435 -> method:29 (call)
  method:537 -> method:29 (call)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:32:38*