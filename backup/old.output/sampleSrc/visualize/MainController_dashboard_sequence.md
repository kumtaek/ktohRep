# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:32:02
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_124 as dashboard()
  participant n2_method_22 as dashboard()
  participant n3_method_226 as dashboard()
  participant n4_method_328 as dashboard()
  participant n5_method_430 as dashboard()
  participant n6_method_532 as dashboard()

  n2_method_22->>n1_method_124: inferred_sequence (10%)
  n1_method_124->>n3_method_226: inferred_sequence (10%)
  n3_method_226->>n4_method_328: inferred_sequence (10%)
  n4_method_328->>n5_method_430: inferred_sequence (10%)
  n5_method_430->>n6_method_532: inferred_sequence (10%)
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
  method:22: dashboard() (method)
  method:124: dashboard() (method)
  method:226: dashboard() (method)
  method:328: dashboard() (method)
  method:430: dashboard() (method)
  method:532: dashboard() (method)
```

엣지 목록 (5)
```json
  method:22 -> method:124 (inferred_sequence)
  method:124 -> method:226 (inferred_sequence)
  method:226 -> method:328 (inferred_sequence)
  method:328 -> method:430 (inferred_sequence)
  method:430 -> method:532 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:32:02*