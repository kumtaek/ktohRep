package com.example.simple;

import java.util.List;
import java.util.ArrayList;

public class MySimpleClass {

    private String name;
    private int value;

    public MySimpleClass(String name, int value) {
        this.name = name;
        this.value = value;
    }

    public String myMethod(String input) {
        // This is a simple method
        if (input == null || input.isEmpty()) {
            return "";
        }
        return "Processed: " + input.toUpperCase();
    }

    private int calculateValue(int multiplier) {
        return this.value * multiplier;
    }

    public List<String> anotherMethod(List<String> items) {
        List<String> processedItems = new ArrayList<>();
        for (String item : items) {
            processedItems.add(myMethod(item));
        }
        return processedItems;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public int getValue() {
        return value;
    }

    public void setValue(int value) {
        this.value = value;
    }
}