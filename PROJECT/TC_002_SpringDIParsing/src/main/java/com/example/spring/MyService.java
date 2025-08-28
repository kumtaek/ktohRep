package com.example.spring;

import org.springframework.stereotype.Service;

@Service
public class MyService {

    public String getServiceData(String input) {
        return "Service processed: " + input.toLowerCase();
    }
}