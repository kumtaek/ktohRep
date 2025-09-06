import sqlite3

conn = sqlite3.connect('../project/sampleSrc/metadata.db')
cursor = conn.cursor()

print('=== 청킹 테이블 구조 확인 ===')
cursor.execute('PRAGMA table_info(chunks)')
columns = cursor.fetchall()
for col in columns:
    print(f'  {col[1]} ({col[2]})')

print('\n=== 청킹 데이터 샘플 ===')
cursor.execute('SELECT * FROM chunks LIMIT 5')
chunks = cursor.fetchall()
for chunk in chunks:
    print(f'  {chunk}')

print('\n=== 파일별 청킹 현황 ===')
cursor.execute('''
    SELECT f.path, COUNT(c.chunk_id) as chunk_count 
    FROM files f 
    LEFT JOIN chunks c ON f.file_id = c.file_id 
    GROUP BY f.file_id, f.path 
    ORDER BY chunk_count DESC
''')
chunk_results = cursor.fetchall()
for row in chunk_results:
    filename = row[0].split("/")[-1]
    print(f'  {filename}: {row[1]}개 청크')

conn.close()

