#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

def check_methods():
    conn = sqlite3.connect('./project/sampleSrc/metadata.db')
    cursor = conn.cursor()

    print('=== 메서드 상세 정보 ===')
    cursor.execute('SELECT m.name, m.return_type, m.parameters, f.path FROM methods m JOIN classes c ON m.class_id = c.class_id JOIN files f ON c.file_id = f.file_id ORDER BY f.path, m.name')
    methods = cursor.fetchall()
    
    current_file = None
    method_count = 0
    for name, return_type, params, path in methods:
        if path != current_file:
            if current_file:
                print(f'  총 {method_count}개 메서드\n')
            current_file = path
            method_count = 0
            print(f'파일: {path}')
        
        print(f'  - {return_type} {name}({params})')
        method_count += 1
    
    if current_file:
        print(f'  총 {method_count}개 메서드\n')
    
    print(f'전체 총 메서드 수: {len(methods)}')
    conn.close()

if __name__ == "__main__":
    check_methods()
