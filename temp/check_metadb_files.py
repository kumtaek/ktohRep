#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os

def check_metadb_files():
    """메타디비의 파일 정보를 확인"""
    db_path = 'phase1/project/sampleSrc/metadata.db'
    
    if not os.path.exists(db_path):
        print(f"메타디비 파일이 존재하지 않습니다: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 언어별 파일 수
        cursor.execute('SELECT language, COUNT(*) FROM files GROUP BY language')
        print('언어별 파일 수:')
        for row in cursor.fetchall():
            print(f'  {row[0]}: {row[1]}개')
        
        # 전체 파일 목록
        cursor.execute('SELECT path, language FROM files ORDER BY language, path')
        print('\n전체 파일 목록:')
        for row in cursor.fetchall():
            print(f'  {row[1]}: {row[0]}')
        
        conn.close()
        
    except Exception as e:
        print(f"메타디비 조회 중 오류: {e}")

if __name__ == "__main__":
    check_metadb_files()


