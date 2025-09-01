# Source Analyzer RELATEDNESS Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: RELATEDNESS
- 생성 시각: 2025-09-01 09:47:14
- 노드 수: 28
- 엣지 수: 31

## 다이어그램

```mermaid
graph TD
  n1_class_1(IntegratedMapper)
  n2_file_1(IntegratedMapper)
  n3_class_2(IntegratedService)
  n4_file_2(IntegratedService)
  n5_class_3(VulnerabilityTest...)
  n6_file_3(VulnerabilityTest...)
  n7_class_4(OrderMapper)
  n8_file_4(OrderMapper)
  n9_class_5(ProductMapper)
  n10_file_5(ProductMapper)
  n11_class_6(UserMapper)
  n12_file_6(UserMapper)
  n13_class_7(ListService)
  n14_file_7(ListService)
  n15_class_8(OrderService)
  n16_file_8(OrderService)
  n17_class_9(OverloadService)
  n18_file_9(OverloadService)
  n19_class_10(ProductService)
  n20_file_10(ProductService)
  n21_class_11(UserService)
  n22_file_11(UserService)
  n23_class_12(DateUtil)
  n24_file_12(DateUtil)
  n25_class_13(Texts)
  n26_file_13(Texts)
  n27_class_14(ListServiceImpl1)
  n28_file_14(ListServiceImpl1)

  n1_class_1 -- 연관성: 0.80 --> n2_file_1
  n3_class_2 -- 연관성: 0.80 --> n4_file_2
  n5_class_3 -- 연관성: 0.80 --> n6_file_3
  n7_class_4 -- 연관성: 0.80 --> n8_file_4
  n9_class_5 -- 연관성: 0.80 --> n10_file_5
  n11_class_6 -- 연관성: 0.80 --> n12_file_6
  n13_class_7 -- 연관성: 0.80 --> n14_file_7
  n15_class_8 -- 연관성: 0.80 --> n16_file_8
  n17_class_9 -- 연관성: 0.80 --> n18_file_9
  n19_class_10 -- 연관성: 0.80 --> n20_file_10
  n21_class_11 -- 연관성: 0.80 --> n22_file_11
  n23_class_12 -- 연관성: 0.80 --> n24_file_12
  n25_class_13 -- 연관성: 0.80 --> n26_file_13
  n27_class_14 -- 연관성: 0.80 --> n28_file_14
  n2_file_1 -- 연관성: 0.60 --> n4_file_2
  n2_file_1 -- 연관성: 0.60 --> n6_file_3
  n4_file_2 -- 연관성: 0.60 --> n6_file_3
  n8_file_4 -- 연관성: 0.60 --> n10_file_5
  n8_file_4 -- 연관성: 0.60 --> n12_file_6
  n10_file_5 -- 연관성: 0.60 --> n12_file_6
  n14_file_7 -- 연관성: 0.60 --> n16_file_8
  n14_file_7 -- 연관성: 0.60 --> n18_file_9
  n16_file_8 -- 연관성: 0.60 --> n18_file_9
  n20_file_10 -- 연관성: 0.60 --> n14_file_7
  n20_file_10 -- 연관성: 0.60 --> n16_file_8
  n20_file_10 -- 연관성: 0.60 --> n18_file_9
  n20_file_10 -- 연관성: 0.60 --> n22_file_11
  n22_file_11 -- 연관성: 0.60 --> n14_file_7
  n22_file_11 -- 연관성: 0.60 --> n16_file_8
  n22_file_11 -- 연관성: 0.60 --> n18_file_9
  n24_file_12 -- 연관성: 0.60 --> n26_file_13

  %% Clustering Styling
  subgraph Cluster cluster_0
    n29_f
    n30_i
    n31_l
    n31_l
    n32__
    n33__
    n34_1
    n35_9
    n36_7
    n37_6
    n38_d
    n39_2
    n40__
    n41_s
    n42_t
    n43_r
    n44_o
    n45_k
    n46_e
    n32__
    n33__
    n47_0
    n38_d
    n48_4
    n36_7
    n49_a
    n34_1
  end
  subgraph Cluster cluster_1
    n29_f
    n30_i
    n31_l
    n31_l
    n32__
    n33__
    n39_2
    n34_1
    n35_9
    n37_6
    n29_f
    n50_3
    n40__
    n41_s
    n42_t
    n43_r
    n44_o
    n45_k
    n46_e
    n32__
    n33__
    n34_1
    n51_5
    n37_6
    n51_5
    n52_c
    n47_0
  end
  subgraph Cluster cluster_2
    n29_f
    n30_i
    n31_l
    n31_l
    n32__
    n33__
    n48_4
    n39_2
    n49_a
    n51_5
    n29_f
    n51_5
    n40__
    n41_s
    n42_t
    n43_r
    n44_o
    n45_k
    n46_e
    n32__
    n33__
    n34_1
    n35_9
    n36_7
    n37_6
    n38_d
    n39_2
  end
  subgraph Cluster cluster_3
    n29_f
    n30_i
    n31_l
    n31_l
    n32__
    n33__
    n53_8
    n34_1
    n38_d
    n48_4
    n29_f
    n49_a
    n40__
    n41_s
    n42_t
    n43_r
    n44_o
    n45_k
    n46_e
    n32__
    n33__
    n48_4
    n39_2
    n49_a
    n51_5
    n29_f
    n51_5
  end
  subgraph Cluster cluster_4
    n29_f
    n30_i
    n31_l
    n31_l
    n32__
    n33__
    n36_7
    n35_9
    n53_8
    n37_6
    n52_c
    n54_b
    n40__
    n41_s
    n42_t
    n43_r
    n44_o
    n45_k
    n46_e
    n32__
    n33__
    n51_5
    n52_c
    n37_6
    n54_b
    n52_c
    n47_0
  end
```

## 범례


## 원본 데이터

<details>
<summary>원본 데이터를 보려면 클릭</summary>

노드 목록 (28)
```json
  class:1: IntegratedMapper (class)
  file:1: IntegratedMapper (file)
  class:2: IntegratedService (class)
  file:2: IntegratedService (file)
  class:3: VulnerabilityTestService (class)
  file:3: VulnerabilityTestService (file)
  class:4: OrderMapper (class)
  file:4: OrderMapper (file)
  class:5: ProductMapper (class)
  file:5: ProductMapper (file)
  class:6: UserMapper (class)
  file:6: UserMapper (file)
  class:7: ListService (class)
  file:7: ListService (file)
  class:8: OrderService (class)
  file:8: OrderService (file)
  class:9: OverloadService (class)
  file:9: OverloadService (file)
  class:10: ProductService (class)
  file:10: ProductService (file)
```

엣지 목록 (31)
```json
  class:1 -> file:1 (related)
  class:2 -> file:2 (related)
  class:3 -> file:3 (related)
  class:4 -> file:4 (related)
  class:5 -> file:5 (related)
  class:6 -> file:6 (related)
  class:7 -> file:7 (related)
  class:8 -> file:8 (related)
  class:9 -> file:9 (related)
  class:10 -> file:10 (related)
  class:11 -> file:11 (related)
  class:12 -> file:12 (related)
  class:13 -> file:13 (related)
  class:14 -> file:14 (related)
  file:1 -> file:2 (related)
  file:1 -> file:3 (related)
  file:2 -> file:3 (related)
  file:4 -> file:5 (related)
  file:4 -> file:6 (related)
  file:5 -> file:6 (related)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-01 09:47:14*