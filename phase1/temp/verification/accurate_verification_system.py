#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
정확한 검증 시스템
실제 소스코드를 기준으로 정확한 검증 수행
"""

import os
import re
import sqlite3
from typing import Dict, List, Any, Set, Tuple

def accurate_verification_system():
    """정확한 검증 시스템"""
    
    print("=== 정확한 검증 시스템 ===")
    
    # 1. 실제 소스코드 기준점 설정
    ground_truth = establish_ground_truth()
    
    # 2. 메타디비 데이터 조회
    metadb_data = get_metadb_data()
    
    # 3. 수작업 분석 데이터 조회
    manual_data = get_manual_analysis_data()
    
    # 4. 정확한 비교 분석
    verification_result = accurate_comparison(ground_truth, metadb_data, manual_data)
    
    # 5. 결과 출력
    print_verification_results(verification_result)
    
    return verification_result

def establish_ground_truth():
    """실제 소스코드 기준점 설정"""
    
    print("\n=== 실제 소스코드 기준점 설정 ===")
    
    ground_truth = {
        'files': [],
        'total_files': 0,
        'total_classes': 0,
        'total_methods': 0,
        'total_sql_queries': 0,
        'total_imports': 0,
        'total_annotations': 0,
        'class_details': [],
        'method_details': [],
        'sql_details': [],
        'import_details': [],
        'annotation_details': []
    }
    
    # Java 파일 분석
    java_dir = '../project/sampleSrc/src/main/java'
    if os.path.exists(java_dir):
        for root, dirs, files in os.walk(java_dir):
            for file in files:
                if file.endswith('.java'):
                    file_path = os.path.join(root, file)
                    file_analysis = analyze_java_file_accurate(file_path)
                    ground_truth['files'].append(file_analysis)
                    ground_truth['total_files'] += 1
                    ground_truth['total_classes'] += len(file_analysis['classes'])
                    ground_truth['total_methods'] += len(file_analysis['methods'])
                    ground_truth['total_sql_queries'] += len(file_analysis['sql_queries'])
                    ground_truth['total_imports'] += len(file_analysis['imports'])
                    ground_truth['total_annotations'] += len(file_analysis['annotations'])
                    
                    ground_truth['class_details'].extend(file_analysis['classes'])
                    ground_truth['method_details'].extend(file_analysis['methods'])
                    ground_truth['sql_details'].extend(file_analysis['sql_queries'])
                    ground_truth['import_details'].extend(file_analysis['imports'])
                    ground_truth['annotation_details'].extend(file_analysis['annotations'])
    
    # JSP 파일 분석
    jsp_dir = '../project/sampleSrc/src/main/webapp'
    if os.path.exists(jsp_dir):
        for root, dirs, files in os.walk(jsp_dir):
            for file in files:
                if file.endswith('.jsp'):
                    file_path = os.path.join(root, file)
                    file_analysis = analyze_jsp_file_accurate(file_path)
                    ground_truth['files'].append(file_analysis)
                    ground_truth['total_files'] += 1
                    ground_truth['total_sql_queries'] += len(file_analysis['sql_queries'])
                    ground_truth['sql_details'].extend(file_analysis['sql_queries'])
    
    # XML 파일 분석
    xml_dir = '../project/sampleSrc/src/main/resources'
    if os.path.exists(xml_dir):
        for root, dirs, files in os.walk(xml_dir):
            for file in files:
                if file.endswith('.xml'):
                    file_path = os.path.join(root, file)
                    file_analysis = analyze_xml_file_accurate(file_path)
                    ground_truth['files'].append(file_analysis)
                    ground_truth['total_files'] += 1
                    ground_truth['total_sql_queries'] += len(file_analysis['sql_queries'])
                    ground_truth['sql_details'].extend(file_analysis['sql_queries'])
    
    print(f"실제 소스코드 기준점 설정 완료:")
    print(f"  총 파일 수: {ground_truth['total_files']}")
    print(f"  총 클래스 수: {ground_truth['total_classes']}")
    print(f"  총 메소드 수: {ground_truth['total_methods']}")
    print(f"  총 SQL 쿼리 수: {ground_truth['total_sql_queries']}")
    print(f"  총 Import 수: {ground_truth['total_imports']}")
    print(f"  총 어노테이션 수: {ground_truth['total_annotations']}")
    
    return ground_truth

def analyze_java_file_accurate(file_path: str) -> Dict[str, Any]:
    """Java 파일 정확한 분석"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    analysis = {
        'file_path': file_path,
        'classes': [],
        'methods': [],
        'sql_queries': [],
        'imports': [],
        'annotations': []
    }
    
    # 클래스 정확한 분석 (접근제어자 + class 키워드 필수)
    class_pattern = re.compile(r'(?:public|private|protected|abstract|final|static\s+)*\s*class\s+(\w+)', re.MULTILINE)
    class_matches = class_pattern.findall(content)
    analysis['classes'] = class_matches
    
    # 메소드 정확한 분석 (접근제어자 + 반환타입 + 메소드명 필수)
    method_pattern = re.compile(r'(?:public|private|protected)\s+(?:\w+\s+)*(\w+)\s*\([^)]*\)\s*\{', re.MULTILINE)
    method_matches = method_pattern.findall(content)
    
    # 키워드 필터링
    java_keywords = {
        'if', 'for', 'while', 'catch', 'try', 'else', 'switch', 'case', 'default',
        'break', 'continue', 'return', 'throw', 'throws', 'new', 'this', 'super',
        'static', 'final', 'abstract', 'synchronized', 'volatile', 'transient',
        'native', 'strictfp', 'interface', 'enum', 'package', 'import'
    }
    
    filtered_methods = [m for m in method_matches if m not in java_keywords]
    analysis['methods'] = filtered_methods
    
    # SQL 쿼리 정확한 분석 (문자열 리터럴 내에서만)
    sql_pattern = re.compile(r'["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|TRUNCATE|MERGE)[^"\']*)["\']', re.IGNORECASE)
    sql_matches = sql_pattern.findall(content)
    analysis['sql_queries'] = [s.strip() for s in sql_matches if len(s.strip()) > 10]
    
    # Import 정확한 분석
    import_pattern = re.compile(r'import\s+([^;]+);', re.MULTILINE)
    import_matches = import_pattern.findall(content)
    analysis['imports'] = import_matches
    
    # 어노테이션 정확한 분석
    annotation_pattern = re.compile(r'@(\w+)(?:\([^)]*\))?', re.MULTILINE)
    annotation_matches = annotation_pattern.findall(content)
    analysis['annotations'] = annotation_matches
    
    return analysis

