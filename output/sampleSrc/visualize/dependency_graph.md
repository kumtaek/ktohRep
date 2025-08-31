# Source Analyzer GRAPH Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: GRAPH
- 생성 시각: 2025-08-31 14:23:06
- 노드 수: 37
- 엣지 수: 35

## 적용된 필터

- kinds: use_table,include,extends,implements
- min_confidence: 0.5
- depth: 2
- max_nodes: 2000

## 다이어그램

```mermaid
graph TD
  n1_file_1(IntegratedMapper....<br/>(LOC=9, Cx=0))
  n2_file_14(IntegratedMapper....<br/>(LOC=9, Cx=0))
  n3_file_27(IntegratedMapper....<br/>(LOC=9, Cx=0))
  n4_file_40(IntegratedMapper....<br/>(LOC=9, Cx=0))
  n5_file_2(IntegratedService...<br/>(LOC=35, Cx=0))
  n6_file_15(IntegratedService...<br/>(LOC=35, Cx=0))
  n7_file_28(IntegratedService...<br/>(LOC=35, Cx=0))
  n8_file_41(IntegratedService...<br/>(LOC=35, Cx=0))
  n9_file_3(VulnerabilityTest...<br/>(LOC=181, Cx=0))
  n10_file_16(VulnerabilityTest...<br/>(LOC=181, Cx=0))
  n11_file_29(VulnerabilityTest...<br/>(LOC=181, Cx=0))
  n12_file_42(VulnerabilityTest...<br/>(LOC=181, Cx=0))
  n13_file_4(OrderMapper.java<br/>(LOC=17, Cx=0))
  n14_file_17(OrderMapper.java<br/>(LOC=17, Cx=0))
  n15_file_30(OrderMapper.java<br/>(LOC=17, Cx=0))
  n16_file_43(OrderMapper.java<br/>(LOC=17, Cx=0))
  n17_file_5(ProductMapper.java<br/>(LOC=14, Cx=0))
  n18_file_18(ProductMapper.java<br/>(LOC=14, Cx=0))
  n19_file_31(ProductMapper.java<br/>(LOC=14, Cx=0))
  n20_file_44(ProductMapper.java<br/>(LOC=14, Cx=0))
  n21_file_6(UserMapper.java<br/>(LOC=15, Cx=0))
  n22_class_1(com.example.integ...<br/>(LOC=0, Cx=0))
  n23_class_2(com.example.integ...<br/>(LOC=0, Cx=0))
  n24_class_3(com.example.integ...<br/>(LOC=0, Cx=0))
  n25_class_4(com.example.mappe...<br/>(LOC=0, Cx=0))
  n26_class_5(com.example.mappe...<br/>(LOC=0, Cx=0))
  n27_class_6(com.example.mappe...<br/>(LOC=0, Cx=0))
  n28_class_7(com.example.servi...<br/>(LOC=0, Cx=0))
  n29_class_8(com.example.servi...<br/>(LOC=0, Cx=0))
  n30_class_9(com.example.servi...<br/>(LOC=0, Cx=0))
  n31_class_10(com.example.servi...<br/>(LOC=0, Cx=0))
  n32_class_11(com.example.servi...<br/>(LOC=0, Cx=0))
  n33_class_12(com.example.util....<br/>(LOC=0, Cx=0))
  n34_class_13(com.example.servi...<br/>(LOC=0, Cx=0))
  n35_class_14(com.example.integ...<br/>(LOC=0, Cx=0))
  n36_class_15(com.example.integ...<br/>(LOC=0, Cx=0))
  n37_class_16(com.example.integ...<br/>(LOC=0, Cx=0))

  n1_file_1 -->|package_relation| n2_file_14
  n1_file_1 -->|package_relation| n3_file_27
  n1_file_1 -->|package_relation| n4_file_40
  n1_file_1 -->|package_relation| n5_file_2
  n1_file_1 -->|package_relation| n6_file_15
  n1_file_1 -->|package_relation| n7_file_28
  n1_file_1 -->|package_relation| n8_file_41
  n1_file_1 -->|package_relation| n9_file_3
  n1_file_1 -->|package_relation| n10_file_16
  n1_file_1 -->|package_relation| n11_file_29
  n1_file_1 -->|package_relation| n12_file_42
  n1_file_1 -->|package_relation| n13_file_4
  n1_file_1 -->|package_relation| n14_file_17
  n1_file_1 -->|package_relation| n15_file_30
  n1_file_1 -->|package_relation| n16_file_43
  n1_file_1 -->|package_relation| n17_file_5
  n1_file_1 -->|package_relation| n18_file_18
  n1_file_1 -->|package_relation| n19_file_31
  n1_file_1 -->|package_relation| n20_file_44
  n1_file_1 -->|package_relation| n21_file_6
  n22_class_1 -->|package_relation| n23_class_2
  n22_class_1 -->|package_relation| n24_class_3
  n22_class_1 -->|package_relation| n25_class_4
  n22_class_1 -->|package_relation| n26_class_5
  n22_class_1 -->|package_relation| n27_class_6
  n22_class_1 -->|package_relation| n28_class_7
  n22_class_1 -->|package_relation| n29_class_8
  n22_class_1 -->|package_relation| n30_class_9
  n22_class_1 -->|package_relation| n31_class_10
  n22_class_1 -->|package_relation| n32_class_11
  n22_class_1 -->|package_relation| n33_class_12
  n22_class_1 -->|package_relation| n34_class_13
  n22_class_1 -->|package_relation| n35_class_14
  n22_class_1 -->|package_relation| n36_class_15
  n22_class_1 -->|package_relation| n37_class_16

  %% Dynamic Cluster Styling
  classDef E_SourceAnalyzer_git_project_sampleSrc_src_main_java_com_example_integrated fill:#f24848,stroke:#333,stroke-width:2px
  classDef E_SourceAnalyzer_git_project_sampleSrc_src_main_java_com_example_mapper fill:#d0f248,stroke:#333,stroke-width:2px
  classDef E_SourceAnalyzer_git_project_sampleSrc_src_main_java_com_example_service fill:#48f28c,stroke:#333,stroke-width:2px
  classDef E_SourceAnalyzer_git_project_sampleSrc_src_main_java_com_example_service_impl fill:#488cf2,stroke:#333,stroke-width:2px
  classDef E_SourceAnalyzer_git_project_sampleSrc_src_main_java_com_example_util fill:#d048f2,stroke:#333,stroke-width:2px

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
  class n1_file_1 Default
  class n1_file_1 hotspot_low
  class n2_file_14 Default
  class n2_file_14 hotspot_low
  class n3_file_27 Default
  class n3_file_27 hotspot_low
  class n4_file_40 Default
  class n4_file_40 hotspot_low
  class n5_file_2 Default
  class n5_file_2 hotspot_low
  class n6_file_15 Default
  class n6_file_15 hotspot_low
  class n7_file_28 Default
  class n7_file_28 hotspot_low
  class n8_file_41 Default
  class n8_file_41 hotspot_low
  class n9_file_3 Default
  class n9_file_3 hotspot_med
  class n10_file_16 Default
  class n10_file_16 hotspot_med
  class n11_file_29 Default
  class n11_file_29 hotspot_med
  class n12_file_42 Default
  class n12_file_42 hotspot_med
  class n13_file_4 Default
  class n13_file_4 hotspot_low
  class n14_file_17 Default
  class n14_file_17 hotspot_low
  class n15_file_30 Default
  class n15_file_30 hotspot_low
  class n16_file_43 Default
  class n16_file_43 hotspot_low
  class n17_file_5 Default
  class n17_file_5 hotspot_low
  class n18_file_18 Default
  class n18_file_18 hotspot_low
  class n19_file_31 Default
  class n19_file_31 hotspot_low
  class n20_file_44 Default
  class n20_file_44 hotspot_low
  class n21_file_6 Default
  class n21_file_6 hotspot_low
  class n22_class_1 E_SourceAnalyzer_git_project_sampleSrc_src_main_java_com_example_integrated
  class n22_class_1 hotspot_low
  class n23_class_2 E_SourceAnalyzer_git_project_sampleSrc_src_main_java_com_example_integrated
  class n23_class_2 hotspot_low
  class n24_class_3 E_SourceAnalyzer_git_project_sampleSrc_src_main_java_com_example_integrated
  class n24_class_3 hotspot_low
  class n25_class_4 E_SourceAnalyzer_git_project_sampleSrc_src_main_java_com_example_mapper
  class n25_class_4 hotspot_low
  class n26_class_5 E_SourceAnalyzer_git_project_sampleSrc_src_main_java_com_example_mapper
  class n26_class_5 hotspot_low
  class n27_class_6 E_SourceAnalyzer_git_project_sampleSrc_src_main_java_com_example_mapper
  class n27_class_6 hotspot_low
  class n28_class_7 E_SourceAnalyzer_git_project_sampleSrc_src_main_java_com_example_service
  class n28_class_7 hotspot_low
  class n29_class_8 E_SourceAnalyzer_git_project_sampleSrc_src_main_java_com_example_service
  class n29_class_8 hotspot_low
  class n30_class_9 E_SourceAnalyzer_git_project_sampleSrc_src_main_java_com_example_service
  class n30_class_9 hotspot_low
  class n31_class_10 E_SourceAnalyzer_git_project_sampleSrc_src_main_java_com_example_service
  class n31_class_10 hotspot_low
  class n32_class_11 E_SourceAnalyzer_git_project_sampleSrc_src_main_java_com_example_service
  class n32_class_11 hotspot_low
  class n33_class_12 E_SourceAnalyzer_git_project_sampleSrc_src_main_java_com_example_util
  class n33_class_12 hotspot_low
  class n34_class_13 E_SourceAnalyzer_git_project_sampleSrc_src_main_java_com_example_service_impl
  class n34_class_13 hotspot_low
  class n35_class_14 E_SourceAnalyzer_git_project_sampleSrc_src_main_java_com_example_integrated
  class n35_class_14 hotspot_low
  class n36_class_15 E_SourceAnalyzer_git_project_sampleSrc_src_main_java_com_example_integrated
  class n36_class_15 hotspot_low
  class n37_class_16 E_SourceAnalyzer_git_project_sampleSrc_src_main_java_com_example_integrated
  class n37_class_16 hotspot_low
```

