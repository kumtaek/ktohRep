#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
메타디비 검증
메타디비 결과가 실제 소스코드와 일치하는지 직접 확인
"""

import os
import sqlite3
import json
from typing import Dict, List, Any

def verify_metadb():
    """메타디비 검증"""
    
    print("=== 메타디비 검증 ===")
    
    # 메타디비 경로
    metadb_path = '../project/sampleSrc/metadata.db'
    if not os.path.exists(metadb_path):
        print(f"메타디비 파일이 없습니다: {metadb_path}")
        return
    
    # 메타디비 연결
    conn = sqlite3.connect(metadb_path)
    cursor = conn.cursor()
    
    # 메타디비 데이터 조회
    metadb_data = query_metadb_data(cursor)
    
    # 실제 소스코드 분석
    actual_data = analyze_actual_source_code()
    
    # 비교 분석
    comparison_result = compare_metadb_vs_actual(metadb_data, actual_data)
    
    # 결과 출력
    print_comparison_results(comparison_result)
    
    conn.close()
    
    return comparison_result

def query_metadb_data(cursor):
    """메타디비 데이터 조회"""
    
    print("\n=== 메타디비 데이터 조회 ===")
    
    metadb_data = {}
    
    # 파일 수 조회
    cursor.execute("SELECT COUNT(*) FROM files")
    metadb_data['total_files'] = cursor.fetchone()[0]
    
    # Java 파일 수 조회
    cursor.execute("SELECT COUNT(*) FROM files WHERE language = 'java'")
    metadb_data['java_files'] = cursor.fetchone()[0]
    
    # JSP 파일 수 조회
    cursor.execute("SELECT COUNT(*) FROM files WHERE language = 'jsp'")
    metadb_data['jsp_files'] = cursor.fetchone()[0]
    
    # XML 파일 수 조회
    cursor.execute("SELECT COUNT(*) FROM files WHERE language = 'xml'")
    metadb_data['xml_files'] = cursor.fetchone()[0]
    
    # 클래스 수 조회
    cursor.execute("SELECT COUNT(*) FROM classes")
    metadb_data['total_classes'] = cursor.fetchone()[0]
    
    # 메소드 수 조회
    cursor.execute("SELECT COUNT(*) FROM methods")
    metadb_data['total_methods'] = cursor.fetchone()[0]
    
    # SQL Units 수 조회
    cursor.execute("SELECT COUNT(*) FROM sql_units")
    metadb_data['total_sql_units'] = cursor.fetchone()[0]
    
    # 테이블 수 조회
    cursor.execute("SELECT COUNT(*) FROM db_tables")
    metadb_data['total_tables'] = cursor.fetchone()[0]
    
    # 컬럼 수 조회
    cursor.execute("SELECT COUNT(*) FROM db_columns")
    metadb_data['total_columns'] = cursor.fetchone()[0]
    
    print(f"메타디비 데이터 조회 완료:")
    print(f"  총 파일 수: {metadb_data['total_files']}")
    print(f"  Java 파일 수: {metadb_data['java_files']}")
    print(f"  JSP 파일 수: {metadb_data['jsp_files']}")
    print(f"  XML 파일 수: {metadb_data['xml_files']}")
    print(f"  총 클래스 수: {metadb_data['total_classes']}")
    print(f"  총 메소드 수: {metadb_data['total_methods']}")
    print(f"  총 SQL Units 수: {metadb_data['total_sql_units']}")
    print(f"  총 테이블 수: {metadb_data['total_tables']}")
    print(f"  총 컬럼 수: {metadb_data['total_columns']}")
    
    return metadb_data

def analyze_actual_source_code():
    """실제 소스코드 분석"""
    
    print("\n=== 실제 소스코드 분석 ===")
    
    actual_data = {
        'total_files': 0,
        'java_files': 0,
        'jsp_files': 0,
        'xml_files': 0,
        'total_classes': 0,
        'total_methods': 0,
        'total_sql_queries': 0,
        'total_tables': 0,
        'total_columns': 0
    }
    
    # Java 파일 분석
    java_dir = '../project/sampleSrc/src/main/java'
    if os.path.exists(java_dir):
        for root, dirs, files in os.walk(java_dir):
            for file in files:
                if file.endswith('.java'):
                    actual_data['total_files'] += 1
                    actual_data['java_files'] += 1
                    
                    file_path = os.path.join(root, file)
                    file_analysis = analyze_java_file(file_path)
                    actual_data['total_classes'] += file_analysis['classes']
                    actual_data['total_methods'] += file_analysis['methods']
                    actual_data['total_sql_queries'] += file_analysis['sql_queries']
    
    # JSP 파일 분석
    jsp_dir = '../project/sampleSrc/src/main/webapp'
    if os.path.exists(jsp_dir):
        for root, dirs, files in os.walk(jsp_dir):
            for file in files:
                if file.endswith('.jsp'):
                    actual_data['total_files'] += 1
                    actual_data['jsp_files'] += 1
                    
                    file_path = os.path.join(root, file)
                    file_analysis = analyze_jsp_file(file_path)
                    actual_data['total_sql_queries'] += file_analysis['sql_queries']
    
    # XML 파일 분석
    xml_dir = '../project/sampleSrc/src/main/resources'
    if os.path.exists(xml_dir):
        for root, dirs, files in os.walk(xml_dir):
            for file in files:
                if file.endswith('.xml'):
                    actual_data['total_files'] += 1
                    actual_data['xml_files'] += 1
                    
                    file_path = os.path.join(root, file)
                    file_analysis = analyze_xml_file(file_path)
                    actual_data['total_sql_queries'] += file_analysis['sql_queries']
    
    print(f"실제 소스코드 분석 완료:")
    print(f"  총 파일 수: {actual_data['total_files']}")
    print(f"  Java 파일 수: {actual_data['java_files']}")
    print(f"  JSP 파일 수: {actual_data['jsp_files']}")
    print(f"  XML 파일 수: {actual_data['xml_files']}")
    print(f"  총 클래스 수: {actual_data['total_classes']}")
    print(f"  총 메소드 수: {actual_data['total_methods']}")
    print(f"  총 SQL 쿼리 수: {actual_data['total_sql_queries']}")
    
    return actual_data

def analyze_java_file(file_path: str) -> Dict[str, Any]:
    """Java 파일 분석"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 클래스 수 계산
    class_pattern = re.compile(r'class\s+(\w+)', re.MULTILINE)
    classes = len(class_pattern.findall(content))
    
    # 메소드 수 계산 (간단한 패턴)
    method_pattern = re.compile(r'(\w+)\s*\([^)]*\)\s*\{', re.MULTILINE)
    methods = len(method_pattern.findall(content))
    
    # SQL 쿼리 수 계산
    sql_pattern = re.compile(r'["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|TRUNCATE|MERGE)[^"\']*)["\']', re.IGNORECASE)
    sql_queries = len(sql_pattern.findall(content))
    
    return {
        'classes': classes,
        'methods': methods,
        'sql_queries': sql_queries
    }

