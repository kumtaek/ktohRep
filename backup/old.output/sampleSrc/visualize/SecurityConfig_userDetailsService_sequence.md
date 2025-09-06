# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:30:56
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_10 as userDetailsService()
  participant n2_method_112 as userDetailsService()
  participant n3_method_214 as userDetailsService()
  participant n4_method_316 as userDetailsService()
  participant n5_method_418 as userDetailsService()
  participant n6_method_520 as userDetailsService()

  n1_method_10->>n2_method_112: inferred_sequence (10%)
  n2_method_112->>n3_method_214: inferred_sequence (10%)
  n3_method_214->>n4_method_316: inferred_sequence (10%)
  n4_method_316->>n5_method_418: inferred_sequence (10%)
  n5_method_418->>n6_method_520: inferred_sequence (10%)
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
  method:10: userDetailsService() (method)
  method:112: userDetailsService() (method)
  method:214: userDetailsService() (method)
  method:316: userDetailsService() (method)
  method:418: userDetailsService() (method)
  method:520: userDetailsService() (method)
```

엣지 목록 (5)
```json
  method:10 -> method:112 (inferred_sequence)
  method:112 -> method:214 (inferred_sequence)
  method:214 -> method:316 (inferred_sequence)
  method:316 -> method:418 (inferred_sequence)
  method:418 -> method:520 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:30:56*