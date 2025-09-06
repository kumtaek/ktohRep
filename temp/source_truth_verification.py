#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sqlite3
from typing import List, Dict, Any

def verify_source_truth():
    """실제 소스코드 직접 검증 - 정확한 기준점 확립"""
    
    print("=== 실제 소스코드 직접 검증 ===")
    
    # 1. 실제 소스코드 직접 분석
    print("\n=== 1. 실제 소스코드 직접 분석 ===")
    actual_source_analysis = analyze_actual_source_code()
    
    # 2. 메타디비 결과 검증
    print("\n=== 2. 메타디비 결과 검증 ===")
    metadb_analysis = analyze_metadb_results()
    
    # 3. 수작업 결과 검증 (있다면)
    print("\n=== 3. 수작업 결과 검증 ===")
    manual_analysis = analyze_manual_results()
    
    # 4. 비교 분석
    print("\n=== 4. 비교 분석 ===")
    compare_analyses(actual_source_analysis, metadb_analysis, manual_analysis)
    
    return {
        'actual_source': actual_source_analysis,
        'metadb': metadb_analysis,
        'manual': manual_analysis
    }

def analyze_actual_source_code():
    """실제 소스코드 직접 분석"""
    
    analysis = {
        'java_files': {},
        'xml_files': {},
        'jsp_files': {},
        'total_files': 0,
        'total_methods': 0,
        'total_classes': 0,
        'total_sql_queries': 0,
        'total_sql_injection_patterns': 0
    }
    
    # Java 파일 분석
    java_dir = "../project/sampleSrc/src/main/java"
    print(f"Java 디렉토리 확인: {java_dir}, 존재: {os.path.exists(java_dir)}")
    if os.path.exists(java_dir):
        for root, dirs, files in os.walk(java_dir):
            print(f"디렉토리: {root}, 파일 수: {len(files)}")
            for file in files:
                if file.endswith('.java'):
                    file_path = os.path.join(root, file)
                    print(f"Java 파일 발견: {file_path}")
                    file_analysis = analyze_java_file_directly(file_path)
                    analysis['java_files'][file_path] = file_analysis
                    analysis['total_files'] += 1
                    analysis['total_methods'] += file_analysis['methods']
                    analysis['total_classes'] += file_analysis['classes']
                    analysis['total_sql_injection_patterns'] += file_analysis['sql_injection_patterns']
    
    # XML 파일 분석
    xml_dir = "../project/sampleSrc/src/main/resources"
    if os.path.exists(xml_dir):
        for root, dirs, files in os.walk(xml_dir):
            for file in files:
                if file.endswith('.xml'):
                    file_path = os.path.join(root, file)
                    file_analysis = analyze_xml_file_directly(file_path)
                    analysis['xml_files'][file_path] = file_analysis
                    analysis['total_files'] += 1
                    analysis['total_sql_queries'] += file_analysis['sql_queries']
    
    # JSP 파일 분석
    jsp_dir = "../project/sampleSrc/src/main/webapp"
    if os.path.exists(jsp_dir):
        for root, dirs, files in os.walk(jsp_dir):
            for file in files:
                if file.endswith('.jsp'):
                    file_path = os.path.join(root, file)
                    file_analysis = analyze_jsp_file_directly(file_path)
                    analysis['jsp_files'][file_path] = file_analysis
                    analysis['total_files'] += 1
                    analysis['total_sql_injection_patterns'] += file_analysis['sql_injection_patterns']
    
    print(f"총 파일 수: {analysis['total_files']}")
    print(f"총 메소드 수: {analysis['total_methods']}")
    print(f"총 클래스 수: {analysis['total_classes']}")
    print(f"총 SQL 쿼리 수: {analysis['total_sql_queries']}")
    print(f"총 SQL Injection 패턴 수: {analysis['total_sql_injection_patterns']}")
    
    return analysis

