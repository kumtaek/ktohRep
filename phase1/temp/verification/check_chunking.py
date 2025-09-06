import sqlite3
conn = sqlite3.connect('../project/sampleSrc/metadata.db')
cursor = conn.cursor()

print('=== 메타DB 청킹 결과 상세 분석 ===')

# 1. 파일별 메소드 수 확인
print('\n1. 파일별 메소드 수:')
cursor.execute('''
    SELECT f.path, COUNT(m.method_id) as method_count
    FROM files f
    LEFT JOIN methods m ON f.file_id = m.file_id
    WHERE f.language = 'java'
    GROUP BY f.file_id, f.path
    ORDER BY method_count DESC
''')
for row in cursor.fetchall():
    filename = row[0].split("/")[-1]
    print(f'  {filename}: {row[1]}개 메소드')

# 2. 파일별 SQL Unit 수 확인
print('\n2. 파일별 SQL Unit 수:')
cursor.execute('''
    SELECT f.path, COUNT(s.sql_unit_id) as sql_count
    FROM files f
    LEFT JOIN sql_units s ON f.file_id = s.file_id
    WHERE f.language IN ('xml', 'jsp')
    GROUP BY f.file_id, f.path
    ORDER BY sql_count DESC
''')
for row in cursor.fetchall():
    filename = row[0].split("/")[-1]
    print(f'  {filename}: {row[1]}개 쿼리')

# 3. 파일별 청크 수 확인
print('\n3. 파일별 청크 수:')
cursor.execute('''
    SELECT f.path, COUNT(c.chunk_id) as chunk_count
    FROM files f
    LEFT JOIN chunks c ON f.file_id = c.file_id
    GROUP BY f.file_id, f.path
    ORDER BY chunk_count DESC
''')
for row in cursor.fetchall():
    filename = row[0].split("/")[-1]
    print(f'  {filename}: {row[1]}개 청크')

# 4. 언어별 통계
print('\n4. 언어별 통계:')
cursor.execute('''
    SELECT f.language, COUNT(f.file_id) as file_count, 
           COUNT(m.method_id) as method_count,
           COUNT(s.sql_unit_id) as sql_count,
           COUNT(c.chunk_id) as chunk_count
    FROM files f
    LEFT JOIN methods m ON f.file_id = m.file_id
    LEFT JOIN sql_units s ON f.file_id = s.file_id
    LEFT JOIN chunks c ON f.file_id = c.file_id
    GROUP BY f.language
''')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[1]}개 파일, {row[2]}개 메소드, {row[3]}개 쿼리, {row[4]}개 청크')

conn.close()