def analyze_jsp_file_accurate(file_path: str) -> Dict[str, Any]:
    """JSP 파일 정확한 분석"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    analysis = {
        'file_path': file_path,
        'classes': [],
        'methods': [],
        'sql_queries': [],
        'imports': [],
        'annotations': []
    }
    
    # JSP 내 SQL 쿼리 분석
    sql_pattern = re.compile(r'<%.*?["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|TRUNCATE|MERGE)[^"\']*)["\'].*?%>', re.IGNORECASE | re.MULTILINE | re.DOTALL)
    sql_matches = sql_pattern.findall(content)
    analysis['sql_queries'] = [s.strip() for s in sql_matches if len(s.strip()) > 10]
    
    return analysis

def analyze_xml_file_accurate(file_path: str) -> Dict[str, Any]:
    """XML 파일 정확한 분석"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    analysis = {
        'file_path': file_path,
        'classes': [],
        'methods': [],
        'sql_queries': [],
        'imports': [],
        'annotations': []
    }
    
    # MyBatis XML 매퍼 분석
    sql_pattern = re.compile(r'<(select|insert|update|delete)[^>]*>', re.IGNORECASE)
    sql_matches = sql_pattern.findall(content)
    analysis['sql_queries'] = sql_matches
    
    return analysis

def get_metadb_data():
    """메타디비 데이터 조회"""
    
    print("\n=== 메타디비 데이터 조회 ===")
    
    metadb_path = '../project/sampleSrc/metadata.db'
    if not os.path.exists(metadb_path):
        print(f"메타디비 파일이 없습니다: {metadb_path}")
        return {}
    
    conn = sqlite3.connect(metadb_path)
    cursor = conn.cursor()
    
    metadb_data = {}
    
    # 각 테이블별 데이터 조회
    tables = ['files', 'classes', 'methods', 'sql_units', 'imports', 'annotations']
    
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            metadb_data[table] = count
        except sqlite3.OperationalError:
            metadb_data[table] = 0
    
    conn.close()
    
    print(f"메타디비 데이터:")
    for table, count in metadb_data.items():
        print(f"  {table}: {count}")
    
    return metadb_data

