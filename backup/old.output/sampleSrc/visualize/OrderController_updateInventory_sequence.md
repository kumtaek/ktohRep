# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:33:51
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_130 as updateInventory()
  participant n2_method_232 as updateInventory()
  participant n3_method_28 as updateInventory()
  participant n4_method_334 as updateInventory()
  participant n5_method_436 as updateInventory()
  participant n6_method_538 as updateInventory()

  n3_method_28->>n1_method_130: inferred_sequence (10%)
  n1_method_130->>n2_method_232: inferred_sequence (10%)
  n2_method_232->>n4_method_334: inferred_sequence (10%)
  n4_method_334->>n5_method_436: inferred_sequence (10%)
  n5_method_436->>n6_method_538: inferred_sequence (10%)
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
  method:28: updateInventory() (method)
  method:130: updateInventory() (method)
  method:232: updateInventory() (method)
  method:334: updateInventory() (method)
  method:436: updateInventory() (method)
  method:538: updateInventory() (method)
```

엣지 목록 (5)
```json
  method:28 -> method:130 (inferred_sequence)
  method:130 -> method:232 (inferred_sequence)
  method:232 -> method:334 (inferred_sequence)
  method:334 -> method:436 (inferred_sequence)
  method:436 -> method:538 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:33:51*