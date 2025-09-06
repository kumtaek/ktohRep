# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:47:08
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_193 as getUserById()
  participant n2_method_295 as getUserById()
  participant n3_method_397 as getUserById()
  participant n4_method_499 as getUserById()
  participant n5_method_601 as getUserById()
  participant n6_method_91 as getUserById()

  n6_method_91->>n1_method_193: inferred_sequence (10%)
  n1_method_193->>n2_method_295: inferred_sequence (10%)
  n2_method_295->>n3_method_397: inferred_sequence (10%)
  n3_method_397->>n4_method_499: inferred_sequence (10%)
  n4_method_499->>n5_method_601: inferred_sequence (10%)
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
  method:91: getUserById() (method)
  method:193: getUserById() (method)
  method:295: getUserById() (method)
  method:397: getUserById() (method)
  method:499: getUserById() (method)
  method:601: getUserById() (method)
```

엣지 목록 (5)
```json
  method:91 -> method:193 (inferred_sequence)
  method:193 -> method:295 (inferred_sequence)
  method:295 -> method:397 (inferred_sequence)
  method:397 -> method:499 (inferred_sequence)
  method:499 -> method:601 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:47:08*