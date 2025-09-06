import sqlite3

conn = sqlite3.connect('../project/sampleSrc/metadata.db')
cursor = conn.cursor()

print('=== A파일 검증 쿼리 실행 ===')

# 1. 호출 관계 복구 확인
print('\n1. 호출 관계 확인:')
cursor.execute('SELECT COUNT(*) FROM edges WHERE edge_kind = "call"')
call_edges = cursor.fetchone()[0]
print(f'  Call edges: {call_edges}개')

# 2. Service 클래스 복구 확인  
print('\n2. Service 클래스 확인:')
cursor.execute('SELECT name FROM classes WHERE name LIKE "%Service%"')
service_classes = cursor.fetchall()
print(f'  Service 클래스 수: {len(service_classes)}개')
for cls in service_classes:
    print(f'    - {cls[0]}')

# 3. 전체 클래스 현황
print('\n3. 전체 클래스 현황:')
cursor.execute('SELECT name FROM classes WHERE name IS NOT NULL ORDER BY name')
all_classes = cursor.fetchall()
print(f'  전체 클래스 수: {len(all_classes)}개')
for cls in all_classes[:10]:  # 처음 10개만 출력
    print(f'    - {cls[0]}')

# 4. 메소드-클래스 연결 확인
print('\n4. 메소드-클래스 연결 확인:')
cursor.execute('''
    SELECT c.name, COUNT(m.method_id) as method_count
    FROM classes c
    LEFT JOIN methods m ON c.class_id = m.class_id
    WHERE c.name IS NOT NULL
    GROUP BY c.class_id, c.name
    ORDER BY method_count DESC
    LIMIT 10
''')
class_methods = cursor.fetchall()
for row in class_methods:
    print(f'    - {row[0]}: {row[1]}개 메소드')

# 5. NULL 클래스 확인
print('\n5. NULL 클래스 확인:')
cursor.execute('SELECT COUNT(*) FROM classes WHERE name IS NULL')
null_classes = cursor.fetchone()[0]
print(f'  NULL 클래스 수: {null_classes}개')

conn.close()

