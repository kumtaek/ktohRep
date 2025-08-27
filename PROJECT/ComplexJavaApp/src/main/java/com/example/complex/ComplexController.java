package com.example.complex;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ComplexController {

    private final ServiceImpl service;

    @Autowired
    public ComplexController(ServiceImpl service) {
        this.service = service;
    }

    @GetMapping("/process/{input}")
    public String handleProcess(@PathVariable String input) {
        String result = service.processData(input);
        int length = service.calculateLength(result);
        return result + " (Length: " + length + ")";
    }

    @GetMapping("/static/{value}")
    public String handleStatic(@PathVariable String value) {
        return ServiceImpl.staticHelper(value);
    }
}