import sqlite3

# 메타디비 연결
conn = sqlite3.connect('../project/sampleSrc/metadata.db')
cursor = conn.cursor()

# 클래스 정보 조회
cursor.execute('SELECT class_id, fqn, name FROM classes ORDER BY fqn')
classes = cursor.fetchall()

print('=== Classes in MetaDB ===')
class_id_map = {}
for class_id, fqn, name in classes:
    class_id_map[fqn] = class_id
    print(f'ID: {class_id}, FQN: {fqn}, Name: {name}')

print('\n=== Edge FQN Resolution Test ===')
# Edge에서 찾으려는 FQN들
test_fqns = [
    'com.example.service.impl.ListServiceImpl1',
    'com.example.service.ListService'
]

for fqn in test_fqns:
    if fqn in class_id_map:
        print(f'✓ {fqn} -> {class_id_map[fqn]}')
    else:
        print(f'✗ {fqn} not found in class_id_map')

conn.close()




