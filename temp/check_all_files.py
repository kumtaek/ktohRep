#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('./project/sampleSrc/metadata.db')
cursor = conn.cursor()

print('=== 메타디비 전체 파일 현황 ===')
cursor.execute('SELECT language, COUNT(*) FROM files GROUP BY language')
file_counts = cursor.fetchall()
for lang, count in file_counts:
    print(f'{lang}: {count}개')

print('\n=== files 테이블 전체 내용 ===')
cursor.execute('SELECT file_id, path, language FROM files ORDER BY file_id')
all_files = cursor.fetchall()
for file_id, path, lang in all_files:
    print(f'{file_id}: {path} ({lang})')

conn.close()

