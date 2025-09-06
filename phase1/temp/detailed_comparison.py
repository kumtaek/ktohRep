#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
import glob
import re

def get_manual_analysis_results():
    """이전에 생성한 수동 분석 결과 재사용"""
    # basic_analysis.py의 결과를 재사용
    project_path = "project/sampleSrc/src"
    
    # Java 파일 분석
    java_files = glob.glob(f"{project_path}/**/*.java", recursive=True)
    java_results = {}
    
    for java_file in java_files:
        relative_path = os.path.relpath(java_file, project_path)
        try:
            with open(java_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 메소드 패턴
            method_pattern = r'(?:public|private|protected|static|\s)*\s*(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?(?:abstract\s+)?(?:native\s+)?(?:strictfp\s+)?(?:transient\s+)?(?:volatile\s+)?(?:[a-zA-Z_][a-zA-Z0-9_<>\[\],\s]*\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*(?:throws\s+[^{]+)?\s*\{'
            methods = re.findall(method_pattern, content, re.MULTILINE | re.DOTALL)
            
            # 생성자
            class_name = os.path.basename(java_file).replace('.java', '')
            constructor_pattern = rf'(?:public|private|protected)\s+{re.escape(class_name)}\s*\('
            constructors = re.findall(constructor_pattern, content)
            
            # 인터페이스 메소드
            interface_method_pattern = r'(?:public|private|protected|static|\s)*\s*(?:static\s+)?(?:default\s+)?(?:[a-zA-Z_][a-zA-Z0-9_<>\[\],\s]*\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*(?:throws\s+[^;]+)?\s*;'
            interface_methods = re.findall(interface_method_pattern, content, re.MULTILINE | re.DOTALL)
            
            total_methods = len(methods) + len(constructors) + len(interface_methods)
            java_results[relative_path] = total_methods
            
        except Exception as e:
            java_results[relative_path] = 0
    
    # XML 파일 분석
    xml_files = glob.glob(f"{project_path}/**/*.xml", recursive=True)
    xml_results = {}
    
    for xml_file in xml_files:
        relative_path = os.path.relpath(xml_file, project_path)
        try:
            with open(xml_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            sql_tags = ['select', 'insert', 'update', 'delete']
            total_queries = 0
            
            for tag in sql_tags:
                pattern = rf'<{tag}\s+[^>]*id\s*=\s*["\'][^"\']*["\'][^>]*>'
                matches = re.findall(pattern, content, re.IGNORECASE)
                total_queries += len(matches)
            
            xml_results[relative_path] = total_queries
            
        except Exception as e:
            xml_results[relative_path] = 0
    
    # JSP 파일 분석
    jsp_files = glob.glob(f"{project_path}/**/*.jsp", recursive=True)
    jsp_results = {}
    
    for jsp_file in jsp_files:
        relative_path = os.path.relpath(jsp_file, project_path)
        try:
            with open(jsp_file, 'r', encoding='utf-8') as f:
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
            jsp_results[relative_path] = total_scripts
            
        except Exception as e:
            jsp_results[relative_path] = 0
    
    return {
        'java': java_results,
        'xml': xml_results,
        'jsp': jsp_results
    }

def get_metadb_results():
    """메타디비 결과 조회"""
    db_path = "project/sampleSrc/metadata.db"
    
    if not os.path.exists(db_path):
        return None
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 파일별 메소드 개수
        cursor.execute("""
            SELECT f.path, COUNT(m.method_id) as method_count
            FROM files f
            LEFT JOIN methods m ON f.file_id = m.class_id
            GROUP BY f.file_id, f.path
            ORDER BY f.path
        """)
        file_methods = cursor.fetchall()
        
        # 파일별 SQL Units 개수
        cursor.execute("""
            SELECT f.path, COUNT(s.sql_id) as sql_count
            FROM files f
            LEFT JOIN sql_units s ON f.file_id = s.file_id
            GROUP BY f.file_id, f.path
            ORDER BY f.path
        """)
        file_sqls = cursor.fetchall()
        
        conn.close()
        
        return {
            'methods': dict(file_methods),
            'sql_units': dict(file_sqls)
        }
        
    except Exception as e:
        print(f"메타디비 조회 오류: {e}")
        return None

def generate_detailed_comparison():
    """상세 비교 리포트 생성"""
    print("=== 수동 분석 vs 메타디비 상세 비교 ===\n")
    
    # 수동 분석 결과
    manual_results = get_manual_analysis_results()
    
    # 메타디비 결과
    metadb_results = get_metadb_results()
    
    if not metadb_results:
        print("메타디비 결과를 가져올 수 없습니다.")
        return
    
    # Java 파일 비교
    print("=== Java 파일 메소드 개수 비교 ===")
    print(f"{'파일명':<60} {'수동':<8} {'메타디비':<10} {'차이':<8} {'정확도':<8}")
    print("-" * 100)
    
    java_total_manual = 0
    java_total_metadb = 0
    
    for file_path, manual_count in manual_results['java'].items():
        metadb_count = metadb_results['methods'].get(file_path, 0)
        diff = manual_count - metadb_count
        accuracy = (metadb_count / manual_count * 100) if manual_count > 0 else 0
        
        print(f"{file_path:<60} {manual_count:<8} {metadb_count:<10} {diff:<8} {accuracy:.1f}%")
        
        java_total_manual += manual_count
        java_total_metadb += metadb_count
    
    print("-" * 100)
    print(f"{'Java 총계':<60} {java_total_manual:<8} {java_total_metadb:<10} {java_total_manual - java_total_metadb:<8} {(java_total_metadb / java_total_manual * 100):.1f}%")
    print()
    
    # XML 파일 비교
    print("=== XML 파일 쿼리 개수 비교 ===")
    print(f"{'파일명':<60} {'수동':<8} {'메타디비':<10} {'차이':<8} {'정확도':<8}")
    print("-" * 100)
    
    xml_total_manual = 0
    xml_total_metadb = 0
    
    for file_path, manual_count in manual_results['xml'].items():
        metadb_count = metadb_results['sql_units'].get(file_path, 0)
        diff = manual_count - metadb_count
        accuracy = (metadb_count / manual_count * 100) if manual_count > 0 else 0
        
        print(f"{file_path:<60} {manual_count:<8} {metadb_count:<10} {diff:<8} {accuracy:.1f}%")
        
        xml_total_manual += manual_count
        xml_total_metadb += metadb_count
    
    print("-" * 100)
    print(f"{'XML 총계':<60} {xml_total_manual:<8} {xml_total_metadb:<10} {xml_total_manual - xml_total_metadb:<8} {(xml_total_metadb / xml_total_manual * 100):.1f}%")
    print()
    
    # JSP 파일 비교
    print("=== JSP 파일 함수/스크립트 개수 비교 ===")
    print(f"{'파일명':<60} {'수동':<8} {'메타디비':<10} {'차이':<8} {'정확도':<8}")
    print("-" * 100)
    
    jsp_total_manual = 0
    jsp_total_metadb = 0
    
    for file_path, manual_count in manual_results['jsp'].items():
        metadb_count = metadb_results['sql_units'].get(file_path, 0)
        diff = manual_count - metadb_count
        accuracy = (metadb_count / manual_count * 100) if manual_count > 0 else 0
        
        print(f"{file_path:<60} {manual_count:<8} {metadb_count:<10} {diff:<8} {accuracy:.1f}%")
        
        jsp_total_manual += manual_count
        jsp_total_metadb += metadb_count
    
    print("-" * 100)
    print(f"{'JSP 총계':<60} {jsp_total_manual:<8} {jsp_total_metadb:<10} {jsp_total_manual - jsp_total_metadb:<8} {(jsp_total_metadb / jsp_total_manual * 100):.1f}%")
    print()
    
    # 전체 요약
    print("=== 전체 요약 ===")
    total_manual = java_total_manual + xml_total_manual + jsp_total_manual
    total_metadb = java_total_metadb + xml_total_metadb + jsp_total_metadb
    
    print(f"Java 메소드: {java_total_manual}개 → {java_total_metadb}개 ({(java_total_metadb / java_total_manual * 100):.1f}%)")
    print(f"XML 쿼리: {xml_total_manual}개 → {xml_total_metadb}개 ({(xml_total_metadb / xml_total_manual * 100):.1f}%)")
    print(f"JSP 함수/스크립트: {jsp_total_manual}개 → {jsp_total_metadb}개 ({(jsp_total_metadb / jsp_total_manual * 100):.1f}%)")
    print(f"총 구성요소: {total_manual}개 → {total_metadb}개 ({(total_metadb / total_manual * 100):.1f}%)")
    
    return {
        'manual': {
            'java': java_total_manual,
            'xml': xml_total_manual,
            'jsp': jsp_total_manual,
            'total': total_manual
        },
        'metadb': {
            'java': java_total_metadb,
            'xml': xml_total_metadb,
            'jsp': jsp_total_metadb,
            'total': total_metadb
        }
    }

if __name__ == "__main__":
    result = generate_detailed_comparison()

