import sqlite3

# 메타디비 연결
conn = sqlite3.connect('../project/sampleSrc/metadata.db')
cursor = conn.cursor()

# 기본 통계
cursor.execute('SELECT COUNT(*) FROM edges')
edges_count = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM classes')
classes_count = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM methods')
methods_count = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM files')
files_count = cursor.fetchone()[0]

print('=== 최종 메타DB 상태 ===')
print(f'Files: {files_count}')
print(f'Classes: {classes_count}')
print(f'Methods: {methods_count}')
print(f'Edges: {edges_count}')

# Edge 상세 정보
if edges_count > 0:
    print('\n=== Edge 상세 정보 ===')
    cursor.execute('SELECT edge_id, src_type, src_id, dst_type, dst_id, edge_kind, confidence FROM edges LIMIT 5')
    edges = cursor.fetchall()
    for edge_id, src_type, src_id, dst_type, dst_id, edge_kind, confidence in edges:
        print(f'ID: {edge_id}, {src_type}:{src_id} -> {dst_type}:{dst_id} ({edge_kind}, conf: {confidence})')

# Service 클래스 확인
print('\n=== Service 클래스 확인 ===')
cursor.execute("SELECT class_id, fqn, name FROM classes WHERE name LIKE '%Service%' ORDER BY fqn")
service_classes = cursor.fetchall()
print(f'Service 클래스 수: {len(service_classes)}')
for class_id, fqn, name in service_classes:
    print(f'  - {name} ({fqn})')

conn.close()