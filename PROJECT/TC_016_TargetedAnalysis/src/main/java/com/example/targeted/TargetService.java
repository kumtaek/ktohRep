package com.example.targeted;

import org.springframework.stereotype.Service;

@Service
public class TargetService {

    public String getTargetData(String id) {
        return "Target Data for " + id;
    }

    public int processTarget(int value) {
        return value * 2;
    }
}