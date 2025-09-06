#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
반복 개선 루프
5% 이내 오차 달성까지 자동화된 개선 프로세스
"""

import os
import sys
import subprocess
import json
import sqlite3
from typing import Dict, List, Any

def iterative_improvement_loop():
    """반복 개선 루프 실행"""
    
    print("=== 반복 개선 루프 시작 ===")
    
    max_iterations = 5
    target_accuracy = 95.0  # 95% 이상 정확도 목표
    
    for iteration in range(1, max_iterations + 1):
        print(f"\n--- 반복 {iteration}/{max_iterations} ---")
        
        # 1. 현재 정확도 측정
        current_accuracy = measure_current_accuracy()
        print(f"현재 정확도: {current_accuracy:.1f}%")
        
        if current_accuracy >= target_accuracy:
            print(f"✅ 목표 정확도 달성! ({current_accuracy:.1f}% >= {target_accuracy}%)")
            break
        
        # 2. 문제점 분석
        issues = analyze_accuracy_issues()
        print(f"발견된 문제점: {len(issues)}개")
        
        # 3. 개선 작업 실행
        improvements = apply_improvements(issues, iteration)
        print(f"적용된 개선사항: {len(improvements)}개")
        
        # 4. 메타DB 재생성
        regenerate_metadb()
        
        # 5. 정확도 재측정
        new_accuracy = measure_current_accuracy()
        print(f"개선 후 정확도: {new_accuracy:.1f}%")
        
        # 6. 개선 효과 평가
        improvement = new_accuracy - current_accuracy
        print(f"정확도 개선: {improvement:+.1f}%")
        
        if improvement < 1.0:  # 1% 미만 개선 시 중단
            print("⚠️ 개선 효과가 미미하여 중단")
            break
    
    print(f"\n=== 반복 개선 루프 완료 ===")
    final_accuracy = measure_current_accuracy()
    print(f"최종 정확도: {final_accuracy:.1f}%")
    
    return final_accuracy

def measure_current_accuracy():
    """현재 정확도 측정"""
    
    # 메타디비 검증 실행
    result = subprocess.run([
        sys.executable, './temp/metadb_verification.py'
    ], capture_output=True, text=True, cwd='.')
    
    if result.returncode != 0:
        print(f"정확도 측정 실패: {result.stderr}")
        return 0.0
    
    # 출력에서 정확도 추출
    output_lines = result.stdout.split('\n')
    for line in output_lines:
        if '평균 정확도:' in line:
            accuracy_str = line.split(':')[1].strip().replace('%', '')
            return float(accuracy_str)
    
    return 0.0

def analyze_accuracy_issues():
    """정확도 문제점 분석"""
    
    print("\n=== 정확도 문제점 분석 ===")
    
    issues = []
    
    # 메타디비 데이터 조회
    metadb_path = '../project/sampleSrc/metadata.db'
    if not os.path.exists(metadb_path):
        print(f"메타디비 파일이 없습니다: {metadb_path}")
        return issues
    
    conn = sqlite3.connect(metadb_path)
    cursor = conn.cursor()
    
    # 클래스 과다추출 분석
    cursor.execute("SELECT COUNT(*) FROM classes")
    class_count = cursor.fetchone()[0]
    if class_count > 20:  # 예상보다 많음
        issues.append({
            'type': 'class_overextraction',
            'count': class_count,
            'expected': 15,
            'severity': 'high'
        })
    
    # 메소드 과다추출 분석
    cursor.execute("SELECT COUNT(*) FROM methods")
    method_count = cursor.fetchone()[0]
    if method_count > 150:  # 예상보다 많음
        issues.append({
            'type': 'method_overextraction',
            'count': method_count,
            'expected': 118,
            'severity': 'high'
        })
    
    # SQL Units 과다추출 분석
    cursor.execute("SELECT COUNT(*) FROM sql_units")
    sql_count = cursor.fetchone()[0]
    if sql_count > 80:  # 예상보다 많음
        issues.append({
            'type': 'sql_overextraction',
            'count': sql_count,
            'expected': 65,
            'severity': 'high'
        })
    
    conn.close()
    
    print(f"발견된 문제점:")
    for issue in issues:
        print(f"  - {issue['type']}: {issue['count']} (예상: {issue['expected']})")
    
    return issues

def apply_improvements(issues: List[Dict], iteration: int):
    """개선사항 적용"""
    
    print(f"\n=== 개선사항 적용 (반복 {iteration}) ===")
    
    improvements = []
    
    for issue in issues:
        if issue['type'] == 'class_overextraction':
            improvement = fix_class_overextraction(issue)
            improvements.append(improvement)
        
        elif issue['type'] == 'method_overextraction':
            improvement = fix_method_overextraction(issue)
            improvements.append(improvement)
        
        elif issue['type'] == 'sql_overextraction':
            improvement = fix_sql_overextraction(issue)
            improvements.append(improvement)
    
    return improvements

def fix_class_overextraction(issue: Dict):
    """클래스 과다추출 수정"""
    
    print(f"클래스 과다추출 수정: {issue['count']} -> {issue['expected']}")
    
    # Java 파서의 클래스 패턴 개선
    java_parser_path = './parsers/java/java_parser.py'
    if os.path.exists(java_parser_path):
        # 클래스 패턴을 더 엄격하게 수정
        with open(java_parser_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 클래스 패턴 개선 (더 엄격한 매칭)
        improved_pattern = r'class\s+(\w+)\s*(?:extends\s+\w+)?\s*(?:implements\s+[\w\s,]+)?\s*\{'
        content = content.replace(
            r'class\s+(\w+)',
            improved_pattern
        )
        
        with open(java_parser_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            'type': 'class_pattern_improvement',
            'description': '클래스 패턴을 더 엄격하게 수정',
            'expected_improvement': 0.8
        }
    
    return None

def fix_method_overextraction(issue: Dict):
    """메소드 과다추출 수정"""
    
    print(f"메소드 과다추출 수정: {issue['count']} -> {issue['expected']}")
    
    # Java 파서의 메소드 패턴 개선
    java_parser_path = './parsers/java/java_parser.py'
    if os.path.exists(java_parser_path):
        # 메소드 패턴을 더 엄격하게 수정
        with open(java_parser_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 메소드 패턴 개선 (키워드 필터링 강화)
        improved_pattern = r'(?:public|private|protected)\s+(?:\w+\s+)*(\w+)\s*\([^)]*\)\s*\{'
        content = content.replace(
            r'(\w+)\s*\([^)]*\)\s*\{',
            improved_pattern
        )
        
        with open(java_parser_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            'type': 'method_pattern_improvement',
            'description': '메소드 패턴을 더 엄격하게 수정',
            'expected_improvement': 0.7
        }
    
    return None

def fix_sql_overextraction(issue: Dict):
    """SQL 과다추출 수정"""
    
    print(f"SQL 과다추출 수정: {issue['count']} -> {issue['expected']}")
    
    # SQL 파서의 패턴 개선
    sql_parser_path = './parsers/sql/sql_parser_context7.py'
    if os.path.exists(sql_parser_path):
        # SQL 패턴을 더 엄격하게 수정
        with open(sql_parser_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # SQL 패턴 개선 (더 정확한 매칭)
        improved_pattern = r'(?:SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|TRUNCATE|MERGE)\s+[^;]+;'
        content = content.replace(
            r'["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|TRUNCATE|MERGE)[^"\']*)["\']',
            improved_pattern
        )
        
        with open(sql_parser_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            'type': 'sql_pattern_improvement',
            'description': 'SQL 패턴을 더 엄격하게 수정',
            'expected_improvement': 0.6
        }
    
    return None

def regenerate_metadb():
    """메타DB 재생성"""
    
    print("\n=== 메타DB 재생성 ===")
    
    # 기존 메타DB 백업
    metadb_path = '../project/sampleSrc/metadata.db'
    if os.path.exists(metadb_path):
        backup_path = f'{metadb_path}.backup'
        os.rename(metadb_path, backup_path)
        print(f"기존 메타DB 백업: {backup_path}")
    
    # 메타DB 재생성
    result = subprocess.run([
        sys.executable, 'main.py', '--project-name', 'sampleSrc'
    ], capture_output=True, text=True, cwd='.')
    
    if result.returncode == 0:
        print("✅ 메타DB 재생성 완료")
    else:
        print(f"❌ 메타DB 재생성 실패: {result.stderr}")
        # 백업 복원
        if os.path.exists(backup_path):
            os.rename(backup_path, metadb_path)
            print("백업 메타DB 복원")

if __name__ == "__main__":
    iterative_improvement_loop()



