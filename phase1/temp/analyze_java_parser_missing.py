#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
import glob
import re

def analyze_java_parser_missing():
    """Java 파서가 놓치는 메소드들 분석"""
    project_path = "project/sampleSrc/src"
    
    print("=== Java 파서 누락 메소드 분석 ===\n")
    
    # Java 파일 분석
    java_files = glob.glob(f"{project_path}/**/*.java", recursive=True)
    
    total_manual_methods = 0
    total_metadb_methods = 0
    missing_analysis = []
    
    for java_file in java_files:
        relative_path = os.path.relpath(java_file, project_path)
        abs_path = os.path.abspath(java_file)
        
        try:
            with open(java_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 수동 분석: 메소드 추출
            method_pattern = r'(?:public|private|protected|static|\s)*\s*(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?(?:abstract\s+)?(?:native\s+)?(?:strictfp\s+)?(?:transient\s+)?(?:volatile\s+)?(?:[a-zA-Z_][a-zA-Z0-9_<>\[\],\s]*\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*(?:throws\s+[^{]+)?\s*\{'
            methods = re.findall(method_pattern, content, re.MULTILINE | re.DOTALL)
            
            # 생성자
            class_name = os.path.basename(java_file).replace('.java', '')
            constructor_pattern = rf'(?:public|private|protected)\s+{re.escape(class_name)}\s*\('
            constructors = re.findall(constructor_pattern, content)
            
            # 인터페이스 메소드
            interface_method_pattern = r'(?:public|private|protected|static|\s)*\s*(?:static\s+)?(?:default\s+)?(?:[a-zA-Z_][a-zA-Z0-9_<>\[\],\s]*\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)\s*(?:throws\s+[^;]+)?\s*;'
            interface_methods = re.findall(interface_method_pattern, content, re.MULTILINE | re.DOTALL)
            
            manual_count = len(methods) + len(constructors) + len(interface_methods)
            
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
            
            total_manual_methods += manual_count
            total_metadb_methods += metadb_count
            
            if manual_count > metadb_count:
                missing_count = manual_count - metadb_count
                missing_analysis.append({
                    'file': relative_path,
                    'manual': manual_count,
                    'metadb': metadb_count,
                    'missing': missing_count,
                    'content': content
                })
                
                print(f"📁 {relative_path}")
                print(f"   수동: {manual_count}개, 메타디비: {metadb_count}개, 누락: {missing_count}개")
                
                # 누락된 메소드 패턴 분석
                if missing_count > 0:
                    print(f"   누락 패턴 분석:")
                    
                    # 특수한 메소드 패턴들 확인
                    special_patterns = [
                        (r'@Override\s*\n\s*(?:public|private|protected).*?([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', "Override 메소드"),
                        (r'@PostMapping.*?\n.*?([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', "PostMapping 메소드"),
                        (r'@GetMapping.*?\n.*?([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', "GetMapping 메소드"),
                        (r'@RequestMapping.*?\n.*?([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', "RequestMapping 메소드"),
                        (r'@Service.*?\n.*?([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', "Service 메소드"),
                        (r'@Transactional.*?\n.*?([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', "Transactional 메소드"),
                        (r'default\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', "default 메소드"),
                        (r'static\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', "static 메소드"),
                    ]
                    
                    for pattern, description in special_patterns:
                        matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
                        if matches:
                            print(f"     - {description}: {len(matches)}개")
                
                print()
        
        except Exception as e:
            print(f"파일 처리 오류 {java_file}: {e}")
    
    print(f"=== 전체 요약 ===")
    print(f"수동 분석 총 메소드: {total_manual_methods}개")
    print(f"메타디비 총 메소드: {total_metadb_methods}개")
    print(f"누락된 메소드: {total_manual_methods - total_metadb_methods}개")
    print(f"정확도: {(total_metadb_methods / total_manual_methods * 100):.1f}%")
    
    return missing_analysis

if __name__ == "__main__":
    missing_analysis = analyze_java_parser_missing()