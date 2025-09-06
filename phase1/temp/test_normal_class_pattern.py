#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def test_normal_class_patterns():
    """정상적인 Java 파일로 클래스 패턴 테스트"""
    
    # 실제 UserController.java의 클래스 선언 부분
    test_content = """@Controller
@RequestMapping("/user")
public class UserController {
    
    @Autowired
    private UserService userService;"""
    
    print("=== 정상적인 Java 파일 테스트 내용 ===")
    print(test_content)
    print()
    
    # 현재 하이브리드 패턴의 클래스 패턴들
    class_patterns = [
        r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)\s*(?:extends\s+\w+)?\s*(?:implements\s+[\w\s,]+)?\s*\{(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?\s*\{',
        r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)\s*(?:extends\s+\w+)?\s*(?:implements\s+[\w\s,]+)?\s*\{(?:\s+extends\s+(\w+))?\s*\{',
        r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)\s*(?:extends\s+\w+)?\s*(?:implements\s+[\w\s,]+)?\s*\{\s*\{',
    ]
    
    print("=== 현재 패턴 테스트 (정상 파일) ===")
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
    
    print("=== 수정된 패턴 테스트 (정상 파일) ===")
    for i, pattern in enumerate(fixed_patterns, 1):
        print(f"수정 패턴 {i}: {pattern}")
        matches = list(re.finditer(pattern, test_content, re.IGNORECASE | re.DOTALL))
        print(f"  매치 수: {len(matches)}")
        for match in matches:
            print(f"  매치: {match.group()}")
            print(f"  클래스명: {match.group(1)}")
        print()
    
    # 전체 파일 내용으로 테스트
    print("=== 전체 파일 내용으로 테스트 ===")
    with open("project/sampleSrc/src/main/java/com/example/controller/UserController.java", "r", encoding="utf-8") as f:
        full_content = f.read()
    
    print("수정된 패턴 1로 전체 파일 테스트:")
    pattern = r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?\s*\{'
    matches = list(re.finditer(pattern, full_content, re.IGNORECASE | re.DOTALL))
    print(f"  매치 수: {len(matches)}")
    for match in matches:
        print(f"  매치: {match.group()}")
        print(f"  클래스명: {match.group(1)}")

if __name__ == "__main__":
    test_normal_class_patterns()
