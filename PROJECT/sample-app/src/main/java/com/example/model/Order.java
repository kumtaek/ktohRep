package com.example.model;

import java.time.LocalDate;
import java.math.BigDecimal;

/**
 * 주문 엔티티 클래스.
 * 주문 ID, 상태, 주문일, 고객 ID를 포함한다.
 */
public class Order {
    private Long id;
    private String status;
    private LocalDate orderDate;
    private Long customerId;

    /**
     * Total monetary amount for this order. Using {@link BigDecimal} avoids
     * floating point precision issues when dealing with currency values.
     */
    private BigDecimal totalAmount;

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public LocalDate getOrderDate() {
        return orderDate;
    }

    public void setOrderDate(LocalDate orderDate) {
        this.orderDate = orderDate;
    }

    public Long getCustomerId() {
        return customerId;
    }

    public void setCustomerId(Long customerId) {
        this.customerId = customerId;
    }

    /**
     * Returns the total amount for this order.
     *
     * @return total amount as BigDecimal or {@code null} if not set
     */
    public BigDecimal getTotalAmount() {
        return totalAmount;
    }

    /**
     * Sets the total amount for this order.
     *
     * @param totalAmount the monetary total to set
     */
    public void setTotalAmount(BigDecimal totalAmount) {
        this.totalAmount = totalAmount;
    }
}
