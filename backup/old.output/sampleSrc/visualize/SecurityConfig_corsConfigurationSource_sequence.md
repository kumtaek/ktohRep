# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:28:48
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_11 as corsConfiguration...
  participant n2_method_113 as corsConfiguration...
  participant n3_method_215 as corsConfiguration...
  participant n4_method_317 as corsConfiguration...
  participant n5_method_419 as corsConfiguration...
  participant n6_method_521 as corsConfiguration...

  n1_method_11->>n2_method_113: inferred_sequence (10%)
  n2_method_113->>n3_method_215: inferred_sequence (10%)
  n3_method_215->>n4_method_317: inferred_sequence (10%)
  n4_method_317->>n5_method_419: inferred_sequence (10%)
  n5_method_419->>n6_method_521: inferred_sequence (10%)
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
  method:11: corsConfigurationSource() (method)
  method:113: corsConfigurationSource() (method)
  method:215: corsConfigurationSource() (method)
  method:317: corsConfigurationSource() (method)
  method:419: corsConfigurationSource() (method)
  method:521: corsConfigurationSource() (method)
```

엣지 목록 (5)
```json
  method:11 -> method:113 (inferred_sequence)
  method:113 -> method:215 (inferred_sequence)
  method:215 -> method:317 (inferred_sequence)
  method:317 -> method:419 (inferred_sequence)
  method:419 -> method:521 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:28:48*