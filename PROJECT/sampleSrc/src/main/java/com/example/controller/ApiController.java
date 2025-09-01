package com.example.controller;

import com.example.service.UserService;
import com.example.service.ProductService;
import com.example.integrated.IntegratedService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;

@RestController
@RequestMapping("/api")
public class ApiController {
    
    @Autowired
    private UserService userService;
    
    @Autowired  
    private ProductService productService;
    
    @Autowired
    private IntegratedService integratedService;
    
    @GetMapping("/health")
    public String healthCheck() {
        return "OK";
    }
    
    @PostMapping("/process")
    public String processData(@RequestBody String data) {
        // 통합 서비스 시작
        integratedService.startProcess();
        
        // 복잡한 비즈니스 로직 처리
        productService.processComplexBusiness(data);
        
        // 사용자 데이터 동적 처리
        userService.getDynamicUserData(data);
        
        return "processed";
    }
    
    @GetMapping("/reports")
    public String generateReports() {
        integratedService.doWork();
        userService.processWithReflection("report");
        return "reports generated";
    }
}