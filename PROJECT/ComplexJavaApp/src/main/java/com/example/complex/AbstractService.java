package com.example.complex;

public abstract class AbstractService {
    public abstract String processData(String input);

    protected String formatOutput(String data) {
        return "Formatted: " + data;
    }
}