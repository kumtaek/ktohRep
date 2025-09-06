#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from pathlib import Path

def main():
    project_path = Path('../project/sampleSrc/src')
    
    print('=== Java 파일 분석 ===')
    java_count = 0
    java_methods = 0
    
    for file_path in project_path.rglob('*.java'):
        java_count += 1
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 클래스명 추출
            class_match = re.search(r'class\s+(\w+)', content)
            class_name = class_match.group(1) if class_match else 'Unknown'
            
            # 메소드 추출
            method_pattern = r'(public|private|protected|static)\s+[\w\<\>\[\]]+\s+(\w+)\s*\([^\)]*\)\s*\{'
            methods = re.findall(method_pattern, content)
            
            # 생성자 추출
            constructor_pattern = r'(public|private|protected)\s+(\w+)\s*\([^\)]*\)\s*\{'
            constructors = re.findall(constructor_pattern, content)
            
            total_methods = len(methods) + len(constructors)
            java_methods += total_methods
            
            relative_path = file_path.relative_to(project_path)
            print(f'[Java] {relative_path}')
            print(f'  클래스: {class_name}')
            print(f'  메소드: {total_methods}개')
            if methods:
                method_names = [m[1] for m in methods[:3]]
                print(f'  메소드명: {", ".join(method_names)}')
            print()
            
        except Exception as e:
            print(f'[Java] {file_path} - 오류: {e}')
    
    print('=== JSP 파일 분석 ===')
    jsp_count = 0
    jsp_elements = 0
    
    for file_path in project_path.rglob('*.jsp'):
        jsp_count += 1
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # JSP 함수 추출
            functions = re.findall(r'function\s+(\w+)\s*\(', content)
            
            # JSP 스크립틀릿 추출
            scriptlets = re.findall(r'<%[^%]*%>', content)
            
            total_elements = len(functions) + len(scriptlets)
            jsp_elements += total_elements
            
            relative_path = file_path.relative_to(project_path)
            print(f'[JSP] {relative_path}')
            print(f'  함수: {len(functions)}개, 스크립틀릿: {len(scriptlets)}개')
            if functions:
                print(f'  함수명: {", ".join(functions[:3])}')
            print()
            
        except Exception as e:
            print(f'[JSP] {file_path} - 오류: {e}')
    
    print('=== SQL/XML 파일 분석 ===')
    sql_count = 0
    sql_queries = 0
    
    for file_path in project_path.rglob('*.xml'):
        sql_count += 1
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # SQL 쿼리 추출
            select_queries = re.findall(r'SELECT\s+', content, re.IGNORECASE)
            insert_queries = re.findall(r'INSERT\s+', content, re.IGNORECASE)
            update_queries = re.findall(r'UPDATE\s+', content, re.IGNORECASE)
            delete_queries = re.findall(r'DELETE\s+', content, re.IGNORECASE)
            
            total_queries = len(select_queries) + len(insert_queries) + len(update_queries) + len(delete_queries)
            sql_queries += total_queries
            
            relative_path = file_path.relative_to(project_path)
            print(f'[SQL] {relative_path}')
            print(f'  SELECT: {len(select_queries)}개, INSERT: {len(insert_queries)}개')
            print(f'  UPDATE: {len(update_queries)}개, DELETE: {len(delete_queries)}개')
            print()
            
        except Exception as e:
            print(f'[SQL] {file_path} - 오류: {e}')
    
    print('=== 전체 통계 ===')
    print(f'Java 파일: {java_count}개, 총 메소드: {java_methods}개')
    print(f'JSP 파일: {jsp_count}개, 총 요소: {jsp_elements}개')
    print(f'SQL/XML 파일: {sql_count}개, 총 쿼리: {sql_queries}개')
    print(f'전체 코드 요소: {java_methods + jsp_elements + sql_queries}개')

if __name__ == "__main__":
    main()
