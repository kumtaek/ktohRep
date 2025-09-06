# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:42:14
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_168 as selectProductById()
  participant n2_method_270 as selectProductById()
  participant n3_method_372 as selectProductById()
  participant n4_method_474 as selectProductById()
  participant n5_method_576 as selectProductById()
  participant n6_method_66 as selectProductById()

  n6_method_66->>n1_method_168: inferred_sequence (10%)
  n1_method_168->>n2_method_270: inferred_sequence (10%)
  n2_method_270->>n3_method_372: inferred_sequence (10%)
  n3_method_372->>n4_method_474: inferred_sequence (10%)
  n4_method_474->>n5_method_576: inferred_sequence (10%)
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
  method:66: selectProductById() (method)
  method:168: selectProductById() (method)
  method:270: selectProductById() (method)
  method:372: selectProductById() (method)
  method:474: selectProductById() (method)
  method:576: selectProductById() (method)
```

엣지 목록 (5)
```json
  method:66 -> method:168 (inferred_sequence)
  method:168 -> method:270 (inferred_sequence)
  method:270 -> method:372 (inferred_sequence)
  method:372 -> method:474 (inferred_sequence)
  method:474 -> method:576 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:42:14*