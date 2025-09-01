# Source Analyzer SEQUENCE Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: SEQUENCE
- 생성 시각: 2025-09-01 19:59:56
- 노드 수: 6
- 엣지 수: 5

## 다이어그램

```mermaid
sequenceDiagram
  participant n1_method_59 as processWithReflec...
  participant n2_unresolved as unresolved: Class...
  participant n3_unresolved as unresolved: Class...
  participant n4_unresolved as unresolved: Objec...
  participant n5_unresolved as unresolved: com.e...
  participant n6_unresolved as unresolved: e.get...

  n1_method_59->>n2_unresolved: call (80%)
  n1_method_59->>n3_unresolved: call (80%)
  n1_method_59->>n5_unresolved: call (80%)
  n1_method_59->>n4_unresolved: call (80%)
  n1_method_59->>n6_unresolved: call (80%)
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
  method:59: processWithReflection() (method)
  unresolved:Class.forName: unresolved: Class.forName (unresolved)
  unresolved:Class.getDeclaredConstructor: unresolved: Class.getDeclaredConstructor (unresolved)
  unresolved:com.example.service.UserService.newInstance: unresolved: com.example.service.UserService.newInstance (unresolved)
  unresolved:Object.toString: unresolved: Object.toString (unresolved)
  unresolved:e.getMessage: unresolved: e.getMessage (unresolved)
```

엣지 목록 (5)
```json
  method:59 -> unresolved:Class.forName (call)
  method:59 -> unresolved:Class.getDeclaredConstructor (call)
  method:59 -> unresolved:com.example.service.UserService.newInstance (call)
  method:59 -> unresolved:Object.toString (call)
  method:59 -> unresolved:e.getMessage (call)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-01 19:59:56*