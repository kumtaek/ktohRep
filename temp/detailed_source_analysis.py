#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
상세 소스코드 분석
과다추출 vs 과소추출 문제 정확한 진단
"""

import os
import re
import ast
from typing import Dict, List, Any, Set

def detailed_source_analysis():
    """상세 소스코드 분석"""
    
    print("=== 상세 소스코드 분석 ===")
    
    # 실제 소스코드 상세 분석
    actual_analysis = analyze_all_source_files()
    
    # 메타디비 데이터와 비교
    metadb_analysis = get_metadb_data()
    
    # 상세 비교 분석
    detailed_comparison = compare_detailed_analysis(actual_analysis, metadb_analysis)
    
    # 결과 출력
    print_detailed_results(detailed_comparison)
    
    return detailed_comparison

def analyze_all_source_files():
    """모든 소스 파일 상세 분석"""
    
    print("\n=== 모든 소스 파일 상세 분석 ===")
    
    analysis = {
        'files': [],
        'total_files': 0,
        'total_classes': 0,
        'total_methods': 0,
        'total_sql_queries': 0,
        'total_imports': 0,
        'total_annotations': 0,
        'file_details': {}
    }
    
    # Java 파일 상세 분석
    java_dir = '../project/sampleSrc/src/main/java'
    if os.path.exists(java_dir):
        for root, dirs, files in os.walk(java_dir):
            for file in files:
                if file.endswith('.java'):
                    file_path = os.path.join(root, file)
                    file_analysis = analyze_java_file_detailed(file_path)
                    analysis['files'].append(file_analysis)
                    analysis['total_files'] += 1
                    analysis['total_classes'] += file_analysis['classes']
                    analysis['total_methods'] += file_analysis['methods']
                    analysis['total_sql_queries'] += file_analysis['sql_queries']
                    analysis['total_imports'] += file_analysis['imports']
                    analysis['total_annotations'] += file_analysis['annotations']
                    analysis['file_details'][file_path] = file_analysis
    
    # JSP 파일 상세 분석
    jsp_dir = '../project/sampleSrc/src/main/webapp'
    if os.path.exists(jsp_dir):
        for root, dirs, files in os.walk(jsp_dir):
            for file in files:
                if file.endswith('.jsp'):
                    file_path = os.path.join(root, file)
                    file_analysis = analyze_jsp_file_detailed(file_path)
                    analysis['files'].append(file_analysis)
                    analysis['total_files'] += 1
                    analysis['total_sql_queries'] += file_analysis['sql_queries']
                    analysis['file_details'][file_path] = file_analysis
    
    # XML 파일 상세 분석
    xml_dir = '../project/sampleSrc/src/main/resources'
    if os.path.exists(xml_dir):
        for root, dirs, files in os.walk(xml_dir):
            for file in files:
                if file.endswith('.xml'):
                    file_path = os.path.join(root, file)
                    file_analysis = analyze_xml_file_detailed(file_path)
                    analysis['files'].append(file_analysis)
                    analysis['total_files'] += 1
                    analysis['total_sql_queries'] += file_analysis['sql_queries']
                    analysis['file_details'][file_path] = file_analysis
    
    print(f"상세 분석 완료:")
    print(f"  총 파일 수: {analysis['total_files']}")
    print(f"  총 클래스 수: {analysis['total_classes']}")
    print(f"  총 메소드 수: {analysis['total_methods']}")
    print(f"  총 SQL 쿼리 수: {analysis['total_sql_queries']}")
    print(f"  총 Import 수: {analysis['total_imports']}")
    print(f"  총 어노테이션 수: {analysis['total_annotations']}")
    
    return analysis

def analyze_java_file_detailed(file_path: str) -> Dict[str, Any]:
    """Java 파일 상세 분석"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    analysis = {
        'file_path': file_path,
        'file_type': 'java',
        'classes': 0,
        'methods': 0,
        'sql_queries': 0,
        'imports': 0,
        'annotations': 0,
        'class_details': [],
        'method_details': [],
        'sql_details': [],
        'import_details': [],
        'annotation_details': []
    }
    
    # 클래스 상세 분석
    class_pattern = re.compile(r'(?:public|private|protected|abstract|final|static\s+)*\s*class\s+(\w+)', re.MULTILINE)
    class_matches = class_pattern.findall(content)
    analysis['classes'] = len(class_matches)
    analysis['class_details'] = class_matches
    
    # 메소드 상세 분석 (더 정확한 패턴)
    method_patterns = [
        # public/private/protected 메소드
        r'(?:public|private|protected)\s+(?:\w+\s+)*(\w+)\s*\([^)]*\)\s*\{',
        # 생성자
        r'(\w+)\s*\([^)]*\)\s*\{',
        # 어노테이션이 있는 메소드
        r'@\w+(?:\([^)]*\))?\s*(?:\w+\s+)*(\w+)\s*\([^)]*\)\s*\{'
    ]
    
    all_methods = set()
    for pattern in method_patterns:
        matches = re.findall(pattern, content, re.MULTILINE)
        for match in matches:
            if match not in ['if', 'for', 'while', 'catch', 'try', 'else', 'switch', 'case']:
                all_methods.add(match)
    
    analysis['methods'] = len(all_methods)
    analysis['method_details'] = list(all_methods)
    
    # SQL 쿼리 상세 분석
    sql_patterns = [
        # 문자열 리터럴 내 SQL
        r'["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|TRUNCATE|MERGE)[^"\']*)["\']',
        # StringBuilder SQL
        r'StringBuilder.*?append\s*\(\s*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|TRUNCATE|MERGE)[^"\']*)["\']',
        # MyBatis XML 태그
        r'<select|<insert|<update|<delete'
    ]
    
    all_sqls = set()
    for pattern in sql_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            if isinstance(match, str) and len(match.strip()) > 10:
                all_sqls.add(match.strip())
            elif isinstance(match, tuple):
                for m in match:
                    if isinstance(m, str) and len(m.strip()) > 10:
                        all_sqls.add(m.strip())
    
    analysis['sql_queries'] = len(all_sqls)
    analysis['sql_details'] = list(all_sqls)
    
    # Import 상세 분석
    import_pattern = re.compile(r'import\s+([^;]+);', re.MULTILINE)
    import_matches = import_pattern.findall(content)
    analysis['imports'] = len(import_matches)
    analysis['import_details'] = import_matches
    
    # 어노테이션 상세 분석
    annotation_pattern = re.compile(r'@(\w+)(?:\([^)]*\))?', re.MULTILINE)
    annotation_matches = annotation_pattern.findall(content)
    analysis['annotations'] = len(annotation_matches)
    analysis['annotation_details'] = annotation_matches
    
    return analysis

