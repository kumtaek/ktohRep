package com.example.spring;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class MyController {

    private final MyService myService;

    @Autowired
    public MyController(MyService myService) {
        this.myService = myService;
    }

    @GetMapping("/hello/{name}")
    public String getHello(@PathVariable String name) {
        return myService.getServiceData(name);
    }

    @GetMapping("/greet")
    public String greet() {
        return "Greetings from MyController!";
    }
}