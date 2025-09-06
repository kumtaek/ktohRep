# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:43:39
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_178 as list()
  participant n2_method_280 as list()
  participant n3_method_382 as list()
  participant n4_method_484 as list()
  participant n5_method_586 as list()
  participant n6_method_76 as list()

  n6_method_76->>n1_method_178: inferred_sequence (10%)
  n1_method_178->>n2_method_280: inferred_sequence (10%)
  n2_method_280->>n3_method_382: inferred_sequence (10%)
  n3_method_382->>n4_method_484: inferred_sequence (10%)
  n4_method_484->>n5_method_586: inferred_sequence (10%)
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
  method:76: list() (method)
  method:178: list() (method)
  method:280: list() (method)
  method:382: list() (method)
  method:484: list() (method)
  method:586: list() (method)
```

엣지 목록 (5)
```json
  method:76 -> method:178 (inferred_sequence)
  method:178 -> method:280 (inferred_sequence)
  method:280 -> method:382 (inferred_sequence)
  method:382 -> method:484 (inferred_sequence)
  method:484 -> method:586 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:43:39*