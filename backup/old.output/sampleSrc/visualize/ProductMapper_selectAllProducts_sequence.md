# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:42:02
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_167 as selectAllProducts()
  participant n2_method_269 as selectAllProducts()
  participant n3_method_371 as selectAllProducts()
  participant n4_method_473 as selectAllProducts()
  participant n5_method_575 as selectAllProducts()
  participant n6_method_65 as selectAllProducts()

  n6_method_65->>n1_method_167: inferred_sequence (10%)
  n1_method_167->>n2_method_269: inferred_sequence (10%)
  n2_method_269->>n3_method_371: inferred_sequence (10%)
  n3_method_371->>n4_method_473: inferred_sequence (10%)
  n4_method_473->>n5_method_575: inferred_sequence (10%)
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
  method:65: selectAllProducts() (method)
  method:167: selectAllProducts() (method)
  method:269: selectAllProducts() (method)
  method:371: selectAllProducts() (method)
  method:473: selectAllProducts() (method)
  method:575: selectAllProducts() (method)
```

엣지 목록 (5)
```json
  method:65 -> method:167 (inferred_sequence)
  method:167 -> method:269 (inferred_sequence)
  method:269 -> method:371 (inferred_sequence)
  method:371 -> method:473 (inferred_sequence)
  method:473 -> method:575 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:42:02*