#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_all_files():
    """모든 파일의 등록 상태 확인"""
    print("=== 모든 파일의 등록 상태 확인 ===\n")
    
    db_path = "project/sampleSrc/metadata.db"
    
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 1. files 테이블에서 모든 파일 확인
            print("=== 1. files 테이블의 모든 파일 ===")
            cursor.execute("SELECT file_id, path, language, loc FROM files ORDER BY file_id")
            all_files = cursor.fetchall()
            
            print(f"전체 파일 수: {len(all_files)}")
            for file_id, path, language, loc in all_files:
                print(f"  ID: {file_id}, 언어: {language}, LOC: {loc}")
                print(f"    경로: {path}")
            
            # 2. 언어별 파일 수 확인
            print(f"\n=== 2. 언어별 파일 수 ===")
            cursor.execute("SELECT language, COUNT(*) as count FROM files GROUP BY language ORDER BY count DESC")
            language_counts = cursor.fetchall()
            
            for language, count in language_counts:
                print(f"  {language}: {count}개")
            
            # 3. Java 파일만 상세 확인
            print(f"\n=== 3. Java 파일 상세 ===")
            cursor.execute("SELECT file_id, path, loc FROM files WHERE language = '.java' ORDER BY file_id")
            java_files = cursor.fetchall()
            
            print(f"Java 파일 수: {len(java_files)}")
            for file_id, path, loc in java_files:
                print(f"  ID: {file_id}, LOC: {loc}")
                print(f"    경로: {path}")
            
            # 4. 클래스가 있는 파일들 확인
            print(f"\n=== 4. 클래스가 있는 파일들 ===")
            cursor.execute("SELECT DISTINCT f.file_id, f.path, f.language, COUNT(c.class_id) as class_count FROM files f LEFT JOIN classes c ON f.file_id = c.file_id GROUP BY f.file_id, f.path, f.language HAVING class_count > 0 ORDER BY f.file_id")
            files_with_classes = cursor.fetchall()
            
            print(f"클래스가 있는 파일 수: {len(files_with_classes)}")
            for file_id, path, language, class_count in files_with_classes:
                print(f"  ID: {file_id}, 언어: {language}, 클래스: {class_count}개")
                print(f"    경로: {path}")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ 메타디비 조회 오류: {e}")
    else:
        print("❌ 메타디비 파일이 없습니다.")

if __name__ == "__main__":
    import os
    check_all_files()

