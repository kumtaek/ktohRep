# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:29:00
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_110 as customAccessDenie...
  participant n2_method_212 as customAccessDenie...
  participant n3_method_314 as customAccessDenie...
  participant n4_method_416 as customAccessDenie...
  participant n5_method_518 as customAccessDenie...
  participant n6_method_8 as customAccessDenie...

  n6_method_8->>n1_method_110: inferred_sequence (10%)
  n1_method_110->>n2_method_212: inferred_sequence (10%)
  n2_method_212->>n3_method_314: inferred_sequence (10%)
  n3_method_314->>n4_method_416: inferred_sequence (10%)
  n4_method_416->>n5_method_518: inferred_sequence (10%)
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
  method:8: customAccessDeniedHandler() (method)
  method:110: customAccessDeniedHandler() (method)
  method:212: customAccessDeniedHandler() (method)
  method:314: customAccessDeniedHandler() (method)
  method:416: customAccessDeniedHandler() (method)
  method:518: customAccessDeniedHandler() (method)
```

엣지 목록 (5)
```json
  method:8 -> method:110 (inferred_sequence)
  method:110 -> method:212 (inferred_sequence)
  method:212 -> method:314 (inferred_sequence)
  method:314 -> method:416 (inferred_sequence)
  method:416 -> method:518 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:29:00*