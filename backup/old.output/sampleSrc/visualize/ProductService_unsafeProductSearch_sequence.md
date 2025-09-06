# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:46:20
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_192 as unsafeProductSear...
  participant n2_method_294 as unsafeProductSear...
  participant n3_method_396 as unsafeProductSear...
  participant n4_method_498 as unsafeProductSear...
  participant n5_method_600 as unsafeProductSear...
  participant n6_method_90 as unsafeProductSear...

  n6_method_90->>n1_method_192: inferred_sequence (10%)
  n1_method_192->>n2_method_294: inferred_sequence (10%)
  n2_method_294->>n3_method_396: inferred_sequence (10%)
  n3_method_396->>n4_method_498: inferred_sequence (10%)
  n4_method_498->>n5_method_600: inferred_sequence (10%)
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
  method:90: unsafeProductSearch() (method)
  method:192: unsafeProductSearch() (method)
  method:294: unsafeProductSearch() (method)
  method:396: unsafeProductSearch() (method)
  method:498: unsafeProductSearch() (method)
  method:600: unsafeProductSearch() (method)
```

엣지 목록 (5)
```json
  method:90 -> method:192 (inferred_sequence)
  method:192 -> method:294 (inferred_sequence)
  method:294 -> method:396 (inferred_sequence)
  method:396 -> method:498 (inferred_sequence)
  method:498 -> method:600 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:46:20*