# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:46:07
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_190 as searchProducts()
  participant n2_method_292 as searchProducts()
  participant n3_method_394 as searchProducts()
  participant n4_method_496 as searchProducts()
  participant n5_method_598 as searchProducts()
  participant n6_method_88 as searchProducts()

  n6_method_88->>n1_method_190: inferred_sequence (10%)
  n1_method_190->>n2_method_292: inferred_sequence (10%)
  n2_method_292->>n3_method_394: inferred_sequence (10%)
  n3_method_394->>n4_method_496: inferred_sequence (10%)
  n4_method_496->>n5_method_598: inferred_sequence (10%)
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
  method:88: searchProducts() (method)
  method:190: searchProducts() (method)
  method:292: searchProducts() (method)
  method:394: searchProducts() (method)
  method:496: searchProducts() (method)
  method:598: searchProducts() (method)
```

엣지 목록 (5)
```json
  method:88 -> method:190 (inferred_sequence)
  method:190 -> method:292 (inferred_sequence)
  method:292 -> method:394 (inferred_sequence)
  method:394 -> method:496 (inferred_sequence)
  method:496 -> method:598 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:46:07*