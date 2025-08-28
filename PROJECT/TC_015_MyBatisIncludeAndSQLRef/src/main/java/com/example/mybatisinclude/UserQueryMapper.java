package com.example.mybatisinclude;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Map;

@Mapper
public interface UserQueryMapper {
    List<Map<String, Object>> selectUser(@Param("userId") String userId);
    List<Map<String, Object>> selectActiveUsers();
}