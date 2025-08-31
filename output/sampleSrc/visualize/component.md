# Source Analyzer COMPONENT Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: COMPONENT
- 생성 시각: 2025-08-31 13:06:05
- 노드 수: 3
- 엣지 수: 1

## 다이어그램

```mermaid
graph TB
  n1_component_{{ Mapper (182) }}
  n2_component_{{ Service (336) }}
  n3_component_{{ Util (14) }}

  n1_component_ -->|package_relation| n2_component_

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
  class n1_component_ Mapper
  class n2_component_ Service
  class n3_component_ Util
```

## 범례

### Component 범례

- package_relation: Package Relation

### 스타일 레이어
- Hotspot(채움): low/med/high/crit
- 취약점(테두리): low/medium/high/critical
- 그룹 색상: JSP/Controller/Service/Mapper/DB

## 원본 데이터

<details>
<summary>원본 데이터를 보려면 클릭</summary>

노드 목록 (3)
```json
  component:Mapper: Mapper (182) (component)
  component:Service: Service (336) (component)
  component:Util: Util (14) (component)
```

엣지 목록 (1)
```json
  component:Mapper -> component:Service (package_relation)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-08-31 13:06:05*