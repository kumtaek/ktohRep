package com.example.complexsql;

import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Map;

@Mapper
public interface ReportMapper {
    List<Map<String, Object>> getComplexReport(@Param("startDate") String startDate, @Param("endDate") String endDate);
}