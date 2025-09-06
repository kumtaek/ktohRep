#!/usr/bin/env python3
"""
XML 파서 정확도 확인
"""

import sqlite3
import os

def check_xml_accuracy():
    """XML 파서 정확도 확인"""
    
    # 수동 분석 결과 (이전에 확인한 값)
    manual_xml_total = 116  # 수동 분석에서 확인한 총 XML 쿼리 수
    
    # MetaDB에서 XML SQL Units 확인
    db_path = "project/sampleSrc/metadata.db"
    if not os.path.exists(db_path):
        print("MetaDB가 존재하지 않습니다.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # XML 파일별 SQL Units 개수 확인
    cursor.execute("""
        SELECT f.path, COUNT(su.sql_id) as sql_count
        FROM files f
        LEFT JOIN sql_units su ON f.file_id = su.file_id
        WHERE f.language = 'xml'
        GROUP BY f.file_id, f.path
        ORDER BY f.path
    """)
    
    xml_files = cursor.fetchall()
    total_metadb_sql_units = 0
    
    print("=== XML 파일별 SQL Units 개수 ===")
    for file_path, sql_count in xml_files:
        relative_path = os.path.relpath(file_path, "E:\\SourceAnalyzer.git\\project\\sampleSrc\\src")
        print(f"{relative_path}: {sql_count}개")
        total_metadb_sql_units += sql_count
    
    print(f"\n=== 정확도 분석 ===")
    print(f"수동 분석 총 XML 쿼리: {manual_xml_total}개")
    print(f"MetaDB 총 SQL Units: {total_metadb_sql_units}개")
    
    if manual_xml_total > 0:
        accuracy = (total_metadb_sql_units / manual_xml_total) * 100
        print(f"XML 파서 정확도: {accuracy:.1f}%")
        
        if accuracy >= 95:
            print("✅ 목표 달성! 95% 이상 정확도")
        else:
            print(f"❌ 목표 미달성. {95 - accuracy:.1f}% 더 개선 필요")
    else:
        print("수동 분석 결과가 없습니다.")
    
    conn.close()

if __name__ == "__main__":
    check_xml_accuracy()
