# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:36:42
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_144 as getStaticUserData()
  participant n2_method_246 as getStaticUserData()
  participant n3_method_348 as getStaticUserData()
  participant n4_method_42 as getStaticUserData()
  participant n5_method_450 as getStaticUserData()
  participant n6_method_552 as getStaticUserData()

  n4_method_42->>n1_method_144: inferred_sequence (10%)
  n1_method_144->>n2_method_246: inferred_sequence (10%)
  n2_method_246->>n3_method_348: inferred_sequence (10%)
  n3_method_348->>n5_method_450: inferred_sequence (10%)
  n5_method_450->>n6_method_552: inferred_sequence (10%)
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
  method:42: getStaticUserData() (method)
  method:144: getStaticUserData() (method)
  method:246: getStaticUserData() (method)
  method:348: getStaticUserData() (method)
  method:450: getStaticUserData() (method)
  method:552: getStaticUserData() (method)
```

엣지 목록 (5)
```json
  method:42 -> method:144 (inferred_sequence)
  method:144 -> method:246 (inferred_sequence)
  method:246 -> method:348 (inferred_sequence)
  method:348 -> method:450 (inferred_sequence)
  method:450 -> method:552 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:36:42*