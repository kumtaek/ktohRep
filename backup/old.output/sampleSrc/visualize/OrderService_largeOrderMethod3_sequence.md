# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:44:54
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_184 as largeOrderMethod3()
  participant n2_method_286 as largeOrderMethod3()
  participant n3_method_388 as largeOrderMethod3()
  participant n4_method_490 as largeOrderMethod3()
  participant n5_method_592 as largeOrderMethod3()
  participant n6_method_82 as largeOrderMethod3()

  n6_method_82->>n1_method_184: inferred_sequence (10%)
  n1_method_184->>n2_method_286: inferred_sequence (10%)
  n2_method_286->>n3_method_388: inferred_sequence (10%)
  n3_method_388->>n4_method_490: inferred_sequence (10%)
  n4_method_490->>n5_method_592: inferred_sequence (10%)
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
  method:82: largeOrderMethod3() (method)
  method:184: largeOrderMethod3() (method)
  method:286: largeOrderMethod3() (method)
  method:388: largeOrderMethod3() (method)
  method:490: largeOrderMethod3() (method)
  method:592: largeOrderMethod3() (method)
```

엣지 목록 (5)
```json
  method:82 -> method:184 (inferred_sequence)
  method:184 -> method:286 (inferred_sequence)
  method:286 -> method:388 (inferred_sequence)
  method:388 -> method:490 (inferred_sequence)
  method:490 -> method:592 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:44:54*