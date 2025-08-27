package com.example.service;

import com.example.mapper.CustomerMapper;
import com.example.model.Customer;
import java.util.List;

/**
 * Service layer for customer related operations.
 *
 * <p>This class delegates persistence operations to the {@link CustomerMapper}
 * and exposes convenience methods for retrieving and inserting customers as well
 * as searching by name. Generic types ensure compile‑time type safety.</p>
 */
public class CustomerService {
    private final CustomerMapper mapper;

    public CustomerService(CustomerMapper mapper) {
        this.mapper = mapper;
    }

    /**
     * Retrieve all customers in the system.
     *
     * @return list of customers; may be empty but never {@code null}
     */
    public List<Customer> findAll() {
        return mapper.findAll();
    }

    /**
     * Insert a new customer.
     *
     * @param c customer to persist
     */
    public void insert(Customer c) {
        mapper.insert(c);
    }

    /**
     * Find customers by their name. The underlying mapper implementation may
     * use a case-insensitive or partial match depending on the query.
     *
     * @param name name fragment to search
     * @return list of matching customers
     */
    public List<Customer> findByName(String name) {
        return mapper.findByName(name);
    }
}