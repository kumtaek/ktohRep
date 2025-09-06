#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
수작업 분석 검증
수작업 결과가 실제 소스코드와 일치하는지 직접 확인
"""

import os
import json
import re
from typing import Dict, List, Any

def verify_manual_analysis():
    """수작업 분석 검증"""
    
    print("=== 수작업 분석 검증 ===")
    
    # 수작업 분석 결과 로드
    manual_analysis_path = './config/ground_truth_data.json'
    if not os.path.exists(manual_analysis_path):
        print(f"수작업 분석 결과 파일이 없습니다: {manual_analysis_path}")
        return
    
    with open(manual_analysis_path, 'r', encoding='utf-8') as f:
        manual_data = json.load(f)
    
    print(f"수작업 분석 결과 로드 완료")
    
    # 실제 소스코드 분석
    source_analysis = analyze_actual_source_code()
    
    # 비교 분석
    comparison_result = compare_manual_vs_actual(manual_data, source_analysis)
    
    # 결과 출력
    print_comparison_results(comparison_result)
    
    return comparison_result

def analyze_actual_source_code():
    """실제 소스코드 분석"""
    
    print("\n=== 실제 소스코드 분석 ===")
    
    source_dir = '../project/sampleSrc/src/main/java'
    if not os.path.exists(source_dir):
        print(f"소스 디렉토리가 없습니다: {source_dir}")
        return {}
    
    analysis_result = {
        'files': [],
        'total_files': 0,
        'total_classes': 0,
        'total_methods': 0,
        'total_sql_queries': 0,
        'total_sql_injections': 0
    }
    
    # Java 파일 분석
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            if file.endswith('.java'):
                file_path = os.path.join(root, file)
                file_analysis = analyze_java_file(file_path)
                analysis_result['files'].append(file_analysis)
                analysis_result['total_files'] += 1
                analysis_result['total_classes'] += file_analysis['classes']
                analysis_result['total_methods'] += file_analysis['methods']
                analysis_result['total_sql_queries'] += file_analysis['sql_queries']
                analysis_result['total_sql_injections'] += file_analysis['sql_injections']
    
    # JSP 파일 분석
    jsp_dir = '../project/sampleSrc/src/main/webapp'
    if os.path.exists(jsp_dir):
        for root, dirs, files in os.walk(jsp_dir):
            for file in files:
                if file.endswith('.jsp'):
                    file_path = os.path.join(root, file)
                    file_analysis = analyze_jsp_file(file_path)
                    analysis_result['files'].append(file_analysis)
                    analysis_result['total_files'] += 1
                    analysis_result['total_sql_queries'] += file_analysis['sql_queries']
                    analysis_result['total_sql_injections'] += file_analysis['sql_injections']
    
    # XML 파일 분석
    xml_dir = '../project/sampleSrc/src/main/resources'
    if os.path.exists(xml_dir):
        for root, dirs, files in os.walk(xml_dir):
            for file in files:
                if file.endswith('.xml'):
                    file_path = os.path.join(root, file)
                    file_analysis = analyze_xml_file(file_path)
                    analysis_result['files'].append(file_analysis)
                    analysis_result['total_files'] += 1
                    analysis_result['total_sql_queries'] += file_analysis['sql_queries']
    
    print(f"실제 소스코드 분석 완료:")
    print(f"  총 파일 수: {analysis_result['total_files']}")
    print(f"  총 클래스 수: {analysis_result['total_classes']}")
    print(f"  총 메소드 수: {analysis_result['total_methods']}")
    print(f"  총 SQL 쿼리 수: {analysis_result['total_sql_queries']}")
    print(f"  총 SQL Injection 수: {analysis_result['total_sql_injections']}")
    
    return analysis_result

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
    
    # SQL Injection 패턴 수 계산
    sql_injection_patterns = [
        r'\+.*["\']',  # 문자열 연결
        r'StringBuilder.*append',  # StringBuilder 사용
        r'String\.format.*%s',  # String.format 사용
        r'PreparedStatement.*setString',  # PreparedStatement 사용
    ]
    
    sql_injections = 0
    for pattern in sql_injection_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        sql_injections += len(matches)
    
    return {
        'file_path': file_path,
        'file_type': 'java',
        'classes': classes,
        'methods': methods,
        'sql_queries': sql_queries,
        'sql_injections': sql_injections
    }

def analyze_jsp_file(file_path: str) -> Dict[str, Any]:
    """JSP 파일 분석"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # SQL 쿼리 수 계산
    sql_pattern = re.compile(r'["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|TRUNCATE|MERGE)[^"\']*)["\']', re.IGNORECASE)
    sql_queries = len(sql_pattern.findall(content))
    
    # SQL Injection 패턴 수 계산
    sql_injection_patterns = [
        r'\+.*["\']',  # 문자열 연결
        r'StringBuilder.*append',  # StringBuilder 사용
        r'String\.format.*%s',  # String.format 사용
    ]
    
    sql_injections = 0
    for pattern in sql_injection_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        sql_injections += len(matches)
    
    return {
        'file_path': file_path,
        'file_type': 'jsp',
        'classes': 0,
        'methods': 0,
        'sql_queries': sql_queries,
        'sql_injections': sql_injections
    }

