# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:41:10
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_162 as selectOrdersBySta...
  participant n2_method_264 as selectOrdersBySta...
  participant n3_method_366 as selectOrdersBySta...
  participant n4_method_468 as selectOrdersBySta...
  participant n5_method_570 as selectOrdersBySta...
  participant n6_method_60 as selectOrdersBySta...

  n6_method_60->>n1_method_162: inferred_sequence (10%)
  n1_method_162->>n2_method_264: inferred_sequence (10%)
  n2_method_264->>n3_method_366: inferred_sequence (10%)
  n3_method_366->>n4_method_468: inferred_sequence (10%)
  n4_method_468->>n5_method_570: inferred_sequence (10%)
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
  method:60: selectOrdersByStatus() (method)
  method:162: selectOrdersByStatus() (method)
  method:264: selectOrdersByStatus() (method)
  method:366: selectOrdersByStatus() (method)
  method:468: selectOrdersByStatus() (method)
  method:570: selectOrdersByStatus() (method)
```

엣지 목록 (5)
```json
  method:60 -> method:162 (inferred_sequence)
  method:162 -> method:264 (inferred_sequence)
  method:264 -> method:366 (inferred_sequence)
  method:366 -> method:468 (inferred_sequence)
  method:468 -> method:570 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:41:10*