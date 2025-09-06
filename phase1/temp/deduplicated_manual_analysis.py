#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import glob
from collections import defaultdict

def extract_java_methods_deduplicated(file_path):
    """Java 파일에서 중복제거된 메소드 추출"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        methods = []
        
        # 일반 메소드 (중복 제거를 위해 시그니처 기반)
        method_pattern = r'(?:public|private|protected|static|\s)*\s*(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?(?:abstract\s+)?(?:native\s+)?(?:strictfp\s+)?(?:transient\s+)?(?:volatile\s+)?(?:[a-zA-Z_][a-zA-Z0-9_<>\[\],\s]*\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*(?:throws\s+[^{]+)?\s*\{'
        
        for match in re.finditer(method_pattern, content, re.MULTILINE | re.DOTALL):
            method_name = match.group(1)
            method_signature = match.group(0)
            
            # 중복 제거: 같은 이름과 파라미터 타입이면 하나로 취급
            param_types = re.findall(r'\(([^)]*)\)', method_signature)[0] if '(' in method_signature else ''
            unique_key = f"{method_name}({param_types})"
            
            methods.append({
                'name': method_name,
                'signature': method_signature.strip(),
                'unique_key': unique_key,
                'type': 'method'
            })
        
        # 생성자 (클래스명과 같은 이름)
        class_name = os.path.basename(file_path).replace('.java', '')
        constructor_pattern = rf'(?:public|private|protected)\s+{re.escape(class_name)}\s*\([^)]*\)\s*(?:throws\s+[^{]+)?\s*\{'
        
        for match in re.finditer(constructor_pattern, content):
            constructor_signature = match.group(0)
            methods.append({
                'name': class_name,
                'signature': constructor_signature.strip(),
                'unique_key': f"{class_name}_constructor",
                'type': 'constructor'
            })
        
        # 인터페이스 메소드 (세미콜론으로 끝나는)
        interface_method_pattern = r'(?:public|private|protected|static|\s)*\s*(?:static\s+)?(?:default\s+)?(?:[a-zA-Z_][a-zA-Z0-9_<>\[\],\s]*\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*(?:throws\s+[^;]+)?\s*;'
        
        for match in re.finditer(interface_method_pattern, content, re.MULTILINE | re.DOTALL):
            method_name = match.group(1)
            method_signature = match.group(0)
            
            param_types = re.findall(r'\(([^)]*)\)', method_signature)[0] if '(' in method_signature else ''
            unique_key = f"{method_name}({param_types})"
            
            methods.append({
                'name': method_name,
                'signature': method_signature.strip(),
                'unique_key': unique_key,
                'type': 'interface_method'
            })
        
        # 중복 제거
        unique_methods = {}
        for method in methods:
            key = method['unique_key']
            if key not in unique_methods:
                unique_methods[key] = method
        
        return list(unique_methods.values())
        
    except Exception as e:
        print(f"Java 파일 읽기 오류 {file_path}: {e}")
        return []

def extract_xml_queries_deduplicated(file_path):
    """XML 파일에서 중복제거된 SQL 쿼리 추출"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        queries = []
        sql_tags = ['select', 'insert', 'update', 'delete']
        
        for tag in sql_tags:
            # <select id="..."> 형태
            pattern = rf'<{tag}\s+[^>]*id\s*=\s*["\']([^"\']*)["\'][^>]*>'
            
            for match in re.finditer(pattern, content, re.IGNORECASE):
                query_id = match.group(1)
                full_match = match.group(0)
                
                # 중복 제거: 같은 id를 가진 쿼리는 하나로 취급
                queries.append({
                    'id': query_id,
                    'tag': tag,
                    'signature': full_match,
                    'unique_key': f"{tag}_{query_id}",
                    'type': 'sql_query'
                })
        
        # 중복 제거
        unique_queries = {}
        for query in queries:
            key = query['unique_key']
            if key not in unique_queries:
                unique_queries[key] = query
        
        return list(unique_queries.values())
        
    except Exception as e:
        print(f"XML 파일 읽기 오류 {file_path}: {e}")
        return []

