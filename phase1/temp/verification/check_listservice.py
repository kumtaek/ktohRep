import sqlite3

# 메타디비 연결
conn = sqlite3.connect('../project/sampleSrc/metadata.db')
cursor = conn.cursor()

# ListService 관련 클래스 조회
cursor.execute("SELECT class_id, fqn, name FROM classes WHERE name LIKE '%ListService%' ORDER BY fqn")
classes = cursor.fetchall()

print('=== ListService 관련 클래스 ===')
for class_id, fqn, name in classes:
    print(f'ID: {class_id}, FQN: {fqn}, Name: {name}')

conn.close()




