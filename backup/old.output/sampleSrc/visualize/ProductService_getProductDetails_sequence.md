# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:45:30
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_189 as getProductDetails()
  participant n2_method_291 as getProductDetails()
  participant n3_method_393 as getProductDetails()
  participant n4_method_495 as getProductDetails()
  participant n5_method_597 as getProductDetails()
  participant n6_method_87 as getProductDetails()

  n6_method_87->>n1_method_189: inferred_sequence (10%)
  n1_method_189->>n2_method_291: inferred_sequence (10%)
  n2_method_291->>n3_method_393: inferred_sequence (10%)
  n3_method_393->>n4_method_495: inferred_sequence (10%)
  n4_method_495->>n5_method_597: inferred_sequence (10%)
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
  method:87: getProductDetails() (method)
  method:189: getProductDetails() (method)
  method:291: getProductDetails() (method)
  method:393: getProductDetails() (method)
  method:495: getProductDetails() (method)
  method:597: getProductDetails() (method)
```

엣지 목록 (5)
```json
  method:87 -> method:189 (inferred_sequence)
  method:189 -> method:291 (inferred_sequence)
  method:291 -> method:393 (inferred_sequence)
  method:393 -> method:495 (inferred_sequence)
  method:495 -> method:597 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:45:30*