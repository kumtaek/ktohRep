package com.example.jsp;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

import java.util.ArrayList;
import java.util.List;

@Controller
public class JspController {

    @GetMapping("/dynamicSqlView")
    public String showDynamicSqlView(@RequestParam(value = "status", required = false) String status, Model model) {
        List<String> data = new ArrayList<>();
        if (status != null && !status.isEmpty()) {
            // Simulate fetching data based on status
            data.add("Item for status: " + status);
        } else {
            data.add("Default Item");
        }
        model.addAttribute("dataList", data);
        model.addAttribute("searchStatus", status);
        return "dynamicSqlView";
    }
}