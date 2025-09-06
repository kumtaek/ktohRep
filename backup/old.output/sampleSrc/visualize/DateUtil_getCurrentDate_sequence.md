# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:48:32
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_199 as getCurrentDate()
  participant n2_method_301 as getCurrentDate()
  participant n3_method_403 as getCurrentDate()
  participant n4_method_505 as getCurrentDate()
  participant n5_method_607 as getCurrentDate()
  participant n6_method_97 as getCurrentDate()

  n6_method_97->>n1_method_199: inferred_sequence (10%)
  n1_method_199->>n2_method_301: inferred_sequence (10%)
  n2_method_301->>n3_method_403: inferred_sequence (10%)
  n3_method_403->>n4_method_505: inferred_sequence (10%)
  n4_method_505->>n5_method_607: inferred_sequence (10%)
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
  method:97: getCurrentDate() (method)
  method:199: getCurrentDate() (method)
  method:301: getCurrentDate() (method)
  method:403: getCurrentDate() (method)
  method:505: getCurrentDate() (method)
  method:607: getCurrentDate() (method)
```

엣지 목록 (5)
```json
  method:97 -> method:199 (inferred_sequence)
  method:199 -> method:301 (inferred_sequence)
  method:301 -> method:403 (inferred_sequence)
  method:403 -> method:505 (inferred_sequence)
  method:505 -> method:607 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:48:32*