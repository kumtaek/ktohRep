package com.example.generics;

import java.util.List;
import java.util.Optional;

public interface CustomerService {
    List<Customer> getCustomers();
    Optional<Customer> getCustomerById(String id);
    void addCustomer(Customer customer);
    List<String> getCustomerNames();
    Map<String, Customer> getCustomerMap(); // Example of Map with generics
}