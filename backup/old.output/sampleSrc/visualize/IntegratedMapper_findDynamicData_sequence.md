# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:35:17
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_138 as findDynamicData()
  participant n2_method_240 as findDynamicData()
  participant n3_method_342 as findDynamicData()
  participant n4_method_36 as findDynamicData()
  participant n5_method_444 as findDynamicData()
  participant n6_method_546 as findDynamicData()

  n4_method_36->>n1_method_138: inferred_sequence (10%)
  n1_method_138->>n2_method_240: inferred_sequence (10%)
  n2_method_240->>n3_method_342: inferred_sequence (10%)
  n3_method_342->>n5_method_444: inferred_sequence (10%)
  n5_method_444->>n6_method_546: inferred_sequence (10%)
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
  method:36: findDynamicData() (method)
  method:138: findDynamicData() (method)
  method:240: findDynamicData() (method)
  method:342: findDynamicData() (method)
  method:444: findDynamicData() (method)
  method:546: findDynamicData() (method)
```

엣지 목록 (5)
```json
  method:36 -> method:138 (inferred_sequence)
  method:138 -> method:240 (inferred_sequence)
  method:240 -> method:342 (inferred_sequence)
  method:342 -> method:444 (inferred_sequence)
  method:444 -> method:546 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:35:17*