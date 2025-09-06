# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:40:45
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_165 as searchOrdersWithC...
  participant n2_method_267 as searchOrdersWithC...
  participant n3_method_369 as searchOrdersWithC...
  participant n4_method_471 as searchOrdersWithC...
  participant n5_method_573 as searchOrdersWithC...
  participant n6_method_63 as searchOrdersWithC...

  n6_method_63->>n1_method_165: inferred_sequence (10%)
  n1_method_165->>n2_method_267: inferred_sequence (10%)
  n2_method_267->>n3_method_369: inferred_sequence (10%)
  n3_method_369->>n4_method_471: inferred_sequence (10%)
  n4_method_471->>n5_method_573: inferred_sequence (10%)
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
  method:63: searchOrdersWithCriteria() (method)
  method:165: searchOrdersWithCriteria() (method)
  method:267: searchOrdersWithCriteria() (method)
  method:369: searchOrdersWithCriteria() (method)
  method:471: searchOrdersWithCriteria() (method)
  method:573: searchOrdersWithCriteria() (method)
```

엣지 목록 (5)
```json
  method:63 -> method:165 (inferred_sequence)
  method:165 -> method:267 (inferred_sequence)
  method:267 -> method:369 (inferred_sequence)
  method:369 -> method:471 (inferred_sequence)
  method:471 -> method:573 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:40:45*