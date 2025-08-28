package com.example.jspinclude;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class JspController {

    @GetMapping("/mainView")
    public String showMainView(Model model) {
        model.addAttribute("pageTitle", "Main Page");
        return "main"; // Renders main.jsp
    }
}