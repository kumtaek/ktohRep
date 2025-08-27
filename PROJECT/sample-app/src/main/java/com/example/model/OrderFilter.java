package com.example.model;

import java.util.List;

/**
 * Filter object used to query orders based on optional criteria.
 *
 * <p>The filter supports filtering by a single {@code status}, date range
 * expressed as ISO-8601 strings ({@code from}, {@code to}), and a list of
 * statuses. The status list is typed with generics for type safety.</p>
 */
public class OrderFilter {
    /**
     * Exact status to filter on (e.g. "NEW", "COMPLETED").
     */
    private String status;

    /**
     * Beginning date of the filter range, inclusive. Expected format is
     * ISO-8601 (yyyy-MM-dd).
     */
    private String from;

    /**
     * Ending date of the filter range, inclusive. Expected format is
     * ISO-8601 (yyyy-MM-dd).
     */
    private String to;

    /**
     * Optional list of statuses to filter on. Each element is a status
     * string. Generics ensure the list only contains {@link String}
     * values.
     */
    private List<String> statuses;

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getFrom() {
        return from;
    }

    public void setFrom(String from) {
        this.from = from;
    }

    public String getTo() {
        return to;
    }

    public void setTo(String to) {
        this.to = to;
    }

    public List<String> getStatuses() {
        return statuses;
    }

    public void setStatuses(List<String> statuses) {
        this.statuses = statuses;
    }
}