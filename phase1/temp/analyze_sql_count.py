import sqlite3

# 메타디비에서 SQL 단위 정보 확인
conn = sqlite3.connect('project/sampleSrc/metadata.db')
cursor = conn.cursor()

# SQL 단위 수 확인
cursor.execute("SELECT COUNT(*) FROM sql_units")
sql_count = cursor.fetchone()[0]
print(f'메타디비 SQL 단위 수: {sql_count}')

# SQL 단위 목록 확인
cursor.execute("""
    SELECT su.origin, su.stmt_kind, su.stmt_id, f.path 
    FROM sql_units su 
    JOIN files f ON su.file_id = f.file_id 
    ORDER BY su.origin, f.path
""")
sql_units = cursor.fetchall()
print(f'\nSQL 단위 목록:')
for sql in sql_units:
    print(f'  {sql[0]} - {sql[1]} - {sql[2]} - {sql[3]}')

# origin별 SQL 단위 수 확인
cursor.execute("""
    SELECT origin, COUNT(*) as count
    FROM sql_units 
    GROUP BY origin
    ORDER BY origin
""")
origin_counts = cursor.fetchall()
print(f'\nOrigin별 SQL 단위 수:')
for oc in origin_counts:
    print(f'  {oc[0]}: {oc[1]}개')

conn.close()




