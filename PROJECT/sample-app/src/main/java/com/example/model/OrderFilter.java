package com.example.model;
import java.util.List;
public class OrderFilter {
    private String status;
    private String from;
    private String to;
    private List<String> statuses;
    public String getStatus(){return status;} public void setStatus(String s){this.status=s;}
    public String getFrom(){return from;} public void setFrom(String f){this.from=f;}
    public String getTo(){return to;} public void setTo(String t){this.to=t;}
    public List<String> getStatuses(){return statuses;} public void setStatuses(List<String> s){this.statuses=s;}
}