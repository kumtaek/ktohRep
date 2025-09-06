# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:42:50
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_176 as insertUser()
  participant n2_method_278 as insertUser()
  participant n3_method_380 as insertUser()
  participant n4_method_482 as insertUser()
  participant n5_method_584 as insertUser()
  participant n6_method_74 as insertUser()

  n6_method_74->>n1_method_176: inferred_sequence (10%)
  n1_method_176->>n2_method_278: inferred_sequence (10%)
  n2_method_278->>n3_method_380: inferred_sequence (10%)
  n3_method_380->>n4_method_482: inferred_sequence (10%)
  n4_method_482->>n5_method_584: inferred_sequence (10%)
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
  method:74: insertUser() (method)
  method:176: insertUser() (method)
  method:278: insertUser() (method)
  method:380: insertUser() (method)
  method:482: insertUser() (method)
  method:584: insertUser() (method)
```

엣지 목록 (5)
```json
  method:74 -> method:176 (inferred_sequence)
  method:176 -> method:278 (inferred_sequence)
  method:278 -> method:380 (inferred_sequence)
  method:380 -> method:482 (inferred_sequence)
  method:482 -> method:584 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:42:50*