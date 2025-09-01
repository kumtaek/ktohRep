# Source Analyzer GRAPH Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: GRAPH
- 생성 시각: 2025-09-02 01:01:58
- 노드 수: 38
- 엣지 수: 123

## 적용된 필터

- kinds: call
- min_confidence: 0.5
- depth: 2
- max_nodes: 2000

## 다이어그램

```mermaid
graph TD
  n1_method_5[IntegratedService...<br/>(LOC=0, Cx=1)]
  n2_method_6[IntegratedService...<br/>(LOC=0, Cx=7)]
  n3_method_8[IntegratedService...<br/>(LOC=0, Cx=1)]
  n4_method_9[IntegratedService...<br/>(LOC=0, Cx=1)]
  n5_method_10[IntegratedService...<br/>(LOC=0, Cx=1)]
  n6_method_11[VulnerabilityTest...<br/>(LOC=0, Cx=1)]
  n7_method_12[VulnerabilityTest...<br/>(LOC=0, Cx=1)]
  n8_method_13[VulnerabilityTest...<br/>(LOC=0, Cx=9)]
  n9_method_15[VulnerabilityTest...<br/>(LOC=0, Cx=3)]
  n10_method_16[VulnerabilityTest...<br/>(LOC=0, Cx=6)]
  n11_method_17[VulnerabilityTest...<br/>(LOC=0, Cx=2)]
  n12_method_18[VulnerabilityTest...<br/>(LOC=0, Cx=4)]
  n13_method_19[VulnerabilityTest...<br/>(LOC=0, Cx=8)]
  n14_method_21[VulnerabilityTest...<br/>(LOC=0, Cx=1)]
  n15_method_22[VulnerabilityTest...<br/>(LOC=0, Cx=19)]
  n16_method_42[OrderService.calc...<br/>(LOC=0, Cx=6)]
  n17_method_43[OrderService.getO...<br/>(LOC=0, Cx=1)]
  n18_method_44[OrderService.gene...<br/>(LOC=0, Cx=1)]
  n19_method_45[OrderService.larg...<br/>(LOC=0, Cx=1)]
  n20_method_46[OrderService.larg...<br/>(LOC=0, Cx=1)]
  n21_method_47[OrderService.larg...<br/>(LOC=0, Cx=1)]
  n22_method_50[OverloadService.p...<br/>(LOC=0, Cx=4)]
  n23_method_51[ProductService.ge...<br/>(LOC=0, Cx=1)]
  n24_method_52[ProductService.ge...<br/>(LOC=0, Cx=1)]
  n25_method_53[ProductService.se...<br/>(LOC=0, Cx=1)]
  n26_method_54[ProductService.pr...<br/>(LOC=0, Cx=8)]
  n27_method_55[ProductService.un...<br/>(LOC=0, Cx=1)]
  n28_method_56[UserService.getUs...<br/>(LOC=0, Cx=2)]
  n29_method_57[UserService.getAc...<br/>(LOC=0, Cx=1)]
  n30_method_58[UserService.creat...<br/>(LOC=0, Cx=1)]
  n31_method_59[UserService.proce...<br/>(LOC=0, Cx=7)]
  n32_method_60[UserService.getDy...<br/>(LOC=0, Cx=1)]
  n33_method_61[UserService.updat...<br/>(LOC=0, Cx=1)]
  n34_method_62[DateUtil.getCurre...<br/>(LOC=0, Cx=3)]
  n35_method_63[DateUtil.convertD...<br/>(LOC=0, Cx=6)]
  n36_method_64[DateUtil.daysBetw...<br/>(LOC=0, Cx=7)]
  n37_method_65[Texts.isEmpty()<br/>(LOC=0, Cx=1)]
  n38_method_66[ListServiceImpl1....<br/>(LOC=0, Cx=1)]

  n1_method_5 -->|call| n39_unknown_ca
  n2_method_6 -->|call| n39_unknown_ca
  n2_method_6 -->|call| n39_unknown_ca
  n2_method_6 -->|call| n39_unknown_ca
  n2_method_6 -->|call| n39_unknown_ca
  n2_method_6 -->|call| n39_unknown_ca
  n2_method_6 -->|call| n39_unknown_ca
  n2_method_6 -->|call| n39_unknown_ca
  n3_method_8 -->|call| n39_unknown_ca
  n4_method_9 -->|call| n39_unknown_ca
  n5_method_10 -->|call| n39_unknown_ca
  n6_method_11 -->|call| n39_unknown_ca
  n7_method_12 -->|call| n39_unknown_ca
  n8_method_13 -->|call| n39_unknown_ca
  n8_method_13 -->|call| n39_unknown_ca
  n8_method_13 -->|call| n39_unknown_ca
  n8_method_13 -->|call| n39_unknown_ca
  n8_method_13 -->|call| n39_unknown_ca
  n8_method_13 -->|call| n39_unknown_ca
  n8_method_13 -->|call| n39_unknown_ca
  n8_method_13 -->|call| n39_unknown_ca
  n8_method_13 -->|call| n39_unknown_ca
  n9_method_15 -->|call| n39_unknown_ca
  n9_method_15 -->|call| n39_unknown_ca
  n9_method_15 -->|call| n39_unknown_ca
  n10_method_16 -->|call| n39_unknown_ca
  n10_method_16 -->|call| n39_unknown_ca
  n10_method_16 -->|call| n39_unknown_ca
  n10_method_16 -->|call| n39_unknown_ca
  n10_method_16 -->|call| n39_unknown_ca
  n10_method_16 -->|call| n39_unknown_ca
  n11_method_17 -->|call| n39_unknown_ca
  n11_method_17 -->|call| n39_unknown_ca
  n12_method_18 -->|call| n39_unknown_ca
  n12_method_18 -->|call| n39_unknown_ca
  n12_method_18 -->|call| n39_unknown_ca
  n12_method_18 -->|call| n39_unknown_ca
  n13_method_19 -->|call| n39_unknown_ca
  n13_method_19 -->|call| n39_unknown_ca
  n13_method_19 -->|call| n39_unknown_ca
  n13_method_19 -->|call| n39_unknown_ca
  n13_method_19 -->|call| n39_unknown_ca
  n13_method_19 -->|call| n39_unknown_ca
  n13_method_19 -->|call| n39_unknown_ca
  n13_method_19 -->|call| n39_unknown_ca
  n14_method_21 -->|call| n39_unknown_ca
  n15_method_22 -->|call| n39_unknown_ca
  n15_method_22 -->|call| n39_unknown_ca
  n15_method_22 -->|call| n39_unknown_ca
  n15_method_22 -->|call| n39_unknown_ca
  n15_method_22 -->|call| n39_unknown_ca
  n15_method_22 -->|call| n39_unknown_ca
  n15_method_22 -->|call| n39_unknown_ca
  n15_method_22 -->|call| n39_unknown_ca
  n15_method_22 -->|call| n39_unknown_ca
  n15_method_22 -->|call| n39_unknown_ca
  n15_method_22 -->|call| n39_unknown_ca
  n15_method_22 -->|call| n39_unknown_ca
  n15_method_22 -->|call| n39_unknown_ca
  n15_method_22 -->|call| n39_unknown_ca
  n15_method_22 -->|call| n39_unknown_ca
  n15_method_22 -->|call| n39_unknown_ca
  n15_method_22 -->|call| n39_unknown_ca
  n15_method_22 -->|call| n39_unknown_ca
  n15_method_22 -->|call| n39_unknown_ca
  n16_method_42 -->|call| n39_unknown_ca
  n16_method_42 -->|call| n39_unknown_ca
  n16_method_42 -->|call| n39_unknown_ca
  n16_method_42 -->|call| n39_unknown_ca
  n16_method_42 -->|call| n39_unknown_ca
  n16_method_42 -->|call| n39_unknown_ca
  n17_method_43 -->|call| n39_unknown_ca
  n18_method_44 -->|call| n39_unknown_ca
  n19_method_45 -->|call| n39_unknown_ca
  n20_method_46 -->|call| n39_unknown_ca
  n21_method_47 -->|call| n39_unknown_ca
  n22_method_50 -->|call| n39_unknown_ca
  n22_method_50 -->|call| n39_unknown_ca
  n22_method_50 -->|call| n39_unknown_ca
  n22_method_50 -->|call| n39_unknown_ca
  n23_method_51 -->|call| n39_unknown_ca
  n24_method_52 -->|call| n39_unknown_ca
  n25_method_53 -->|call| n39_unknown_ca
  n26_method_54 -->|call| n39_unknown_ca
  n26_method_54 -->|call| n39_unknown_ca
  n26_method_54 -->|call| n39_unknown_ca
  n26_method_54 -->|call| n39_unknown_ca
  n26_method_54 -->|call| n39_unknown_ca
  n26_method_54 -->|call| n39_unknown_ca
  n26_method_54 -->|call| n39_unknown_ca
  n26_method_54 -->|call| n39_unknown_ca
  n27_method_55 -->|call| n39_unknown_ca
  n28_method_56 -->|call| n39_unknown_ca
  n28_method_56 -->|call| n39_unknown_ca
  n29_method_57 -->|call| n39_unknown_ca
  n30_method_58 -->|call| n39_unknown_ca
  n31_method_59 -->|call| n39_unknown_ca
  n31_method_59 -->|call| n39_unknown_ca
  n31_method_59 -->|call| n39_unknown_ca
  n31_method_59 -->|call| n39_unknown_ca
  n31_method_59 -->|call| n39_unknown_ca
  n31_method_59 -->|call| n39_unknown_ca
  n31_method_59 -->|call| n39_unknown_ca
  n32_method_60 -->|call| n39_unknown_ca
  n33_method_61 -->|call| n39_unknown_ca
  n34_method_62 -->|call| n39_unknown_ca
  n34_method_62 -->|call| n39_unknown_ca
  n34_method_62 -->|call| n39_unknown_ca
  n35_method_63 -->|call| n39_unknown_ca
  n35_method_63 -->|call| n39_unknown_ca
  n35_method_63 -->|call| n39_unknown_ca
  n35_method_63 -->|call| n39_unknown_ca
  n35_method_63 -->|call| n39_unknown_ca
  n35_method_63 -->|call| n39_unknown_ca
  n36_method_64 -->|call| n39_unknown_ca
  n36_method_64 -->|call| n39_unknown_ca
  n36_method_64 -->|call| n39_unknown_ca
  n36_method_64 -->|call| n39_unknown_ca
  n36_method_64 -->|call| n39_unknown_ca
  n36_method_64 -->|call| n39_unknown_ca
  n36_method_64 -->|call| n39_unknown_ca
  n37_method_65 -->|call| n39_unknown_ca
  n38_method_66 -->|call| n39_unknown_ca

  %% Dynamic Cluster Styling
  classDef PROJECT_sampleSrc_src_main_java_com_example_integrated fill:#f24848,stroke:#333,stroke-width:2px
  classDef PROJECT_sampleSrc_src_main_java_com_example_service fill:#9df248,stroke:#333,stroke-width:2px
  classDef PROJECT_sampleSrc_src_main_java_com_example_service_impl fill:#48f2f2,stroke:#333,stroke-width:2px
  classDef PROJECT_sampleSrc_src_main_java_com_example_util fill:#9d48f2,stroke:#333,stroke-width:2px

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
  class n1_method_5 PROJECT_sampleSrc_src_main_java_com_example_integrated
  class n1_method_5 hotspot_low
  class n2_method_6 PROJECT_sampleSrc_src_main_java_com_example_integrated
  class n2_method_6 hotspot_low
  class n3_method_8 PROJECT_sampleSrc_src_main_java_com_example_integrated
  class n3_method_8 hotspot_low
  class n4_method_9 PROJECT_sampleSrc_src_main_java_com_example_integrated
  class n4_method_9 hotspot_low
  class n5_method_10 PROJECT_sampleSrc_src_main_java_com_example_integrated
  class n5_method_10 hotspot_low
  class n6_method_11 PROJECT_sampleSrc_src_main_java_com_example_integrated
  class n6_method_11 hotspot_low
  class n7_method_12 PROJECT_sampleSrc_src_main_java_com_example_integrated
  class n7_method_12 hotspot_low
  class n8_method_13 PROJECT_sampleSrc_src_main_java_com_example_integrated
  class n8_method_13 hotspot_low
  class n9_method_15 PROJECT_sampleSrc_src_main_java_com_example_integrated
  class n9_method_15 hotspot_low
  class n10_method_16 PROJECT_sampleSrc_src_main_java_com_example_integrated
  class n10_method_16 hotspot_low
  class n11_method_17 PROJECT_sampleSrc_src_main_java_com_example_integrated
  class n11_method_17 hotspot_low
  class n12_method_18 PROJECT_sampleSrc_src_main_java_com_example_integrated
  class n12_method_18 hotspot_low
  class n13_method_19 PROJECT_sampleSrc_src_main_java_com_example_integrated
  class n13_method_19 hotspot_low
  class n14_method_21 PROJECT_sampleSrc_src_main_java_com_example_integrated
  class n14_method_21 hotspot_low
  class n15_method_22 PROJECT_sampleSrc_src_main_java_com_example_integrated
  class n15_method_22 hotspot_low
  class n16_method_42 PROJECT_sampleSrc_src_main_java_com_example_service
  class n16_method_42 hotspot_low
  class n17_method_43 PROJECT_sampleSrc_src_main_java_com_example_service
  class n17_method_43 hotspot_low
  class n18_method_44 PROJECT_sampleSrc_src_main_java_com_example_service
  class n18_method_44 hotspot_low
  class n19_method_45 PROJECT_sampleSrc_src_main_java_com_example_service
  class n19_method_45 hotspot_low
  class n20_method_46 PROJECT_sampleSrc_src_main_java_com_example_service
  class n20_method_46 hotspot_low
  class n21_method_47 PROJECT_sampleSrc_src_main_java_com_example_service
  class n21_method_47 hotspot_low
  class n22_method_50 PROJECT_sampleSrc_src_main_java_com_example_service
  class n22_method_50 hotspot_low
  class n23_method_51 PROJECT_sampleSrc_src_main_java_com_example_service
  class n23_method_51 hotspot_low
  class n24_method_52 PROJECT_sampleSrc_src_main_java_com_example_service
  class n24_method_52 hotspot_low
  class n25_method_53 PROJECT_sampleSrc_src_main_java_com_example_service
  class n25_method_53 hotspot_low
  class n26_method_54 PROJECT_sampleSrc_src_main_java_com_example_service
  class n26_method_54 hotspot_low
  class n27_method_55 PROJECT_sampleSrc_src_main_java_com_example_service
  class n27_method_55 hotspot_low
  class n28_method_56 PROJECT_sampleSrc_src_main_java_com_example_service
  class n28_method_56 hotspot_low
  class n29_method_57 PROJECT_sampleSrc_src_main_java_com_example_service
  class n29_method_57 hotspot_low
  class n30_method_58 PROJECT_sampleSrc_src_main_java_com_example_service
  class n30_method_58 hotspot_low
  class n31_method_59 PROJECT_sampleSrc_src_main_java_com_example_service
  class n31_method_59 hotspot_low
  class n32_method_60 PROJECT_sampleSrc_src_main_java_com_example_service
  class n32_method_60 hotspot_low
  class n33_method_61 PROJECT_sampleSrc_src_main_java_com_example_service
  class n33_method_61 hotspot_low
  class n34_method_62 PROJECT_sampleSrc_src_main_java_com_example_util
  class n34_method_62 hotspot_low
  class n35_method_63 PROJECT_sampleSrc_src_main_java_com_example_util
  class n35_method_63 hotspot_low
  class n36_method_64 PROJECT_sampleSrc_src_main_java_com_example_util
  class n36_method_64 hotspot_low
  class n37_method_65 PROJECT_sampleSrc_src_main_java_com_example_util
  class n37_method_65 hotspot_low
  class n38_method_66 PROJECT_sampleSrc_src_main_java_com_example_service_impl
  class n38_method_66 hotspot_low
```

