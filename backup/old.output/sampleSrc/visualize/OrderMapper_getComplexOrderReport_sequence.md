# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-03 07:40:20
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_164 as getComplexOrderRe...
  participant n2_method_266 as getComplexOrderRe...
  participant n3_method_368 as getComplexOrderRe...
  participant n4_method_470 as getComplexOrderRe...
  participant n5_method_572 as getComplexOrderRe...
  participant n6_method_62 as getComplexOrderRe...

  n6_method_62->>n1_method_164: inferred_sequence (10%)
  n1_method_164->>n2_method_266: inferred_sequence (10%)
  n2_method_266->>n3_method_368: inferred_sequence (10%)
  n3_method_368->>n4_method_470: inferred_sequence (10%)
  n4_method_470->>n5_method_572: inferred_sequence (10%)
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
  method:62: getComplexOrderReport() (method)
  method:164: getComplexOrderReport() (method)
  method:266: getComplexOrderReport() (method)
  method:368: getComplexOrderReport() (method)
  method:470: getComplexOrderReport() (method)
  method:572: getComplexOrderReport() (method)
```

엣지 목록 (5)
```json
  method:62 -> method:164 (inferred_sequence)
  method:164 -> method:266 (inferred_sequence)
  method:266 -> method:368 (inferred_sequence)
  method:368 -> method:470 (inferred_sequence)
  method:470 -> method:572 (inferred_sequence)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-03 07:40:20*