def analyze_java_file_directly(file_path: str) -> Dict[str, Any]:
    """Java 파일 직접 분석"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        analysis = {
            'file_path': file_path,
            'methods': 0,
            'classes': 0,
            'imports': 0,
            'annotations': 0,
            'sql_strings': 0,
            'sql_injection_patterns': 0,
            'syntax_errors': 0,
            'missing_imports': []
        }
        
        # 메소드 개수 (정확한 패턴)
        method_pattern = r'(?:public|private|protected)\s+(?:static\s+)?(?:[\w<>\[\],\s?&\.]+\s+)?(\w+)\s*\([^)]*\)\s*\{'
        methods = re.findall(method_pattern, content, re.MULTILINE)
        analysis['methods'] = len(methods)
        
        # 클래스 개수
        class_pattern = r'class\s+(\w+)'
        classes = re.findall(class_pattern, content)
        analysis['classes'] = len(classes)
        
        # Import 개수
        import_pattern = r'^import\s+([^;]+);'
        imports = re.findall(import_pattern, content, re.MULTILINE)
        analysis['imports'] = len(imports)
        
        # 어노테이션 개수
        annotation_pattern = r'@(\w+)'
        annotations = re.findall(annotation_pattern, content)
        analysis['annotations'] = len(annotations)
        
        # SQL 문자열 개수 (정확한 패턴)
        sql_pattern = r'["\']([^"\']*(?:SELECT\s+|FROM\s+|WHERE\s+|JOIN\s+|UPDATE\s+|INSERT\s+|DELETE\s+|CREATE\s+|ALTER\s+|DROP\s+|TRUNCATE\s+|MERGE\s+)[^"\']*)["\']'
        sql_strings = re.findall(sql_pattern, content, re.IGNORECASE)
        analysis['sql_strings'] = len(sql_strings)
        
        # SQL Injection 패턴 검출
        sql_injection_pattern = r'["\']([^"\']*)\s*\+\s*[^"\']*["\']'
        sql_injection_matches = re.findall(sql_injection_pattern, content)
        analysis['sql_injection_patterns'] = len(sql_injection_matches)
        
        # 누락된 Import 검출
        if 'ResponseEntity' in content and 'import org.springframework.http.ResponseEntity' not in content:
            analysis['missing_imports'].append('ResponseEntity')
        if 'Order' in content and 'import.*Order' not in content:
            analysis['missing_imports'].append('Order')
        if 'User' in content and 'import.*User' not in content:
            analysis['missing_imports'].append('User')
        
        # 문법 오류 검출 (간단한 패턴)
        if 'String test = "hello"' in content and 'String test = "hello";' not in content:
            analysis['syntax_errors'] += 1
        
        return analysis
        
    except Exception as e:
        return {
            'file_path': file_path,
            'error': str(e),
            'methods': 0,
            'classes': 0,
            'imports': 0,
            'annotations': 0,
            'sql_strings': 0,
            'sql_injection_patterns': 0,
            'syntax_errors': 0,
            'missing_imports': []
        }

def analyze_xml_file_directly(file_path: str) -> Dict[str, Any]:
    """XML 파일 직접 분석"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        analysis = {
            'file_path': file_path,
            'sql_queries': 0,
            'select_queries': 0,
            'insert_queries': 0,
            'update_queries': 0,
            'delete_queries': 0,
            'sql_injection_patterns': 0,
            'syntax_errors': 0
        }
        
        # SQL 쿼리 개수
        select_pattern = r'<select[^>]*>.*?</select>'
        select_queries = re.findall(select_pattern, content, re.DOTALL | re.IGNORECASE)
        analysis['select_queries'] = len(select_queries)
        
        insert_pattern = r'<insert[^>]*>.*?</insert>'
        insert_queries = re.findall(insert_pattern, content, re.DOTALL | re.IGNORECASE)
        analysis['insert_queries'] = len(insert_queries)
        
        update_pattern = r'<update[^>]*>.*?</update>'
        update_queries = re.findall(update_pattern, content, re.DOTALL | re.IGNORECASE)
        analysis['update_queries'] = len(update_queries)
        
        delete_pattern = r'<delete[^>]*>.*?</delete>'
        delete_queries = re.findall(delete_pattern, content, re.DOTALL | re.IGNORECASE)
        analysis['delete_queries'] = len(delete_queries)
        
        analysis['sql_queries'] = analysis['select_queries'] + analysis['insert_queries'] + analysis['update_queries'] + analysis['delete_queries']
        
        # SQL Injection 패턴 검출 (${} 패턴)
        sql_injection_pattern = r'\$\{[^}]+\}'
        sql_injection_matches = re.findall(sql_injection_pattern, content)
        analysis['sql_injection_patterns'] = len(sql_injection_matches)
        
        # XML 문법 오류 검출
        if '<select' in content and '</select>' not in content:
            analysis['syntax_errors'] += 1
        
        return analysis
        
    except Exception as e:
        return {
            'file_path': file_path,
            'error': str(e),
            'sql_queries': 0,
            'select_queries': 0,
            'insert_queries': 0,
            'update_queries': 0,
            'delete_queries': 0,
            'sql_injection_patterns': 0,
            'syntax_errors': 0
        }

