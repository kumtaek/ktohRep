package com.example.integrated;

import java.util.List;
import java.util.Map;

public interface IntegratedMapper {
    List<Map<String, Object>> findDynamicData(Map<String, Object> params);
    List<Map<String, Object>> getComplexReport(Map<String, Object> params);
    List<Map<String, Object>> getOrdersWithCustomerAnsiJoin(String customerId);
    List<Map<String, Object>> getOrdersWithCustomerImplicitJoin(String customerId);
}

