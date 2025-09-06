# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:28:10
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_104 as getConnectionStri...
  participant n2_method_2 as getConnectionStri...
  participant n3_method_206 as getConnectionStri...
  participant n4_method_308 as getConnectionStri...
  participant n5_method_410 as getConnectionStri...
  participant n6_method_512 as getConnectionStri...

  n2_method_2->>n1_method_104: inferred_sequence (10%)
  n1_method_104->>n3_method_206: inferred_sequence (10%)
  n3_method_206->>n4_method_308: inferred_sequence (10%)
  n4_method_308->>n5_method_410: inferred_sequence (10%)
  n5_method_410->>n6_method_512: inferred_sequence (10%)
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
  method:2: getConnectionString() (method)
  method:104: getConnectionString() (method)
  method:206: getConnectionString() (method)
  method:308: getConnectionString() (method)
  method:410: getConnectionString() (method)
  method:512: getConnectionString() (method)
```

엣지 목록 (5)
```json
  method:2 -> method:104 (inferred_sequence)
  method:104 -> method:206 (inferred_sequence)
  method:206 -> method:308 (inferred_sequence)
  method:308 -> method:410 (inferred_sequence)
  method:410 -> method:512 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:28:10*