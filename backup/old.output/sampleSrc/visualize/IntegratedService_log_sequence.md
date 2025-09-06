# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:36:55
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_147 as log()
  participant n2_method_249 as log()
  participant n3_method_351 as log()
  participant n4_method_45 as log()
  participant n5_method_453 as log()
  participant n6_method_555 as log()

  n4_method_45->>n1_method_147: inferred_sequence (10%)
  n1_method_147->>n2_method_249: inferred_sequence (10%)
  n2_method_249->>n3_method_351: inferred_sequence (10%)
  n3_method_351->>n5_method_453: inferred_sequence (10%)
  n5_method_453->>n6_method_555: inferred_sequence (10%)
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
  method:45: log() (method)
  method:147: log() (method)
  method:249: log() (method)
  method:351: log() (method)
  method:453: log() (method)
  method:555: log() (method)
```

엣지 목록 (5)
```json
  method:45 -> method:147 (inferred_sequence)
  method:147 -> method:249 (inferred_sequence)
  method:249 -> method:351 (inferred_sequence)
  method:351 -> method:453 (inferred_sequence)
  method:453 -> method:555 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:36:55*