package com.example.mapper;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import java.util.List;
import java.util.Map;

@Mapper
public interface UserMapper {
    
    Object selectUserById(@Param("userId") String userId);
    
    List<Object> selectActiveUsers();
    
    List<Object> searchUsersByCondition(Map<String, Object> params);
    
    List<Object> findUsersWithDynamicConditions(Map<String, Object> conditions);
    
    int insertUser(Object user);
    
    // 동적 SQL 실행용 (테스트/분석 목적)
    List<Map<String, Object>> executeDynamicQuery(@Param("sql") String sql);
}