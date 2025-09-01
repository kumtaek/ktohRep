# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-01 19:59:55
- 노드 수: 2
- 엣지 수: 1

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_58 as createUser()
  participant n2_unresolved as unresolved: com.i...

  n1_method_58->>n2_unresolved: call (80%)
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
  method:58: createUser() (method)
  unresolved:com.insertUser: unresolved: com.insertUser (unresolved)
```

엣지 목록 (1)
```json
  method:58 -> unresolved:com.insertUser (call)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-01 19:59:55*