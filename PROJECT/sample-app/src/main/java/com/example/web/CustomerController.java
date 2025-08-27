package com.example.web;

import com.example.service.CustomerService;
import com.example.model.Customer;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.ui.Model;
import java.util.List;

@Controller
@RequestMapping("/customers")
public class CustomerController {
    private final CustomerService service;
    public CustomerController(CustomerService service) { this.service = service; }

    @GetMapping
    public String list(Model model) {
        List<Customer> items = service.findAll();
        model.addAttribute("items", items);
        return "customers";
    }

    @PostMapping("/add")
    public String add(Customer c) {
        service.insert(c);
        return "redirect:/customers";
    }
}
