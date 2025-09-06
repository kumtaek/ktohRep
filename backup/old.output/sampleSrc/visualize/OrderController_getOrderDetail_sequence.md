# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:33:03
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_127 as getOrderDetail()
  participant n2_method_229 as getOrderDetail()
  participant n3_method_25 as getOrderDetail()
  participant n4_method_331 as getOrderDetail()
  participant n5_method_433 as getOrderDetail()
  participant n6_method_535 as getOrderDetail()

  n3_method_25->>n1_method_127: inferred_sequence (10%)
  n1_method_127->>n2_method_229: inferred_sequence (10%)
  n2_method_229->>n4_method_331: inferred_sequence (10%)
  n4_method_331->>n5_method_433: inferred_sequence (10%)
  n5_method_433->>n6_method_535: inferred_sequence (10%)
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
  method:25: getOrderDetail() (method)
  method:127: getOrderDetail() (method)
  method:229: getOrderDetail() (method)
  method:331: getOrderDetail() (method)
  method:433: getOrderDetail() (method)
  method:535: getOrderDetail() (method)
```

엣지 목록 (5)
```json
  method:25 -> method:127 (inferred_sequence)
  method:127 -> method:229 (inferred_sequence)
  method:229 -> method:331 (inferred_sequence)
  method:331 -> method:433 (inferred_sequence)
  method:433 -> method:535 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:33:03*