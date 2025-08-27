package com.example.dynamic;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Map;

@Mapper
public interface DynamicMapper {
    List<Map<String, Object>> findDynamicData(@Param("params") Map<String, Object> params);
    int updateDynamicStatus(@Param("status") String status, @Param("ids") List<Integer> ids);
    List<String> searchProducts(@Param("criteria") Map<String, Object> criteria);
}