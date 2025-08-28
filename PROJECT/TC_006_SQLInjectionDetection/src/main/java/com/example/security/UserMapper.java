package com.example.security;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Map;

@Mapper
public interface UserMapper {
    List<Map<String, Object>> findUserByDynamicColumn(@Param("columnName") String columnName, @Param("value") String value);
    List<Map<String, Object>> findUserSafely(@Param("columnName") String columnName, @Param("value") String value);
}