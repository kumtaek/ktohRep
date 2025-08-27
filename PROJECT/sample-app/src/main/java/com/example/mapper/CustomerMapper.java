package com.example.mapper;

import com.example.model.Customer;
import java.util.List;

/**
 * Mapper interface for customer persistence operations.
 */
public interface CustomerMapper {
    /**
     * Retrieve all customers from the database.
     *
     * @return list of customers
     */
    List<Customer> findAll();

    /**
     * Persist a new customer record.
     *
     * @param c customer to insert
     * @return number of rows affected
     */
    int insert(Customer c);

    /**
     * Find customers whose name matches the provided fragment.
     *
     * @param name name fragment to search for
     * @return list of customers matching the criteria
     */
    List<Customer> findByName(String name);
}