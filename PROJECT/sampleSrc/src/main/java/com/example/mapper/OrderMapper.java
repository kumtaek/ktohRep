package com.example.mapper;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

@Mapper
public interface OrderMapper {
    
    Object selectOrderById(@Param("orderId") String orderId);
    
    BigDecimal calculateOrderAmount(@Param("orderId") String orderId);
    
    List<Object> selectOrdersByStatus(@Param("status") String status);
    
    List<Object> getOrdersWithCustomerImplicitJoin(@Param("status") String status);
    
    List<Map<String, Object>> getComplexOrderReport(Map<String, Object> params);
    
    List<Object> searchOrdersWithCriteria(Map<String, Object> criteria);
    
    // 동적 SQL 실행용
    List<Map<String, Object>> executeDynamicQuery(@Param("sql") String sql);
}