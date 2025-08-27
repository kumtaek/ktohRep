package com.example.mapper;
import com.example.model.Customer;
import java.util.List;
public interface CustomerMapper {
    List<Customer> findAll();
    int insert(Customer c);
}