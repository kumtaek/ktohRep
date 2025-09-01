# Source Analyzer RELATEDNESS Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: RELATEDNESS
- 생성 시각: 2025-09-01 20:42:28
- 노드 수: 13
- 엣지 수: 17

## 다이어그램

```mermaid
graph TD
  n1_file_1(IntegratedMapper)
  n2_file_2(IntegratedService)
  n3_file_3(VulnerabilityTest...)
  n4_file_4(OrderMapper)
  n5_file_5(ProductMapper)
  n6_file_6(UserMapper)
  n7_file_7(ListService)
  n8_file_8(OrderService)
  n9_file_9(OverloadService)
  n10_file_10(ProductService)
  n11_file_11(UserService)
  n12_file_12(DateUtil)
  n13_file_13(Texts)

  n1_file_1 -- 연관성: 0.60 --> n2_file_2
  n1_file_1 -- 연관성: 0.60 --> n3_file_3
  n2_file_2 -- 연관성: 0.60 --> n3_file_3
  n4_file_4 -- 연관성: 0.60 --> n5_file_5
  n4_file_4 -- 연관성: 0.60 --> n6_file_6
  n5_file_5 -- 연관성: 0.60 --> n6_file_6
  n7_file_7 -- 연관성: 0.60 --> n8_file_8
  n7_file_7 -- 연관성: 0.60 --> n9_file_9
  n8_file_8 -- 연관성: 0.60 --> n9_file_9
  n10_file_10 -- 연관성: 0.60 --> n7_file_7
  n10_file_10 -- 연관성: 0.60 --> n8_file_8
  n10_file_10 -- 연관성: 0.60 --> n9_file_9
  n10_file_10 -- 연관성: 0.60 --> n11_file_11
  n11_file_11 -- 연관성: 0.60 --> n7_file_7
  n11_file_11 -- 연관성: 0.60 --> n8_file_8
  n11_file_11 -- 연관성: 0.60 --> n9_file_9
  n12_file_12 -- 연관성: 0.60 --> n13_file_13

  %% Clustering Styling
  subgraph Cluster cluster_0
    n14_f
    n15_i
    n16_l
    n16_l
    n17__
    n18__
    n19_1
    n20_9
    n21_7
    n22_6
    n23_d
    n24_2
    n25__
    n26_s
    n27_t
    n28_r
    n29_o
    n30_k
    n31_e
    n17__
    n18__
    n32_0
    n23_d
    n33_4
    n21_7
    n34_a
    n19_1
  end
  subgraph Cluster cluster_1
    n14_f
    n15_i
    n16_l
    n16_l
    n17__
    n18__
    n24_2
    n19_1
    n20_9
    n22_6
    n14_f
    n35_3
    n25__
    n26_s
    n27_t
    n28_r
    n29_o
    n30_k
    n31_e
    n17__
    n18__
    n19_1
    n36_5
    n22_6
    n36_5
    n37_c
    n32_0
  end
  subgraph Cluster cluster_2
    n14_f
    n15_i
    n16_l
    n16_l
    n17__
    n18__
    n33_4
    n24_2
    n34_a
    n36_5
    n14_f
    n36_5
    n25__
    n26_s
    n27_t
    n28_r
    n29_o
    n30_k
    n31_e
    n17__
    n18__
    n19_1
    n20_9
    n21_7
    n22_6
    n23_d
    n24_2
  end
  subgraph Cluster cluster_3
    n14_f
    n15_i
    n16_l
    n16_l
    n17__
    n18__
    n38_8
    n19_1
    n23_d
    n33_4
    n14_f
    n34_a
    n25__
    n26_s
    n27_t
    n28_r
    n29_o
    n30_k
    n31_e
    n17__
    n18__
    n33_4
    n24_2
    n34_a
    n36_5
    n14_f
    n36_5
  end
```

## 범례


## 원본 데이터

<details>
<summary>원본 데이터를 보려면 클릭</summary>

노드 목록 (13)
```json
  file:1: IntegratedMapper (file)
  file:2: IntegratedService (file)
  file:3: VulnerabilityTestService (file)
  file:4: OrderMapper (file)
  file:5: ProductMapper (file)
  file:6: UserMapper (file)
  file:7: ListService (file)
  file:8: OrderService (file)
  file:9: OverloadService (file)
  file:10: ProductService (file)
  file:11: UserService (file)
  file:12: DateUtil (file)
  file:13: Texts (file)
```

엣지 목록 (17)
```json
  file:1 -> file:2 (related)
  file:1 -> file:3 (related)
  file:2 -> file:3 (related)
  file:4 -> file:5 (related)
  file:4 -> file:6 (related)
  file:5 -> file:6 (related)
  file:7 -> file:8 (related)
  file:7 -> file:9 (related)
  file:8 -> file:9 (related)
  file:10 -> file:7 (related)
  file:10 -> file:8 (related)
  file:10 -> file:9 (related)
  file:10 -> file:11 (related)
  file:11 -> file:7 (related)
  file:11 -> file:8 (related)
  file:11 -> file:9 (related)
  file:12 -> file:13 (related)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-09-01 20:42:28*