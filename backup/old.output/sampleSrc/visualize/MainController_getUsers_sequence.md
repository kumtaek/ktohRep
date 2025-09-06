# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:32:14
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_122 as getUsers()
  participant n2_method_20 as getUsers()
  participant n3_method_224 as getUsers()
  participant n4_method_326 as getUsers()
  participant n5_method_428 as getUsers()
  participant n6_method_530 as getUsers()

  n2_method_20->>n1_method_122: inferred_sequence (10%)
  n1_method_122->>n3_method_224: inferred_sequence (10%)
  n3_method_224->>n4_method_326: inferred_sequence (10%)
  n4_method_326->>n5_method_428: inferred_sequence (10%)
  n5_method_428->>n6_method_530: inferred_sequence (10%)
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
  method:20: getUsers() (method)
  method:122: getUsers() (method)
  method:224: getUsers() (method)
  method:326: getUsers() (method)
  method:428: getUsers() (method)
  method:530: getUsers() (method)
```

엣지 목록 (5)
```json
  method:20 -> method:122 (inferred_sequence)
  method:122 -> method:224 (inferred_sequence)
  method:224 -> method:326 (inferred_sequence)
  method:326 -> method:428 (inferred_sequence)
  method:428 -> method:530 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:32:14*