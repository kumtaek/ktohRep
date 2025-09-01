# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-01 19:59:50
- 노드 수: 2
- 엣지 수: 1

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_44 as generateOrderRepo...
  participant n2_unresolved as unresolved: com.g...

  n1_method_44->>n2_unresolved: call (80%)
```

## 범례

### 시퀀스 범례
- 실선 화살표: 해석된 메소드 호출
- 점선 화살표: 미해석 호출
- 숫자: 호출 순서

## 원본 데이터

<details>
<summary>원본 데이터를 보려면 클릭</summary>

노드 목록 (2)
```json
  method:44: generateOrderReport() (method)
  unresolved:com.getComplexOrderReport: unresolved: com.getComplexOrderReport (unresolved)
```

엣지 목록 (1)
```json
  method:44 -> unresolved:com.getComplexOrderReport (call)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-01 19:59:50*