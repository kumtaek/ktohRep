#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os

def test_class_patterns():
    """클래스 패턴 테스트 - 오류 파일 vs 정상 파일"""
    
    print("=== 클래스 패턴 테스트 (오류 파일 vs 정상 파일) ===\n")
    
    # 1. 정상 파일 테스트
    print("=== 1. 정상 파일 (UserController.java) ===")
    normal_file = "project/sampleSrc/src/main/java/com/example/controller/UserController.java"
    
    if os.path.exists(normal_file):
        with open(normal_file, 'r', encoding='utf-8') as f:
            normal_content = f.read()
        
        print(f"파일 크기: {len(normal_content)} 문자")
        
        # 클래스 선언 부분 추출
        class_match = re.search(r'public class (\w+)', normal_content)
        if class_match:
            print(f"클래스명: {class_match.group(1)}")
            print(f"클래스 선언: {class_match.group(0)}")
        
        # 현재 하이브리드 패턴 테스트
        current_pattern = r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)\s*(?:extends\s+\w+)?\s*(?:implements\s+[\w\s,]+)?\s*\{(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?\s*\{'
        matches = list(re.finditer(current_pattern, normal_content, re.IGNORECASE | re.DOTALL))
        print(f"현재 패턴 매치 수: {len(matches)}")
        
        # 수정된 패턴 테스트
        fixed_pattern = r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?\s*\{'
        matches = list(re.finditer(fixed_pattern, normal_content, re.IGNORECASE | re.DOTALL))
        print(f"수정 패턴 매치 수: {len(matches)}")
        
        if matches:
            for match in matches:
                print(f"  매치: {match.group()}")
                print(f"  클래스명: {match.group(1)}")
    else:
        print(f"❌ 파일을 찾을 수 없음: {normal_file}")
    
    print()
    
    # 2. 오류가 있는 파일 테스트
    print("=== 2. 오류가 있는 파일 (ErrorController.java) ===")
    error_file = "project/sampleSrc/src/main/java/com/example/controller/ErrorController.java"
    
    if os.path.exists(error_file):
        with open(error_file, 'r', encoding='utf-8') as f:
            error_content = f.read()
        
        print(f"파일 크기: {len(error_content)} 문자")
        
        # 클래스 선언 부분 추출
        class_match = re.search(r'public class (\w+)', error_content)
        if class_match:
            print(f"클래스명: {class_match.group(1)}")
            print(f"클래스 선언: {class_match.group(0)}")
        
        # 현재 하이브리드 패턴 테스트
        current_pattern = r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)\s*(?:extends\s+\w+)?\s*(?:implements\s+[\w\s,]+)?\s*\{(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?\s*\{'
        matches = list(re.finditer(current_pattern, error_content, re.IGNORECASE | re.DOTALL))
        print(f"현재 패턴 매치 수: {len(matches)}")
        
        # 수정된 패턴 테스트
        fixed_pattern = r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?\s*\{'
        matches = list(re.finditer(fixed_pattern, error_content, re.IGNORECASE | re.DOTALL))
        print(f"수정 패턴 매치 수: {len(matches)}")
        
        if matches:
            for match in matches:
                print(f"  매치: {match.group()}")
                print(f"  클래스명: {match.group(1)}")
    else:
        print(f"❌ 파일을 찾을 수 없음: {error_file}")
    
    print()
    
    # 3. 결론
    print("=== 3. 결론 ===")
    print("문제 원인: 하이브리드 패턴의 클래스 패턴에서 중괄호가 두 번 나타나야 매치됨")
    print("해결 방법: 클래스 패턴을 수정하여 중괄호 하나만 매치하도록 변경")
    print("영향: 정상 파일과 오류 파일 모두 클래스 추출 실패")

if __name__ == "__main__":
    test_class_patterns()
