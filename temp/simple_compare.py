#!/usr/bin/env python3
"""
간단한 메타디비 비교 스크립트
"""

import sqlite3
from datetime import datetime

def get_metadb_data():
    """메타디비 데이터 조회"""
    conn = sqlite3.connect('./project/sampleSrc/metadata.db')
    cursor = conn.cursor()
    
    data = {}
    
    # 기본 통계
    cursor.execute('SELECT COUNT(*) FROM files')
    data['total_files'] = cursor.fetchone()[0]
    
    cursor.execute('SELECT language, COUNT(*) FROM files GROUP BY language')
    data['files_by_type'] = dict(cursor.fetchall())
    
    cursor.execute('SELECT COUNT(*) FROM classes')
    data['total_classes'] = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM methods')
    data['total_methods'] = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM sql_units')
    data['total_sql_units'] = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM chunks')
    data['total_chunks'] = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM parse_results WHERE success = 0')
    data['total_errors'] = cursor.fetchone()[0]
    
    conn.close()
    return data

def compare_with_spec():
    """명세서와 비교"""
    
    # 샘플소스명세서 기준값
    spec = {
        'total_files': 32,  # Java 16개 + JSP 8개 + XML 4개 + CSV 4개
        'java_files': 16,
        'jsp_files': 8,
        'xml_files': 4,
        'csv_files': 4,
        'total_classes': 16,
        'total_methods': 77,
        'total_sql_units': 31,
        'total_errors': 7
    }
    
    metadb = get_metadb_data()
    
    print("=== 메타디비 vs 명세서 비교 ===")
    print()
    
    # 파일 수 비교
    print("📁 파일 수 비교:")
    print(f"  명세서 기준: {spec['total_files']}개")
    print(f"  메타디비 결과: {metadb['total_files']}개")
    diff = metadb['total_files'] - spec['total_files']
    diff_percent = (diff / spec['total_files'] * 100) if spec['total_files'] > 0 else 0
    print(f"  차이: {diff:+d}개 ({diff_percent:+.1f}%)")
    
    if diff < 0:
        print("  ❌ 과소추출: 심각한 문제!")
    elif diff_percent > 10:
        print("  ⚠️ 과다추출: 10% 초과")
    else:
        print("  ✅ 정상 범위")
    
    print()
    
    # 파일 타입별 비교
    print("📂 파일 타입별 비교:")
    for file_type, expected in [('java', 16), ('jsp', 8), ('xml', 4), ('csv', 4)]:
        actual = metadb['files_by_type'].get(f'.{file_type}' if file_type == 'java' else file_type, 0)
        diff = actual - expected
        diff_percent = (diff / expected * 100) if expected > 0 else 0
        print(f"  {file_type}: {expected} → {actual} ({diff:+d}, {diff_percent:+.1f}%)")
    
    print()
    
    # 클래스 수 비교
    print("🏗️ 클래스 수 비교:")
    print(f"  명세서 기준: {spec['total_classes']}개")
    print(f"  메타디비 결과: {metadb['total_classes']}개")
    diff = metadb['total_classes'] - spec['total_classes']
    diff_percent = (diff / spec['total_classes'] * 100) if spec['total_classes'] > 0 else 0
    print(f"  차이: {diff:+d}개 ({diff_percent:+.1f}%)")
    
    if diff < 0:
        print("  ❌ 과소추출: 심각한 문제!")
    elif diff_percent > 10:
        print("  ⚠️ 과다추출: 10% 초과")
    else:
        print("  ✅ 정상 범위")
    
    print()
    
    # 메소드 수 비교
    print("⚙️ 메소드 수 비교:")
    print(f"  명세서 기준: {spec['total_methods']}개")
    print(f"  메타디비 결과: {metadb['total_methods']}개")
    diff = metadb['total_methods'] - spec['total_methods']
    diff_percent = (diff / spec['total_methods'] * 100) if spec['total_methods'] > 0 else 0
    print(f"  차이: {diff:+d}개 ({diff_percent:+.1f}%)")
    
    if diff < 0:
        print("  ❌ 과소추출: 심각한 문제!")
    elif diff_percent > 10:
        print("  ⚠️ 과다추출: 10% 초과")
    else:
        print("  ✅ 정상 범위")
    
    print()
    
    # SQL 쿼리 수 비교
    print("🗄️ SQL 쿼리 수 비교:")
    print(f"  명세서 기준: {spec['total_sql_units']}개")
    print(f"  메타디비 결과: {metadb['total_sql_units']}개")
    diff = metadb['total_sql_units'] - spec['total_sql_units']
    diff_percent = (diff / spec['total_sql_units'] * 100) if spec['total_sql_units'] > 0 else 0
    print(f"  차이: {diff:+d}개 ({diff_percent:+.1f}%)")
    
    if diff < 0:
        print("  ❌ 과소추출: 심각한 문제!")
    elif diff_percent > 10:
        print("  ⚠️ 과다추출: 10% 초과")
    else:
        print("  ✅ 정상 범위")
    
    print()
    
    # 오류 수 비교
    print("🚨 오류 수 비교:")
    print(f"  명세서 기준: {spec['total_errors']}개")
    print(f"  메타디비 결과: {metadb['total_errors']}개")
    diff = metadb['total_errors'] - spec['total_errors']
    diff_percent = (diff / spec['total_errors'] * 100) if spec['total_errors'] > 0 else 0
    print(f"  차이: {diff:+d}개 ({diff_percent:+.1f}%)")
    
    print()
    
    # 전체 요약
    print("📊 전체 요약:")
    print(f"  총 청크 수: {metadb['total_chunks']}개")
    print()
    
    # 심각한 문제 확인
    serious_issues = []
    if metadb['total_files'] < spec['total_files']:
        serious_issues.append(f"파일 수 과소추출 ({metadb['total_files']}/{spec['total_files']})")
    if metadb['total_classes'] < spec['total_classes']:
        serious_issues.append(f"클래스 수 과소추출 ({metadb['total_classes']}/{spec['total_classes']})")
    if metadb['total_methods'] < spec['total_methods']:
        serious_issues.append(f"메소드 수 과소추출 ({metadb['total_methods']}/{spec['total_methods']})")
    if metadb['total_sql_units'] < spec['total_sql_units']:
        serious_issues.append(f"SQL 쿼리 수 과소추출 ({metadb['total_sql_units']}/{spec['total_sql_units']})")
    
    if serious_issues:
        print("❌ 심각한 문제 발견:")
        for issue in serious_issues:
            print(f"  - {issue}")
        print()
        print("🔧 해결 방안:")
        print("  1. 메타디비 재생성 필요")
        print("  2. 파서 로직 점검 필요")
        print("  3. 파일 스캔 범위 확인 필요")
    else:
        print("✅ 심각한 과소추출 문제는 없습니다.")
    
    return metadb, spec

if __name__ == "__main__":
    compare_with_spec()
