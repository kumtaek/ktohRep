#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
파일별 메소드/함수/쿼리 개수 상세 분석
"""

import os
import re
from pathlib import Path

def analyze_java_file(file_path):
    """Java 파일 분석"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 클래스명 추출
        class_match = re.search(r'class\s+(\w+)', content)
        class_name = class_match.group(1) if class_match else 'Unknown'
        
        # 메소드 추출 (더 정확한 패턴)
        method_pattern = r'(public|private|protected|static)\s+[\w\<\>\[\]]+\s+(\w+)\s*\([^\)]*\)\s*\{'
        methods = re.findall(method_pattern, content)
        
        # 생성자 추출
        constructor_pattern = r'(public|private|protected)\s+(\w+)\s*\([^\)]*\)\s*\{'
        constructors = re.findall(constructor_pattern, content)
        
        # 어노테이션 추출
        annotations = re.findall(r'@(\w+)', content)
        
        # import 문 개수
        imports = re.findall(r'import\s+', content)
        
        return {
            'class_name': class_name,
            'methods': len(methods),
            'constructors': len(constructors),
            'annotations': len(annotations),
            'imports': len(imports),
            'method_names': [m[1] for m in methods] + [c[1] for c in constructors]
        }
    except Exception as e:
        return {'error': str(e)}

def analyze_jsp_file(file_path):
    """JSP 파일 분석"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # JSP 함수 추출
        functions = re.findall(r'function\s+(\w+)\s*\(', content)
        
        # JSP 스크립틀릿 추출
        scriptlets = re.findall(r'<%[^%]*%>', content)
        
        # JSP 태그 추출
        jsp_tags = re.findall(r'<jsp:[^>]*>', content)
        
        # HTML 폼 요소 추출
        form_elements = re.findall(r'<(input|select|textarea|button)[^>]*>', content)
        
        return {
            'functions': len(functions),
            'scriptlets': len(scriptlets),
            'jsp_tags': len(jsp_tags),
            'form_elements': len(form_elements),
            'function_names': functions
        }
    except Exception as e:
        return {'error': str(e)}

def analyze_sql_file(file_path):
    """SQL/XML 파일 분석"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # SQL 쿼리 타입별 추출
        select_queries = re.findall(r'SELECT\s+', content, re.IGNORECASE)
        insert_queries = re.findall(r'INSERT\s+', content, re.IGNORECASE)
        update_queries = re.findall(r'UPDATE\s+', content, re.IGNORECASE)
        delete_queries = re.findall(r'DELETE\s+', content, re.IGNORECASE)
        
        # MyBatis 매퍼 메소드 추출
        mapper_methods = re.findall(r'<select|<insert|<update|<delete', content)
        
        return {
            'select': len(select_queries),
            'insert': len(insert_queries),
            'update': len(update_queries),
            'delete': len(delete_queries),
            'mapper_methods': len(mapper_methods)
        }
    except Exception as e:
        return {'error': str(e)}

def main():
    # 프로젝트 경로
    project_path = Path('../project/sampleSrc/src')
    
    print('=== Java 파일 상세 분석 ===')
    print()
    
    java_files = []
    
    for file_path in project_path.rglob('*.java'):
        relative_path = file_path.relative_to(project_path)
        result = analyze_java_file(file_path)
        if 'error' not in result:
            java_files.append((relative_path, result))
    
    # Java 파일별 상세 정보 출력
    for path, data in java_files:
        print(f'[Java] {path}')
        print(f'   클래스: {data["class_name"]}')
        print(f'   메소드: {data["methods"]}개, 생성자: {data["constructors"]}개')
        print(f'   어노테이션: {data["annotations"]}개, Import: {data["imports"]}개')
        if data['method_names']:
            method_list = ', '.join(data['method_names'][:3])
            if len(data['method_names']) > 3:
                method_list += '...'
            print(f'   메소드명: {method_list}')
        print()
    
    print('=== JSP 파일 상세 분석 ===')
    print()
    
    jsp_files = []
    
    for file_path in project_path.rglob('*.jsp'):
        relative_path = file_path.relative_to(project_path)
        result = analyze_jsp_file(file_path)
        if 'error' not in result:
            jsp_files.append((relative_path, result))
    
    for path, data in jsp_files:
        print(f'[Java] {path}')
        print(f'   함수: {data["functions"]}개, 스크립틀릿: {data["scriptlets"]}개')
        print(f'   JSP태그: {data["jsp_tags"]}개, 폼요소: {data["form_elements"]}개')
        if data['function_names']:
            func_list = ', '.join(data['function_names'][:3])
            if len(data['function_names']) > 3:
                func_list += '...'
            print(f'   함수명: {func_list}')
        print()
    
    print('=== SQL/XML 파일 상세 분석 ===')
    print()
    
    sql_files = []
    
    for file_path in project_path.rglob('*.xml'):
        relative_path = file_path.relative_to(project_path)
        result = analyze_sql_file(file_path)
        if 'error' not in result:
            sql_files.append((relative_path, result))
    
    for path, data in sql_files:
        print(f'[Java] {path}')
        print(f'   SELECT: {data["select"]}개, INSERT: {data["insert"]}개')
        print(f'   UPDATE: {data["update"]}개, DELETE: {data["delete"]}개')
        print(f'   매퍼메소드: {data["mapper_methods"]}개')
        print()
    
    print('=== 전체 통계 ===')
    total_java_methods = sum(data['methods'] + data['constructors'] for _, data in java_files)
    total_jsp_elements = sum(data['functions'] + data['scriptlets'] for _, data in jsp_files)
    total_sql_queries = sum(data['select'] + data['insert'] + data['update'] + data['delete'] for _, data in sql_files)
    
    print(f'Java 파일: {len(java_files)}개, 총 메소드: {total_java_methods}개')
    print(f'JSP 파일: {len(jsp_files)}개, 총 요소: {total_jsp_elements}개')
    print(f'SQL/XML 파일: {len(sql_files)}개, 총 쿼리: {total_sql_queries}개')
    print(f'전체 코드 요소: {total_java_methods + total_jsp_elements + total_sql_queries}개')

if __name__ == "__main__":
    main()
