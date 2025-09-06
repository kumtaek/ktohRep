# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:30:31
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_108 as jwtAuthentication...
  participant n2_method_210 as jwtAuthentication...
  participant n3_method_312 as jwtAuthentication...
  participant n4_method_414 as jwtAuthentication...
  participant n5_method_516 as jwtAuthentication...
  participant n6_method_6 as jwtAuthentication...

  n6_method_6->>n1_method_108: inferred_sequence (10%)
  n1_method_108->>n2_method_210: inferred_sequence (10%)
  n2_method_210->>n3_method_312: inferred_sequence (10%)
  n3_method_312->>n4_method_414: inferred_sequence (10%)
  n4_method_414->>n5_method_516: inferred_sequence (10%)
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
  method:6: jwtAuthenticationFilter() (method)
  method:108: jwtAuthenticationFilter() (method)
  method:210: jwtAuthenticationFilter() (method)
  method:312: jwtAuthenticationFilter() (method)
  method:414: jwtAuthenticationFilter() (method)
  method:516: jwtAuthenticationFilter() (method)
```

엣지 목록 (5)
```json
  method:6 -> method:108 (inferred_sequence)
  method:108 -> method:210 (inferred_sequence)
  method:210 -> method:312 (inferred_sequence)
  method:312 -> method:414 (inferred_sequence)
  method:414 -> method:516 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:30:31*