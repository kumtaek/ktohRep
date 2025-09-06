#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def test_class_patterns():
    """클래스 패턴 테스트"""
    
    # 실제 ErrorController.java의 클래스 선언 부분
    test_content = """@Controller
@RequestMapping("/error")
public class ErrorController {
    
    @Autowired
    private UserService userService;"""
    
    print("=== 테스트 내용 ===")
    print(test_content)
    print()
    
    # 현재 하이브리드 패턴의 클래스 패턴들
    class_patterns = [
        r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)\s*(?:extends\s+\w+)?\s*(?:implements\s+[\w\s,]+)?\s*\{(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?\s*\{',
        r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)\s*(?:extends\s+\w+)?\s*(?:implements\s+[\w\s,]+)?\s*\{(?:\s+extends\s+(\w+))?\s*\{',
        r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)\s*(?:extends\s+\w+)?\s*(?:implements\s+[\w\s,]+)?\s*\{\s*\{',
    ]
    
    print("=== 현재 패턴 테스트 ===")
    for i, pattern in enumerate(class_patterns, 1):
        print(f"패턴 {i}: {pattern}")
        matches = list(re.finditer(pattern, test_content, re.IGNORECASE | re.DOTALL))
        print(f"  매치 수: {len(matches)}")
        for match in matches:
            print(f"  매치: {match.group()}")
            print(f"  클래스명: {match.group(1)}")
        print()
    
    # 수정된 패턴들
    fixed_patterns = [
        r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?\s*\{',
        r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{',
        r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)\s*\{',
    ]
    
    print("=== 수정된 패턴 테스트 ===")
    for i, pattern in enumerate(fixed_patterns, 1):
        print(f"수정 패턴 {i}: {pattern}")
        matches = list(re.finditer(pattern, test_content, re.IGNORECASE | re.DOTALL))
        print(f"  매치 수: {len(matches)}")
        for match in matches:
            print(f"  매치: {match.group()}")
            print(f"  클래스명: {match.group(1)}")
        print()

if __name__ == "__main__":
    test_class_patterns()
