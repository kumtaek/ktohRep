#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def test_simple_regex():
    """간단한 정규식 패턴 테스트"""
    print("=== 간단한 정규식 패턴 테스트 ===\n")
    
    # VulnerabilityTestService.java 파일 내용
    file_path = "project/sampleSrc/src/main/java/com/example/integrated/VulnerabilityTestService.java"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"파일: {file_path}")
        print(f"파일 크기: {len(content)} bytes")
        print()
        
        # 1. 가장 간단한 메소드 패턴 테스트
        print("=== 1. 가장 간단한 메소드 패턴 ===")
        simple_pattern = r'public\s+(\w+)\s+(\w+)\s*\(([^)]*)\)\s*\{'
        matches = re.findall(simple_pattern, content, re.IGNORECASE | re.DOTALL)
        print(f"패턴: {simple_pattern}")
        print(f"매치 수: {len(matches)}")
        for i, (return_type, method_name, params) in enumerate(matches[:5]):
            print(f"  {i+1}. {return_type} {method_name}({params})")
        if len(matches) > 5:
            print(f"  ... 외 {len(matches)-5}개")
        print()
        
        # 2. 어노테이션 포함 메소드 패턴
        print("=== 2. 어노테이션 포함 메소드 패턴 ===")
        annotation_pattern = r'(?:@\w+(?:\([^)]*\))?\s*\n\s*)*public\s+(\w+)\s+(\w+)\s*\(([^)]*)\)\s*\{'
        matches = re.findall(annotation_pattern, content, re.IGNORECASE | re.DOTALL)
        print(f"패턴: {annotation_pattern}")
        print(f"매치 수: {len(matches)}")
        for i, (return_type, method_name, params) in enumerate(matches[:5]):
            print(f"  {i+1}. {return_type} {method_name}({params})")
        if len(matches) > 5:
            print(f"  ... 외 {len(matches)-5}개")
        print()
        
        # 3. private/protected 메소드 포함
        print("=== 3. private/protected 메소드 포함 ===")
        visibility_pattern = r'(?:@\w+(?:\([^)]*\))?\s*\n\s*)*(?:public|private|protected)\s+(\w+)\s+(\w+)\s*\(([^)]*)\)\s*\{'
        matches = re.findall(visibility_pattern, content, re.IGNORECASE | re.DOTALL)
        print(f"패턴: {visibility_pattern}")
        print(f"매치 수: {len(matches)}")
        for i, (return_type, method_name, params) in enumerate(matches[:5]):
            print(f"  {i+1}. {return_type} {method_name}({params})")
        if len(matches) > 5:
            print(f"  ... 외 {len(matches)-5}개")
        print()
        
        # 4. static 메소드 포함
        print("=== 4. static 메소드 포함 ===")
        static_pattern = r'(?:@\w+(?:\([^)]*\))?\s*\n\s*)*(?:public|private|protected|static)\s+(\w+)\s+(\w+)\s*\(([^)]*)\)\s*\{'
        matches = re.findall(static_pattern, content, re.IGNORECASE | re.DOTALL)
        print(f"패턴: {static_pattern}")
        print(f"매치 수: {len(matches)}")
        for i, (return_type, method_name, params) in enumerate(matches[:5]):
            print(f"  {i+1}. {return_type} {method_name}({params})")
        if len(matches) > 5:
            print(f"  ... 외 {len(matches)-5}개")
        print()
        
        # 5. 생성자 패턴
        print("=== 5. 생성자 패턴 ===")
        class_name = "VulnerabilityTestService"
        constructor_pattern = r'(?:@\w+(?:\([^)]*\))?\s*\n\s*)*(?:public|private|protected)?\s+' + re.escape(class_name) + r'\s*\(([^)]*)\)\s*\{'
        matches = re.findall(constructor_pattern, content, re.IGNORECASE | re.DOTALL)
        print(f"패턴: {constructor_pattern}")
        print(f"매치 수: {len(matches)}")
        for i, params in enumerate(matches):
            print(f"  {i+1}. {class_name}({params})")
        print()
        
        # 6. 인터페이스 메소드 패턴
        print("=== 6. 인터페이스 메소드 패턴 ===")
        interface_pattern = r'(?:@\w+(?:\([^)]*\))?\s*\n\s*)*(?:public|private|protected|static|default)?\s*(\w+)\s+(\w+)\s*\(([^)]*)\)\s*;'
        matches = re.findall(interface_pattern, content, re.IGNORECASE | re.DOTALL)
        print(f"패턴: {interface_pattern}")
        print(f"매치 수: {len(matches)}")
        for i, (return_type, method_name, params) in enumerate(matches[:3]):
            print(f"  {i+1}. {return_type} {method_name}({params});")
        if len(matches) > 3:
            print(f"  ... 외 {len(matches)-3}개")
        print()
        
        # 7. 전체 합계
        print("=== 7. 전체 합계 ===")
        total_methods = 0
        
        # 일반 메소드
        general_pattern = r'(?:@\w+(?:\([^)]*\))?\s*\n\s*)*(?:public|private|protected|static)\s+(\w+)\s+(\w+)\s*\(([^)]*)\)\s*\{'
        general_matches = re.findall(general_pattern, content, re.IGNORECASE | re.DOTALL)
        total_methods += len(general_matches)
        
        # 생성자
        constructor_matches = re.findall(constructor_pattern, content, re.IGNORECASE | re.DOTALL)
        total_methods += len(constructor_matches)
        
        # 인터페이스 메소드
        interface_matches = re.findall(interface_pattern, content, re.IGNORECASE | re.DOTALL)
        total_methods += len(interface_matches)
        
        print(f"일반 메소드: {len(general_matches)}개")
        print(f"생성자: {len(constructor_matches)}개")
        print(f"인터페이스 메소드: {len(interface_matches)}개")
        print(f"총 메소드: {total_methods}개")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_regex()

