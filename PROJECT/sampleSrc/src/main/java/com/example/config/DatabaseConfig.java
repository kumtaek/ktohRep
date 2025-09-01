package com.example.config;

import com.example.util.DateUtil;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Bean;

@Configuration
public class DatabaseConfig {
    
    @Bean
    public DateUtil dateUtil() {
        return new DateUtil();
    }
    
    public String getConnectionString() {
        DateUtil dateUtil = new DateUtil();
        String currentDate = dateUtil.getCurrentDate();
        return "jdbc:mysql://localhost:3306/mydb?created=" + currentDate;
    }
    
    public void initializeDatabase() {
        String connection = getConnectionString();
        // 데이터베이스 초기화 로직
    }
}