## 범례

### Graph 범례

- package_relation: Package Relation

### 스타일 레이어
- Hotspot(채움): low/med/high/crit
- 취약점(테두리): low/medium/high/critical
- 그룹 색상: JSP/Controller/Service/Mapper/DB

## 원본 데이터

<details>
<summary>원본 데이터를 보려면 클릭</summary>

노드 목록 (37)
```json
  file:1: IntegratedMapper.java (file)
  file:14: IntegratedMapper.java (file)
  file:27: IntegratedMapper.java (file)
  file:40: IntegratedMapper.java (file)
  file:2: IntegratedService.java (file)
  file:15: IntegratedService.java (file)
  file:28: IntegratedService.java (file)
  file:41: IntegratedService.java (file)
  file:3: VulnerabilityTestService.java (file)
  file:16: VulnerabilityTestService.java (file)
  file:29: VulnerabilityTestService.java (file)
  file:42: VulnerabilityTestService.java (file)
  file:4: OrderMapper.java (file)
  file:17: OrderMapper.java (file)
  file:30: OrderMapper.java (file)
  file:43: OrderMapper.java (file)
  file:5: ProductMapper.java (file)
  file:18: ProductMapper.java (file)
  file:31: ProductMapper.java (file)
  file:44: ProductMapper.java (file)
```

엣지 목록 (35)
```json
  file:1 -> file:14 (package_relation)
  file:1 -> file:27 (package_relation)
  file:1 -> file:40 (package_relation)
  file:1 -> file:2 (package_relation)
  file:1 -> file:15 (package_relation)
  file:1 -> file:28 (package_relation)
  file:1 -> file:41 (package_relation)
  file:1 -> file:3 (package_relation)
  file:1 -> file:16 (package_relation)
  file:1 -> file:29 (package_relation)
  file:1 -> file:42 (package_relation)
  file:1 -> file:4 (package_relation)
  file:1 -> file:17 (package_relation)
  file:1 -> file:30 (package_relation)
  file:1 -> file:43 (package_relation)
  file:1 -> file:5 (package_relation)
  file:1 -> file:18 (package_relation)
  file:1 -> file:31 (package_relation)
  file:1 -> file:44 (package_relation)
  file:1 -> file:6 (package_relation)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-08-31 14:23:06*