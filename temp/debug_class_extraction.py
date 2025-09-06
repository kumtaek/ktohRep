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

# 현재 fallback 패턴
current_pattern = re.compile(
    r'(?:public|private|protected|abstract|final|static\s+)*class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w\s,]+))?',
    re.IGNORECASE
)

print("=== 클래스 추출 원인 분석 ===")
print(f"파일 내용 길이: {len(content)} 문자")
print()

# 현재 패턴으로 테스트
matches = current_pattern.finditer(content)
match_count = 0
for match in matches:
    match_count += 1
    print(f"매치 {match_count}: {match.group(0)}")
    print(f"  클래스명: {match.group(1)}")
    print(f"  extends: {match.group(2) if match.group(2) else 'None'}")
    print(f"  implements: {match.group(3) if match.group(3) else 'None'}")
    print()

if match_count == 0:
    print("❌ 현재 패턴으로는 클래스를 찾을 수 없습니다.")
    print()
    print("=== 원인 분석 ===")
    print("실제 클래스 선언:")
    print("@Controller")
    print("@RequestMapping(\"/user\")")
    print("public class UserController {")
    print()
    print("현재 패턴의 문제점:")
    print("1. 어노테이션(@Controller, @RequestMapping)을 고려하지 않음")
    print("2. static\\s+ 패턴이 잘못됨 (static 뒤에 공백이 있어야 함)")
    print("3. 어노테이션과 클래스 선언 사이의 공백/줄바꿈을 고려하지 않음")
else:
    print(f"✅ {match_count}개 클래스 발견")

