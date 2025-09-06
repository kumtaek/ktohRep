#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import re
sys.path.append('..')
sys.path.append('../phase1')

from parsers.java.java_parser import JavaParser
import yaml

def test_error_vs_normal_files():
    """오류가 있는 파일과 정상 파일 비교 테스트"""
    
    print("=== 오류 파일 vs 정상 파일 파싱 비교 테스트 ===\n")
    
    # Config 로드
    config_path = "../phase1/config/config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Java 파서 초기화
    java_parser = JavaParser(config)
    
    # 1. 정상 파일 테스트 (UserController.java)
    print("=== 1. 정상 파일 테스트 (UserController.java) ===")
    normal_file = "../project/sampleSrc/src/main/java/com/example/controller/UserController.java"
    
    try:
        with open(normal_file, 'r', encoding='utf-8') as f:
            normal_content = f.read()
        
        print(f"파일 크기: {len(normal_content)} 문자")
        print(f"클래스 선언: {'public class UserController {' in normal_content}")
        
        result = java_parser.parse_content(normal_content, normal_file)
        print(f"파싱 결과:")
        print(f"  - 클래스 수: {len(result.get('classes', []))}")
        print(f"  - 메서드 수: {len(result.get('methods', []))}")
        print(f"  - SQL 유닛 수: {len(result.get('sql_units', []))}")
        
        if result.get('classes'):
            for cls in result['classes']:
                print(f"  - 클래스: {cls.get('name', 'Unknown')}")
        
        if result.get('methods'):
            for method in result['methods'][:3]:  # 처음 3개만
                print(f"  - 메서드: {method.get('name', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ 정상 파일 파싱 실패: {e}")
    
    print()
    
    # 2. 오류가 있는 파일 테스트 (ErrorController.java)
    print("=== 2. 오류가 있는 파일 테스트 (ErrorController.java) ===")
    error_file = "../project/sampleSrc/src/main/java/com/example/controller/ErrorController.java"
    
    try:
        with open(error_file, 'r', encoding='utf-8') as f:
            error_content = f.read()
        
        print(f"파일 크기: {len(error_content)} 문자")
        print(f"클래스 선언: {'public class ErrorController {' in error_content}")
        
        result = java_parser.parse_content(error_content, error_file)
        print(f"파싱 결과:")
        print(f"  - 클래스 수: {len(result.get('classes', []))}")
        print(f"  - 메서드 수: {len(result.get('methods', []))}")
        print(f"  - SQL 유닛 수: {len(result.get('sql_units', []))}")
        
        if result.get('classes'):
            for cls in result['classes']:
                print(f"  - 클래스: {cls.get('name', 'Unknown')}")
        
        if result.get('methods'):
            for method in result['methods'][:3]:  # 처음 3개만
                print(f"  - 메서드: {method.get('name', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ 오류 파일 파싱 실패: {e}")
    
    print()
    
    # 3. 클래스 패턴 직접 테스트
    print("=== 3. 클래스 패턴 직접 테스트 ===")
    
    # 정상 파일의 클래스 선언 부분
    normal_class_declaration = "public class UserController {"
    error_class_declaration = "public class ErrorController {"
    
    # 현재 하이브리드 패턴
    current_pattern = r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)\s*(?:extends\s+\w+)?\s*(?:implements\s+[\w\s,]+)?\s*\{(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?\s*\{'
    
    print(f"현재 패턴: {current_pattern}")
    print(f"정상 파일 매치: {bool(re.search(current_pattern, normal_class_declaration))}")
    print(f"오류 파일 매치: {bool(re.search(current_pattern, error_class_declaration))}")
    
    # 수정된 패턴
    fixed_pattern = r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?\s*\{'
    
    print(f"수정 패턴: {fixed_pattern}")
    print(f"정상 파일 매치: {bool(re.search(fixed_pattern, normal_class_declaration))}")
    print(f"오류 파일 매치: {bool(re.search(fixed_pattern, error_class_declaration))}")

if __name__ == "__main__":
    test_error_vs_normal_files()
