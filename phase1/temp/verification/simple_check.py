import sqlite3

conn = sqlite3.connect('../project/sampleSrc/metadata.db')
cursor = conn.cursor()

# 기본 통계
cursor.execute('SELECT COUNT(*) FROM methods')
methods = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM sql_units')
sql_units = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM chunks')
chunks = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM files')
files = cursor.fetchone()[0]

print(f"Files: {files}")
print(f"Methods: {methods}")
print(f"SQL Units: {sql_units}")
print(f"Chunks: {chunks}")

# Java 파일별 메소드 수
print("\nJava 파일별 메소드 수:")
cursor.execute('''
    SELECT f.path, COUNT(m.method_id) as method_count
    FROM files f
    LEFT JOIN methods m ON f.file_id = m.file_id
    WHERE f.language = 'java'
    GROUP BY f.file_id, f.path
    ORDER BY method_count DESC
''')
for row in cursor.fetchall():
    filename = row[0].split("/")[-1]
    print(f"  {filename}: {row[1]}개")

# XML 파일별 SQL Unit 수
print("\nXML 파일별 SQL Unit 수:")
cursor.execute('''
    SELECT f.path, COUNT(s.sql_unit_id) as sql_count
    FROM files f
    LEFT JOIN sql_units s ON f.file_id = s.file_id
    WHERE f.language = 'xml'
    GROUP BY f.file_id, f.path
    ORDER BY sql_count DESC
''')
for row in cursor.fetchall():
    filename = row[0].split("/")[-1]
    print(f"  {filename}: {row[1]}개")

conn.close()
