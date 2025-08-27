package com.example.mapper;
import com.example.model.Order;
import com.example.model.OrderFilter;
import java.util.List;
public interface OrderMapper {
    List<Order> listByFilter(OrderFilter f);
    int insertOrder(Order o);
    int updateStatus(Long id, String status);
    Order findById(Long id);
}