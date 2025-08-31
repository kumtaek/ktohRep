# Source Analyzer CLASS Diagram (Project 1)

## 개요
- 프로젝트 ID: 1
- 다이어그램 유형: CLASS
- 생성 시각: 2025-08-31 17:11:58
- 노드 수: 209
- 엣지 수: 5672

## 다이어그램

```mermaid
classDiagram
  class n1_class_1 {
    +findDynamicData()
    +getComplexReport()
    +getOrdersWithCustomerAnsiJoin()
    +getOrdersWithCustomerImplicitJoin()
  }
  class n2_class_14 {
    +findDynamicData()
    +getComplexReport()
    +getOrdersWithCustomerAnsiJoin()
    +getOrdersWithCustomerImplicitJoin()
  }
  class n3_class_27 {
    +findDynamicData()
    +getComplexReport()
    +getOrdersWithCustomerAnsiJoin()
    +getOrdersWithCustomerImplicitJoin()
  }
  class n4_class_40 {
    +findDynamicData()
    +getComplexReport()
    +getOrdersWithCustomerAnsiJoin()
    +getOrdersWithCustomerImplicitJoin()
  }
  class n5_class_53 {
    +findDynamicData()
    +getComplexReport()
    +getOrdersWithCustomerAnsiJoin()
    +getOrdersWithCustomerImplicitJoin()
  }
  class n6_class_66 {
    +findDynamicData()
    +getComplexReport()
    +getOrdersWithCustomerAnsiJoin()
    +getOrdersWithCustomerImplicitJoin()
  }
  class n7_class_79 {
    +findDynamicData()
    +getComplexReport()
    +getOrdersWithCustomerAnsiJoin()
    +getOrdersWithCustomerImplicitJoin()
  }
  class n8_class_92 {
    +findDynamicData()
    +getComplexReport()
    +getOrdersWithCustomerAnsiJoin()
    +getOrdersWithCustomerImplicitJoin()
  }
  class n9_class_105 {
    +findDynamicData()
    +getComplexReport()
    +getOrdersWithCustomerAnsiJoin()
    +getOrdersWithCustomerImplicitJoin()
  }
  class n10_class_118 {
    +findDynamicData()
    +getComplexReport()
    +getOrdersWithCustomerAnsiJoin()
    +getOrdersWithCustomerImplicitJoin()
  }
  class n11_class_131 {
    +findDynamicData()
    +getComplexReport()
    +getOrdersWithCustomerAnsiJoin()
    +getOrdersWithCustomerImplicitJoin()
  }
  class n12_class_144 {
    +findDynamicData()
    +getComplexReport()
    +getOrdersWithCustomerAnsiJoin()
    +getOrdersWithCustomerImplicitJoin()
  }
  class n13_class_157 {
    +findDynamicData()
    +getComplexReport()
    +getOrdersWithCustomerAnsiJoin()
    +getOrdersWithCustomerImplicitJoin()
  }
  class n14_class_170 {
    +findDynamicData()
    +getComplexReport()
    +getOrdersWithCustomerAnsiJoin()
    +getOrdersWithCustomerImplicitJoin()
  }
  class n15_class_183 {
    +findDynamicData()
    +getComplexReport()
    +getOrdersWithCustomerAnsiJoin()
    +getOrdersWithCustomerImplicitJoin()
  }
  class n16_class_196 {
    +findDynamicData()
    +getComplexReport()
    +getOrdersWithCustomerAnsiJoin()
    +getOrdersWithCustomerImplicitJoin()
  }
  class n17_class_2 {
    +startProcess()
    +doWork()
    +getStaticUserData()
    +calculateOrderTotal()
    +getFormattedId()
    +log()
  }
  class n18_class_15 {
    +startProcess()
    +doWork()
    +getStaticUserData()
    +calculateOrderTotal()
    +getFormattedId()
    +log()
  }
  class n19_class_28 {
    +startProcess()
    +doWork()
    +getStaticUserData()
    +calculateOrderTotal()
    +getFormattedId()
    +log()
  }
  class n20_class_41 {
    +startProcess()
    +doWork()
    +getStaticUserData()
    +calculateOrderTotal()
    +getFormattedId()
    +log()
  }
  class n21_class_54 {
    +startProcess()
    +doWork()
    +getStaticUserData()
    +calculateOrderTotal()
    +getFormattedId()
    +log()
  }
  class n22_class_67 {
    +startProcess()
    +doWork()
    +getStaticUserData()
    +calculateOrderTotal()
    +getFormattedId()
    +log()
  }
  class n23_class_80 {
    +startProcess()
    +doWork()
    +getStaticUserData()
    +calculateOrderTotal()
    +getFormattedId()
    +log()
  }
  class n24_class_93 {
    +startProcess()
    +doWork()
    +getStaticUserData()
    +calculateOrderTotal()
    +getFormattedId()
    +log()
  }
  class n25_class_106 {
    +startProcess()
    +doWork()
    +getStaticUserData()
    +calculateOrderTotal()
    +getFormattedId()
    +log()
  }
  class n26_class_119 {
    +startProcess()
    +doWork()
    +getStaticUserData()
    +calculateOrderTotal()
    +getFormattedId()
    +log()
  }
  class n27_class_132 {
    +startProcess()
    +doWork()
    +getStaticUserData()
    +calculateOrderTotal()
    +getFormattedId()
    +log()
  }
  class n28_class_145 {
    +startProcess()
    +doWork()
    +getStaticUserData()
    +calculateOrderTotal()
    +getFormattedId()
    +log()
  }
  class n29_class_158 {
    +startProcess()
    +doWork()
    +getStaticUserData()
    +calculateOrderTotal()
    +getFormattedId()
    +log()
  }
  class n30_class_171 {
    +startProcess()
    +doWork()
    +getStaticUserData()
    +calculateOrderTotal()
    +getFormattedId()
    +log()
  }
  class n31_class_184 {
    +startProcess()
    +doWork()
    +getStaticUserData()
    +calculateOrderTotal()
    +getFormattedId()
    +log()
  }
  class n32_class_197 {
    +startProcess()
    +doWork()
    +getStaticUserData()
    +calculateOrderTotal()
    +getFormattedId()
    +log()
  }
  class n33_class_3 {
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
  class n34_class_16 {
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
  class n35_class_29 {
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
  class n36_class_42 {
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
  class n37_class_55 {
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
  class n38_class_68 {
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
  class n39_class_81 {
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
  class n40_class_94 {
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
  class n41_class_107 {
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
  class n42_class_120 {
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
  class n43_class_133 {
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
  class n44_class_146 {
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
  class n45_class_159 {
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
  class n46_class_172 {
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
  class n47_class_185 {
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
  class n48_class_198 {
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
  class n49_class_4 {
    +selectOrderById()
    +calculateOrderAmount()
    +selectOrdersByStatus()
    +getOrdersWithCustomerImplicitJoin()
    +getComplexOrderReport()
    +searchOrdersWithCriteria()
    +executeDynamicQuery()
  }
  class n50_class_17 {
    +selectOrderById()
    +calculateOrderAmount()
    +selectOrdersByStatus()
    +getOrdersWithCustomerImplicitJoin()
    +getComplexOrderReport()
    +searchOrdersWithCriteria()
    +executeDynamicQuery()
  }
  class n51_class_30 {
    +selectOrderById()
    +calculateOrderAmount()
    +selectOrdersByStatus()
    +getOrdersWithCustomerImplicitJoin()
    +getComplexOrderReport()
    +searchOrdersWithCriteria()
    +executeDynamicQuery()
  }
  class n52_class_43 {
    +selectOrderById()
    +calculateOrderAmount()
    +selectOrdersByStatus()
    +getOrdersWithCustomerImplicitJoin()
    +getComplexOrderReport()
    +searchOrdersWithCriteria()
    +executeDynamicQuery()
  }
  class n53_class_56 {
    +selectOrderById()
    +calculateOrderAmount()
    +selectOrdersByStatus()
    +getOrdersWithCustomerImplicitJoin()
    +getComplexOrderReport()
    +searchOrdersWithCriteria()
    +executeDynamicQuery()
  }
  class n54_class_69 {
    +selectOrderById()
    +calculateOrderAmount()
    +selectOrdersByStatus()
    +getOrdersWithCustomerImplicitJoin()
    +getComplexOrderReport()
    +searchOrdersWithCriteria()
    +executeDynamicQuery()
  }
  class n55_class_82 {
    +selectOrderById()
    +calculateOrderAmount()
    +selectOrdersByStatus()
    +getOrdersWithCustomerImplicitJoin()
    +getComplexOrderReport()
    +searchOrdersWithCriteria()
    +executeDynamicQuery()
  }
  class n56_class_95 {
    +selectOrderById()
    +calculateOrderAmount()
    +selectOrdersByStatus()
    +getOrdersWithCustomerImplicitJoin()
    +getComplexOrderReport()
    +searchOrdersWithCriteria()
    +executeDynamicQuery()
  }
  class n57_class_108 {
    +selectOrderById()
    +calculateOrderAmount()
    +selectOrdersByStatus()
    +getOrdersWithCustomerImplicitJoin()
    +getComplexOrderReport()
    +searchOrdersWithCriteria()
    +executeDynamicQuery()
  }
  class n58_class_121 {
    +selectOrderById()
    +calculateOrderAmount()
    +selectOrdersByStatus()
    +getOrdersWithCustomerImplicitJoin()
    +getComplexOrderReport()
    +searchOrdersWithCriteria()
    +executeDynamicQuery()
  }
  class n59_class_134 {
    +selectOrderById()
    +calculateOrderAmount()
    +selectOrdersByStatus()
    +getOrdersWithCustomerImplicitJoin()
    +getComplexOrderReport()
    +searchOrdersWithCriteria()
    +executeDynamicQuery()
  }
  class n60_class_147 {
    +selectOrderById()
    +calculateOrderAmount()
    +selectOrdersByStatus()
    +getOrdersWithCustomerImplicitJoin()
    +getComplexOrderReport()
    +searchOrdersWithCriteria()
    +executeDynamicQuery()
  }
  class n61_class_160 {
    +selectOrderById()
    +calculateOrderAmount()
    +selectOrdersByStatus()
    +getOrdersWithCustomerImplicitJoin()
    +getComplexOrderReport()
    +searchOrdersWithCriteria()
    +executeDynamicQuery()
  }
  class n62_class_173 {
    +selectOrderById()
    +calculateOrderAmount()
    +selectOrdersByStatus()
    +getOrdersWithCustomerImplicitJoin()
    +getComplexOrderReport()
    +searchOrdersWithCriteria()
    +executeDynamicQuery()
  }
  class n63_class_186 {
    +selectOrderById()
    +calculateOrderAmount()
    +selectOrdersByStatus()
    +getOrdersWithCustomerImplicitJoin()
    +getComplexOrderReport()
    +searchOrdersWithCriteria()
    +executeDynamicQuery()
  }
  class n64_class_199 {
    +selectOrderById()
    +calculateOrderAmount()
    +selectOrdersByStatus()
    +getOrdersWithCustomerImplicitJoin()
    +getComplexOrderReport()
    +searchOrdersWithCriteria()
    +executeDynamicQuery()
  }
  class n65_class_5 {
    +selectAllProducts()
    +selectProductById()
    +searchProductsWithCriteria()
    +getComplexProductAnalysis()
    +executeDynamicQuery()
  }
  class n66_class_18 {
    +selectAllProducts()
    +selectProductById()
    +searchProductsWithCriteria()
    +getComplexProductAnalysis()
    +executeDynamicQuery()
  }
  class n67_class_31 {
    +selectAllProducts()
    +selectProductById()
    +searchProductsWithCriteria()
    +getComplexProductAnalysis()
    +executeDynamicQuery()
  }
  class n68_class_44 {
    +selectAllProducts()
    +selectProductById()
    +searchProductsWithCriteria()
    +getComplexProductAnalysis()
    +executeDynamicQuery()
  }
  class n69_class_57 {
    +selectAllProducts()
    +selectProductById()
    +searchProductsWithCriteria()
    +getComplexProductAnalysis()
    +executeDynamicQuery()
  }
  class n70_class_70 {
    +selectAllProducts()
    +selectProductById()
    +searchProductsWithCriteria()
    +getComplexProductAnalysis()
    +executeDynamicQuery()
  }
  class n71_class_83 {
    +selectAllProducts()
    +selectProductById()
    +searchProductsWithCriteria()
    +getComplexProductAnalysis()
    +executeDynamicQuery()
  }
  class n72_class_96 {
    +selectAllProducts()
    +selectProductById()
    +searchProductsWithCriteria()
    +getComplexProductAnalysis()
    +executeDynamicQuery()
  }
  class n73_class_109 {
    +selectAllProducts()
    +selectProductById()
    +searchProductsWithCriteria()
    +getComplexProductAnalysis()
    +executeDynamicQuery()
  }
  class n74_class_122 {
    +selectAllProducts()
    +selectProductById()
    +searchProductsWithCriteria()
    +getComplexProductAnalysis()
    +executeDynamicQuery()
  }
  class n75_class_135 {
    +selectAllProducts()
    +selectProductById()
    +searchProductsWithCriteria()
    +getComplexProductAnalysis()
    +executeDynamicQuery()
  }
  class n76_class_148 {
    +selectAllProducts()
    +selectProductById()
    +searchProductsWithCriteria()
    +getComplexProductAnalysis()
    +executeDynamicQuery()
  }
  class n77_class_161 {
    +selectAllProducts()
    +selectProductById()
    +searchProductsWithCriteria()
    +getComplexProductAnalysis()
    +executeDynamicQuery()
  }
  class n78_class_174 {
    +selectAllProducts()
    +selectProductById()
    +searchProductsWithCriteria()
    +getComplexProductAnalysis()
    +executeDynamicQuery()
  }
  class n79_class_187 {
    +selectAllProducts()
    +selectProductById()
    +searchProductsWithCriteria()
    +getComplexProductAnalysis()
    +executeDynamicQuery()
  }
  class n80_class_200 {
    +selectAllProducts()
    +selectProductById()
    +searchProductsWithCriteria()
    +getComplexProductAnalysis()
    +executeDynamicQuery()
  }
  class n81_class_6 {
    +selectUserById()
    +selectActiveUsers()
    +searchUsersByCondition()
    +findUsersWithDynamicConditions()
    +insertUser()
    +executeDynamicQuery()
  }
  class n82_class_19 {
    +selectUserById()
    +selectActiveUsers()
    +searchUsersByCondition()
    +findUsersWithDynamicConditions()
    +insertUser()
    +executeDynamicQuery()
  }
  class n83_class_32 {
    +selectUserById()
    +selectActiveUsers()
    +searchUsersByCondition()
    +findUsersWithDynamicConditions()
    +insertUser()
    +executeDynamicQuery()
  }
  class n84_class_45 {
    +selectUserById()
    +selectActiveUsers()
    +searchUsersByCondition()
    +findUsersWithDynamicConditions()
    +insertUser()
    +executeDynamicQuery()
  }
  class n85_class_58 {
    +selectUserById()
    +selectActiveUsers()
    +searchUsersByCondition()
    +findUsersWithDynamicConditions()
    +insertUser()
    +executeDynamicQuery()
  }
  class n86_class_71 {
    +selectUserById()
    +selectActiveUsers()
    +searchUsersByCondition()
    +findUsersWithDynamicConditions()
    +insertUser()
    +executeDynamicQuery()
  }
  class n87_class_84 {
    +selectUserById()
    +selectActiveUsers()
    +searchUsersByCondition()
    +findUsersWithDynamicConditions()
    +insertUser()
    +executeDynamicQuery()
  }
  class n88_class_97 {
    +selectUserById()
    +selectActiveUsers()
    +searchUsersByCondition()
    +findUsersWithDynamicConditions()
    +insertUser()
    +executeDynamicQuery()
  }
  class n89_class_110 {
    +selectUserById()
    +selectActiveUsers()
    +searchUsersByCondition()
    +findUsersWithDynamicConditions()
    +insertUser()
    +executeDynamicQuery()
  }
  class n90_class_123 {
    +selectUserById()
    +selectActiveUsers()
    +searchUsersByCondition()
    +findUsersWithDynamicConditions()
    +insertUser()
    +executeDynamicQuery()
  }
  class n91_class_136 {
    +selectUserById()
    +selectActiveUsers()
    +searchUsersByCondition()
    +findUsersWithDynamicConditions()
    +insertUser()
    +executeDynamicQuery()
  }
  class n92_class_149 {
    +selectUserById()
    +selectActiveUsers()
    +searchUsersByCondition()
    +findUsersWithDynamicConditions()
    +insertUser()
    +executeDynamicQuery()
  }
  class n93_class_162 {
    +selectUserById()
    +selectActiveUsers()
    +searchUsersByCondition()
    +findUsersWithDynamicConditions()
    +insertUser()
    +executeDynamicQuery()
  }
  class n94_class_175 {
    +selectUserById()
    +selectActiveUsers()
    +searchUsersByCondition()
    +findUsersWithDynamicConditions()
    +insertUser()
    +executeDynamicQuery()
  }
  class n95_class_188 {
    +selectUserById()
    +selectActiveUsers()
    +searchUsersByCondition()
    +findUsersWithDynamicConditions()
    +insertUser()
    +executeDynamicQuery()
  }
  class n96_class_201 {
    +selectUserById()
    +selectActiveUsers()
    +searchUsersByCondition()
    +findUsersWithDynamicConditions()
    +insertUser()
    +executeDynamicQuery()
  }
  class n97_class_7 {
    +list()
  }
  class n98_class_20 {
    +list()
  }
  class n99_class_33 {
    +list()
  }
  class n100_class_46 {
    +list()
  }
  class n101_class_59 {
    +list()
  }
  class n102_class_72 {
    +list()
  }
  class n103_class_85 {
    +list()
  }
  class n104_class_98 {
    +list()
  }
  class n105_class_111 {
    +list()
  }
  class n106_class_124 {
    +list()
  }
  class n107_class_137 {
    +list()
  }
  class n108_class_150 {
    +list()
  }
  class n109_class_163 {
    +list()
  }
  class n110_class_176 {
    +list()
  }
  class n111_class_189 {
    +list()
  }
  class n112_class_202 {
    +list()
  }
  class n113_class_8 {
    +calculateOrderTotal()
    +getOrdersByStatus()
    +generateOrderReport()
    +largeOrderMethod1()
    +largeOrderMethod2()
    +largeOrderMethod3()
  }
  class n114_class_21 {
    +calculateOrderTotal()
    +getOrdersByStatus()
    +generateOrderReport()
    +largeOrderMethod1()
    +largeOrderMethod2()
    +largeOrderMethod3()
  }
  class n115_class_34 {
    +calculateOrderTotal()
    +getOrdersByStatus()
    +generateOrderReport()
    +largeOrderMethod1()
    +largeOrderMethod2()
    +largeOrderMethod3()
  }
  class n116_class_47 {
    +calculateOrderTotal()
    +getOrdersByStatus()
    +generateOrderReport()
    +largeOrderMethod1()
    +largeOrderMethod2()
    +largeOrderMethod3()
  }
  class n117_class_60 {
    +calculateOrderTotal()
    +getOrdersByStatus()
    +generateOrderReport()
    +largeOrderMethod1()
    +largeOrderMethod2()
    +largeOrderMethod3()
  }
  class n118_class_73 {
    +calculateOrderTotal()
    +getOrdersByStatus()
    +generateOrderReport()
    +largeOrderMethod1()
    +largeOrderMethod2()
    +largeOrderMethod3()
  }
  class n119_class_86 {
    +calculateOrderTotal()
    +getOrdersByStatus()
    +generateOrderReport()
    +largeOrderMethod1()
    +largeOrderMethod2()
    +largeOrderMethod3()
  }
  class n120_class_99 {
    +calculateOrderTotal()
    +getOrdersByStatus()
    +generateOrderReport()
    +largeOrderMethod1()
    +largeOrderMethod2()
    +largeOrderMethod3()
  }
  class n121_class_112 {
    +calculateOrderTotal()
    +getOrdersByStatus()
    +generateOrderReport()
    +largeOrderMethod1()
    +largeOrderMethod2()
    +largeOrderMethod3()
  }
  class n122_class_125 {
    +calculateOrderTotal()
    +getOrdersByStatus()
    +generateOrderReport()
    +largeOrderMethod1()
    +largeOrderMethod2()
    +largeOrderMethod3()
  }
  class n123_class_138 {
    +calculateOrderTotal()
    +getOrdersByStatus()
    +generateOrderReport()
    +largeOrderMethod1()
    +largeOrderMethod2()
    +largeOrderMethod3()
  }
  class n124_class_151 {
    +calculateOrderTotal()
    +getOrdersByStatus()
    +generateOrderReport()
    +largeOrderMethod1()
    +largeOrderMethod2()
    +largeOrderMethod3()
  }
  class n125_class_164 {
    +calculateOrderTotal()
    +getOrdersByStatus()
    +generateOrderReport()
    +largeOrderMethod1()
    +largeOrderMethod2()
    +largeOrderMethod3()
  }
  class n126_class_177 {
    +calculateOrderTotal()
    +getOrdersByStatus()
    +generateOrderReport()
    +largeOrderMethod1()
    +largeOrderMethod2()
    +largeOrderMethod3()
  }
  class n127_class_190 {
    +calculateOrderTotal()
    +getOrdersByStatus()
    +generateOrderReport()
    +largeOrderMethod1()
    +largeOrderMethod2()
    +largeOrderMethod3()
  }
  class n128_class_203 {
    +calculateOrderTotal()
    +getOrdersByStatus()
    +generateOrderReport()
    +largeOrderMethod1()
    +largeOrderMethod2()
    +largeOrderMethod3()
  }
  class n129_class_9 {
    +find()
    +find()
    +process()
  }
  class n130_class_22 {
    +find()
    +find()
    +process()
  }
  class n131_class_35 {
    +find()
    +find()
    +process()
  }
  class n132_class_48 {
    +find()
    +find()
    +process()
  }
  class n133_class_61 {
    +find()
    +find()
    +process()
  }
  class n134_class_74 {
    +find()
    +find()
    +process()
  }
  class n135_class_87 {
    +find()
    +find()
    +process()
  }
  class n136_class_100 {
    +find()
    +find()
    +process()
  }
  class n137_class_113 {
    +find()
    +find()
    +process()
  }
  class n138_class_126 {
    +find()
    +find()
    +process()
  }
  class n139_class_139 {
    +find()
    +find()
    +process()
  }
  class n140_class_152 {
    +find()
    +find()
    +process()
  }
  class n141_class_165 {
    +find()
    +find()
    +process()
  }
  class n142_class_178 {
    +find()
    +find()
    +process()
  }
  class n143_class_191 {
    +find()
    +find()
    +process()
  }
  class n144_class_204 {
    +find()
    +find()
    +process()
  }
  class n145_class_10 {
    +getProductList()
    +getProductDetails()
    +searchProducts()
    +processComplexBusiness()
    +unsafeProductSearch()
  }
  class n146_class_23 {
    +getProductList()
    +getProductDetails()
    +searchProducts()
    +processComplexBusiness()
    +unsafeProductSearch()
  }
  class n147_class_36 {
    +getProductList()
    +getProductDetails()
    +searchProducts()
    +processComplexBusiness()
    +unsafeProductSearch()
  }
  class n148_class_49 {
    +getProductList()
    +getProductDetails()
    +searchProducts()
    +processComplexBusiness()
    +unsafeProductSearch()
  }
  class n149_class_62 {
    +getProductList()
    +getProductDetails()
    +searchProducts()
    +processComplexBusiness()
    +unsafeProductSearch()
  }
  class n150_class_75 {
    +getProductList()
    +getProductDetails()
    +searchProducts()
    +processComplexBusiness()
    +unsafeProductSearch()
  }
  class n151_class_88 {
    +getProductList()
    +getProductDetails()
    +searchProducts()
    +processComplexBusiness()
    +unsafeProductSearch()
  }
  class n152_class_101 {
    +getProductList()
    +getProductDetails()
    +searchProducts()
    +processComplexBusiness()
    +unsafeProductSearch()
  }
  class n153_class_114 {
    +getProductList()
    +getProductDetails()
    +searchProducts()
    +processComplexBusiness()
    +unsafeProductSearch()
  }
  class n154_class_127 {
    +getProductList()
    +getProductDetails()
    +searchProducts()
    +processComplexBusiness()
    +unsafeProductSearch()
  }
  class n155_class_140 {
    +getProductList()
    +getProductDetails()
    +searchProducts()
    +processComplexBusiness()
    +unsafeProductSearch()
  }
  class n156_class_153 {
    +getProductList()
    +getProductDetails()
    +searchProducts()
    +processComplexBusiness()
    +unsafeProductSearch()
  }
  class n157_class_166 {
    +getProductList()
    +getProductDetails()
    +searchProducts()
    +processComplexBusiness()
    +unsafeProductSearch()
  }
  class n158_class_179 {
    +getProductList()
    +getProductDetails()
    +searchProducts()
    +processComplexBusiness()
    +unsafeProductSearch()
  }
  class n159_class_192 {
    +getProductList()
    +getProductDetails()
    +searchProducts()
    +processComplexBusiness()
    +unsafeProductSearch()
  }
  class n160_class_205 {
    +getProductList()
    +getProductDetails()
    +searchProducts()
    +processComplexBusiness()
    +unsafeProductSearch()
  }
  class n161_class_11 {
    +getUserById()
    +getActiveUsers()
    +createUser()
    +processWithReflection()
    +getDynamicUserData()
  }
  class n162_class_24 {
    +getUserById()
    +getActiveUsers()
    +createUser()
    +processWithReflection()
    +getDynamicUserData()
  }
  class n163_class_37 {
    +getUserById()
    +getActiveUsers()
    +createUser()
    +processWithReflection()
    +getDynamicUserData()
  }
  class n164_class_50 {
    +getUserById()
    +getActiveUsers()
    +createUser()
    +processWithReflection()
    +getDynamicUserData()
  }
  class n165_class_63 {
    +getUserById()
    +getActiveUsers()
    +createUser()
    +processWithReflection()
    +getDynamicUserData()
  }
  class n166_class_76 {
    +getUserById()
    +getActiveUsers()
    +createUser()
    +processWithReflection()
    +getDynamicUserData()
  }
  class n167_class_89 {
    +getUserById()
    +getActiveUsers()
    +createUser()
    +processWithReflection()
    +getDynamicUserData()
  }
  class n168_class_102 {
    +getUserById()
    +getActiveUsers()
    +createUser()
    +processWithReflection()
    +getDynamicUserData()
  }
  class n169_class_115 {
    +getUserById()
    +getActiveUsers()
    +createUser()
    +processWithReflection()
    +getDynamicUserData()
  }
  class n170_class_128 {
    +getUserById()
    +getActiveUsers()
    +createUser()
    +processWithReflection()
    +getDynamicUserData()
  }
  class n171_class_141 {
    +getUserById()
    +getActiveUsers()
    +createUser()
    +processWithReflection()
    +getDynamicUserData()
  }
  class n172_class_154 {
    +getUserById()
    +getActiveUsers()
    +createUser()
    +processWithReflection()
    +getDynamicUserData()
  }
  class n173_class_167 {
    +getUserById()
    +getActiveUsers()
    +createUser()
    +processWithReflection()
    +getDynamicUserData()
  }
  class n174_class_180 {
    +getUserById()
    +getActiveUsers()
    +createUser()
    +processWithReflection()
    +getDynamicUserData()
  }
  class n175_class_193 {
    +getUserById()
    +getActiveUsers()
    +createUser()
    +processWithReflection()
    +getDynamicUserData()
  }
  class n176_class_206 {
    +getUserById()
    +getActiveUsers()
    +createUser()
    +processWithReflection()
    +getDynamicUserData()
    +updateUserStatus()
  }
  class n177_class_13 {
    +list()
    +helper()
  }
  class n178_class_26 {
    +list()
    +helper()
  }
  class n179_class_39 {
    +list()
    +helper()
  }
  class n180_class_52 {
    +list()
    +helper()
  }
  class n181_class_65 {
    +list()
    +helper()
  }
  class n182_class_78 {
    +list()
    +helper()
  }
  class n183_class_91 {
    +list()
    +helper()
  }
  class n184_class_104 {
    +list()
    +helper()
  }
  class n185_class_117 {
    +list()
    +helper()
  }
  class n186_class_130 {
    +list()
    +helper()
  }
  class n187_class_143 {
    +list()
    +helper()
  }
  class n188_class_156 {
    +list()
    +helper()
  }
  class n189_class_169 {
    +list()
    +helper()
  }
  class n190_class_182 {
    +list()
    +helper()
  }
  class n191_class_195 {
    +list()
    +helper()
  }
  class n192_class_209 {
    +list()
    +helper()
  }
  class n193_class_207 {
    +getCurrentDate()
    +convertDateFormat()
    +daysBetween()
  }
  class n194_class_12 {
    +isEmpty()
  }
  class n195_class_25 {
    +isEmpty()
  }
  class n196_class_38 {
    +isEmpty()
  }
  class n197_class_51 {
    +isEmpty()
  }
  class n198_class_64 {
    +isEmpty()
  }
  class n199_class_77 {
    +isEmpty()
  }
  class n200_class_90 {
    +isEmpty()
  }
  class n201_class_103 {
    +isEmpty()
  }
  class n202_class_116 {
    +isEmpty()
  }
  class n203_class_129 {
    +isEmpty()
  }
  class n204_class_142 {
    +isEmpty()
  }
  class n205_class_155 {
    +isEmpty()
  }
  class n206_class_168 {
    +isEmpty()
  }
  class n207_class_181 {
    +isEmpty()
  }
  class n208_class_194 {
    +isEmpty()
  }
  class n209_class_208 {
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

---
*Source Analyzer v1.1 — 생성 시각: 2025-08-31 17:11:58*