package com.example.service;

import com.example.mapper.CustomerMapper;
import com.example.model.Customer;
import java.util.List;

public class CustomerService {
    private final CustomerMapper mapper;
    public CustomerService(CustomerMapper mapper) { this.mapper = mapper; }
    public List<Customer> findAll() { return mapper.findAll(); }
    public void insert(Customer c) { mapper.insert(c); }
}
