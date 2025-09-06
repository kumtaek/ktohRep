#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
import glob
import re

def simple_java_analysis():
    """간단한 Java 분석"""
    project_path = "project/sampleSrc/src"
    db_path = "project/sampleSrc/metadata.db"
    
    print("=== 간단한 Java 분석 ===\n")
    
    # Java 파일 분석
    java_files = glob.glob(f"{project_path}/**/*.java", recursive=True)
    
    total_manual = 0
    total_metadb = 0
    
    for java_file in java_files:
        relative_path = os.path.relpath(java_file, project_path)
        abs_path = os.path.abspath(java_file)
        
        try:
            with open(java_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 간단한 메소드 카운트
            method_pattern = r'(?:@\w+(?:\([^)]*\))?\s*\n\s*)*(?:public|private|protected|static|final|abstract|synchronized|native|strictfp)?\s*(?:<[^>]+>\s+)?(\w+)\s+(\w+)\s*\(([^)]*)\)\s*(?:throws\s+([^{]+))?\s*\{'
            methods = re.findall(method_pattern, content, re.IGNORECASE | re.DOTALL)
            
            # 생성자
            class_name = os.path.basename(java_file).replace('.java', '')
            constructor_pattern = r'(?:@\w+(?:\([^)]*\))?\s*\n\s*)*(?:public|private|protected)?\s+' + re.escape(class_name) + r'\s*\(([^)]*)\)\s*(?:throws\s+([^{]+))?\s*\{'
            constructors = re.findall(constructor_pattern, content, re.IGNORECASE | re.DOTALL)
            
            # 인터페이스 메소드
            interface_pattern = r'(?:@\w+(?:\([^)]*\))?\s*\n\s*)*(?:public|private|protected|static|default)?\s*(?:<[^>]+>\s+)?(\w+)\s+(\w+)\s*\(([^)]*)\)\s*(?:throws\s+([^;]+))?\s*;'
            interface_methods = re.findall(interface_pattern, content, re.IGNORECASE | re.DOTALL)
            
            manual_count = len(methods) + len(constructors) + len(interface_methods)
            
            # 메타디비에서 조회
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
                    print(f"DB 오류 {java_file}: {e}")
            
            total_manual += manual_count
            total_metadb += metadb_count
            
            if manual_count != metadb_count:
                print(f"FILE: {relative_path}")
                print(f"   수동: {manual_count}개, 메타디비: {metadb_count}개, 차이: {manual_count - metadb_count}개")
        
        except Exception as e:
            print(f"파일 오류 {java_file}: {e}")
    
    print(f"\n=== 전체 요약 ===")
    print(f"수동 분석 총 메소드: {total_manual}개")
    print(f"메타디비 총 메소드: {total_metadb}개")
    print(f"차이: {total_manual - total_metadb}개")
    if total_manual > 0:
        print(f"정확도: {(total_metadb / total_manual * 100):.1f}%")

if __name__ == "__main__":
    simple_java_analysis()