def analyze_jsp_file_directly(file_path: str) -> Dict[str, Any]:
    """JSP 파일 직접 분석"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        analysis = {
            'file_path': file_path,
            'scriptlets': 0,
            'jstl_tags': 0,
            'sql_strings': 0,
            'sql_injection_patterns': 0,
            'syntax_errors': 0
        }
        
        # 스크립틀릿 개수
        scriptlet_pattern = r'<%[^%]*%>'
        scriptlets = re.findall(scriptlet_pattern, content)
        analysis['scriptlets'] = len(scriptlets)
        
        # JSTL 태그 개수
        jstl_pattern = r'<c:[^>]*>'
        jstl_tags = re.findall(jstl_pattern, content)
        analysis['jstl_tags'] = len(jstl_tags)
        
        # SQL 문자열 개수
        sql_pattern = r'["\']([^"\']*(?:SELECT\s+|FROM\s+|WHERE\s+|JOIN\s+|UPDATE\s+|INSERT\s+|DELETE\s+|CREATE\s+|ALTER\s+|DROP\s+|TRUNCATE\s+|MERGE\s+)[^"\']*)["\']'
        sql_strings = re.findall(sql_pattern, content, re.IGNORECASE)
        analysis['sql_strings'] = len(sql_strings)
        
        # SQL Injection 패턴 검출
        sql_injection_pattern = r'["\']([^"\']*)\s*\+\s*[^"\']*["\']'
        sql_injection_matches = re.findall(sql_injection_pattern, content)
        analysis['sql_injection_patterns'] = len(sql_injection_matches)
        
        # JSP 문법 오류 검출
        if '<%' in content and '%>' not in content:
            analysis['syntax_errors'] += 1
        
        return analysis
        
    except Exception as e:
        return {
            'file_path': file_path,
            'error': str(e),
            'scriptlets': 0,
            'jstl_tags': 0,
            'sql_strings': 0,
            'sql_injection_patterns': 0,
            'syntax_errors': 0
        }

def analyze_metadb_results():
    """메타디비 결과 분석"""
    
    analysis = {
        'total_files': 0,
        'total_methods': 0,
        'total_classes': 0,
        'total_sql_units': 0,
        'java_files': 0,
        'xml_files': 0,
        'jsp_files': 0
    }
    
    try:
        conn = sqlite3.connect('../project/sampleSrc/metadata.db')
        cursor = conn.cursor()
        
        # 파일 개수
        cursor.execute("SELECT COUNT(*) FROM files")
        analysis['total_files'] = cursor.fetchone()[0]
        
        # Java 파일 개수
        cursor.execute("SELECT COUNT(*) FROM files WHERE language = 'java'")
        analysis['java_files'] = cursor.fetchone()[0]
        
        # 메소드 개수
        cursor.execute("SELECT COUNT(*) FROM methods")
        analysis['total_methods'] = cursor.fetchone()[0]
        
        # 클래스 개수
        cursor.execute("SELECT COUNT(*) FROM classes")
        analysis['total_classes'] = cursor.fetchone()[0]
        
        # SQL 유닛 개수
        cursor.execute("SELECT COUNT(*) FROM sql_units")
        analysis['total_sql_units'] = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"메타디비 - 총 파일 수: {analysis['total_files']}")
        print(f"메타디비 - Java 파일 수: {analysis['java_files']}")
        print(f"메타디비 - 총 메소드 수: {analysis['total_methods']}")
        print(f"메타디비 - 총 클래스 수: {analysis['total_classes']}")
        print(f"메타디비 - 총 SQL 유닛 수: {analysis['total_sql_units']}")
        
    except Exception as e:
        print(f"메타디비 분석 오류: {e}")
        analysis['error'] = str(e)
    
    return analysis

def analyze_manual_results():
    """수작업 결과 분석 (있다면)"""
    
    # 수작업 결과 파일이 있는지 확인
    manual_files = [
        './config/ground_truth_data.json',
        '../project/sampleSrc/report/수작업분석결과.md',
        '../project/sampleSrc/report/수동분석결과.md'
    ]
    
    analysis = {
        'found': False,
        'total_files': 0,
        'total_methods': 0,
        'total_classes': 0,
        'total_sql_queries': 0
    }
    
    for file_path in manual_files:
        if os.path.exists(file_path):
            analysis['found'] = True
            print(f"수작업 결과 파일 발견: {file_path}")
            # 파일 내용 분석 로직 추가 가능
            break
    
    if not analysis['found']:
        print("수작업 결과 파일을 찾을 수 없습니다.")
    
    return analysis

def compare_analyses(actual_source, metadb, manual):
    """분석 결과 비교"""
    
    print("\n=== 분석 결과 비교 ===")
    
    # 실제 소스코드 vs 메타디비
    print("\n--- 실제 소스코드 vs 메타디비 ---")
    print(f"파일 수: 실제 {actual_source['total_files']} vs 메타디비 {metadb['total_files']}")
    print(f"메소드 수: 실제 {actual_source['total_methods']} vs 메타디비 {metadb['total_methods']}")
    print(f"클래스 수: 실제 {actual_source['total_classes']} vs 메타디비 {metadb['total_classes']}")
    
    # 차이 계산
    file_diff = abs(actual_source['total_files'] - metadb['total_files'])
    method_diff = abs(actual_source['total_methods'] - metadb['total_methods'])
    class_diff = abs(actual_source['total_classes'] - metadb['total_classes'])
    
    print(f"\n차이:")
    print(f"파일 수 차이: {file_diff}")
    print(f"메소드 수 차이: {method_diff}")
    print(f"클래스 수 차이: {class_diff}")
    
    # 정확도 계산
    if actual_source['total_files'] > 0:
        file_accuracy = (1 - file_diff / actual_source['total_files']) * 100
        print(f"파일 수 정확도: {file_accuracy:.1f}%")
    
    if actual_source['total_methods'] > 0:
        method_accuracy = (1 - method_diff / actual_source['total_methods']) * 100
        print(f"메소드 수 정확도: {method_accuracy:.1f}%")
    
    if actual_source['total_classes'] > 0:
        class_accuracy = (1 - class_diff / actual_source['total_classes']) * 100
        print(f"클래스 수 정확도: {class_accuracy:.1f}%")

if __name__ == "__main__":
    verify_source_truth()
