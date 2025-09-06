import sqlite3

# 메타디비에서 메서드 정보 확인
conn = sqlite3.connect('project/sampleSrc/metadata.db')
cursor = conn.cursor()

# 메서드 수 확인
cursor.execute("SELECT COUNT(*) FROM methods")
method_count = cursor.fetchone()[0]
print(f'메타디비 메서드 수: {method_count}')

# 메서드 테이블 직접 확인
cursor.execute("SELECT * FROM methods LIMIT 10")
methods = cursor.fetchall()
print(f'\n메서드 테이블 (처음 10개):')
for method in methods:
    print(f'  {method}')

# 클래스 수 확인
cursor.execute("SELECT COUNT(*) FROM classes")
class_count = cursor.fetchone()[0]
print(f'\n클래스 수: {class_count}')

# 클래스 목록 확인
cursor.execute("""
    SELECT c.name, f.path 
    FROM classes c 
    JOIN files f ON c.file_id = f.file_id 
    ORDER BY f.path
""")
classes = cursor.fetchall()
print(f'\n클래스 목록:')
for cls in classes:
    print(f'  {cls[1]} -> {cls[0]}')

conn.close()