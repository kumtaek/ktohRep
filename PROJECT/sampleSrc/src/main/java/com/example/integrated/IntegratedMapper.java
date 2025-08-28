package com.example.integrated;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import java.util.List;
import java.util.Map;

@Mapper
public interface IntegratedMapper {

    // For static/dynamic query execution from IntegratedService
    List<Map<String, Object>> executeStaticQuery(@Param("sql") String sql);
    List<Map<String, Object>> executeDynamicQuery(@Param("sql") String sql);

    // From DynamicMyBatis: DynamicMapper
    List<Map<String, Object>> findDynamicData(@Param("params") Map<String, Object> params);
    int updateDynamicStatus(@Param("status") String status, @Param("ids") List<Integer> ids);

    // From MixedTechLegacy: LegacyMapper
    List<Map<String, Object>> selectLegacyRecords(@Param("params") Map<String, Object> params);

    // New: Complex SQL queries
    List<Map<String, Object>> getComplexReport(@Param("startDate") String startDate, @Param("endDate") String endDate);
    List<Map<String, Object>> getProductSalesByRegion(@Param("regionId") String regionId);
    List<Map<String, Object>> getCustomerOrderSummary(@Param("customerId") String customerId);
    List<Map<String, Object>> getEmployeePerformance(@Param("year") String year);
    List<Map<String, Object>> getInventoryStatus(@Param("warehouseId") String warehouseId);

    // New: General test cases
    List<Map<String, Object>> getActiveUsers();
    List<Map<String, Object>> getOrdersByStatus(@Param("status") String status);
    List<Map<String, Object>> getProductDetails(@Param("productId") String productId);

    // New: ANSI Join and Oracle Implicit Join
    List<Map<String, Object>> getOrdersWithCustomerAnsiJoin();
    List<Map<String, Object>> getOrdersWithCustomerImplicitJoin();

    // New: Complex SQL queries with 10 table joins, subqueries, scalar queries, SF function calls
    List<Map<String, Object>> getSalesPerformanceReport(@Param("reportDate") String reportDate);
    List<Map<String, Object>> getCustomerActivitySummary(@Param("activityType") String activityType);
    List<Map<String, Object>> getProjectResourceUtilization(@Param("projectId") String projectId);
    List<Map<String, Object>> getFinancialTransactionAudit(@Param("auditDate") String auditDate);
    List<Map<String, Object>> getSupplyChainOptimization(@Param("supplierId") String supplierId);
}