def analyze_jsp_file(file_path: str) -> Dict[str, Any]:
    """JSP 파일 분석"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # SQL 쿼리 수 계산
    sql_pattern = re.compile(r'["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|TRUNCATE|MERGE)[^"\']*)["\']', re.IGNORECASE)
    sql_queries = len(sql_pattern.findall(content))
    
    return {
        'sql_queries': sql_queries
    }

def analyze_xml_file(file_path: str) -> Dict[str, Any]:
    """XML 파일 분석"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # SQL 쿼리 수 계산 (MyBatis 매퍼)
    sql_pattern = re.compile(r'<select|<insert|<update|<delete', re.IGNORECASE)
    sql_queries = len(sql_pattern.findall(content))
    
    return {
        'sql_queries': sql_queries
    }

def compare_metadb_vs_actual(metadb_data: Dict, actual_data: Dict) -> Dict[str, Any]:
    """메타디비 vs 실제 소스코드 비교"""
    
    print("\n=== 메타디비 vs 실제 소스코드 비교 ===")
    
    comparison = {
        'files': {
            'metadb': metadb_data.get('total_files', 0),
            'actual': actual_data.get('total_files', 0),
            'difference': 0,
            'accuracy': 0.0
        },
        'java_files': {
            'metadb': metadb_data.get('java_files', 0),
            'actual': actual_data.get('java_files', 0),
            'difference': 0,
            'accuracy': 0.0
        },
        'jsp_files': {
            'metadb': metadb_data.get('jsp_files', 0),
            'actual': actual_data.get('jsp_files', 0),
            'difference': 0,
            'accuracy': 0.0
        },
        'xml_files': {
            'metadb': metadb_data.get('xml_files', 0),
            'actual': actual_data.get('xml_files', 0),
            'difference': 0,
            'accuracy': 0.0
        },
        'classes': {
            'metadb': metadb_data.get('total_classes', 0),
            'actual': actual_data.get('total_classes', 0),
            'difference': 0,
            'accuracy': 0.0
        },
        'methods': {
            'metadb': metadb_data.get('total_methods', 0),
            'actual': actual_data.get('total_methods', 0),
            'difference': 0,
            'accuracy': 0.0
        },
        'sql_queries': {
            'metadb': metadb_data.get('total_sql_units', 0),
            'actual': actual_data.get('total_sql_queries', 0),
            'difference': 0,
            'accuracy': 0.0
        }
    }
    
    # 차이 및 정확도 계산
    for key in comparison:
        metadb_val = comparison[key]['metadb']
        actual_val = comparison[key]['actual']
        
        if actual_val > 0:
            comparison[key]['difference'] = metadb_val - actual_val
            comparison[key]['accuracy'] = (metadb_val / actual_val) * 100
        else:
            comparison[key]['difference'] = 0
            comparison[key]['accuracy'] = 100.0 if metadb_val == 0 else 0.0
    
    return comparison

def print_comparison_results(comparison: Dict[str, Any]):
    """비교 결과 출력"""
    
    print(f"\n=== 메타디비 검증 결과 ===")
    
    for key, data in comparison.items():
        print(f"\n{key.upper()}:")
        print(f"  메타디비: {data['metadb']}")
        print(f"  실제: {data['actual']}")
        print(f"  차이: {data['difference']}")
        print(f"  정확도: {data['accuracy']:.1f}%")
        
        if abs(data['difference']) > 5:
            print(f"  WARNING: 5% 이상 차이 발생!")
        else:
            print(f"  OK: 정확도 양호 (5% 이내)")
    
    # 전체 정확도 평가
    total_accuracy = sum(data['accuracy'] for data in comparison.values()) / len(comparison)
    print(f"\n=== 전체 정확도 평가 ===")
    print(f"평균 정확도: {total_accuracy:.1f}%")
    
    if total_accuracy >= 95:
        print("✅ 메타디비 결과 매우 정확함")
    elif total_accuracy >= 90:
        print("✅ 메타디비 결과 정확함")
    elif total_accuracy >= 80:
        print("⚠️ 메타디비 결과 보통")
    else:
        print("❌ 메타디비 결과 부정확함")

if __name__ == "__main__":
    import re
    verify_metadb()
