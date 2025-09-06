#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
sys.path.append('phase1')

from parsers.java.java_parser import JavaParser

def test_class_extraction():
    """클래스 추출 테스트"""
    print("=== 클래스 추출 테스트 ===\n")
    
    # Java 파서 초기화
    config = {}
    parser = JavaParser(config)
    
    # VulnerabilityTestService.java 파일 테스트
    file_path = "project/sampleSrc/src/main/java/com/example/integrated/VulnerabilityTestService.java"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"파일: {file_path}")
        print(f"파일 크기: {len(content)} bytes")
        print()
        
        # 클래스 추출 직접 테스트
        print("=== 클래스 추출 직접 테스트 ===")
        classes = parser._extract_classes_aggressive(content)
        print(f"추출된 클래스 수: {len(classes)}")
        
        for i, cls in enumerate(classes):
            print(f"  {i+1}. {cls.get('name', 'Unknown')}")
            print(f"     상속: {cls.get('extends', 'None')}")
            print(f"     구현: {cls.get('implements', [])}")
            print()
        
        # 정규식 패턴 직접 테스트
        print("=== 정규식 패턴 직접 테스트 ===")
        class_patterns = [
            r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?\s*\{',
            r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{',
            r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)\s*\{',
        ]
        
        for i, pattern in enumerate(class_patterns, 1):
            print(f"패턴 {i}: {pattern}")
            matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
            match_list = list(matches)
            print(f"매치 수: {len(match_list)}")
            
            for j, match in enumerate(match_list):
                print(f"  {j+1}. {match.group(1)}")
                if len(match.groups()) > 1 and match.group(2):
                    print(f"     상속: {match.group(2)}")
                if len(match.groups()) > 2 and match.group(3):
                    print(f"     구현: {match.group(3)}")
            print()
        
        # 간단한 클래스 패턴 테스트
        print("=== 간단한 클래스 패턴 테스트 ===")
        simple_pattern = r'class\s+(\w+)\s*\{'
        matches = re.finditer(simple_pattern, content, re.IGNORECASE | re.DOTALL)
        match_list = list(matches)
        print(f"간단한 패턴 매치 수: {len(match_list)}")
        
        for j, match in enumerate(match_list):
            print(f"  {j+1}. {match.group(1)}")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_class_extraction()

