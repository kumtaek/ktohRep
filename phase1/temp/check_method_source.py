#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_method_source():
    conn = sqlite3.connect('./project/sampleSrc/metadata.db')
    cursor = conn.cursor()

    print('=== 메서드 추출 소스 확인 ===')
    cursor.execute('SELECT m.name, m.signature, f.path FROM methods m JOIN classes c ON m.class_id = c.class_id JOIN files f ON c.file_id = f.file_id LIMIT 10')
    methods = cursor.fetchall()
    
    for name, signature, path in methods:
        print(f'{path}: {name} - {signature}')

    print(f'\n총 메서드 수: {cursor.execute("SELECT COUNT(*) FROM methods").fetchone()[0]}')
    
    # 파일별 메서드 수 확인
    print('\n=== 파일별 메서드 수 ===')
    cursor.execute('SELECT f.path, COUNT(m.method_id) as method_count FROM files f LEFT JOIN classes c ON f.file_id = c.file_id LEFT JOIN methods m ON c.class_id = m.class_id GROUP BY f.path ORDER BY method_count DESC')
    file_methods = cursor.fetchall()
    
    for path, count in file_methods:
        if count > 0:
            print(f'{path}: {count}개')
    
    conn.close()

if __name__ == "__main__":
    check_method_source()




