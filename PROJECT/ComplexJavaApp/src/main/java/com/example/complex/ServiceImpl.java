package com.example.complex;

import org.springframework.stereotype.Service;

@Service
public class ServiceImpl extends AbstractService implements ComplexProcessor {

    @Override
    public String processData(String input) {
        String processed = input.toUpperCase();
        return formatOutput(processed);
    }

    @Override
    public int calculateLength(String text) {
        return text.length();
    }

    public static String staticHelper(String value) {
        return "Static: " + value;
    }
}