def extract_jsp_functions_deduplicated(file_path):
    """JSP 파일에서 중복제거된 함수/스크립트 추출"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        functions = []
        
        # JavaScript 함수
        js_function_pattern = r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*\{'
        
        for match in re.finditer(js_function_pattern, content):
            func_name = match.group(1)
            func_signature = match.group(0)
            
            functions.append({
                'name': func_name,
                'signature': func_signature.strip(),
                'unique_key': f"js_{func_name}",
                'type': 'javascript_function'
            })
        
        # JSP 스크립트릿 (<% ... %>)
        scriptlet_pattern = r'<%([^%]*)%>'
        
        for i, match in enumerate(re.finditer(scriptlet_pattern, content)):
            scriptlet_content = match.group(1).strip()
            if scriptlet_content:  # 빈 스크립트릿 제외
                functions.append({
                    'name': f"scriptlet_{i+1}",
                    'signature': f"<%{scriptlet_content}%>",
                    'unique_key': f"scriptlet_{i+1}_{hash(scriptlet_content)}",
                    'type': 'jsp_scriptlet'
                })
        
        # JSP 표현식 (<%= ... %>)
        expression_pattern = r'<%=([^%]*)%>'
        
        for i, match in enumerate(re.finditer(expression_pattern, content)):
            expr_content = match.group(1).strip()
            if expr_content:  # 빈 표현식 제외
                functions.append({
                    'name': f"expression_{i+1}",
                    'signature': f"<%= {expr_content} %>",
                    'unique_key': f"expression_{i+1}_{hash(expr_content)}",
                    'type': 'jsp_expression'
                })
        
        # 중복 제거
        unique_functions = {}
        for func in functions:
            key = func['unique_key']
            if key not in unique_functions:
                unique_functions[key] = func
        
        return list(unique_functions.values())
        
    except Exception as e:
        print(f"JSP 파일 읽기 오류 {file_path}: {e}")
        return []

def analyze_deduplicated_components():
    """중복제거된 구성요소 분석"""
    project_path = "project/sampleSrc/src"
    
    print("=== 중복제거된 구성요소 수동 분석 ===\n")
    
    all_components = {
        'java_methods': [],
        'xml_queries': [],
        'jsp_functions': []
    }
    
    # Java 파일 분석
    print("=== Java 파일 메소드 분석 (중복제거) ===")
    java_files = glob.glob(f"{project_path}/**/*.java", recursive=True)
    java_total_methods = 0
    
    for java_file in java_files:
        relative_path = os.path.relpath(java_file, project_path)
        methods = extract_java_methods_deduplicated(java_file)
        java_total_methods += len(methods)
        all_components['java_methods'].extend(methods)
        
        print(f"{relative_path}: {len(methods)}개 메소드")
        for method in methods:
            print(f"  - {method['type']}: {method['name']}")
    
    print(f"\nJava 총 메소드 수 (중복제거): {java_total_methods}개")
    
    # XML 파일 분석
    print("\n=== XML 파일 쿼리 분석 (중복제거) ===")
    xml_files = glob.glob(f"{project_path}/**/*.xml", recursive=True)
    xml_total_queries = 0
    
    for xml_file in xml_files:
        relative_path = os.path.relpath(xml_file, project_path)
        queries = extract_xml_queries_deduplicated(xml_file)
        xml_total_queries += len(queries)
        all_components['xml_queries'].extend(queries)
        
        print(f"{relative_path}: {len(queries)}개 쿼리")
        for query in queries:
            print(f"  - {query['tag']}: {query['id']}")
    
    print(f"\nXML 총 쿼리 수 (중복제거): {xml_total_queries}개")
    
    # JSP 파일 분석
    print("\n=== JSP 파일 함수/스크립트 분석 (중복제거) ===")
    jsp_files = glob.glob(f"{project_path}/**/*.jsp", recursive=True)
    jsp_total_functions = 0
    
    for jsp_file in jsp_files:
        relative_path = os.path.relpath(jsp_file, project_path)
        functions = extract_jsp_functions_deduplicated(jsp_file)
        jsp_total_functions += len(functions)
        all_components['jsp_functions'].extend(functions)
        
        print(f"{relative_path}: {len(functions)}개 함수/스크립트")
        for func in functions:
            print(f"  - {func['type']}: {func['name']}")
    
    print(f"\nJSP 총 함수/스크립트 수 (중복제거): {jsp_total_functions}개")
    
    # 전체 요약
    print("\n=== 전체 요약 (중복제거) ===")
    print(f"Java 메소드: {java_total_methods}개")
    print(f"XML 쿼리: {xml_total_queries}개")
    print(f"JSP 함수/스크립트: {jsp_total_functions}개")
    print(f"총 구성요소: {java_total_methods + xml_total_queries + jsp_total_functions}개")
    
    return all_components

if __name__ == "__main__":
    result = analyze_deduplicated_components()

