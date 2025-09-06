# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:46:32
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_195 as createUser()
  participant n2_method_297 as createUser()
  participant n3_method_399 as createUser()
  participant n4_method_501 as createUser()
  participant n5_method_603 as createUser()
  participant n6_method_93 as createUser()

  n6_method_93->>n1_method_195: inferred_sequence (10%)
  n1_method_195->>n2_method_297: inferred_sequence (10%)
  n2_method_297->>n3_method_399: inferred_sequence (10%)
  n3_method_399->>n4_method_501: inferred_sequence (10%)
  n4_method_501->>n5_method_603: inferred_sequence (10%)
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
  method:93: createUser() (method)
  method:195: createUser() (method)
  method:297: createUser() (method)
  method:399: createUser() (method)
  method:501: createUser() (method)
  method:603: createUser() (method)
```

엣지 목록 (5)
```json
  method:93 -> method:195 (inferred_sequence)
  method:195 -> method:297 (inferred_sequence)
  method:297 -> method:399 (inferred_sequence)
  method:399 -> method:501 (inferred_sequence)
  method:501 -> method:603 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:46:32*