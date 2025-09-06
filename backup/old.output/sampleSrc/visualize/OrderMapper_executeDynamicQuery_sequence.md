# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:40:08
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_166 as executeDynamicQue...
  participant n2_method_268 as executeDynamicQue...
  participant n3_method_370 as executeDynamicQue...
  participant n4_method_472 as executeDynamicQue...
  participant n5_method_574 as executeDynamicQue...
  participant n6_method_64 as executeDynamicQue...

  n6_method_64->>n1_method_166: inferred_sequence (10%)
  n1_method_166->>n2_method_268: inferred_sequence (10%)
  n2_method_268->>n3_method_370: inferred_sequence (10%)
  n3_method_370->>n4_method_472: inferred_sequence (10%)
  n4_method_472->>n5_method_574: inferred_sequence (10%)
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
  method:64: executeDynamicQuery() (method)
  method:166: executeDynamicQuery() (method)
  method:268: executeDynamicQuery() (method)
  method:370: executeDynamicQuery() (method)
  method:472: executeDynamicQuery() (method)
  method:574: executeDynamicQuery() (method)
```

엣지 목록 (5)
```json
  method:64 -> method:166 (inferred_sequence)
  method:166 -> method:268 (inferred_sequence)
  method:268 -> method:370 (inferred_sequence)
  method:370 -> method:472 (inferred_sequence)
  method:472 -> method:574 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:40:08*