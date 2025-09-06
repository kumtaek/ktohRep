#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
import re

def find_overextracted_getter():
    """과대추출된 getter/setter 사례 찾기"""
    
    db_path = './project/sampleSrc/metadata.db'
    if not os.path.exists(db_path):
        print(f"메타데이터베이스가 존재하지 않습니다: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # getter/setter 메서드 조회
    query = """
    SELECT m.name, m.signature, m.start_line, m.end_line, f.path
    FROM methods m
    JOIN classes c ON m.class_id = c.class_id
    JOIN files f ON c.file_id = f.file_id
    WHERE (m.name LIKE 'get%' OR m.name LIKE 'set%' OR m.name LIKE 'is%')
    ORDER BY m.name
    LIMIT 5
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print("=== 과대추출된 getter/setter 사례 ===")
    
    for i, (name, signature, start_line, end_line, path) in enumerate(results, 1):
        print(f"\n--- 사례 {i} ---")
        print(f"메서드명: {name}")
        print(f"시그니처: {signature}")
        print(f"파일: {path}")
        print(f"라인: {start_line}-{end_line}")
        print(f"라인 수: {end_line - start_line + 1}")
        
        # 실제 파일에서 해당 메서드 내용 확인
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                # 해당 라인 범위의 내용 추출
                method_lines = lines[start_line-1:end_line]
                method_content = '\n'.join(method_lines)
                
                print(f"실제 메서드 내용:")
                print(method_content)
                
                # 본문 길이 계산 (커멘트 제외)
                brace_start = method_content.find('{')
                brace_end = method_content.rfind('}')
                if brace_start != -1 and brace_end != -1:
                    body = method_content[brace_start+1:brace_end]
                    # 커멘트 제거
                    body_no_comments = re.sub(r'//.*$', '', body, flags=re.MULTILINE)
                    body_no_comments = re.sub(r'/\*.*?\*/', '', body_no_comments, flags=re.DOTALL)
                    body_no_comments = re.sub(r'\s+', ' ', body_no_comments).strip()
                    
                    print(f"본문 (커멘트 제외): '{body_no_comments}'")
                    print(f"본문 길이 (커멘트 제외): {len(body_no_comments)}자")
                    
                    if len(body_no_comments) <= 500:
                        print("→ 500자 이하이므로 매치되어야 함 (과대추출)")
                    else:
                        print("→ 500자 초과이므로 매치되지 않아야 함")
        
        # 첫 번째 사례만 상세히 보여주고 종료
        if i == 1:
            break
    
    conn.close()

if __name__ == "__main__":
    find_overextracted_getter()
