# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:41:49
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_169 as searchProductsWit...
  participant n2_method_271 as searchProductsWit...
  participant n3_method_373 as searchProductsWit...
  participant n4_method_475 as searchProductsWit...
  participant n5_method_577 as searchProductsWit...
  participant n6_method_67 as searchProductsWit...

  n6_method_67->>n1_method_169: inferred_sequence (10%)
  n1_method_169->>n2_method_271: inferred_sequence (10%)
  n2_method_271->>n3_method_373: inferred_sequence (10%)
  n3_method_373->>n4_method_475: inferred_sequence (10%)
  n4_method_475->>n5_method_577: inferred_sequence (10%)
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
  method:67: searchProductsWithCriteria() (method)
  method:169: searchProductsWithCriteria() (method)
  method:271: searchProductsWithCriteria() (method)
  method:373: searchProductsWithCriteria() (method)
  method:475: searchProductsWithCriteria() (method)
  method:577: searchProductsWithCriteria() (method)
```

엣지 목록 (5)
```json
  method:67 -> method:169 (inferred_sequence)
  method:169 -> method:271 (inferred_sequence)
  method:271 -> method:373 (inferred_sequence)
  method:373 -> method:475 (inferred_sequence)
  method:475 -> method:577 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:41:49*