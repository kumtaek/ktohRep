# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:44:29
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_182 as largeOrderMethod1()
  participant n2_method_284 as largeOrderMethod1()
  participant n3_method_386 as largeOrderMethod1()
  participant n4_method_488 as largeOrderMethod1()
  participant n5_method_590 as largeOrderMethod1()
  participant n6_method_80 as largeOrderMethod1()

  n6_method_80->>n1_method_182: inferred_sequence (10%)
  n1_method_182->>n2_method_284: inferred_sequence (10%)
  n2_method_284->>n3_method_386: inferred_sequence (10%)
  n3_method_386->>n4_method_488: inferred_sequence (10%)
  n4_method_488->>n5_method_590: inferred_sequence (10%)
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
  method:80: largeOrderMethod1() (method)
  method:182: largeOrderMethod1() (method)
  method:284: largeOrderMethod1() (method)
  method:386: largeOrderMethod1() (method)
  method:488: largeOrderMethod1() (method)
  method:590: largeOrderMethod1() (method)
```

엣지 목록 (5)
```json
  method:80 -> method:182 (inferred_sequence)
  method:182 -> method:284 (inferred_sequence)
  method:284 -> method:386 (inferred_sequence)
  method:386 -> method:488 (inferred_sequence)
  method:488 -> method:590 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:44:29*