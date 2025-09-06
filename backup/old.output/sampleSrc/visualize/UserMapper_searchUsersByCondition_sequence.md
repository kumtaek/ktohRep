# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:43:02
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_174 as searchUsersByCond...
  participant n2_method_276 as searchUsersByCond...
  participant n3_method_378 as searchUsersByCond...
  participant n4_method_480 as searchUsersByCond...
  participant n5_method_582 as searchUsersByCond...
  participant n6_method_72 as searchUsersByCond...

  n6_method_72->>n1_method_174: inferred_sequence (10%)
  n1_method_174->>n2_method_276: inferred_sequence (10%)
  n2_method_276->>n3_method_378: inferred_sequence (10%)
  n3_method_378->>n4_method_480: inferred_sequence (10%)
  n4_method_480->>n5_method_582: inferred_sequence (10%)
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
  method:72: searchUsersByCondition() (method)
  method:174: searchUsersByCondition() (method)
  method:276: searchUsersByCondition() (method)
  method:378: searchUsersByCondition() (method)
  method:480: searchUsersByCondition() (method)
  method:582: searchUsersByCondition() (method)
```

엣지 목록 (5)
```json
  method:72 -> method:174 (inferred_sequence)
  method:174 -> method:276 (inferred_sequence)
  method:276 -> method:378 (inferred_sequence)
  method:378 -> method:480 (inferred_sequence)
  method:480 -> method:582 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:43:02*