## 범례

### Graph 범례

- call: 메소드 호출

### 스타일 레이어
- Hotspot(채움): low/med/high/crit
- 취약점(테두리): low/medium/high/critical
- 그룹 색상: JSP/Controller/Service/Mapper/DB

## 원본 데이터

<details>
<summary>원본 데이터를 보려면 클릭</summary>

노드 목록 (38)
```json
  method:5: IntegratedService.startProcess() (method)
  method:6: IntegratedService.doWork() (method)
  method:8: IntegratedService.calculateOrderTotal() (method)
  method:9: IntegratedService.getFormattedId() (method)
  method:10: IntegratedService.log() (method)
  method:11: VulnerabilityTestService.getUsersByName_VULNERABLE() (method)
  method:12: VulnerabilityTestService.getUsersByName_SAFE() (method)
  method:13: VulnerabilityTestService.searchUsers_VULNERABLE() (method)
  method:15: VulnerabilityTestService.readFile_VULNERABLE() (method)
  method:16: VulnerabilityTestService.hashPassword_WEAK() (method)
  method:17: VulnerabilityTestService.authenticateAdmin_VULNERABLE() (method)
  method:18: VulnerabilityTestService.connectToDatabase_VULNERABLE() (method)
  method:19: VulnerabilityTestService.executeCommand_VULNERABLE() (method)
  method:21: VulnerabilityTestService.deserializeData_VULNERABLE() (method)
  method:22: VulnerabilityTestService.processComplexBusiness() (method)
  method:42: OrderService.calculateOrderTotal() (method)
  method:43: OrderService.getOrdersByStatus() (method)
  method:44: OrderService.generateOrderReport() (method)
  method:45: OrderService.largeOrderMethod1() (method)
  method:46: OrderService.largeOrderMethod2() (method)
```

엣지 목록 (123)
```json
  method:5 -> unknown:call (call)
  method:6 -> unknown:call (call)
  method:6 -> unknown:call (call)
  method:6 -> unknown:call (call)
  method:6 -> unknown:call (call)
  method:6 -> unknown:call (call)
  method:6 -> unknown:call (call)
  method:6 -> unknown:call (call)
  method:8 -> unknown:call (call)
  method:9 -> unknown:call (call)
  method:10 -> unknown:call (call)
  method:11 -> unknown:call (call)
  method:12 -> unknown:call (call)
  method:13 -> unknown:call (call)
  method:13 -> unknown:call (call)
  method:13 -> unknown:call (call)
  method:13 -> unknown:call (call)
  method:13 -> unknown:call (call)
  method:13 -> unknown:call (call)
  method:13 -> unknown:call (call)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-02 01:01:58*