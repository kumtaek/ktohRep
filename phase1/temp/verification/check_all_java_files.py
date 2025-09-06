#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_all_java_files():
    """모든 Java 파일의 파싱 상태 확인"""
    print("=== 모든 Java 파일의 파싱 상태 확인 ===\n")
    
    db_path = "project/sampleSrc/metadata.db"
    
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 1. files 테이블에서 모든 Java 파일 확인
            print("=== 1. files 테이블의 모든 Java 파일 ===")
            cursor.execute("SELECT file_id, path, language, loc FROM files WHERE language = 'java' ORDER BY file_id")
            java_files = cursor.fetchall()
            
            print(f"Java 파일 수: {len(java_files)}")
            for file_id, path, language, loc in java_files:
                print(f"  ID: {file_id}, LOC: {loc}, 경로: {path}")
            
            # 2. classes 테이블에서 각 파일의 클래스 수 확인
            print(f"\n=== 2. classes 테이블의 클래스 수 ===")
            cursor.execute("SELECT file_id, COUNT(*) as class_count FROM classes GROUP BY file_id ORDER BY file_id")
            class_counts = cursor.fetchall()
            
            print(f"클래스가 있는 파일 수: {len(class_counts)}")
            for file_id, class_count in class_counts:
                print(f"  파일 ID: {file_id}, 클래스 수: {class_count}")
            
            # 3. methods 테이블에서 각 클래스의 메소드 수 확인
            print(f"\n=== 3. methods 테이블의 메소드 수 ===")
            cursor.execute("SELECT class_id, COUNT(*) as method_count FROM methods GROUP BY class_id ORDER BY class_id")
            method_counts = cursor.fetchall()
            
            print(f"메소드가 있는 클래스 수: {len(method_counts)}")
            for class_id, method_count in method_counts:
                print(f"  클래스 ID: {class_id}, 메소드 수: {method_count}")
            
            # 4. parse_results 테이블 확인
            print(f"\n=== 4. parse_results 테이블 ===")
            cursor.execute("SELECT COUNT(*) FROM parse_results")
            parse_count = cursor.fetchone()[0]
            print(f"파싱 결과 수: {parse_count}")
            
            if parse_count > 0:
                cursor.execute("SELECT file_id, parser_type, success, error_message FROM parse_results LIMIT 10")
                parse_results = cursor.fetchall()
                print("파싱 결과 샘플:")
                for file_id, parser_type, success, error_message in parse_results:
                    print(f"  파일 ID: {file_id}, 파서: {parser_type}, 성공: {success}, 오류: {error_message}")
            
            # 5. 파일별 요약
            print(f"\n=== 5. 파일별 요약 ===")
            for file_id, path, language, loc in java_files:
                # 클래스 수 확인
                cursor.execute("SELECT COUNT(*) FROM classes WHERE file_id = ?", (file_id,))
                class_count = cursor.fetchone()[0]
                
                # 메소드 수 확인
                cursor.execute("SELECT COUNT(*) FROM methods m JOIN classes c ON m.class_id = c.class_id WHERE c.file_id = ?", (file_id,))
                method_count = cursor.fetchone()[0]
                
                print(f"파일 ID: {file_id}")
                print(f"  경로: {path}")
                print(f"  LOC: {loc}")
                print(f"  클래스: {class_count}개")
                print(f"  메소드: {method_count}개")
                print()
            
            conn.close()
            
        except Exception as e:
            print(f"❌ 메타디비 조회 오류: {e}")
    else:
        print("❌ 메타디비 파일이 없습니다.")

if __name__ == "__main__":
    import os
    check_all_java_files()
