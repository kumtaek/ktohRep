# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:33:39
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_131 as restoreInventory()
  participant n2_method_233 as restoreInventory()
  participant n3_method_29 as restoreInventory()
  participant n4_method_335 as restoreInventory()
  participant n5_method_437 as restoreInventory()
  participant n6_method_539 as restoreInventory()

  n3_method_29->>n1_method_131: inferred_sequence (10%)
  n1_method_131->>n2_method_233: inferred_sequence (10%)
  n2_method_233->>n4_method_335: inferred_sequence (10%)
  n4_method_335->>n5_method_437: inferred_sequence (10%)
  n5_method_437->>n6_method_539: inferred_sequence (10%)
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
  method:29: restoreInventory() (method)
  method:131: restoreInventory() (method)
  method:233: restoreInventory() (method)
  method:335: restoreInventory() (method)
  method:437: restoreInventory() (method)
  method:539: restoreInventory() (method)
```

엣지 목록 (5)
```json
  method:29 -> method:131 (inferred_sequence)
  method:131 -> method:233 (inferred_sequence)
  method:233 -> method:335 (inferred_sequence)
  method:335 -> method:437 (inferred_sequence)
  method:437 -> method:539 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:33:39*