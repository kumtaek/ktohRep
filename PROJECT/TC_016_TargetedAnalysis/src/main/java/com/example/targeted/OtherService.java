package com.example.targeted;

import org.springframework.stereotype.Service;

@Service
public class OtherService {

    public String getOtherData(String id) {
        return "Other Data for " + id;
    }

    public int processOther(int value) {
        return value + 10;
    }
}