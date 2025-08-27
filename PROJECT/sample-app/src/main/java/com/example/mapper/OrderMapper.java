package com.example.mapper;

import com.example.model.Order;
import com.example.model.OrderFilter;
import java.util.List;

/**
 * MyBatis mapper interface for performing CRUD operations on {@link Order} entities.
 *
 * <p>Generic list return types are specified to avoid raw types and provide
 * compile‑time type safety. The implementation of this interface is provided
 * at runtime by MyBatis based on the corresponding XML mapper.</p>
 */
public interface OrderMapper {
    /**
     * Retrieve a list of orders that satisfy the given filter.
     *
     * @param f filter criteria
     * @return list of matching orders
     */
    List<Order> listByFilter(OrderFilter f);

    /**
     * Insert a new order.
     *
     * @param o order to insert
     * @return number of rows affected
     */
    int insertOrder(Order o);

    /**
     * Update the status of an existing order.
     *
     * @param id identifier of the order to update
     * @param status new status value
     * @return number of rows affected
     */
    int updateStatus(Long id, String status);

    /**
     * Find an order by its primary key.
     *
     * @param id primary key
     * @return the order or {@code null} if not found
     */
    Order findById(Long id);
}