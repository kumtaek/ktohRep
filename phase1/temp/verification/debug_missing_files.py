#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append('phase1')

from phase1.parsers.java.java_parser import JavaParser

def debug_missing_files():
    """누락된 파일들의 파싱 문제 디버깅"""
    print("=== 누락된 파일들의 파싱 문제 디버깅 ===\n")
    
    # 누락된 파일들
    missing_files = [
        "project/sampleSrc/src/main/java/com/example/integrated/VulnerabilityTestService.java",
        "project/sampleSrc/src/main/java/com/example/service/OrderService.java", 
        "project/sampleSrc/src/main/java/com/example/service/ProductService.java",
        "project/sampleSrc/src/main/java/com/example/service/UserService.java"
    ]
    
    # Java 파서 초기화
    config = {}
    parser = JavaParser(config)
    
    for file_path in missing_files:
        print(f"=== {file_path} ===")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"파일 크기: {len(content)} bytes")
            print(f"파일 존재: {os.path.exists(file_path)}")
            
            # 1. 클래스 추출 테스트
            print("\n1. 클래스 추출 테스트:")
            classes = parser._extract_classes_aggressive(content)
            print(f"추출된 클래스 수: {len(classes)}")
            for i, cls in enumerate(classes):
                print(f"  {i+1}. {cls.get('name', 'Unknown')}")
            
            # 2. 메소드 추출 테스트
            print("\n2. 메소드 추출 테스트:")
            methods = parser._extract_methods_aggressive(content)
            print(f"추출된 메소드 수: {len(methods)}")
            for i, method in enumerate(methods[:5]):  # 처음 5개만 출력
                print(f"  {i+1}. {method.get('name', 'Unknown')} ({method.get('return_type', 'Unknown')})")
            if len(methods) > 5:
                print(f"  ... 외 {len(methods) - 5}개")
            
            # 3. 파서 호환성 테스트
            print("\n3. 파서 호환성 테스트:")
            can_parse = parser.can_parse(file_path)
            print(f"can_parse: {can_parse}")
            
            # 4. 간단한 클래스 패턴 테스트
            print("\n4. 간단한 클래스 패턴 테스트:")
            import re
            simple_pattern = r'class\s+(\w+)\s*\{'
            matches = re.finditer(simple_pattern, content, re.IGNORECASE | re.DOTALL)
            match_list = list(matches)
            print(f"간단한 패턴 매치 수: {len(match_list)}")
            for j, match in enumerate(match_list):
                print(f"  {j+1}. {match.group(1)}")
            
            # 5. 간단한 메소드 패턴 테스트
            print("\n5. 간단한 메소드 패턴 테스트:")
            method_pattern = r'(public|private|protected)\s+[\w\<\>\[\]]+\s+(\w+)\s*\([^\)]*\)\s*\{'
            method_matches = re.finditer(method_pattern, content, re.IGNORECASE | re.DOTALL)
            method_list = list(method_matches)
            print(f"간단한 메소드 패턴 매치 수: {len(method_list)}")
            for j, match in enumerate(method_list[:5]):  # 처음 5개만 출력
                print(f"  {j+1}. {match.group(2)}")
            if len(method_list) > 5:
                print(f"  ... 외 {len(method_list) - 5}개")
            
        except Exception as e:
            print(f"오류 발생: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    debug_missing_files()

