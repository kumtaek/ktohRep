import sqlite3

conn = sqlite3.connect('../project/sampleSrc/metadata.db')
cursor = conn.cursor()

print('=== 누락된 클래스들 상세 확인 ===')

# 1. 실제 Java 파일 목록
print('\n1. 실제 Java 파일 목록:')
cursor.execute('''
    SELECT f.path, c.name
    FROM files f
    LEFT JOIN classes c ON f.file_id = c.file_id
    WHERE f.language = 'java'
    ORDER BY f.path
''')
file_classes = cursor.fetchall()
for row in file_classes:
    filename = row[0].split("\\")[-1]  # Windows 경로 구분자
    class_name = row[1] if row[1] else "NULL"
    print(f'  {filename}: {class_name}')

# 2. 누락된 Service 클래스들 확인
print('\n2. 누락된 Service 클래스들:')
missing_services = ['OrderService', 'UserService', 'ProductService']
for service in missing_services:
    cursor.execute('SELECT COUNT(*) FROM classes WHERE name = ?', (service,))
    count = cursor.fetchone()[0]
    if count == 0:
        print(f'  ❌ {service}: 누락')
    else:
        print(f'  ✅ {service}: 존재')

# 3. 파일별 메소드 수 확인
print('\n3. 파일별 메소드 수:')
cursor.execute('''
    SELECT f.path, COUNT(m.method_id) as method_count
    FROM files f
    LEFT JOIN classes c ON f.file_id = c.file_id
    LEFT JOIN methods m ON c.class_id = m.class_id
    WHERE f.language = 'java'
    GROUP BY f.file_id, f.path
    ORDER BY method_count DESC
''')
file_methods = cursor.fetchall()
for row in file_methods:
    filename = row[0].split("\\")[-1]
    method_count = row[1]
    print(f'  {filename}: {method_count}개 메소드')

conn.close()

