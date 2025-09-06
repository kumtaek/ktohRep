# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:30:44
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_107 as passwordEncoder()
  participant n2_method_209 as passwordEncoder()
  participant n3_method_311 as passwordEncoder()
  participant n4_method_413 as passwordEncoder()
  participant n5_method_5 as passwordEncoder()
  participant n6_method_515 as passwordEncoder()

  n5_method_5->>n1_method_107: inferred_sequence (10%)
  n1_method_107->>n2_method_209: inferred_sequence (10%)
  n2_method_209->>n3_method_311: inferred_sequence (10%)
  n3_method_311->>n4_method_413: inferred_sequence (10%)
  n4_method_413->>n6_method_515: inferred_sequence (10%)
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
  method:5: passwordEncoder() (method)
  method:107: passwordEncoder() (method)
  method:209: passwordEncoder() (method)
  method:311: passwordEncoder() (method)
  method:413: passwordEncoder() (method)
  method:515: passwordEncoder() (method)
```

엣지 목록 (5)
```json
  method:5 -> method:107 (inferred_sequence)
  method:107 -> method:209 (inferred_sequence)
  method:209 -> method:311 (inferred_sequence)
  method:311 -> method:413 (inferred_sequence)
  method:413 -> method:515 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:30:44*