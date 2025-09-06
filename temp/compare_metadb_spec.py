#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
import re
from datetime import datetime

def get_metadb_counts():
    """메타디비에서 각종 카운트를 가져옴"""
    db_path = 'phase1/project/sampleSrc/metadata.db'
    
    if not os.path.exists(db_path):
        print(f"메타디비 파일이 존재하지 않습니다: {db_path}")
        return {}
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        counts = {}
        
        # 언어별 파일 수
        cursor.execute('SELECT language, COUNT(*) FROM files GROUP BY language')
        for row in cursor.fetchall():
            counts[f'{row[0].upper()}_파일'] = row[1]
        
        # 클래스 수
        cursor.execute('SELECT COUNT(*) FROM classes')
        counts['CLASSES'] = cursor.fetchone()[0]
        
        # 메서드 수
        cursor.execute('SELECT COUNT(*) FROM methods')
        counts['METHODS'] = cursor.fetchone()[0]
        
        # SQL Units 수
        cursor.execute('SELECT COUNT(*) FROM sql_units')
        counts['SQL_UNITS'] = cursor.fetchone()[0]
        
        # 에러 수
        cursor.execute('SELECT COUNT(*) FROM parse_results WHERE success = 0')
        counts['ERRORS'] = cursor.fetchone()[0]
        
        # 청크 수
        cursor.execute('SELECT COUNT(*) FROM chunks')
        counts['CHUNKS'] = cursor.fetchone()[0]
        
        conn.close()
        return counts
        
    except Exception as e:
        print(f"메타디비 조회 중 오류: {e}")
        return {}

def get_spec_counts():
    """명세서에서 각종 카운트를 가져옴"""
    spec_files = [
        'Dev.Report/샘플소스명세서_20250905_175951_1.md',
        'Dev.Report/샘플소스명세서_20250905_175951_2.md'
    ]
    
    counts = {}
    
    for spec_file in spec_files:
        if not os.path.exists(spec_file):
            continue
            
        try:
            with open(spec_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 파일 수 추출
            file_patterns = [
                (r'Java 파일 \((\d+)개\)', 'JAVA_파일'),
                (r'JSP 파일 \((\d+)개\)', 'JSP_파일'),
                (r'XML 파일 \((\d+)개\)', 'XML_파일'),
                (r'CSV 파일 \((\d+)개\)', 'CSV_파일'),
            ]
            
            for pattern, key in file_patterns:
                match = re.search(pattern, content)
                if match:
                    counts[key] = int(match.group(1))
            
            # 기타 카운트 추출
            other_patterns = [
                (r'클래스 인식.*?(\d+)개', 'CLASSES'),
                (r'메소드 인식.*?(\d+)개', 'METHODS'),
                (r'MyBatis 쿼리 인식.*?(\d+)개', 'SQL_UNITS'),
                (r'오류 감지.*?(\d+)개', 'ERRORS'),
                (r'총 청크.*?(\d+)개', 'CHUNKS'),
            ]
            
            for pattern, key in other_patterns:
                match = re.search(pattern, content)
                if match:
                    counts[key] = int(match.group(1))
                    
        except Exception as e:
            print(f"명세서 파일 읽기 오류 {spec_file}: {e}")
    
    return counts

def compare_counts():
    """메타디비와 명세서 카운트를 비교"""
    print("메타디비 카운트 조회 중...")
    metadb_counts = get_metadb_counts()
    print(f"메타디비 카운트: {metadb_counts}")
    
    print("명세서 카운트 조회 중...")
    spec_counts = get_spec_counts()
    print(f"명세서 카운트: {spec_counts}")
    
    print("=== 메타디비 vs 명세서 비교 ===")
    print(f"비교 시점: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    all_keys = set(metadb_counts.keys()) | set(spec_counts.keys())
    print(f"비교할 키들: {sorted(all_keys)}")
    
    differences = []
    
    for key in sorted(all_keys):
        metadb_count = metadb_counts.get(key, 0)
        spec_count = spec_counts.get(key, 0)
        diff = metadb_count - spec_count
        
        if diff != 0:
            diff_percent = (diff / spec_count * 100) if spec_count > 0 else 0
            status = "과대" if diff > 0 else "과소"
            differences.append({
                'key': key,
                'metadb': metadb_count,
                'spec': spec_count,
                'diff': diff,
                'percent': diff_percent,
                'status': status
            })
        
        print(f"{key}: 메타디비 {metadb_count}개 vs 명세서 {spec_count}개 (차이: {diff:+d}개, {diff_percent:+.1f}%, {status if diff != 0 else '일치'})")
    
    return differences

if __name__ == "__main__":
    differences = compare_counts()