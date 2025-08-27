package com.example.service;

import com.example.mapper.OrderMapper;
import com.example.model.Order;
import com.example.model.OrderFilter;
import java.util.List;

public class OrderService {
    private final OrderMapper mapper;
    public OrderService(OrderMapper mapper) { this.mapper = mapper; }

    public List<Order> listByFilter(OrderFilter f) { return mapper.listByFilter(f); }
    public int insertOrder(Order o) { return mapper.insertOrder(o); }
    public int updateStatus(Long id, String status) { return mapper.updateStatus(id, status); }
    public Order findById(Long id) { return mapper.findById(id); }
}
