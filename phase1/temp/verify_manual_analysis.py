#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import glob

def verify_manual_analysis():
    """수동 분석 결과를 실제 파일로 검증"""
    project_path = "project/sampleSrc/src"
    
    print("=== 수동 분석 검증 ===\n")
    
    # 가장 문제가 많은 파일들부터 검증
    problem_files = [
        "main/java/com/example/controller/OrderController.java",
        "main/java/com/example/controller/PaymentController.java", 
        "main/java/com/example/integrated/VulnerabilityTestService.java"
    ]
    
    for file_path in problem_files:
        full_path = os.path.join(project_path, file_path)
        if not os.path.exists(full_path):
            print(f"❌ 파일 없음: {file_path}")
            continue
            
        print(f"📁 {file_path}")
        print("=" * 80)
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 실제 메소드들을 찾아서 출력
            print("🔍 실제 메소드들:")
            
            # 1. 일반 메소드 (어노테이션 포함)
            method_pattern = r'(?:@\w+(?:\([^)]*\))?\s*\n\s*)*(?:public|private|protected|static|final|abstract|synchronized|native|strictfp)?\s*(?:<[^>]+>\s+)?(\w+)\s+(\w+)\s*\(([^)]*)\)\s*(?:throws\s+([^{]+))?\s*\{'
            methods = re.findall(method_pattern, content, re.IGNORECASE | re.DOTALL)
            
            print(f"   일반 메소드: {len(methods)}개")
            for i, (return_type, method_name, params, throws) in enumerate(methods[:5]):  # 처음 5개만 출력
                print(f"     {i+1}. {return_type} {method_name}({params})")
            if len(methods) > 5:
                print(f"     ... 외 {len(methods)-5}개")
            
            # 2. 생성자
            class_name = os.path.basename(full_path).replace('.java', '')
            constructor_pattern = r'(?:@\w+(?:\([^)]*\))?\s*\n\s*)*(?:public|private|protected)?\s+' + re.escape(class_name) + r'\s*\(([^)]*)\)\s*(?:throws\s+([^{]+))?\s*\{'
            constructors = re.findall(constructor_pattern, content, re.IGNORECASE | re.DOTALL)
            
            print(f"   생성자: {len(constructors)}개")
            for i, (params, throws) in enumerate(constructors):
                print(f"     {i+1}. {class_name}({params})")
            
            # 3. 인터페이스 메소드 (세미콜론으로 끝나는)
            interface_pattern = r'(?:@\w+(?:\([^)]*\))?\s*\n\s*)*(?:public|private|protected|static|default)?\s*(?:<[^>]+>\s+)?(\w+)\s+(\w+)\s*\(([^)]*)\)\s*(?:throws\s+([^;]+))?\s*;'
            interface_methods = re.findall(interface_pattern, content, re.IGNORECASE | re.DOTALL)
            
            print(f"   인터페이스 메소드: {len(interface_methods)}개")
            for i, (return_type, method_name, params, throws) in enumerate(interface_methods[:3]):  # 처음 3개만 출력
                print(f"     {i+1}. {return_type} {method_name}({params});")
            if len(interface_methods) > 3:
                print(f"     ... 외 {len(interface_methods)-3}개")
            
            total_count = len(methods) + len(constructors) + len(interface_methods)
            print(f"\n   📊 총 메소드/생성자/인터페이스: {total_count}개")
            
            # 4. 특수한 패턴들 확인
            print(f"\n🔍 특수 패턴 분석:")
            
            # 어노테이션 메소드들
            annotation_methods = re.findall(r'@(\w+).*?\n.*?(\w+)\s+(\w+)\s*\(', content, re.MULTILINE | re.DOTALL)
            if annotation_methods:
                print(f"   어노테이션 메소드: {len(annotation_methods)}개")
                for annotation, return_type, method_name in annotation_methods[:3]:
                    print(f"     @{annotation} {return_type} {method_name}()")
                if len(annotation_methods) > 3:
                    print(f"     ... 외 {len(annotation_methods)-3}개")
            
            # static 메소드들
            static_methods = re.findall(r'static\s+(\w+)\s+(\w+)\s*\(', content)
            if static_methods:
                print(f"   static 메소드: {len(static_methods)}개")
                for return_type, method_name in static_methods[:3]:
                    print(f"     static {return_type} {method_name}()")
                if len(static_methods) > 3:
                    print(f"     ... 외 {len(static_methods)-3}개")
            
            print("\n" + "="*80 + "\n")
            
        except Exception as e:
            print(f"❌ 파일 읽기 오류: {e}\n")

if __name__ == "__main__":
    verify_manual_analysis()
