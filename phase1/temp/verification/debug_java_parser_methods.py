#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
sys.path.append('phase1')

from phase1.parsers.java.java_parser import JavaParser

def debug_java_parser_methods():
    """Java 파서 메소드 추출 디버깅"""
    print("=== Java 파서 메소드 추출 디버깅 ===\n")
    
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
        
        # _extract_methods_aggressive 메소드를 직접 호출
        print("=== _extract_methods_aggressive 직접 호출 ===")
        
        # 정규화된 컨텐츠 생성
        normalized_content = parser._normalize_content(content)
        print(f"정규화된 컨텐츠 크기: {len(normalized_content)} bytes")
        print(f"정규화된 컨텐츠 첫 200자: {normalized_content[:200]}...")
        print()
        
        # 메소드 추출
        methods = parser._extract_methods_aggressive(normalized_content)
        print(f"추출된 메소드 수: {len(methods)}")
        
        for i, method in enumerate(methods):
            print(f"  {i+1}. {method.get('name', 'Unknown')} - {method.get('return_type', 'Unknown')}")
            print(f"     매개변수: {method.get('parameters', [])}")
            print(f"     수정자: {method.get('modifiers', [])}")
            print()
        
        # 정규식 패턴 직접 테스트
        print("=== 정규식 패턴 직접 테스트 ===")
        pattern = r'(?:@\w+(?:\([^)]*\))?\s*\n\s*)*(?:public|private|protected|static)\s+(\w+)\s+(\w+)\s*\(([^)]*)\)\s*\{'
        print(f"패턴: {pattern}")
        
        matches = re.finditer(pattern, normalized_content, re.IGNORECASE | re.DOTALL)
        match_list = list(matches)
        print(f"정규화된 컨텐츠에서 매치 수: {len(match_list)}")
        
        for i, match in enumerate(match_list[:3]):
            print(f"  {i+1}. {match.group(1)} {match.group(2)}({match.group(3)})")
        
        if len(match_list) > 3:
            print(f"  ... 외 {len(match_list)-3}개")
        
        # 원본 컨텐츠에서도 테스트
        print(f"\n원본 컨텐츠에서 매치 수: {len(list(re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)))}")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_java_parser_methods()