def get_manual_analysis_data():
    """수작업 분석 데이터 조회"""
    
    print("\n=== 수작업 분석 데이터 조회 ===")
    
    manual_data_path = './config/ground_truth_data.json'
    if not os.path.exists(manual_data_path):
        print(f"수작업 분석 데이터 파일이 없습니다: {manual_data_path}")
        return {}
    
    import json
    with open(manual_data_path, 'r', encoding='utf-8') as f:
        manual_data = json.load(f)
    
    print(f"수작업 분석 데이터:")
    print(f"  총 파일 수: {manual_data.get('total_files', 0)}")
    print(f"  총 클래스 수: {manual_data.get('total_classes', 0)}")
    print(f"  총 메소드 수: {manual_data.get('total_methods', 0)}")
    print(f"  총 SQL 쿼리 수: {manual_data.get('total_sql_queries', 0)}")
    
    return manual_data

def accurate_comparison(ground_truth: Dict, metadb_data: Dict, manual_data: Dict) -> Dict[str, Any]:
    """정확한 비교 분석"""
    
    print("\n=== 정확한 비교 분석 ===")
    
    comparison = {
        'ground_truth': ground_truth,
        'metadb_accuracy': {},
        'manual_accuracy': {},
        'recommendations': []
    }
    
    # 메타디비 정확도 계산
    metadb_accuracy = {
        'files': calculate_accuracy(ground_truth['total_files'], metadb_data.get('files', 0)),
        'classes': calculate_accuracy(ground_truth['total_classes'], metadb_data.get('classes', 0)),
        'methods': calculate_accuracy(ground_truth['total_methods'], metadb_data.get('methods', 0)),
        'sql_queries': calculate_accuracy(ground_truth['total_sql_queries'], metadb_data.get('sql_units', 0)),
        'imports': calculate_accuracy(ground_truth['total_imports'], metadb_data.get('imports', 0)),
        'annotations': calculate_accuracy(ground_truth['total_annotations'], metadb_data.get('annotations', 0))
    }
    
    # 수작업 분석 정확도 계산
    manual_accuracy = {
        'files': calculate_accuracy(ground_truth['total_files'], manual_data.get('total_files', 0)),
        'classes': calculate_accuracy(ground_truth['total_classes'], manual_data.get('total_classes', 0)),
        'methods': calculate_accuracy(ground_truth['total_methods'], manual_data.get('total_methods', 0)),
        'sql_queries': calculate_accuracy(ground_truth['total_sql_queries'], manual_data.get('total_sql_queries', 0))
    }
    
    comparison['metadb_accuracy'] = metadb_accuracy
    comparison['manual_accuracy'] = manual_accuracy
    
    # 개선 권장사항 생성
    recommendations = generate_recommendations(metadb_accuracy, manual_accuracy)
    comparison['recommendations'] = recommendations
    
    return comparison

