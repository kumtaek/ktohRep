# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:45:43
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_188 as getProductList()
  participant n2_method_290 as getProductList()
  participant n3_method_392 as getProductList()
  participant n4_method_494 as getProductList()
  participant n5_method_596 as getProductList()
  participant n6_method_86 as getProductList()

  n6_method_86->>n1_method_188: inferred_sequence (10%)
  n1_method_188->>n2_method_290: inferred_sequence (10%)
  n2_method_290->>n3_method_392: inferred_sequence (10%)
  n3_method_392->>n4_method_494: inferred_sequence (10%)
  n4_method_494->>n5_method_596: inferred_sequence (10%)
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
  method:86: getProductList() (method)
  method:188: getProductList() (method)
  method:290: getProductList() (method)
  method:392: getProductList() (method)
  method:494: getProductList() (method)
  method:596: getProductList() (method)
```

엣지 목록 (5)
```json
  method:86 -> method:188 (inferred_sequence)
  method:188 -> method:290 (inferred_sequence)
  method:290 -> method:392 (inferred_sequence)
  method:392 -> method:494 (inferred_sequence)
  method:494 -> method:596 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:45:43*