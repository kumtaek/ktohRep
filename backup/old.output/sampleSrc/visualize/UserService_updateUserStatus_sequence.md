# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:47:32
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_198 as updateUserStatus()
  participant n2_method_300 as updateUserStatus()
  participant n3_method_402 as updateUserStatus()
  participant n4_method_504 as updateUserStatus()
  participant n5_method_606 as updateUserStatus()
  participant n6_method_96 as updateUserStatus()

  n6_method_96->>n1_method_198: inferred_sequence (10%)
  n1_method_198->>n2_method_300: inferred_sequence (10%)
  n2_method_300->>n3_method_402: inferred_sequence (10%)
  n3_method_402->>n4_method_504: inferred_sequence (10%)
  n4_method_504->>n5_method_606: inferred_sequence (10%)
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
  method:96: updateUserStatus() (method)
  method:198: updateUserStatus() (method)
  method:300: updateUserStatus() (method)
  method:402: updateUserStatus() (method)
  method:504: updateUserStatus() (method)
  method:606: updateUserStatus() (method)
```

엣지 목록 (5)
```json
  method:96 -> method:198 (inferred_sequence)
  method:198 -> method:300 (inferred_sequence)
  method:300 -> method:402 (inferred_sequence)
  method:402 -> method:504 (inferred_sequence)
  method:504 -> method:606 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:47:32*