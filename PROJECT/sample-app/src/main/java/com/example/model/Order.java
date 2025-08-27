package com.example.model;
public class Order {
    private Long id;
    private Long customerId;
    private String status;
    private String createdAt;
    public Long getId(){return id;} public void setId(Long id){this.id=id;}
    public Long getCustomerId(){return customerId;} public void setCustomerId(Long c){this.customerId=c;}
    public String getStatus(){return status;} public void setStatus(String s){this.status=s;}
    public String getCreatedAt(){return createdAt;} public void setCreatedAt(String c){this.createdAt=c;}
}