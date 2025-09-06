#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('./project/sampleSrc/metadata.db')
cursor = conn.cursor()

print('=== 메타디비 JSP 파일 상세 분석 ===')
cursor.execute('SELECT path, language FROM files WHERE language = "jsp"')
jsp_files = cursor.fetchall()
print(f'메타디비 JSP 파일 수: {len(jsp_files)}')
for path, lang in jsp_files:
    print(f'  {path}')

print('\n=== parse_results 테이블 확인 ===')
cursor.execute('SELECT file_id, parser_type, success, error_message FROM parse_results')
results = cursor.fetchall()
print(f'파싱 결과 수: {len(results)}')
for file_id, parser_type, success, error_msg in results:
    print(f'  file_id: {file_id}, parser: {parser_type}, success: {success}, error: {error_msg}')

print('\n=== files와 parse_results 조인 확인 ===')
cursor.execute('''
    SELECT f.path, f.language, pr.parser_type, pr.success, pr.error_message 
    FROM files f 
    LEFT JOIN parse_results pr ON f.file_id = pr.file_id
    WHERE f.language = "jsp"
''')
joined_results = cursor.fetchall()
print(f'조인 결과 수: {len(joined_results)}')
for path, lang, parser_type, success, error_msg in joined_results:
    print(f'  {path} -> parser: {parser_type}, success: {success}, error: {error_msg}')

conn.close()

