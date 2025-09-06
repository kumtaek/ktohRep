#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os

def analyze_java_overextraction():
    """Java 파서 과추출 문제 분석"""
    
    print("=== Java 파서 과추출 문제 분석 ===\n")
    
    # 샘플 Java 파일 분석
    sample_file = "../project/sampleSrc/src/main/java/com/example/controller/OrderController.java"
    
    if not os.path.exists(sample_file):
        print(f"파일을 찾을 수 없습니다: {sample_file}")
        return
    
    with open(sample_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"분석 파일: {sample_file}")
    print(f"파일 크기: {len(content)} 문자\n")
    
    # 1. 실제 메소드 개수 (수동 분석)
    print("1. 실제 메소드 분석:")
    
    # 간단한 메소드 패턴 (과추출 방지)
    simple_method_pattern = r'(?:public|private|protected)\s+(?:static\s+)?(?:[\w<>\[\],\s?&\.]+\s+)?(\w+)\s*\([^)]*\)\s*\{'
    simple_methods = re.findall(simple_method_pattern, content, re.MULTILINE)
    
    print(f"   간단한 패턴으로 찾은 메소드: {len(simple_methods)}개")
    for i, method in enumerate(simple_methods[:10], 1):
        print(f"   {i}. {method}")
    
    # 2. 복잡한 메소드 패턴 (현재 파서가 사용하는 패턴과 유사)
    print(f"\n2. 복잡한 메소드 패턴 분석:")
    
    # 현재 파서의 메소드 패턴과 유사한 패턴
    complex_method_pattern = r'(?:@\w+(?:\([^)]*\))?\s*)*\s*(?:public|private|protected)?\s*(?:static|final|abstract|synchronized)?\s*(?:[\w<>\[\],\s?&\.]+\s+)?(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w\s,\.]+)?\s*[;{]'
    complex_methods = re.findall(complex_method_pattern, content, re.MULTILINE | re.DOTALL)
    
    print(f"   복잡한 패턴으로 찾은 메소드: {len(complex_methods)}개")
    for i, method in enumerate(complex_methods[:10], 1):
        print(f"   {i}. {method}")
    
    # 3. 클래스 분석
    print(f"\n3. 클래스 분석:")
    
    # 간단한 클래스 패턴
    simple_class_pattern = r'class\s+(\w+)'
    simple_classes = re.findall(simple_class_pattern, content)
    
    print(f"   간단한 패턴으로 찾은 클래스: {len(simple_classes)}개")
    for i, class_name in enumerate(simple_classes, 1):
        print(f"   {i}. {class_name}")
    
    # 4. 과추출 원인 분석
    print(f"\n4. 과추출 원인 분석:")
    
    # 생성자, 내부 클래스, 익명 클래스 등이 메소드로 잘못 인식되는지 확인
    constructor_pattern = r'(\w+)\s*\([^)]*\)\s*\{'
    constructors = re.findall(constructor_pattern, content, re.MULTILINE)
    
    print(f"   생성자/메소드로 인식될 수 있는 패턴: {len(constructors)}개")
    for i, constructor in enumerate(constructors[:10], 1):
        print(f"   {i}. {constructor}")
    
    # 5. SQL 문자열 분석
    print(f"\n5. SQL 문자열 분석:")
    
    # SQL 문자열 패턴
    sql_pattern = r'["\']([^"\']*(?:SELECT\s+|FROM\s+|WHERE\s+|JOIN\s+|UPDATE\s+|INSERT\s+|DELETE\s+|CREATE\s+|ALTER\s+|DROP\s+|TRUNCATE\s+|MERGE\s+)[^"\']*)["\']'
    sql_strings = re.findall(sql_pattern, content, re.IGNORECASE)
    
    print(f"   SQL 문자열: {len(sql_strings)}개")
    for i, sql in enumerate(sql_strings[:5], 1):
        print(f"   {i}. {sql[:50]}...")
    
    # 6. 과추출 문제 요약
    print(f"\n6. 과추출 문제 요약:")
    print(f"   - 간단한 메소드 패턴: {len(simple_methods)}개")
    print(f"   - 복잡한 메소드 패턴: {len(complex_methods)}개")
    print(f"   - 차이: {len(complex_methods) - len(simple_methods)}개 과추출")
    print(f"   - 과추출률: {((len(complex_methods) - len(simple_methods)) / len(simple_methods) * 100):.1f}%" if simple_methods else "0%")
    
    # 7. 개선 방안
    print(f"\n7. 개선 방안:")
    print(f"   - 메소드 패턴을 더 엄격하게 제한")
    print(f"   - 생성자와 메소드를 구분")
    print(f"   - 내부 클래스, 익명 클래스 제외")
    print(f"   - 어노테이션 처리 개선")
    print(f"   - SQL 문자열 패턴 정밀도 향상")

if __name__ == "__main__":
    analyze_java_overextraction()



