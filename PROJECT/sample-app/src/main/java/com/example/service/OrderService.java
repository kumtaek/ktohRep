package com.example.service;

import com.example.mapper.OrderMapper;
import com.example.model.Order;
import com.example.model.OrderFilter;
import java.math.BigDecimal;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * Service layer encapsulating business logic related to orders.
 *
 * <p>This class delegates persistence operations to the {@link OrderMapper}
 * and exposes additional aggregate functionality such as computing order counts
 * by status and calculating total revenue. Generic types are used throughout
 * to provide type safety.</p>
 */
public class OrderService {
    private final OrderMapper mapper;

    public OrderService(OrderMapper mapper) {
        this.mapper = mapper;
    }

    /**
     * Return a list of orders matching the given filter.
     *
     * @param f filtering criteria
     * @return a list of orders (never {@code null})
     */
    public List<Order> listByFilter(OrderFilter f) {
        return mapper.listByFilter(f);
    }

    /**
     * Insert a new order into the persistence layer.
     *
     * @param o order to insert
     * @return number of rows affected
     */
    public int insertOrder(Order o) {
        return mapper.insertOrder(o);
    }

    /**
     * Update the status of an existing order.
     *
     * @param id    identifier of the order
     * @param status new status string
     * @return number of rows affected
     */
    public int updateStatus(Long id, String status) {
        return mapper.updateStatus(id, status);
    }

    /**
     * Find an order by its primary key.
     *
     * @param id identifier of the order
     * @return the order or {@code null} if not found
     */
    public Order findById(Long id) {
        return mapper.findById(id);
    }

    /**
     * Compute the number of orders for each status across all orders.
     *
     * @return a map keyed by status with counts of orders
     */
    public Map<String, Long> countOrdersByStatus() {
        List<Order> allOrders = mapper.listByFilter(new OrderFilter());
        return allOrders.stream()
                .collect(Collectors.groupingBy(Order::getStatus, Collectors.counting()));
    }

    /**
     * Calculate the total revenue for orders matching the given filter.
     * This sums the {@link Order#getTotalAmount()} field for each order.
     * Missing totals are treated as zero.
     *
     * @param filter filter to apply when retrieving orders
     * @return aggregated revenue as a {@link BigDecimal}
     */
    public BigDecimal calculateTotalRevenue(OrderFilter filter) {
        return mapper.listByFilter(filter)
                .stream()
                .map(o -> o.getTotalAmount() == null ? BigDecimal.ZERO : o.getTotalAmount())
                .reduce(BigDecimal.ZERO, BigDecimal::add);
    }
}