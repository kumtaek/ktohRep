#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re

def direct_source_analysis():
    """실제 소스코드 직접 분석"""
    
    print("=== 실제 소스코드 직접 분석 ===")
    
    total_files = 0
    total_methods = 0
    total_classes = 0
    total_sql_queries = 0
    total_sql_injection = 0
    
    # Java 파일 분석
    java_dir = "../project/sampleSrc/src/main/java"
    print(f"\nJava 디렉토리: {java_dir}")
    
    if os.path.exists(java_dir):
        for root, dirs, files in os.walk(java_dir):
            for file in files:
                if file.endswith('.java'):
                    file_path = os.path.join(root, file)
                    print(f"분석 중: {file_path}")
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 메소드 개수
                        method_pattern = r'(?:public|private|protected)\s+(?:static\s+)?(?:[\w<>\[\],\s?&\.]+\s+)?(\w+)\s*\([^)]*\)\s*\{'
                        methods = re.findall(method_pattern, content, re.MULTILINE)
                        method_count = len(methods)
                        
                        # 클래스 개수
                        class_pattern = r'class\s+(\w+)'
                        classes = re.findall(class_pattern, content)
                        class_count = len(classes)
                        
                        # SQL 문자열 개수
                        sql_pattern = r'["\']([^"\']*(?:SELECT\s+|FROM\s+|WHERE\s+|JOIN\s+|UPDATE\s+|INSERT\s+|DELETE\s+|CREATE\s+|ALTER\s+|DROP\s+|TRUNCATE\s+|MERGE\s+)[^"\']*)["\']'
                        sql_strings = re.findall(sql_pattern, content, re.IGNORECASE)
                        sql_count = len(sql_strings)
                        
                        # SQL Injection 패턴
                        sql_injection_pattern = r'["\']([^"\']*)\s*\+\s*[^"\']*["\']'
                        sql_injection_matches = re.findall(sql_injection_pattern, content)
                        injection_count = len(sql_injection_matches)
                        
                        print(f"  메소드: {method_count}, 클래스: {class_count}, SQL: {sql_count}, Injection: {injection_count}")
                        
                        total_files += 1
                        total_methods += method_count
                        total_classes += class_count
                        total_sql_queries += sql_count
                        total_sql_injection += injection_count
                        
                    except Exception as e:
                        print(f"  오류: {e}")
    
    # XML 파일 분석
    xml_dir = "../project/sampleSrc/src/main/resources"
    print(f"\nXML 디렉토리: {xml_dir}")
    
    if os.path.exists(xml_dir):
        for root, dirs, files in os.walk(xml_dir):
            for file in files:
                if file.endswith('.xml'):
                    file_path = os.path.join(root, file)
                    print(f"분석 중: {file_path}")
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # SQL 쿼리 개수
                        select_pattern = r'<select[^>]*>.*?</select>'
                        select_queries = re.findall(select_pattern, content, re.DOTALL | re.IGNORECASE)
                        
                        insert_pattern = r'<insert[^>]*>.*?</insert>'
                        insert_queries = re.findall(insert_pattern, content, re.DOTALL | re.IGNORECASE)
                        
                        update_pattern = r'<update[^>]*>.*?</update>'
                        update_queries = re.findall(update_pattern, content, re.DOTALL | re.IGNORECASE)
                        
                        delete_pattern = r'<delete[^>]*>.*?</delete>'
                        delete_queries = re.findall(delete_pattern, content, re.DOTALL | re.IGNORECASE)
                        
                        sql_count = len(select_queries) + len(insert_queries) + len(update_queries) + len(delete_queries)
                        
                        # SQL Injection 패턴 (${} 패턴)
                        sql_injection_pattern = r'\$\{[^}]+\}'
                        sql_injection_matches = re.findall(sql_injection_pattern, content)
                        injection_count = len(sql_injection_matches)
                        
                        print(f"  SQL 쿼리: {sql_count}, Injection: {injection_count}")
                        
                        total_files += 1
                        total_sql_queries += sql_count
                        total_sql_injection += injection_count
                        
                    except Exception as e:
                        print(f"  오류: {e}")
    
    # JSP 파일 분석
    jsp_dir = "../project/sampleSrc/src/main/webapp"
    print(f"\nJSP 디렉토리: {jsp_dir}")
    
    if os.path.exists(jsp_dir):
        for root, dirs, files in os.walk(jsp_dir):
            for file in files:
                if file.endswith('.jsp'):
                    file_path = os.path.join(root, file)
                    print(f"분석 중: {file_path}")
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # SQL Injection 패턴
                        sql_injection_pattern = r'["\']([^"\']*)\s*\+\s*[^"\']*["\']'
                        sql_injection_matches = re.findall(sql_injection_pattern, content)
                        injection_count = len(sql_injection_matches)
                        
                        print(f"  Injection: {injection_count}")
                        
                        total_files += 1
                        total_sql_injection += injection_count
                        
                    except Exception as e:
                        print(f"  오류: {e}")
    
    print(f"\n=== 실제 소스코드 분석 결과 ===")
    print(f"총 파일 수: {total_files}")
    print(f"총 메소드 수: {total_methods}")
    print(f"총 클래스 수: {total_classes}")
    print(f"총 SQL 쿼리 수: {total_sql_queries}")
    print(f"총 SQL Injection 패턴 수: {total_sql_injection}")
    
    return {
        'total_files': total_files,
        'total_methods': total_methods,
        'total_classes': total_classes,
        'total_sql_queries': total_sql_queries,
        'total_sql_injection': total_sql_injection
    }

if __name__ == "__main__":
    direct_source_analysis()




