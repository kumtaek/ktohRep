# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:27:59
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_1 as dateUtil()
  participant n2_method_103 as dateUtil()
  participant n3_method_205 as dateUtil()
  participant n4_method_307 as dateUtil()
  participant n5_method_409 as dateUtil()
  participant n6_method_511 as dateUtil()

  n1_method_1->>n2_method_103: inferred_sequence (10%)
  n2_method_103->>n3_method_205: inferred_sequence (10%)
  n3_method_205->>n4_method_307: inferred_sequence (10%)
  n4_method_307->>n5_method_409: inferred_sequence (10%)
  n5_method_409->>n6_method_511: inferred_sequence (10%)
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
  method:1: dateUtil() (method)
  method:103: dateUtil() (method)
  method:205: dateUtil() (method)
  method:307: dateUtil() (method)
  method:409: dateUtil() (method)
  method:511: dateUtil() (method)
```

엣지 목록 (5)
```json
  method:1 -> method:103 (inferred_sequence)
  method:103 -> method:205 (inferred_sequence)
  method:205 -> method:307 (inferred_sequence)
  method:307 -> method:409 (inferred_sequence)
  method:409 -> method:511 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:27:59*