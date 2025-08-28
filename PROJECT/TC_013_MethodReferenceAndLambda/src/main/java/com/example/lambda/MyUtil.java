package com.example.lambda;

public class MyUtil {
    public static String transform(String input) {
        return input.trim().toUpperCase();
    }

    public String reverse(String input) {
        return new StringBuilder(input).reverse().toString();
    }
}