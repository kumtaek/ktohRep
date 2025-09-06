#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
import glob

def check_java_parser_coverage():
    """Java 파서가 처리한 파일들 확인"""
    project_path = "project/sampleSrc/src"
    db_path = "project/sampleSrc/metadata.db"
    
    print("=== Java 파서 커버리지 분석 ===\n")
    
    # 모든 Java 파일 목록
    java_files = glob.glob(f"{project_path}/**/*.java", recursive=True)
    all_java_files = [os.path.relpath(f, project_path) for f in java_files]
    
    print(f"📁 전체 Java 파일: {len(all_java_files)}개")
    for f in all_java_files:
        print(f"   - {f}")
    
    print(f"\n📊 메타디비에서 처리된 Java 파일들:")
    
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 메타디비에서 Java 파일들 조회
            cursor.execute("""
                SELECT f.path, COUNT(m.method_id) as method_count
                FROM files f
                LEFT JOIN classes c ON f.file_id = c.file_id
                LEFT JOIN methods m ON c.class_id = m.class_id
                WHERE f.path LIKE '%.java'
                GROUP BY f.file_id, f.path
                ORDER BY f.path
            """)
            
            results = cursor.fetchall()
            processed_files = []
            
            for abs_path, method_count in results:
                # 절대 경로를 상대 경로로 변환
                try:
                    rel_path = os.path.relpath(abs_path, os.path.abspath(project_path))
                    processed_files.append(rel_path)
                    print(f"   ✅ {rel_path}: {method_count}개 메소드")
                except:
                    print(f"   ✅ {abs_path}: {method_count}개 메소드")
            
            conn.close()
            
            # 처리되지 않은 파일들
            unprocessed_files = [f for f in all_java_files if f not in processed_files]
            
            print(f"\n❌ 처리되지 않은 Java 파일들: {len(unprocessed_files)}개")
            for f in unprocessed_files:
                print(f"   - {f}")
            
            print(f"\n📈 커버리지 통계:")
            print(f"   전체 Java 파일: {len(all_java_files)}개")
            print(f"   처리된 파일: {len(processed_files)}개")
            print(f"   처리되지 않은 파일: {len(unprocessed_files)}개")
            print(f"   파일 커버리지: {(len(processed_files) / len(all_java_files) * 100):.1f}%")
            
        except Exception as e:
            print(f"❌ 메타디비 조회 오류: {e}")
    else:
        print("❌ 메타디비 파일이 없습니다.")

if __name__ == "__main__":
    check_java_parser_coverage()