def analyze_jsp_file_detailed(file_path: str) -> Dict[str, Any]:
    """JSP 파일 상세 분석"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    analysis = {
        'file_path': file_path,
        'file_type': 'jsp',
        'classes': 0,
        'methods': 0,
        'sql_queries': 0,
        'imports': 0,
        'annotations': 0,
        'sql_details': []
    }
    
    # JSP 내 SQL 쿼리 분석
    sql_patterns = [
        # JSP 스크립틀릿 내 SQL
        r'<%.*?["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|TRUNCATE|MERGE)[^"\']*)["\'].*?%>',
        # JSP 표현식 내 SQL
        r'<%=.*?["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|TRUNCATE|MERGE)[^"\']*)["\'].*?%>'
    ]
    
    all_sqls = set()
    for pattern in sql_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        for match in matches:
            if len(match.strip()) > 10:
                all_sqls.add(match.strip())
    
    analysis['sql_queries'] = len(all_sqls)
    analysis['sql_details'] = list(all_sqls)
    
    return analysis

def analyze_xml_file_detailed(file_path: str) -> Dict[str, Any]:
    """XML 파일 상세 분석"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    analysis = {
        'file_path': file_path,
        'file_type': 'xml',
        'classes': 0,
        'methods': 0,
        'sql_queries': 0,
        'imports': 0,
        'annotations': 0,
        'sql_details': []
    }
    
    # MyBatis XML 매퍼 분석
    sql_patterns = [
        # MyBatis SQL 태그
        r'<(select|insert|update|delete)[^>]*>',
        # SQL 문장
        r'["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|TRUNCATE|MERGE)[^"\']*)["\']'
    ]
    
    all_sqls = set()
    for pattern in sql_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            if isinstance(match, str) and len(match.strip()) > 5:
                all_sqls.add(match.strip())
    
    analysis['sql_queries'] = len(all_sqls)
    analysis['sql_details'] = list(all_sqls)
    
    return analysis

