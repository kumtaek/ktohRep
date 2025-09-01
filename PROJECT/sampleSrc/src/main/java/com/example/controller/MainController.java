package com.example.controller;

import com.example.service.UserService;
import com.example.service.OrderService;
import com.example.service.ProductService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

@RestController
public class MainController {
    
    @Autowired
    private UserService userService;
    
    @Autowired
    private OrderService orderService;
    
    @Autowired
    private ProductService productService;
    
    @GetMapping("/")
    public String home() {
        return "Hello World!";
    }
    
    @GetMapping("/users")
    public String getUsers(@RequestParam String userId) {
        return userService.getUserById(userId);
    }
    
    @PostMapping("/orders")
    public String createOrder(@RequestParam String userId, @RequestParam String productId) {
        // 사용자 정보 확인
        String user = userService.getUserById(userId);
        
        // 제품 정보 확인
        String product = productService.getProductDetails(productId);
        
        // 주문 생성
        return orderService.calculateOrderTotal(userId);
    }
    
    @GetMapping("/dashboard")
    public String dashboard() {
        userService.getActiveUsers();
        orderService.generateOrderReport("ACTIVE");
        productService.getProductList();
        return "dashboard";
    }
}