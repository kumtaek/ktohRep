# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:42:26
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_177 as executeDynamicQue...
  participant n2_method_279 as executeDynamicQue...
  participant n3_method_381 as executeDynamicQue...
  participant n4_method_483 as executeDynamicQue...
  participant n5_method_585 as executeDynamicQue...
  participant n6_method_75 as executeDynamicQue...

  n6_method_75->>n1_method_177: inferred_sequence (10%)
  n1_method_177->>n2_method_279: inferred_sequence (10%)
  n2_method_279->>n3_method_381: inferred_sequence (10%)
  n3_method_381->>n4_method_483: inferred_sequence (10%)
  n4_method_483->>n5_method_585: inferred_sequence (10%)
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
  method:75: executeDynamicQuery() (method)
  method:177: executeDynamicQuery() (method)
  method:279: executeDynamicQuery() (method)
  method:381: executeDynamicQuery() (method)
  method:483: executeDynamicQuery() (method)
  method:585: executeDynamicQuery() (method)
```

엣지 목록 (5)
```json
  method:75 -> method:177 (inferred_sequence)
  method:177 -> method:279 (inferred_sequence)
  method:279 -> method:381 (inferred_sequence)
  method:381 -> method:483 (inferred_sequence)
  method:483 -> method:585 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:42:26*