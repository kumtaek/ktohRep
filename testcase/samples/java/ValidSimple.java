package com.example;

public class ValidSimple {
    // 간단한 정상 자바 클래스 (호출 관계 포함)
    public void run() {
        helper();
    }

    private int add(int a, int b) {
        return a + b;
    }

    private void helper() {
        int v = add(1, 2);
        System.out.println(v);
    }
}
