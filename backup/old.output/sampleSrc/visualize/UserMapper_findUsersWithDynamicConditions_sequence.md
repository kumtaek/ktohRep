# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:42:38
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_175 as findUsersWithDyna...
  participant n2_method_277 as findUsersWithDyna...
  participant n3_method_379 as findUsersWithDyna...
  participant n4_method_481 as findUsersWithDyna...
  participant n5_method_583 as findUsersWithDyna...
  participant n6_method_73 as findUsersWithDyna...

  n6_method_73->>n1_method_175: inferred_sequence (10%)
  n1_method_175->>n2_method_277: inferred_sequence (10%)
  n2_method_277->>n3_method_379: inferred_sequence (10%)
  n3_method_379->>n4_method_481: inferred_sequence (10%)
  n4_method_481->>n5_method_583: inferred_sequence (10%)
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
  method:73: findUsersWithDynamicConditions() (method)
  method:175: findUsersWithDynamicConditions() (method)
  method:277: findUsersWithDynamicConditions() (method)
  method:379: findUsersWithDynamicConditions() (method)
  method:481: findUsersWithDynamicConditions() (method)
  method:583: findUsersWithDynamicConditions() (method)
```

엣지 목록 (5)
```json
  method:73 -> method:175 (inferred_sequence)
  method:175 -> method:277 (inferred_sequence)
  method:277 -> method:379 (inferred_sequence)
  method:379 -> method:481 (inferred_sequence)
  method:481 -> method:583 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:42:38*