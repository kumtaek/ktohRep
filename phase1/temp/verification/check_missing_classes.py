import sqlite3

conn = sqlite3.connect('../project/sampleSrc/metadata.db')
cursor = conn.cursor()

print('=== 누락된 클래스 확인 ===')

# 1. 파일별 클래스 현황
print('\n1. 파일별 클래스 현황:')
cursor.execute('''
    SELECT f.path, c.name
    FROM files f
    LEFT JOIN classes c ON f.file_id = c.file_id
    WHERE f.language = 'java'
    ORDER BY f.path
''')
file_classes = cursor.fetchall()
for row in file_classes:
    filename = row[0].split("/")[-1]
    class_name = row[1] if row[1] else "NULL"
    print(f'  {filename}: {class_name}')

# 2. 누락된 Service 클래스들
print('\n2. 누락된 Service 클래스들:')
missing_services = ['OrderService', 'UserService', 'ProductService', 'VulnerabilityTestService']
for service in missing_services:
    cursor.execute('SELECT COUNT(*) FROM classes WHERE name = ?', (service,))
    count = cursor.fetchone()[0]
    if count == 0:
        print(f'  ❌ {service}: 누락')
    else:
        print(f'  ✅ {service}: 존재')

# 3. 누락된 기타 클래스들
print('\n3. 누락된 기타 클래스들:')
missing_others = ['Texts', 'SecurityConfig']
for cls in missing_others:
    cursor.execute('SELECT COUNT(*) FROM classes WHERE name = ?', (cls,))
    count = cursor.fetchone()[0]
    if count == 0:
        print(f'  ❌ {cls}: 누락')
    else:
        print(f'  ✅ {cls}: 존재')

conn.close()

