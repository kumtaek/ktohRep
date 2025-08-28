package com.example.llm;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Map;

@Mapper
public interface UserMapper {
    List<Map<String, Object>> findAllUsers();
    List<Map<String, Object>> findUsersByStatus(@Param("status") String status);
    void updateStatus(@Param("userId") String userId, @Param("newStatus") String newStatus);
}