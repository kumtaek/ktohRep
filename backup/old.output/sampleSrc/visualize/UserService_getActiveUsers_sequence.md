# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:46:44
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_194 as getActiveUsers()
  participant n2_method_296 as getActiveUsers()
  participant n3_method_398 as getActiveUsers()
  participant n4_method_500 as getActiveUsers()
  participant n5_method_602 as getActiveUsers()
  participant n6_method_92 as getActiveUsers()

  n6_method_92->>n1_method_194: inferred_sequence (10%)
  n1_method_194->>n2_method_296: inferred_sequence (10%)
  n2_method_296->>n3_method_398: inferred_sequence (10%)
  n3_method_398->>n4_method_500: inferred_sequence (10%)
  n4_method_500->>n5_method_602: inferred_sequence (10%)
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
  method:92: getActiveUsers() (method)
  method:194: getActiveUsers() (method)
  method:296: getActiveUsers() (method)
  method:398: getActiveUsers() (method)
  method:500: getActiveUsers() (method)
  method:602: getActiveUsers() (method)
```

엣지 목록 (5)
```json
  method:92 -> method:194 (inferred_sequence)
  method:194 -> method:296 (inferred_sequence)
  method:296 -> method:398 (inferred_sequence)
  method:398 -> method:500 (inferred_sequence)
  method:500 -> method:602 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:46:44*