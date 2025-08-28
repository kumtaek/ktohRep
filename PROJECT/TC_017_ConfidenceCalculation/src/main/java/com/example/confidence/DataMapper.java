package com.example.confidence;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Map;

@Mapper
public interface DataMapper {
    List<Map<String, Object>> getStaticData(@Param("id") String id);
    List<Map<String, Object>> getDynamicData(@Param("columnName") String columnName, @Param("value") String value);
}