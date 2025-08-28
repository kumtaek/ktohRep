package com.example.mapper;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import java.util.List;
import java.util.Map;

@Mapper
public interface ProductMapper {
    
    List<Object> selectAllProducts();
    
    Object selectProductById(@Param("productId") String productId);
    
    List<Object> searchProductsWithCriteria(Map<String, Object> criteria);
    
    List<Map<String, Object>> getComplexProductAnalysis(Map<String, Object> params);
    
    // 동적 SQL 실행용
    List<Map<String, Object>> executeDynamicQuery(@Param("sql") String sql);
}