# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:43:15
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_173 as selectActiveUsers()
  participant n2_method_275 as selectActiveUsers()
  participant n3_method_377 as selectActiveUsers()
  participant n4_method_479 as selectActiveUsers()
  participant n5_method_581 as selectActiveUsers()
  participant n6_method_71 as selectActiveUsers()

  n6_method_71->>n1_method_173: inferred_sequence (10%)
  n1_method_173->>n2_method_275: inferred_sequence (10%)
  n2_method_275->>n3_method_377: inferred_sequence (10%)
  n3_method_377->>n4_method_479: inferred_sequence (10%)
  n4_method_479->>n5_method_581: inferred_sequence (10%)
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
  method:71: selectActiveUsers() (method)
  method:173: selectActiveUsers() (method)
  method:275: selectActiveUsers() (method)
  method:377: selectActiveUsers() (method)
  method:479: selectActiveUsers() (method)
  method:581: selectActiveUsers() (method)
```

엣지 목록 (5)
```json
  method:71 -> method:173 (inferred_sequence)
  method:173 -> method:275 (inferred_sequence)
  method:275 -> method:377 (inferred_sequence)
  method:377 -> method:479 (inferred_sequence)
  method:479 -> method:581 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:43:15*