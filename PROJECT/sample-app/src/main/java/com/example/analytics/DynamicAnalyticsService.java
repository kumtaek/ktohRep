package com.example.analytics;

import org.springframework.stereotype.Service;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.StringJoiner;

/**
 * Service providing generic analytics calculations. It illustrates dynamic
 * aggregation of metrics defined at runtime and the construction of SQL
 * statements on the fly. Such patterns are challenging for static
 * analyzers because the set of columns and functions is not known until
 * execution time.
 */
@Service
public class DynamicAnalyticsService {

    /**
     * Aggregate numeric metrics using the specified operation. Supported
     * operations include "sum", "avg" (average), "min" and "max". If an
     * unsupported operation is requested, an {@link IllegalArgumentException}
     * is thrown.
     *
     * @param metrics map where the key is a metric name and the value is a list of values
     * @param operation the aggregation operation to apply
     * @return a map of aggregated results keyed by metric name
     */
    public Map<String, Double> aggregateMetrics(Map<String, List<Double>> metrics, String operation) {
        Map<String, Double> result = new HashMap<>();
        if (operation == null) {
            throw new IllegalArgumentException("operation must not be null");
        }
        String op = operation.toLowerCase();
        for (Map.Entry<String, List<Double>> entry : metrics.entrySet()) {
            String key = entry.getKey();
            List<Double> values = entry.getValue();
            if (values == null || values.isEmpty()) {
                result.put(key, 0.0);
                continue;
            }
            switch (op) {
                case "sum":
                    result.put(key, values.stream().mapToDouble(Double::doubleValue).sum());
                    break;
                case "avg":
                case "average":
                    result.put(key, values.stream().mapToDouble(Double::doubleValue).average().orElse(0.0));
                    break;
                case "min":
                    result.put(key, values.stream().mapToDouble(Double::doubleValue).min().orElse(0.0));
                    break;
                case "max":
                    result.put(key, values.stream().mapToDouble(Double::doubleValue).max().orElse(0.0));
                    break;
                default:
                    throw new IllegalArgumentException("Unsupported operation: " + operation);
            }
        }
        return result;
    }

    /**
     * Build a SQL SELECT statement that performs aggregate functions on
     * specified columns. For example, passing {@code {"sales"->"AVG", "expenses"->"SUM"}}
     * produces {@code SELECT AVG(sales) AS sales_avg, SUM(expenses) AS expenses_sum FROM table}. This
     * method does not execute the SQL; it merely returns the statement as a
     * string.
     *
     * @param tableName name of the table to query
     * @param aggregates map where the key is a column name and the value is an SQL aggregate function
     * @return SQL query string
     */
    public String buildAggregatedSql(String tableName, Map<String, String> aggregates) {
        if (tableName == null || tableName.isEmpty()) {
            throw new IllegalArgumentException("tableName must not be null or empty");
        }
        if (aggregates == null || aggregates.isEmpty()) {
            throw new IllegalArgumentException("aggregates must not be empty");
        }
        StringJoiner selectJoiner = new StringJoiner(", ");
        for (Map.Entry<String, String> entry : aggregates.entrySet()) {
            String column = entry.getKey();
            String function = entry.getValue();
            String alias = column + "_" + function.toLowerCase();
            selectJoiner.add(function + "(" + column + ") AS " + alias);
        }
        return "SELECT " + selectJoiner.toString() + " FROM " + tableName;
    }
}