package com.example.complexity;

import org.springframework.stereotype.Service;

@Service
public class ComplexityService {

    public int complexMethod(int a, int b, int c) {
        int result = 0;
        if (a > 0) { // +1
            result = a + b;
        } else if (b < 0) { // +1
            result = a - b;
        } else { // +1
            result = c;
        }

        for (int i = 0; i < 10; i++) { // +1
            if (i % 2 == 0) { // +1
                result += i;
            }
        }

        while (c > 0) { // +1
            c--;
        }
        return result;
    }

    public String simpleMethod(String input) {
        if (input == null) { // +1
            return "";
        }
        return input.trim();
    }

    public void switchMethod(int choice) {
        switch (choice) { // +1
            case 1: // +1
                System.out.println("Choice 1");
                break;
            case 2: // +1
                System.out.println("Choice 2");
                break;
            default: // +1
                System.out.println("Default choice");
                break;
        }
    }
}