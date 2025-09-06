# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:36:06
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_145 as calculateOrderTot...
  participant n2_method_247 as calculateOrderTot...
  participant n3_method_349 as calculateOrderTot...
  participant n4_method_43 as calculateOrderTot...
  participant n5_method_451 as calculateOrderTot...
  participant n6_method_553 as calculateOrderTot...

  n4_method_43->>n1_method_145: inferred_sequence (10%)
  n1_method_145->>n2_method_247: inferred_sequence (10%)
  n2_method_247->>n3_method_349: inferred_sequence (10%)
  n3_method_349->>n5_method_451: inferred_sequence (10%)
  n5_method_451->>n6_method_553: inferred_sequence (10%)
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
  method:43: calculateOrderTotal() (method)
  method:145: calculateOrderTotal() (method)
  method:247: calculateOrderTotal() (method)
  method:349: calculateOrderTotal() (method)
  method:451: calculateOrderTotal() (method)
  method:553: calculateOrderTotal() (method)
```

엣지 목록 (5)
```json
  method:43 -> method:145 (inferred_sequence)
  method:145 -> method:247 (inferred_sequence)
  method:247 -> method:349 (inferred_sequence)
  method:349 -> method:451 (inferred_sequence)
  method:451 -> method:553 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:36:06*