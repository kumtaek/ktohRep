import re

# UserController.java 내용
content = """package com.example.controller;

import com.example.model.User;
import com.example.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@Controller
@RequestMapping("/user")
public class UserController {
    
    @Autowired
    private UserService userService;
    
    @GetMapping("/list")
    public String getUserList(@RequestParam(required = false) String name,
                             @RequestParam(required = false) String email,
                             @RequestParam(required = false) String status,
                             Model model) {
        
        // 다이나믹 쿼리 파라미터 구성
        Map<String, Object> params = new java.util.HashMap<>();
        if (name != null && !name.trim().isEmpty()) {
            params.put("name", "%" + name + "%");
        }
        if (email != null && !email.trim().isEmpty()) {
            params.put("email", "%" + email + "%");
        }
        if (status != null && !status.trim().isEmpty()) {
            params.put("status", status);
        }
        
        List<User> users = userService.getUsersByCondition(params);
        model.addAttribute("users", users);
        model.addAttribute("searchParams", params);
        
        return "user/list";
    }
    
    @PostMapping("/search")
    public String searchUsers(@RequestParam Map<String, String> searchParams, Model model) {
        
        // 복잡한 다이나믹 쿼리 조건 구성
        Map<String, Object> params = new java.util.HashMap<>();
        
        if (searchParams.get("userType") != null) {
            params.put("userType", searchParams.get("userType"));
        }
        
        if (searchParams.get("minAge") != null && !searchParams.get("minAge").isEmpty()) {
            params.put("minAge", Integer.parseInt(searchParams.get("minAge")));
        }
        
        if (searchParams.get("maxAge") != null && !searchParams.get("maxAge").isEmpty()) {
            params.put("maxAge", Integer.parseInt(searchParams.get("maxAge")));
        }
        
        // 날짜 범위 검색
        if (searchParams.get("startDate") != null && !searchParams.get("startDate").isEmpty()) {
            params.put("startDate", searchParams.get("startDate"));
        }
        
        if (searchParams.get("endDate") != null && !searchParams.get("endDate").isEmpty()) {
            params.put("endDate", searchParams.get("endDate"));
        }
        
        List<User> users = userService.getUsersByAdvancedCondition(params);
        model.addAttribute("users", users);
        model.addAttribute("searchParams", searchParams);
        
        return "user/searchResult";
    }
    
    @GetMapping("/dynamic/{type}")
    public String getUsersByType(@PathVariable String type, Model model) {
        
        // 타입별 다이나믹 쿼리
        List<User> users = userService.getUsersByType(type);
        model.addAttribute("users", users);
        model.addAttribute("userType", type);
        
        return "user/typeList";
    }
}"""

print("=== Aggressive 클래스 패턴 테스트 ===")

# 현재 aggressive 패턴들
class_patterns = [
    r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)\s*(?:extends\s+\w+)?\s*(?:implements\s+[\w\s,]+)?\s*\{(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?\s*\{',
    r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)\s*(?:extends\s+\w+)?\s*(?:implements\s+[\w\s,]+)?\s*\{(?:\s+extends\s+(\w+))?\s*\{',
    r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)\s*(?:extends\s+\w+)?\s*(?:implements\s+[\w\s,]+)?\s*\{\s*\{',
]

for i, pattern in enumerate(class_patterns):
    print(f"\n패턴 {i+1}: {pattern}")
    matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
    match_count = 0
    for match in matches:
        match_count += 1
        print(f"  매치 {match_count}: {match.group(0)[:50]}...")
        print(f"  클래스명: {match.group(1)}")
    if match_count == 0:
        print("  ❌ 매치 없음")

# 간단한 패턴으로 테스트
print(f"\n=== 간단한 패턴 테스트 ===")
simple_pattern = r'class\s+(\w+)\s*\{'
matches = re.finditer(simple_pattern, content, re.IGNORECASE)
match_count = 0
for match in matches:
    match_count += 1
    print(f"매치 {match_count}: {match.group(0)}")
    print(f"클래스명: {match.group(1)}")

if match_count == 0:
    print("❌ 간단한 패턴으로도 매치 없음")
else:
    print(f"✅ 간단한 패턴으로 {match_count}개 클래스 발견")

