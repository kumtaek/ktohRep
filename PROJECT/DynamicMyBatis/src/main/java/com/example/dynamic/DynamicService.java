package com.example.dynamic;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

@Service
public class DynamicService {

    private final DynamicMapper dynamicMapper;

    @Autowired
    public DynamicService(DynamicMapper dynamicMapper) {
        this.dynamicMapper = dynamicMapper;
    }

    public List<Map<String, Object>> getFilteredData(Map<String, Object> params) {
        return dynamicMapper.findDynamicData(params);
    }

    public int updateStatuses(String status, List<Integer> ids) {
        return dynamicMapper.updateDynamicStatus(status, ids);
    }

    public List<String> getProductsByCriteria(Map<String, Object> criteria) {
        return dynamicMapper.searchProducts(criteria);
    }
}