def get_metadb_data():
    """메타디비 데이터 조회"""
    
    print("\n=== 메타디비 데이터 조회 ===")
    
    import sqlite3
    
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

def compare_detailed_analysis(actual: Dict, metadb: Dict) -> Dict[str, Any]:
    """상세 분석 비교"""
    
    print("\n=== 상세 분석 비교 ===")
    
    comparison = {
        'files': {
            'actual': actual.get('total_files', 0),
            'metadb': metadb.get('files', 0),
            'difference': 0,
            'accuracy': 0.0,
            'status': 'unknown'
        },
        'classes': {
            'actual': actual.get('total_classes', 0),
            'metadb': metadb.get('classes', 0),
            'difference': 0,
            'accuracy': 0.0,
            'status': 'unknown'
        },
        'methods': {
            'actual': actual.get('total_methods', 0),
            'metadb': metadb.get('methods', 0),
            'difference': 0,
            'accuracy': 0.0,
            'status': 'unknown'
        },
        'sql_queries': {
            'actual': actual.get('total_sql_queries', 0),
            'metadb': metadb.get('sql_units', 0),
            'difference': 0,
            'accuracy': 0.0,
            'status': 'unknown'
        },
        'imports': {
            'actual': actual.get('total_imports', 0),
            'metadb': metadb.get('imports', 0),
            'difference': 0,
            'accuracy': 0.0,
            'status': 'unknown'
        },
        'annotations': {
            'actual': actual.get('total_annotations', 0),
            'metadb': metadb.get('annotations', 0),
            'difference': 0,
            'accuracy': 0.0,
            'status': 'unknown'
        }
    }
    
    # 차이 및 정확도 계산
    for key, data in comparison.items():
        actual_val = data['actual']
        metadb_val = data['metadb']
        
        data['difference'] = metadb_val - actual_val
        
        if actual_val > 0:
            data['accuracy'] = (metadb_val / actual_val) * 100
        else:
            data['accuracy'] = 100.0 if metadb_val == 0 else 0.0
        
        # 상태 판단
        if abs(data['difference']) <= 5:
            data['status'] = 'accurate'
        elif data['difference'] > 5:
            data['status'] = 'overextraction'
        else:
            data['status'] = 'underextraction'
    
    return comparison

def print_detailed_results(comparison: Dict[str, Any]):
    """상세 결과 출력"""
    
    print(f"\n=== 상세 분석 결과 ===")
    
    for key, data in comparison.items():
        print(f"\n{key.upper()}:")
        print(f"  실제 소스코드: {data['actual']}")
        print(f"  메타디비: {data['metadb']}")
        print(f"  차이: {data['difference']:+d}")
        print(f"  정확도: {data['accuracy']:.1f}%")
        
        if data['status'] == 'accurate':
            print(f"  상태: ACCURATE (정확함)")
        elif data['status'] == 'overextraction':
            print(f"  상태: OVEREXTRACTION (과다추출)")
        else:
            print(f"  상태: UNDEREXTRACTION (과소추출)")
    
    # 전체 평가
    print(f"\n=== 전체 평가 ===")
    
    overextraction_count = sum(1 for data in comparison.values() if data['status'] == 'overextraction')
    underextraction_count = sum(1 for data in comparison.values() if data['status'] == 'underextraction')
    accurate_count = sum(1 for data in comparison.values() if data['status'] == 'accurate')
    
    print(f"정확한 항목: {accurate_count}개")
    print(f"과다추출 항목: {overextraction_count}개")
    print(f"과소추출 항목: {underextraction_count}개")
    
    if overextraction_count > underextraction_count:
        print("결론: 과다추출이 주요 문제")
    elif underextraction_count > overextraction_count:
        print("결론: 과소추출이 주요 문제")
    else:
        print("결론: 과다추출과 과소추출이 혼재")

if __name__ == "__main__":
    detailed_source_analysis()



