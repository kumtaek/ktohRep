# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:29:13
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_109 as customAuthenticat...
  participant n2_method_211 as customAuthenticat...
  participant n3_method_313 as customAuthenticat...
  participant n4_method_415 as customAuthenticat...
  participant n5_method_517 as customAuthenticat...
  participant n6_method_7 as customAuthenticat...

  n6_method_7->>n1_method_109: inferred_sequence (10%)
  n1_method_109->>n2_method_211: inferred_sequence (10%)
  n2_method_211->>n3_method_313: inferred_sequence (10%)
  n3_method_313->>n4_method_415: inferred_sequence (10%)
  n4_method_415->>n5_method_517: inferred_sequence (10%)
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
  method:7: customAuthenticationEntryPoint() (method)
  method:109: customAuthenticationEntryPoint() (method)
  method:211: customAuthenticationEntryPoint() (method)
  method:313: customAuthenticationEntryPoint() (method)
  method:415: customAuthenticationEntryPoint() (method)
  method:517: customAuthenticationEntryPoint() (method)
```

엣지 목록 (5)
```json
  method:7 -> method:109 (inferred_sequence)
  method:109 -> method:211 (inferred_sequence)
  method:211 -> method:313 (inferred_sequence)
  method:313 -> method:415 (inferred_sequence)
  method:415 -> method:517 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:29:13*