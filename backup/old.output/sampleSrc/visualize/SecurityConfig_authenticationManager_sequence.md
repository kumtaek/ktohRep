# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:28:35
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_111 as authenticationMan...
  participant n2_method_213 as authenticationMan...
  participant n3_method_315 as authenticationMan...
  participant n4_method_417 as authenticationMan...
  participant n5_method_519 as authenticationMan...
  participant n6_method_9 as authenticationMan...

  n6_method_9->>n1_method_111: inferred_sequence (10%)
  n1_method_111->>n2_method_213: inferred_sequence (10%)
  n2_method_213->>n3_method_315: inferred_sequence (10%)
  n3_method_315->>n4_method_417: inferred_sequence (10%)
  n4_method_417->>n5_method_519: inferred_sequence (10%)
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
  method:9: authenticationManager() (method)
  method:111: authenticationManager() (method)
  method:213: authenticationManager() (method)
  method:315: authenticationManager() (method)
  method:417: authenticationManager() (method)
  method:519: authenticationManager() (method)
```

엣지 목록 (5)
```json
  method:9 -> method:111 (inferred_sequence)
  method:111 -> method:213 (inferred_sequence)
  method:213 -> method:315 (inferred_sequence)
  method:315 -> method:417 (inferred_sequence)
  method:417 -> method:519 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:28:35*