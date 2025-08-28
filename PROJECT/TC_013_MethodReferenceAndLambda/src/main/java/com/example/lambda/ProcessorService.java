package com.example.lambda;

import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

public class ProcessorService {

    public List<String> processList(List<String> data) {
        MyUtil util = new MyUtil();
        return data.stream()
                   .map(MyUtil::transform) // Static method reference
                   .map(util::reverse) // Instance method reference
                   .collect(Collectors.toList());
    }

    public void executeAction(Runnable action) {
        action.run();
    }

    public void exampleLambda() {
        List<String> names = Arrays.asList("alice", "bob");
        names.forEach(name -> System.out.println(name.toUpperCase())); // Lambda expression

        executeAction(() -> {
            System.out.println("Lambda action executed.");
            MyUtil.transform("test"); // Call inside lambda
        });
    }
}