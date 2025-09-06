# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:46:56
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_197 as getDynamicUserData()
  participant n2_method_299 as getDynamicUserData()
  participant n3_method_401 as getDynamicUserData()
  participant n4_method_503 as getDynamicUserData()
  participant n5_method_605 as getDynamicUserData()
  participant n6_method_95 as getDynamicUserData()

  n6_method_95->>n1_method_197: inferred_sequence (10%)
  n1_method_197->>n2_method_299: inferred_sequence (10%)
  n2_method_299->>n3_method_401: inferred_sequence (10%)
  n3_method_401->>n4_method_503: inferred_sequence (10%)
  n4_method_503->>n5_method_605: inferred_sequence (10%)
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
  method:95: getDynamicUserData() (method)
  method:197: getDynamicUserData() (method)
  method:299: getDynamicUserData() (method)
  method:401: getDynamicUserData() (method)
  method:503: getDynamicUserData() (method)
  method:605: getDynamicUserData() (method)
```

엣지 목록 (5)
```json
  method:95 -> method:197 (inferred_sequence)
  method:197 -> method:299 (inferred_sequence)
  method:299 -> method:401 (inferred_sequence)
  method:401 -> method:503 (inferred_sequence)
  method:503 -> method:605 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:46:56*