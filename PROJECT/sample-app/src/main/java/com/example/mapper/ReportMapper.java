package com.example.mapper;

import java.util.List;
import java.util.Map;

/**
 * Mapper interface exposing reporting queries.
 *
 * <p>Generic map types are used to describe the column/value structure
 * returned from aggregation queries such as sales by customer.</p>
 */
public interface ReportMapper {
    /**
     * Retrieve aggregated sales per customer. Each map in the returned
     * list should contain at least keys such as {@code customerId} and
     * {@code total} but the exact schema is defined in the corresponding
     * MyBatis XML.
     *
     * @return list of maps representing aggregated sales data
     */
    List<Map<String, Object>> salesByCustomer();
}