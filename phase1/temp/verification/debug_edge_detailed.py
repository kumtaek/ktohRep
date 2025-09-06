import sqlite3

# 메타디비 연결
conn = sqlite3.connect('../project/sampleSrc/metadata.db')
cursor = conn.cursor()

# ListServiceImpl1과 ListService 클래스 정보 확인
print('=== ListServiceImpl1과 ListService 클래스 정보 ===')
cursor.execute("SELECT class_id, fqn, name FROM classes WHERE name IN ('ListServiceImpl1', 'ListService') ORDER BY fqn")
classes = cursor.fetchall()
for class_id, fqn, name in classes:
    print(f'ID: {class_id}, FQN: {fqn}, Name: {name}')

# Edge 테이블 구조 확인
print('\n=== Edge 테이블 구조 ===')
cursor.execute("PRAGMA table_info(edges)")
columns = cursor.fetchall()
for col in columns:
    print(f'{col[1]} ({col[2]})')

# Edge 테이블에 데이터가 있는지 확인
print('\n=== Edge 테이블 데이터 확인 ===')
cursor.execute("SELECT COUNT(*) FROM edges")
count = cursor.fetchone()[0]
print(f'Edge 테이블 총 레코드 수: {count}')

if count > 0:
    cursor.execute("SELECT * FROM edges LIMIT 3")
    edges = cursor.fetchall()
    for edge in edges:
        print(f'Edge: {edge}')
else:
    print('Edge 테이블이 비어있습니다.')

conn.close()




