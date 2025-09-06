# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:39:56
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_161 as calculateOrderAmo...
  participant n2_method_263 as calculateOrderAmo...
  participant n3_method_365 as calculateOrderAmo...
  participant n4_method_467 as calculateOrderAmo...
  participant n5_method_569 as calculateOrderAmo...
  participant n6_method_59 as calculateOrderAmo...

  n6_method_59->>n1_method_161: inferred_sequence (10%)
  n1_method_161->>n2_method_263: inferred_sequence (10%)
  n2_method_263->>n3_method_365: inferred_sequence (10%)
  n3_method_365->>n4_method_467: inferred_sequence (10%)
  n4_method_467->>n5_method_569: inferred_sequence (10%)
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
  method:59: calculateOrderAmount() (method)
  method:161: calculateOrderAmount() (method)
  method:263: calculateOrderAmount() (method)
  method:365: calculateOrderAmount() (method)
  method:467: calculateOrderAmount() (method)
  method:569: calculateOrderAmount() (method)
```

엣지 목록 (5)
```json
  method:59 -> method:161 (inferred_sequence)
  method:161 -> method:263 (inferred_sequence)
  method:263 -> method:365 (inferred_sequence)
  method:365 -> method:467 (inferred_sequence)
  method:467 -> method:569 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:39:56*