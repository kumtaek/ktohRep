# Source Analyzer COMPONENT Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: COMPONENT
- 생성 시각: 2025-09-02 17:28:42
- 노드 수: 7
- 엣지 수: 3

## 다이어그램

```mermaid
graph TB
  n1_component_{{ Config (51) }}
  n2_component_{{ Controller (72) }}
  n3_component_{{ Mapper (255) }}
  n4_component_{{ Service (147) }}
  n5_component_{{ Util (18) }}
  n6_component_{{ View (42) }}
  n7_component_{{ DB (5) }}

  n4_component_ -->|call| n3_component_
  n4_component_ -->|call| n5_component_
  n3_component_ -->|use_table| n7_component_

  %% Dynamic Cluster Styling
  classDef JSP fill:#ffebee,stroke:#d32f2f
  classDef Controller fill:#e3f2fd,stroke:#1976d2
  classDef Service fill:#e8f5e8,stroke:#388e3c
  classDef Mapper fill:#f3e5f5,stroke:#7b1fa2
  classDef DB fill:#fff9c4,stroke:#f9a825

  %% Hotspot styling
  classDef hotspot_low fill:#e8f5e9,stroke:#43a047
  classDef hotspot_med fill:#fffde7,stroke:#f9a825
  classDef hotspot_high fill:#ffe0b2,stroke:#fb8c00,stroke-width:2px
  classDef hotspot_crit fill:#ffebee,stroke:#e53935,stroke-width:3px

  %% Vulnerability styling
  classDef vuln_low stroke:#8bc34a,stroke-width:2px,stroke-dasharray:2 2
  classDef vuln_medium stroke:#fbc02d,stroke-width:2px
  classDef vuln_high stroke:#fb8c00,stroke-width:3px
  classDef vuln_critical stroke:#e53935,stroke-width:4px
  class n1_component_ Config
  class n2_component_ Controller
  class n3_component_ Mapper
  class n4_component_ Service
  class n5_component_ Util
  class n6_component_ View
  class n7_component_ DB
```

## 범례

### Component 범례

- call: 메소드 호출
- use_table: DB 테이블 사용

### 스타일 레이어
- Hotspot(채움): low/med/high/crit
- 취약점(테두리): low/medium/high/critical
- 그룹 색상: JSP/Controller/Service/Mapper/DB

## 원본 데이터

<details>
<summary>원본 데이터를 보려면 클릭</summary>

노드 목록 (7)
```json
  component:Config: Config (51) (component)
  component:Controller: Controller (72) (component)
  component:Mapper: Mapper (255) (component)
  component:Service: Service (147) (component)
  component:Util: Util (18) (component)
  component:View: View (42) (component)
  component:DB: DB (5) (component)
```

엣지 목록 (3)
```json
  component:Service -> component:Mapper (call)
  component:Service -> component:Util (call)
  component:Mapper -> component:DB (use_table)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-02 17:28:42*