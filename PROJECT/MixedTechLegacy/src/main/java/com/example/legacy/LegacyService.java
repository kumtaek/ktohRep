package com.example.legacy;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

@Service
public class LegacyService {

    private final LegacyMapper legacyMapper;

    @Autowired
    public LegacyService(LegacyMapper legacyMapper) {
        this.legacyMapper = legacyMapper;
    }

    public List<Map<String, Object>> getLegacyData(String type, String status) {
        // Complex business logic to determine parameters
        Map<String, Object> params = Map.of("dataType", type, "dataStatus", status);
        return legacyMapper.selectLegacyRecords(params);
    }

    public String generateReport(List<Map<String, Object>> data) {
        StringBuilder report = new StringBuilder();
        data.forEach(row -> report.append(row.get("NAME")).append(" - ").append(row.get("VALUE")).append("\n"));
        return report.toString();
    }
}
