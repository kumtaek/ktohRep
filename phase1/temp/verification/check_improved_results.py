import sqlite3

conn = sqlite3.connect('../project/sampleSrc/metadata.db')
cursor = conn.cursor()

print('=== 개선된 메타DB 상태 ===')

# 기본 통계
cursor.execute('SELECT COUNT(*) FROM files')
files = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM classes')
classes = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM methods')
methods = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM sql_units')
sql_units = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM chunks')
chunks = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM edges')
edges = cursor.fetchone()[0]

print(f'Files: {files}')
print(f'Classes: {classes}')
print(f'Methods: {methods}')
print(f'SQL Units: {sql_units}')
print(f'Chunks: {chunks}')
print(f'Edges: {edges}')

# Service 클래스 확인
print('\n=== Service 클래스 확인 ===')
cursor.execute('SELECT name FROM classes WHERE name LIKE "%Service%"')
service_classes = cursor.fetchall()
print(f'Service 클래스 수: {len(service_classes)}')
for cls in service_classes:
    print(f'  - {cls[0]}')

# 전체 클래스 목록
print('\n=== 전체 클래스 목록 ===')
cursor.execute('SELECT name FROM classes WHERE name IS NOT NULL ORDER BY name')
all_classes = cursor.fetchall()
print(f'전체 클래스 수: {len(all_classes)}')
for cls in all_classes:
    print(f'  - {cls[0]}')

conn.close()

