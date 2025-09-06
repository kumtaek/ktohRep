#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def check_hybrid_results():
    """하이브리드 패턴 적용 후 결과 확인"""
    
    # 메타디비 경로
    db_path = "project/sampleSrc/metadata.db"
    
    if not os.path.exists(db_path):
        print("❌ 메타데이터베이스가 존재하지 않습니다.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=== 하이브리드 패턴 적용 후 결과 검토 ===\n")
        
        # 1. 전체 파일 수
        cursor.execute("SELECT COUNT(*) FROM files")
        file_count = cursor.fetchone()[0]
        print(f"📁 전체 파일 수: {file_count}")
        
        # 2. 전체 클래스 수
        cursor.execute("SELECT COUNT(*) FROM classes")
        class_count = cursor.fetchone()[0]
        print(f"🏗️ 전체 클래스 수: {class_count}")
        
        # 3. 전체 메서드 수
        cursor.execute("SELECT COUNT(*) FROM methods")
        method_count = cursor.fetchone()[0]
        print(f"⚙️ 전체 메서드 수: {method_count}")
        
        # 4. 메서드 타입별 분류
        print(f"\n=== 메서드 타입별 분류 ===")
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN name LIKE 'get%' THEN 'getter'
                    WHEN name LIKE 'set%' THEN 'setter'
                    WHEN name = class_name THEN 'constructor'
                    ELSE 'business_method'
                END as method_type,
                COUNT(*) as count
            FROM methods m
            JOIN classes c ON m.class_id = c.id
            GROUP BY method_type
            ORDER BY count DESC
        """)
        
        for row in cursor.fetchall():
            method_type, count = row
            print(f"  {method_type}: {count}개")
        
        # 5. 생성자 vs 메서드 분류
        print(f"\n=== 생성자 vs 메서드 분류 ===")
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN m.name = c.name THEN 'constructor'
                    ELSE 'method'
                END as type,
                COUNT(*) as count
            FROM methods m
            JOIN classes c ON m.class_id = c.id
            GROUP BY type
            ORDER BY count DESC
        """)
        
        for row in cursor.fetchall():
            method_type, count = row
            print(f"  {method_type}: {count}개")
        
        # 6. 어노테이션 있는 메서드 확인
        print(f"\n=== 어노테이션 있는 메서드 확인 ===")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM methods 
            WHERE signature LIKE '%@%'
        """)
        annotated_count = cursor.fetchone()[0]
        print(f"  어노테이션 있는 메서드: {annotated_count}개")
        
        # 7. 샘플 메서드들 확인
        print(f"\n=== 샘플 메서드들 ===")
        cursor.execute("""
            SELECT m.name, m.signature, c.name as class_name
            FROM methods m
            JOIN classes c ON m.class_id = c.id
            ORDER BY m.name
            LIMIT 10
        """)
        
        for row in cursor.fetchall():
            method_name, signature, class_name = row
            print(f"  {class_name}.{method_name}(): {signature[:50]}...")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    check_hybrid_results()