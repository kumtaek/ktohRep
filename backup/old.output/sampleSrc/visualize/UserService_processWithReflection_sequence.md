# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:47:20
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_196 as processWithReflec...
  participant n2_method_298 as processWithReflec...
  participant n3_method_400 as processWithReflec...
  participant n4_method_502 as processWithReflec...
  participant n5_method_604 as processWithReflec...
  participant n6_method_94 as processWithReflec...

  n6_method_94->>n1_method_196: inferred_sequence (10%)
  n1_method_196->>n2_method_298: inferred_sequence (10%)
  n2_method_298->>n3_method_400: inferred_sequence (10%)
  n3_method_400->>n4_method_502: inferred_sequence (10%)
  n4_method_502->>n5_method_604: inferred_sequence (10%)
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
  method:94: processWithReflection() (method)
  method:196: processWithReflection() (method)
  method:298: processWithReflection() (method)
  method:400: processWithReflection() (method)
  method:502: processWithReflection() (method)
  method:604: processWithReflection() (method)
```

엣지 목록 (5)
```json
  method:94 -> method:196 (inferred_sequence)
  method:196 -> method:298 (inferred_sequence)
  method:298 -> method:400 (inferred_sequence)
  method:400 -> method:502 (inferred_sequence)
  method:502 -> method:604 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:47:20*