def calculate_accuracy(ground_truth_count: int, actual_count: int) -> Dict[str, Any]:
    """정확도 계산"""
    
    if ground_truth_count == 0:
        return {
            'ground_truth': 0,
            'actual': actual_count,
            'difference': actual_count,
            'accuracy': 100.0 if actual_count == 0 else 0.0,
            'status': 'accurate' if actual_count == 0 else 'overextraction'
        }
    
    difference = actual_count - ground_truth_count
    accuracy = (actual_count / ground_truth_count) * 100
    
    if abs(difference) <= 5:
        status = 'accurate'
    elif difference > 5:
        status = 'overextraction'
    else:
        status = 'underextraction'
    
    return {
        'ground_truth': ground_truth_count,
        'actual': actual_count,
        'difference': difference,
        'accuracy': accuracy,
        'status': status
    }

def generate_recommendations(metadb_accuracy: Dict, manual_accuracy: Dict) -> List[str]:
    """개선 권장사항 생성"""
    
    recommendations = []
    
    # 메타디비 개선 권장사항
    for key, data in metadb_accuracy.items():
        if data['status'] == 'overextraction':
            recommendations.append(f"메타디비 {key} 과다추출 수정 필요: {data['actual']} -> {data['ground_truth']}")
        elif data['status'] == 'underextraction':
            recommendations.append(f"메타디비 {key} 과소추출 수정 필요: {data['actual']} -> {data['ground_truth']}")
    
    # 수작업 분석 개선 권장사항
    for key, data in manual_accuracy.items():
        if data['status'] == 'overextraction':
            recommendations.append(f"수작업 분석 {key} 과다추출 수정 필요: {data['actual']} -> {data['ground_truth']}")
        elif data['status'] == 'underextraction':
            recommendations.append(f"수작업 분석 {key} 과소추출 수정 필요: {data['actual']} -> {data['ground_truth']}")
    
    return recommendations

def print_verification_results(comparison: Dict[str, Any]):
    """검증 결과 출력"""
    
    print(f"\n=== 정확한 검증 결과 ===")
    
    print(f"\n--- 메타디비 정확도 ---")
    for key, data in comparison['metadb_accuracy'].items():
        print(f"{key.upper()}:")
        print(f"  기준점: {data['ground_truth']}")
        print(f"  메타디비: {data['actual']}")
        print(f"  차이: {data['difference']:+d}")
        print(f"  정확도: {data['accuracy']:.1f}%")
        print(f"  상태: {data['status'].upper()}")
    
    print(f"\n--- 수작업 분석 정확도 ---")
    for key, data in comparison['manual_accuracy'].items():
        print(f"{key.upper()}:")
        print(f"  기준점: {data['ground_truth']}")
        print(f"  수작업: {data['actual']}")
        print(f"  차이: {data['difference']:+d}")
        print(f"  정확도: {data['accuracy']:.1f}%")
        print(f"  상태: {data['status'].upper()}")
    
    print(f"\n--- 개선 권장사항 ---")
    for i, recommendation in enumerate(comparison['recommendations'], 1):
        print(f"{i}. {recommendation}")
    
    # 전체 평가
    metadb_avg_accuracy = sum(data['accuracy'] for data in comparison['metadb_accuracy'].values()) / len(comparison['metadb_accuracy'])
    manual_avg_accuracy = sum(data['accuracy'] for data in comparison['manual_accuracy'].values()) / len(comparison['manual_accuracy'])
    
    print(f"\n--- 전체 평가 ---")
    print(f"메타디비 평균 정확도: {metadb_avg_accuracy:.1f}%")
    print(f"수작업 분석 평균 정확도: {manual_avg_accuracy:.1f}%")
    
    if metadb_avg_accuracy > manual_avg_accuracy:
        print("결론: 메타디비가 수작업 분석보다 정확함")
    elif manual_avg_accuracy > metadb_avg_accuracy:
        print("결론: 수작업 분석이 메타디비보다 정확함")
    else:
        print("결론: 메타디비와 수작업 분석이 비슷한 정확도")

if __name__ == "__main__":
    accurate_verification_system()
