package com.example.web;

import com.example.service.OrderService;
import com.example.model.Order;
import com.example.model.OrderFilter;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;
import org.springframework.ui.Model;
import java.util.List;

@Controller
@RequestMapping("/orders")
public class OrderController {
    private final OrderService service;
    public OrderController(OrderService service) { this.service = service; }

    @GetMapping
    public String list(@RequestParam(required=false) String status,
                       @RequestParam(required=false) String from,
                       @RequestParam(required=false) String to,
                       @RequestParam(required=false) List<String> statuses,
                       Model model) {
        OrderFilter f = new OrderFilter();
        f.setStatus(status);
        f.setFrom(from);
        f.setTo(to);
        f.setStatuses(statuses);
        model.addAttribute("items", service.listByFilter(f));
        return "orders";
    }

    @GetMapping("/{id}")
    public String detail(@PathVariable("id") Long id, Model model) {
        Order o = service.findById(id);
        model.addAttribute("order", o);
        return "orderDetail";
    }

    @PostMapping
    public String create(Order o) {
        service.insertOrder(o);
        return "redirect:/orders";
    }

    @PostMapping("/{id}/status")
    public String changeStatus(@PathVariable("id") Long id, @RequestParam String status) {
        service.updateStatus(id, status);
        return "redirect:/orders/" + id;
    }
}
