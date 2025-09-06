# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:41:23
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_171 as executeDynamicQue...
  participant n2_method_273 as executeDynamicQue...
  participant n3_method_375 as executeDynamicQue...
  participant n4_method_477 as executeDynamicQue...
  participant n5_method_579 as executeDynamicQue...
  participant n6_method_69 as executeDynamicQue...

  n6_method_69->>n1_method_171: inferred_sequence (10%)
  n1_method_171->>n2_method_273: inferred_sequence (10%)
  n2_method_273->>n3_method_375: inferred_sequence (10%)
  n3_method_375->>n4_method_477: inferred_sequence (10%)
  n4_method_477->>n5_method_579: inferred_sequence (10%)
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
  method:69: executeDynamicQuery() (method)
  method:171: executeDynamicQuery() (method)
  method:273: executeDynamicQuery() (method)
  method:375: executeDynamicQuery() (method)
  method:477: executeDynamicQuery() (method)
  method:579: executeDynamicQuery() (method)
```

엣지 목록 (5)
```json
  method:69 -> method:171 (inferred_sequence)
  method:171 -> method:273 (inferred_sequence)
  method:273 -> method:375 (inferred_sequence)
  method:375 -> method:477 (inferred_sequence)
  method:477 -> method:579 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:41:23*