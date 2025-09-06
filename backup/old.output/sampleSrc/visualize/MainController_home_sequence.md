# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:32:26
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_121 as home()
  participant n2_method_19 as home()
  participant n3_method_223 as home()
  participant n4_method_325 as home()
  participant n5_method_427 as home()
  participant n6_method_529 as home()

  n2_method_19->>n1_method_121: inferred_sequence (10%)
  n1_method_121->>n3_method_223: inferred_sequence (10%)
  n3_method_223->>n4_method_325: inferred_sequence (10%)
  n4_method_325->>n5_method_427: inferred_sequence (10%)
  n5_method_427->>n6_method_529: inferred_sequence (10%)
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
  method:19: home() (method)
  method:121: home() (method)
  method:223: home() (method)
  method:325: home() (method)
  method:427: home() (method)
  method:529: home() (method)
```

엣지 목록 (5)
```json
  method:19 -> method:121 (inferred_sequence)
  method:121 -> method:223 (inferred_sequence)
  method:223 -> method:325 (inferred_sequence)
  method:325 -> method:427 (inferred_sequence)
  method:427 -> method:529 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:32:26*