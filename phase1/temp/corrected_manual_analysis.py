#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import glob
import sqlite3

def corrected_manual_analysis():
    """수정된 수동 분석으로 실제 메소드 개수 파악"""
    project_path = "project/sampleSrc/src"
    
    print("=== 수정된 수동 분석 ===\n")
    
    # Java 파일 분석
    java_files = glob.glob(f"{project_path}/**/*.java", recursive=True)
    
    total_corrected_methods = 0
    total_metadb_methods = 0
    file_analysis = []
    
    for java_file in java_files:
        relative_path = os.path.relpath(java_file, project_path)
        abs_path = os.path.abspath(java_file)
        
        try:
            with open(java_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 수정된 메소드 추출 (더 정확한 패턴)
            methods = []
            
            # 1. 일반 메소드 (어노테이션 포함, 중괄호로 끝나는 것만)
            method_pattern = r'(?:@\w+(?:\([^)]*\))?\s*\n\s*)*(?:public|private|protected|static|final|abstract|synchronized|native|strictfp)?\s*(?:<[^>]+>\s+)?(\w+)\s+(\w+)\s*\(([^)]*)\)\s*(?:throws\s+([^{]+))?\s*\{'
            method_matches = re.findall(method_pattern, content, re.IGNORECASE | re.DOTALL)
            methods.extend(method_matches)
            
            # 2. 생성자 (클래스명과 같은 이름)
            class_name = os.path.basename(java_file).replace('.java', '')
            constructor_pattern = r'(?:@\w+(?:\([^)]*\))?\s*\n\s*)*(?:public|private|protected)?\s+' + re.escape(class_name) + r'\s*\(([^)]*)\)\s*(?:throws\s+([^{]+))?\s*\{'
            constructor_matches = re.findall(constructor_pattern, content, re.IGNORECASE | re.DOTALL)
            methods.extend([(class_name, class_name, params, throws) for params, throws in constructor_matches])
            
            # 3. 인터페이스 메소드 (세미콜론으로 끝나는 것만)
            interface_pattern = r'(?:@\w+(?:\([^)]*\))?\s*\n\s*)*(?:public|private|protected|static|default)?\s*(?:<[^>]+>\s+)?(\w+)\s+(\w+)\s*\(([^)]*)\)\s*(?:throws\s+([^;]+))?\s*;'
            interface_matches = re.findall(interface_pattern, content, re.IGNORECASE | re.DOTALL)
            methods.extend(interface_matches)
            
            corrected_count = len(methods)
            
            # 메타디비에서 해당 파일의 메소드 개수 조회
            db_path = "project/sampleSrc/metadata.db"
            metadb_count = 0
            
            if os.path.exists(db_path):
                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    cursor.execute("""
                        SELECT COUNT(m.method_id) as method_count
                        FROM files f
                        LEFT JOIN classes c ON f.file_id = c.file_id
                        LEFT JOIN methods m ON c.class_id = m.class_id
                        WHERE f.path = ?
                        GROUP BY f.file_id
                    """, (abs_path,))
                    
                    result = cursor.fetchone()
                    if result:
                        metadb_count = result[0]
                    
                    conn.close()
                except Exception as e:
                    print(f"메타디비 조회 오류 {java_file}: {e}")
            
            total_corrected_methods += corrected_count
            total_metadb_methods += metadb_count
            
            file_analysis.append({
                'file': relative_path,
                'corrected': corrected_count,
                'metadb': metadb_count,
                'difference': corrected_count - metadb_count
            })
            
            if corrected_count != metadb_count:
                print(f"FILE: {relative_path}")
                print(f"   수정된 수동: {corrected_count}개, 메타디비: {metadb_count}개, 차이: {corrected_count - metadb_count}개")
        
        except Exception as e:
            print(f"파일 처리 오류 {java_file}: {e}")
    
    print(f"\n=== 수정된 전체 요약 ===")
    print(f"수정된 수동 분석 총 메소드: {total_corrected_methods}개")
    print(f"메타디비 총 메소드: {total_metadb_methods}개")
    print(f"차이: {total_corrected_methods - total_metadb_methods}개")
    if total_corrected_methods > 0:
        print(f"정확도: {(total_metadb_methods / total_corrected_methods * 100):.1f}%")
    
    # 차이가 큰 파일들 분석
    print(f"\n=== 차이가 큰 파일들 ===")
    large_diff_files = [f for f in file_analysis if abs(f['difference']) > 2]
    for f in sorted(large_diff_files, key=lambda x: abs(x['difference']), reverse=True):
        print(f"FILE: {f['file']}: 수동 {f['corrected']}개 vs 메타디비 {f['metadb']}개 (차이: {f['difference']}개)")
    
    return file_analysis

if __name__ == "__main__":
    file_analysis = corrected_manual_analysis()
