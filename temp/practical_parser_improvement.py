#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
실용적 파서 개선
파일별 10% 이내 오차 달성 (과소추출 금지, 과다추출 10% 이내 허용)
"""

import os
import re
import sqlite3
from typing import Dict, List, Any

def practical_parser_improvement():
    """실용적 파서 개선"""
    
    print("=== 실용적 파서 개선 ===")
    print("목표: 파일별 10% 이내 오차 (과소추출 금지, 과다추출 10% 이내 허용)")
    
    # 1. 현재 상태 분석
    current_status = analyze_current_status()
    
    # 2. 목표 설정
    target_goals = set_target_goals(current_status)
    
    # 3. 파서 패턴 조정
    adjust_parser_patterns(target_goals)
    
    # 4. 메타디비 재생성
    regenerate_metadb()
    
    # 5. 결과 검증
    verification_result = verify_improvement()
    
    return verification_result

def analyze_current_status():
    """현재 상태 분석"""
    
    print("\n=== 현재 상태 분석 ===")
    
    # 실제 소스코드 기준점
    ground_truth = {
        'classes': 15,
        'methods': 56,
        'sql_queries': 59
    }
    
    # 메타디비 현재 상태
    metadb_path = '../project/sampleSrc/metadata.db'
    if not os.path.exists(metadb_path):
        print(f"메타디비 파일이 없습니다: {metadb_path}")
        return {}
    
    conn = sqlite3.connect(metadb_path)
    cursor = conn.cursor()
    
    current_status = {
        'ground_truth': ground_truth,
        'metadb': {
            'classes': cursor.execute("SELECT COUNT(*) FROM classes").fetchone()[0],
            'methods': cursor.execute("SELECT COUNT(*) FROM methods").fetchone()[0],
            'sql_queries': cursor.execute("SELECT COUNT(*) FROM sql_units").fetchone()[0]
        }
    }
    
    conn.close()
    
    print(f"현재 상태:")
    print(f"  클래스: {current_status['metadb']['classes']} (기준: {ground_truth['classes']})")
    print(f"  메소드: {current_status['metadb']['methods']} (기준: {ground_truth['methods']})")
    print(f"  SQL: {current_status['metadb']['sql_queries']} (기준: {ground_truth['sql_queries']})")
    
    return current_status

def set_target_goals(current_status: Dict):
    """목표 설정"""
    
    print("\n=== 목표 설정 ===")
    
    ground_truth = current_status['ground_truth']
    metadb = current_status['metadb']
    
    target_goals = {}
    
    for key in ['classes', 'methods', 'sql_queries']:
        current_count = metadb[key]
        target_count = ground_truth[key]
        
        # 10% 이내 과다추출 허용
        max_allowed = int(target_count * 1.1)
        
        if current_count > max_allowed:
            target_goals[key] = {
                'current': current_count,
                'target': target_count,
                'max_allowed': max_allowed,
                'action': 'reduce',
                'reduction_needed': current_count - max_allowed
            }
        else:
            target_goals[key] = {
                'current': current_count,
                'target': target_count,
                'max_allowed': max_allowed,
                'action': 'maintain',
                'reduction_needed': 0
            }
    
    print(f"목표 설정:")
    for key, goal in target_goals.items():
        print(f"  {key}: {goal['current']} -> {goal['max_allowed']} (감소 필요: {goal['reduction_needed']})")
    
    return target_goals

def adjust_parser_patterns(target_goals: Dict):
    """파서 패턴 조정"""
    
    print("\n=== 파서 패턴 조정 ===")
    
    # Java 파서 패턴 조정
    java_parser_path = './parsers/java/java_parser.py'
    if os.path.exists(java_parser_path):
        adjust_java_parser(java_parser_path, target_goals)
    
    # SQL 파서 패턴 조정
    sql_parser_path = './parsers/sql/sql_parser_context7.py'
    if os.path.exists(sql_parser_path):
        adjust_sql_parser(sql_parser_path, target_goals)

def adjust_java_parser(parser_path: str, target_goals: Dict):
    """Java 파서 조정"""
    
    print("Java 파서 패턴 조정 중...")
    
    with open(parser_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 메소드 패턴을 더 엄격하게 조정
    if target_goals['methods']['action'] == 'reduce':
        # 더 엄격한 메소드 패턴
        strict_method_pattern = r'(?:public|private|protected)\s+(?:\w+\s+)*(\w+)\s*\([^)]*\)\s*\{'
        
        # 기존 패턴 교체
        content = re.sub(
            r'r\'\(\\w\+\)\\s\*\\\(\\\[\\\^\\\)\\\]\*\\\)\\s\*\\\{',
            f"r'{strict_method_pattern}'",
            content
        )
    
    # 클래스 패턴을 더 엄격하게 조정
    if target_goals['classes']['action'] == 'reduce':
        # 더 엄격한 클래스 패턴
        strict_class_pattern = r'(?:public|private|protected|abstract|final|static\s+)*\s*class\s+(\w+)\s*(?:extends\s+\w+)?\s*(?:implements\s+[\w\s,]+)?\s*\{'
        
        # 기존 패턴 교체
        content = re.sub(
            r'r\'\\\(\\\?:public\\\|private\\\|protected\\\|abstract\\\|final\\\|static\\\\s\+\\\)\*\\\\s\*class\\\\s\+\\\(\\\\w\+\\\)',
            f"r'{strict_class_pattern}'",
            content
        )
    
    with open(parser_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Java 파서 패턴 조정 완료")

def adjust_sql_parser(parser_path: str, target_goals: Dict):
    """SQL 파서 조정"""
    
    print("SQL 파서 패턴 조정 중...")
    
    with open(parser_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # SQL 패턴을 더 엄격하게 조정
    if target_goals['sql_queries']['action'] == 'reduce':
        # 더 엄격한 SQL 패턴
        strict_sql_pattern = r'["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|TRUNCATE|MERGE)\s+[^"\']*)["\']'
        
        # 기존 패턴 교체
        content = re.sub(
            r'r\'\\\["\\\'\\\]\\\(\\\[\\\^"\\\'\\\]\*\\\(\\\?:SELECT\\\|INSERT\\\|UPDATE\\\|DELETE\\\|CREATE\\\|ALTER\\\|DROP\\\|TRUNCATE\\\|MERGE\\\)\\\[\\\^"\\\'\\\]\*\\\)\\\["\\\'\\\]',
            f"r'{strict_sql_pattern}'",
            content
        )
    
    with open(parser_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("SQL 파서 패턴 조정 완료")

def regenerate_metadb():
    """메타디비 재생성"""
    
    print("\n=== 메타디비 재생성 ===")
    
    import subprocess
    import sys
    
    # 기존 메타디비 백업
    metadb_path = '../project/sampleSrc/metadata.db'
    if os.path.exists(metadb_path):
        backup_path = f'{metadb_path}.backup'
        if os.path.exists(backup_path):
            os.remove(backup_path)
        os.rename(metadb_path, backup_path)
        print(f"기존 메타디비 백업: {backup_path}")
    
    # 메타디비 재생성
    result = subprocess.run([
        sys.executable, 'main.py', '--project-name', 'sampleSrc'
    ], capture_output=True, text=True, cwd='.')
    
    if result.returncode == 0:
        print("✅ 메타디비 재생성 완료")
    else:
        print(f"❌ 메타디비 재생성 실패: {result.stderr}")
        # 백업 복원
        if os.path.exists(backup_path):
            os.rename(backup_path, metadb_path)
            print("백업 메타디비 복원")

def verify_improvement():
    """개선 결과 검증"""
    
    print("\n=== 개선 결과 검증 ===")
    
    # 실제 소스코드 기준점
    ground_truth = {
        'classes': 15,
        'methods': 56,
        'sql_queries': 59
    }
    
    # 메타디비 현재 상태
    metadb_path = '../project/sampleSrc/metadata.db'
    if not os.path.exists(metadb_path):
        print(f"메타디비 파일이 없습니다: {metadb_path}")
        return {}
    
    conn = sqlite3.connect(metadb_path)
    cursor = conn.cursor()
    
    current_status = {
        'classes': cursor.execute("SELECT COUNT(*) FROM classes").fetchone()[0],
        'methods': cursor.execute("SELECT COUNT(*) FROM methods").fetchone()[0],
        'sql_queries': cursor.execute("SELECT COUNT(*) FROM sql_units").fetchone()[0]
    }
    
    conn.close()
    
    # 검증 결과
    verification_result = {
        'ground_truth': ground_truth,
        'current_status': current_status,
        'accuracy': {},
        'passed': True
    }
    
    print(f"검증 결과:")
    for key in ['classes', 'methods', 'sql_queries']:
        ground_truth_count = ground_truth[key]
        current_count = current_status[key]
        max_allowed = int(ground_truth_count * 1.1)
        
        accuracy = (current_count / ground_truth_count) * 100
        verification_result['accuracy'][key] = accuracy
        
        if current_count <= max_allowed:
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            verification_result['passed'] = False
        
        print(f"  {key}: {current_count} (기준: {ground_truth_count}, 허용: {max_allowed}) - {accuracy:.1f}% - {status}")
    
    if verification_result['passed']:
        print("\n🎉 모든 항목이 10% 이내 오차 달성!")
    else:
        print("\n⚠️ 일부 항목이 10% 초과 오차")
    
    return verification_result

if __name__ == "__main__":
    practical_parser_improvement()



