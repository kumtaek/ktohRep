# Source Analyzer CLASS Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: CLASS
- 생성 시각: 2025-08-31 21:54:34
- 노드 수: 14
- 엣지 수: 17

## 다이어그램

```mermaid
classDiagram
  class n1_class_1 {
    +findDynamicData()
    +getComplexReport()
    +getOrdersWithCustomerAnsiJoin()
    +getOrdersWithCustomerImplicitJoin()
  }
  class n2_class_2 {
    +startProcess()
    +doWork()
    +getStaticUserData()
    +calculateOrderTotal()
    +getFormattedId()
    +log()
  }
  class n3_class_3 {
    +getUsersByName_VULNERABLE()
    +getUsersByName_SAFE()
    +searchUsers_VULNERABLE()
    +displayUserInfo_VULNERABLE()
    +readFile_VULNERABLE()
    +hashPassword_WEAK()
    +authenticateAdmin_VULNERABLE()
    +connectToDatabase_VULNERABLE()
    +executeCommand_VULNERABLE()
    +searchLDAP_VULNERABLE()
  }
  class n4_class_4 {
    +selectOrderById()
    +calculateOrderAmount()
    +selectOrdersByStatus()
    +getOrdersWithCustomerImplicitJoin()
    +getComplexOrderReport()
    +searchOrdersWithCriteria()
    +executeDynamicQuery()
  }
  class n5_class_5 {
    +selectAllProducts()
    +selectProductById()
    +searchProductsWithCriteria()
    +getComplexProductAnalysis()
    +executeDynamicQuery()
  }
  class n6_class_6 {
    +selectUserById()
    +selectActiveUsers()
    +searchUsersByCondition()
    +findUsersWithDynamicConditions()
    +insertUser()
    +executeDynamicQuery()
  }
  class n7_class_7 {
    +list()
  }
  class n8_class_8 {
    +calculateOrderTotal()
    +getOrdersByStatus()
    +generateOrderReport()
    +largeOrderMethod1()
    +largeOrderMethod2()
    +largeOrderMethod3()
  }
  class n9_class_9 {
    +find()
    +find()
    +process()
  }
  class n10_class_10 {
    +getProductList()
    +getProductDetails()
    +searchProducts()
    +processComplexBusiness()
    +unsafeProductSearch()
  }
  class n11_class_11 {
    +getUserById()
    +getActiveUsers()
    +createUser()
    +processWithReflection()
    +getDynamicUserData()
    +updateUserStatus()
  }
  class n12_class_14 {
    +list()
    +helper()
  }
  class n13_class_12 {
    +getCurrentDate()
    +convertDateFormat()
    +daysBetween()
  }
  class n14_class_13 {
    +isEmpty()
  }

```

## 범례

### 클래스 다이어그램 범례
- 실선 화살표: 상속 관계
- 점선 화살표: 연관 관계
- 사각형: 일반 클래스
- 점선 사각형: 추상 클래스
- `+` : public 멤버
- `-` : private 멤버
- `#` : protected 멤버
- `*` : static 멤버

## 원본 데이터

<details>
<summary>원본 데이터를 보려면 클릭</summary>

노드 목록 (14)
```json
  class:1: IntegratedMapper (class)
  class:2: IntegratedService (class)
  class:3: VulnerabilityTestService (class)
  class:4: OrderMapper (class)
  class:5: ProductMapper (class)
  class:6: UserMapper (class)
  class:7: ListService (class)
  class:8: OrderService (class)
  class:9: OverloadService (class)
  class:10: ProductService (class)
  class:11: UserService (class)
  class:14: ListServiceImpl1 (class)
  class:12: DateUtil (class)
  class:13: Texts (class)
```

엣지 목록 (17)
```json
  class:1 -> class:2 (same_package)
  class:1 -> class:3 (same_package)
  class:2 -> class:3 (same_package)
  class:4 -> class:5 (same_package)
  class:4 -> class:6 (same_package)
  class:5 -> class:6 (same_package)
  class:7 -> class:8 (same_package)
  class:7 -> class:9 (same_package)
  class:7 -> class:10 (same_package)
  class:7 -> class:11 (same_package)
  class:8 -> class:9 (same_package)
  class:8 -> class:10 (same_package)
  class:8 -> class:11 (same_package)
  class:9 -> class:10 (same_package)
  class:9 -> class:11 (same_package)
  class:10 -> class:11 (same_package)
  class:12 -> class:13 (same_package)
```

</details>

---
*Source Analyzer v1.1 — 생성 시각: 2025-08-31 21:54:34*