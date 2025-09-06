#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import glob

def extract_java_methods_simple(file_path):
    """Java 파일에서 메소드 추출 (간단한 방식)"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        methods = []
        
        # 메소드 패턴: return_type method_name(parameters) {
        method_pattern = r'(?:public|private|protected|static|\s)*\s*(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?(?:abstract\s+)?(?:native\s+)?(?:strictfp\s+)?(?:transient\s+)?(?:volatile\s+)?(?:[a-zA-Z_][a-zA-Z0-9_<>\[\],\s]*\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*(?:throws\s+[^{]+)?\s*\{'
        
        for match in re.finditer(method_pattern, content, re.MULTILINE | re.DOTALL):
            method_name = match.group(1)
            methods.append({
                'name': method_name,
                'type': 'method'
            })
        
        # 생성자
        class_name = os.path.basename(file_path).replace('.java', '')
        constructor_pattern = rf'(?:public|private|protected)\s+{re.escape(class_name)}\s*\([^)]*\)\s*(?:throws\s+[^{]+)?\s*\{'
        
        for match in re.finditer(constructor_pattern, content):
            methods.append({
                'name': class_name,
                'type': 'constructor'
            })
        
        # 인터페이스 메소드
        interface_method_pattern = r'(?:public|private|protected|static|\s)*\s*(?:static\s+)?(?:default\s+)?(?:[a-zA-Z_][a-zA-Z0-9_<>\[\],\s]*\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*(?:throws\s+[^;]+)?\s*;'
        
        for match in re.finditer(interface_method_pattern, content, re.MULTILINE | re.DOTALL):
            method_name = match.group(1)
            methods.append({
                'name': method_name,
                'type': 'interface_method'
            })
        
        # 중복 제거 (같은 이름의 메소드는 하나로)
        unique_methods = {}
        for method in methods:
            key = method['name']
            if key not in unique_methods:
                unique_methods[key] = method
        
        return list(unique_methods.values())
        
    except Exception as e:
        print(f"Java 파일 읽기 오류 {file_path}: {e}")
        return []

def extract_xml_queries_simple(file_path):
    """XML 파일에서 SQL 쿼리 추출 (간단한 방식)"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        queries = []
        sql_tags = ['select', 'insert', 'update', 'delete']
        
        for tag in sql_tags:
            pattern = rf'<{tag}\s+[^>]*id\s*=\s*["\']([^"\']*)["\'][^>]*>'
            
            for match in re.finditer(pattern, content, re.IGNORECASE):
                query_id = match.group(1)
                queries.append({
                    'id': query_id,
                    'tag': tag,
                    'type': 'sql_query'
                })
        
        # 중복 제거 (같은 id의 쿼리는 하나로)
        unique_queries = {}
        for query in queries:
            key = query['id']
            if key not in unique_queries:
                unique_queries[key] = query
        
        return list(unique_queries.values())
        
    except Exception as e:
        print(f"XML 파일 읽기 오류 {file_path}: {e}")
        return []

def extract_jsp_functions_simple(file_path):
    """JSP 파일에서 함수/스크립트 추출 (간단한 방식)"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        functions = []
        
        # JavaScript 함수
        js_function_pattern = r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*\{'
        
        for match in re.finditer(js_function_pattern, content):
            func_name = match.group(1)
            functions.append({
                'name': func_name,
                'type': 'javascript_function'
            })
        
        # JSP 스크립트릿
        scriptlet_pattern = r'<%([^%]*)%>'
        scriptlet_count = 0
        
        for match in re.finditer(scriptlet_pattern, content):
            scriptlet_content = match.group(1).strip()
            if scriptlet_content:
                scriptlet_count += 1
                functions.append({
                    'name': f"scriptlet_{scriptlet_count}",
                    'type': 'jsp_scriptlet'
                })
        
        # JSP 표현식
        expression_pattern = r'<%=([^%]*)%>'
        expression_count = 0
        
        for match in re.finditer(expression_pattern, content):
            expr_content = match.group(1).strip()
            if expr_content:
                expression_count += 1
                functions.append({
                    'name': f"expression_{expression_count}",
                    'type': 'jsp_expression'
                })
        
        return functions
        
    except Exception as e:
        print(f"JSP 파일 읽기 오류 {file_path}: {e}")
        return []

def analyze_components_simple():
    """간단한 구성요소 분석"""
    project_path = "project/sampleSrc/src"
    
    print("=== 중복제거된 구성요소 수동 분석 (간단 버전) ===\n")
    
    # Java 파일 분석
    print("=== Java 파일 메소드 분석 ===")
    java_files = glob.glob(f"{project_path}/**/*.java", recursive=True)
    java_total_methods = 0
    java_methods = []
    
    for java_file in java_files:
        relative_path = os.path.relpath(java_file, project_path)
        methods = extract_java_methods_simple(java_file)
        java_total_methods += len(methods)
        java_methods.extend(methods)
        
        print(f"{relative_path}: {len(methods)}개 메소드")
        for method in methods:
            print(f"  - {method['type']}: {method['name']}")
    
    print(f"\nJava 총 메소드 수: {java_total_methods}개")
    
    # XML 파일 분석
    print("\n=== XML 파일 쿼리 분석 ===")
    xml_files = glob.glob(f"{project_path}/**/*.xml", recursive=True)
    xml_total_queries = 0
    xml_queries = []
    
    for xml_file in xml_files:
        relative_path = os.path.relpath(xml_file, project_path)
        queries = extract_xml_queries_simple(xml_file)
        xml_total_queries += len(queries)
        xml_queries.extend(queries)
        
        print(f"{relative_path}: {len(queries)}개 쿼리")
        for query in queries:
            print(f"  - {query['tag']}: {query['id']}")
    
    print(f"\nXML 총 쿼리 수: {xml_total_queries}개")
    
    # JSP 파일 분석
    print("\n=== JSP 파일 함수/스크립트 분석 ===")
    jsp_files = glob.glob(f"{project_path}/**/*.jsp", recursive=True)
    jsp_total_functions = 0
    jsp_functions = []
    
    for jsp_file in jsp_files:
        relative_path = os.path.relpath(jsp_file, project_path)
        functions = extract_jsp_functions_simple(jsp_file)
        jsp_total_functions += len(functions)
        jsp_functions.extend(functions)
        
        print(f"{relative_path}: {len(functions)}개 함수/스크립트")
        for func in functions:
            print(f"  - {func['type']}: {func['name']}")
    
    print(f"\nJSP 총 함수/스크립트 수: {jsp_total_functions}개")
    
    # 전체 요약
    print("\n=== 전체 요약 ===")
    print(f"Java 메소드: {java_total_methods}개")
    print(f"XML 쿼리: {xml_total_queries}개")
    print(f"JSP 함수/스크립트: {jsp_total_functions}개")
    print(f"총 구성요소: {java_total_methods + xml_total_queries + jsp_total_functions}개")
    
    return {
        'java_methods': java_methods,
        'xml_queries': xml_queries,
        'jsp_functions': jsp_functions,
        'counts': {
            'java': java_total_methods,
            'xml': xml_total_queries,
            'jsp': jsp_total_functions
        }
    }

if __name__ == "__main__":
    result = analyze_components_simple()

