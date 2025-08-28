package com.example.mybatis;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Map;

@Mapper
public interface DynamicDataMapper {
    List<Map<String, Object>> selectDynamicData(@Param("params") Map<String, Object> params);
    int insertData(@Param("data") Map<String, Object> data);
}