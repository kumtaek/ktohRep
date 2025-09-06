#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
import glob

def analyze_java_files():
    """Java 파일 분석"""
    print("=== Java 파일 분석 ===")
    
    # 실제 파일 시스템의 Java 파일
    java_files = glob.glob('project/sampleSrc/**/*.java', recursive=True)
    print(f"실제 Java 파일 수: {len(java_files)}")
    for f in java_files[:3]:  # 처음 3개만 출력
        print(f"  - {f}")
    
    # 메타디비의 Java 파일
    db_path = 'phase1/project/sampleSrc/metadata.db'
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT path FROM files WHERE language = 'java'")
        db_java_files = cursor.fetchall()
        print(f"메타디비 Java 파일 수: {len(db_java_files)}")
        for f in db_java_files[:3]:  # 처음 3개만 출력
            print(f"  - {f[0]}")
        conn.close()
    
    return java_files, db_java_files

def analyze_xml_files():
    """XML 파일 분석"""
    print("\n=== XML 파일 분석 ===")
    
    # 실제 파일 시스템의 XML 파일
    xml_files = glob.glob('project/sampleSrc/**/*.xml', recursive=True)
    print(f"실제 XML 파일 수: {len(xml_files)}")
    for f in xml_files:
        print(f"  - {f}")
    
    # 메타디비의 XML 파일
    db_path = 'phase1/project/sampleSrc/metadata.db'
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT path FROM files WHERE language = 'xml'")
        db_xml_files = cursor.fetchall()
        print(f"메타디비 XML 파일 수: {len(db_xml_files)}")
        for f in db_xml_files:
            print(f"  - {f[0]}")
        conn.close()
    
    return xml_files, db_xml_files

def analyze_csv_files():
    """CSV 파일 분석"""
    print("\n=== CSV 파일 분석 ===")
    
    # 실제 파일 시스템의 CSV 파일
    csv_files = glob.glob('project/sampleSrc/**/*.csv', recursive=True)
    print(f"실제 CSV 파일 수: {len(csv_files)}")
    for f in csv_files:
        print(f"  - {f}")
    
    # 메타디비의 CSV 파일
    db_path = 'phase1/project/sampleSrc/metadata.db'
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT path FROM files WHERE language = 'csv'")
        db_csv_files = cursor.fetchall()
        print(f"메타디비 CSV 파일 수: {len(db_csv_files)}")
        for f in db_csv_files:
            print(f"  - {f[0]}")
        conn.close()
    
    return csv_files, db_csv_files

def analyze_methods():
    """메서드 분석"""
    print("\n=== 메서드 분석 ===")
    
    db_path = 'phase1/project/sampleSrc/metadata.db'
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 메서드 수
        cursor.execute("SELECT COUNT(*) FROM methods")
        method_count = cursor.fetchone()[0]
        print(f"메타디비 메서드 수: {method_count}")
        
        # 파일별 메서드 수
        cursor.execute("""
            SELECT f.path, COUNT(m.method_id) as method_count 
            FROM files f 
            LEFT JOIN methods m ON f.file_id = m.class_id 
            WHERE f.language = 'java'
            GROUP BY f.file_id, f.path
            ORDER BY method_count DESC
        """)
        file_methods = cursor.fetchall()
        print("파일별 메서드 수:")
        for f, count in file_methods[:5]:  # 상위 5개만
            print(f"  - {f}: {count}개")
        
        conn.close()

def analyze_errors():
    """에러 분석"""
    print("\n=== 에러 분석 ===")
    
    db_path = 'phase1/project/sampleSrc/metadata.db'
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 에러 수
        cursor.execute("SELECT COUNT(*) FROM parse_results WHERE success = 0")
        error_count = cursor.fetchone()[0]
        print(f"메타디비 에러 수: {error_count}")
        
        # 성공/실패 파일 수
        cursor.execute("SELECT success, COUNT(*) FROM parse_results GROUP BY success")
        results = cursor.fetchall()
        for success, count in results:
            status = "성공" if success else "실패"
            print(f"  - {status}: {count}개")
        
        conn.close()

if __name__ == "__main__":
    analyze_java_files()
    analyze_xml_files()
    analyze_csv_files()
    analyze_methods()
    analyze_errors()