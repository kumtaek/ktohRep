package com.example.incremental;

import org.springframework.stereotype.Service;

@Service
public class MyIncrementalService {

    public String getData(String id) {
        // Initial version of the method
        return "Data for " + id;
    }

    public int calculateHash(String input) {
        return input.hashCode();
    }
}