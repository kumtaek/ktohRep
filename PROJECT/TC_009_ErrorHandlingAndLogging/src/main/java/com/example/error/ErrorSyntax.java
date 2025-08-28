package com.example.error;

public class ErrorSyntax {
    public void brokenMethod() {
        // This line has a syntax error
        String message = "Hello;
        System.out.println(message);
    }
}