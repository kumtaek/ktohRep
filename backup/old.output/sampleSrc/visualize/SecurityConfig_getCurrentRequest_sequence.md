# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:29:53
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_117 as getCurrentRequest()
  participant n2_method_15 as getCurrentRequest()
  participant n3_method_219 as getCurrentRequest()
  participant n4_method_321 as getCurrentRequest()
  participant n5_method_423 as getCurrentRequest()
  participant n6_method_525 as getCurrentRequest()

  n2_method_15->>n1_method_117: inferred_sequence (10%)
  n1_method_117->>n3_method_219: inferred_sequence (10%)
  n3_method_219->>n4_method_321: inferred_sequence (10%)
  n4_method_321->>n5_method_423: inferred_sequence (10%)
  n5_method_423->>n6_method_525: inferred_sequence (10%)
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
  method:15: getCurrentRequest() (method)
  method:117: getCurrentRequest() (method)
  method:219: getCurrentRequest() (method)
  method:321: getCurrentRequest() (method)
  method:423: getCurrentRequest() (method)
  method:525: getCurrentRequest() (method)
```

엣지 목록 (5)
```json
  method:15 -> method:117 (inferred_sequence)
  method:117 -> method:219 (inferred_sequence)
  method:219 -> method:321 (inferred_sequence)
  method:321 -> method:423 (inferred_sequence)
  method:423 -> method:525 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:29:53*