def analyze_xml_file(file_path: str) -> Dict[str, Any]:
    """XML 파일 분석"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # SQL 쿼리 수 계산 (MyBatis 매퍼)
    sql_pattern = re.compile(r'<select|<insert|<update|<delete', re.IGNORECASE)
    sql_queries = len(sql_pattern.findall(content))
    
    return {
        'file_path': file_path,
        'file_type': 'xml',
        'classes': 0,
        'methods': 0,
        'sql_queries': sql_queries,
        'sql_injections': 0
    }

def compare_manual_vs_actual(manual_data: Dict, actual_data: Dict) -> Dict[str, Any]:
    """수작업 vs 실제 소스코드 비교"""
    
    print("\n=== 수작업 vs 실제 소스코드 비교 ===")
    
    comparison = {
        'files': {
            'manual': manual_data.get('total_files', 0),
            'actual': actual_data.get('total_files', 0),
            'difference': 0,
            'accuracy': 0.0
        },
        'classes': {
            'manual': manual_data.get('total_classes', 0),
            'actual': actual_data.get('total_classes', 0),
            'difference': 0,
            'accuracy': 0.0
        },
        'methods': {
            'manual': manual_data.get('total_methods', 0),
            'actual': actual_data.get('total_methods', 0),
            'difference': 0,
            'accuracy': 0.0
        },
        'sql_queries': {
            'manual': manual_data.get('total_sql_queries', 0),
            'actual': actual_data.get('total_sql_queries', 0),
            'difference': 0,
            'accuracy': 0.0
        },
        'sql_injections': {
            'manual': manual_data.get('total_sql_injections', 0),
            'actual': actual_data.get('total_sql_injections', 0),
            'difference': 0,
            'accuracy': 0.0
        }
    }
    
    # 차이 및 정확도 계산
    for key in comparison:
        manual_val = comparison[key]['manual']
        actual_val = comparison[key]['actual']
        
        if actual_val > 0:
            comparison[key]['difference'] = actual_val - manual_val
            comparison[key]['accuracy'] = (manual_val / actual_val) * 100
        else:
            comparison[key]['difference'] = 0
            comparison[key]['accuracy'] = 100.0 if manual_val == 0 else 0.0
    
    return comparison

def print_comparison_results(comparison: Dict[str, Any]):
    """비교 결과 출력"""
    
    print(f"\n=== 수작업 분석 검증 결과 ===")
    
    for key, data in comparison.items():
        print(f"\n{key.upper()}:")
        print(f"  수작업: {data['manual']}")
        print(f"  실제: {data['actual']}")
        print(f"  차이: {data['difference']}")
        print(f"  정확도: {data['accuracy']:.1f}%")
        
        if abs(data['difference']) > 5:
            print(f"  ⚠️ 5% 이상 차이 발생!")
        else:
            print(f"  ✅ 정확도 양호 (5% 이내)")
    
    # 전체 정확도 평가
    total_accuracy = sum(data['accuracy'] for data in comparison.values()) / len(comparison)
    print(f"\n=== 전체 정확도 평가 ===")
    print(f"평균 정확도: {total_accuracy:.1f}%")
    
    if total_accuracy >= 95:
        print("✅ 수작업 분석 결과 매우 정확함")
    elif total_accuracy >= 90:
        print("✅ 수작업 분석 결과 정확함")
    elif total_accuracy >= 80:
        print("⚠️ 수작업 분석 결과 보통")
    else:
        print("❌ 수작업 분석 결과 부정확함")

if __name__ == "__main__":
    verify_manual_analysis()
