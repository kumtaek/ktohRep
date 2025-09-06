# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:31:24
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_118 as healthCheck()
  participant n2_method_16 as healthCheck()
  participant n3_method_220 as healthCheck()
  participant n4_method_322 as healthCheck()
  participant n5_method_424 as healthCheck()
  participant n6_method_526 as healthCheck()

  n2_method_16->>n1_method_118: inferred_sequence (10%)
  n1_method_118->>n3_method_220: inferred_sequence (10%)
  n3_method_220->>n4_method_322: inferred_sequence (10%)
  n4_method_322->>n5_method_424: inferred_sequence (10%)
  n5_method_424->>n6_method_526: inferred_sequence (10%)
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
  method:16: healthCheck() (method)
  method:118: healthCheck() (method)
  method:220: healthCheck() (method)
  method:322: healthCheck() (method)
  method:424: healthCheck() (method)
  method:526: healthCheck() (method)
```

엣지 목록 (5)
```json
  method:16 -> method:118 (inferred_sequence)
  method:118 -> method:220 (inferred_sequence)
  method:220 -> method:322 (inferred_sequence)
  method:322 -> method:424 (inferred_sequence)
  method:424 -> method:526 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:31:24*