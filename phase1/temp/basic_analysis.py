#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import glob

def count_java_methods_basic(file_path):
    """Java 파일의 메소드 개수 계산 (기본 방식)"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 간단한 메소드 패턴
        method_pattern = r'(?:public|private|protected|static|\s)*\s*(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?(?:abstract\s+)?(?:native\s+)?(?:strictfp\s+)?(?:transient\s+)?(?:volatile\s+)?(?:[a-zA-Z_][a-zA-Z0-9_<>\[\],\s]*\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*(?:throws\s+[^{]+)?\s*\{'
        
        methods = re.findall(method_pattern, content, re.MULTILINE | re.DOTALL)
        
        # 생성자도 포함
        class_name = os.path.basename(file_path).replace('.java', '')
        constructor_pattern = rf'(?:public|private|protected)\s+{re.escape(class_name)}\s*\('
        constructors = re.findall(constructor_pattern, content)
        
        # 인터페이스 메소드
        interface_method_pattern = r'(?:public|private|protected|static|\s)*\s*(?:static\s+)?(?:default\s+)?(?:[a-zA-Z_][a-zA-Z0-9_<>\[\],\s]*\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*(?:throws\s+[^;]+)?\s*;'
        interface_methods = re.findall(interface_method_pattern, content, re.MULTILINE | re.DOTALL)
        
        total_methods = len(methods) + len(constructors) + len(interface_methods)
        
        return total_methods, methods, constructors, interface_methods
        
    except Exception as e:
        print(f"Java 파일 읽기 오류 {file_path}: {e}")
        return 0, [], [], []

def count_xml_queries_basic(file_path):
    """XML 파일의 SQL 쿼리 개수 계산 (기본 방식)"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        sql_tags = ['select', 'insert', 'update', 'delete']
        total_queries = 0
        query_details = []
        
        for tag in sql_tags:
            pattern = rf'<{tag}\s+[^>]*id\s*=\s*["\'][^"\']*["\'][^>]*>'
            matches = re.findall(pattern, content, re.IGNORECASE)
            total_queries += len(matches)
            query_details.extend([(tag, match) for match in matches])
        
        return total_queries, query_details
        
    except Exception as e:
        print(f"XML 파일 읽기 오류 {file_path}: {e}")
        return 0, []

def count_jsp_functions_basic(file_path):
    """JSP 파일의 함수/스크립트 개수 계산 (기본 방식)"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # JavaScript 함수
        js_function_pattern = r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        js_functions = re.findall(js_function_pattern, content)
        
        # JSP 스크립트릿
        scriptlet_pattern = r'<%[^%]*%>'
        scriptlets = re.findall(scriptlet_pattern, content)
        
        # JSP 표현식
        expression_pattern = r'<%=.*?%>'
        expressions = re.findall(expression_pattern, content)
        
        total_scripts = len(js_functions) + len(scriptlets) + len(expressions)
        
        return total_scripts, js_functions, scriptlets, expressions
        
    except Exception as e:
        print(f"JSP 파일 읽기 오류 {file_path}: {e}")
        return 0, [], [], []

def analyze_basic():
    """기본 구성요소 분석"""
    project_path = "project/sampleSrc/src"
    
    print("=== 중복제거된 구성요소 수동 분석 ===\n")
    
    # Java 파일 분석
    print("=== Java 파일 메소드 분석 ===")
    java_files = glob.glob(f"{project_path}/**/*.java", recursive=True)
    java_total_methods = 0
    java_details = []
    
    for java_file in java_files:
        relative_path = os.path.relpath(java_file, project_path)
        method_count, methods, constructors, interface_methods = count_java_methods_basic(java_file)
        java_total_methods += method_count
        java_details.append((relative_path, method_count, methods, constructors, interface_methods))
        print(f"{relative_path}: {method_count}개 메소드")
    
    print(f"\nJava 총 메소드 수: {java_total_methods}개")
    
    # XML 파일 분석
    print("\n=== XML 파일 쿼리 분석 ===")
    xml_files = glob.glob(f"{project_path}/**/*.xml", recursive=True)
    xml_total_queries = 0
    xml_details = []
    
    for xml_file in xml_files:
        relative_path = os.path.relpath(xml_file, project_path)
        query_count, query_details = count_xml_queries_basic(xml_file)
        xml_total_queries += query_count
        xml_details.append((relative_path, query_count, query_details))
        print(f"{relative_path}: {query_count}개 쿼리")
    
    print(f"\nXML 총 쿼리 수: {xml_total_queries}개")
    
    # JSP 파일 분석
    print("\n=== JSP 파일 함수/스크립트 분석 ===")
    jsp_files = glob.glob(f"{project_path}/**/*.jsp", recursive=True)
    jsp_total_functions = 0
    jsp_details = []
    
    for jsp_file in jsp_files:
        relative_path = os.path.relpath(jsp_file, project_path)
        script_count, js_functions, scriptlets, expressions = count_jsp_functions_basic(jsp_file)
        jsp_total_functions += script_count
        jsp_details.append((relative_path, script_count, js_functions, scriptlets, expressions))
        print(f"{relative_path}: {script_count}개 함수/스크립트")
    
    print(f"\nJSP 총 함수/스크립트 수: {jsp_total_functions}개")
    
    # 전체 요약
    print("\n=== 전체 요약 ===")
    print(f"Java 메소드: {java_total_methods}개")
    print(f"XML 쿼리: {xml_total_queries}개")
    print(f"JSP 함수/스크립트: {jsp_total_functions}개")
    print(f"총 구성요소: {java_total_methods + xml_total_queries + jsp_total_functions}개")
    
    return {
        'java_total': java_total_methods,
        'xml_total': xml_total_queries,
        'jsp_total': jsp_total_functions,
        'java_details': java_details,
        'xml_details': xml_details,
        'jsp_details': jsp_details
    }

if __name__ == "__main__":
    result = analyze_basic()

