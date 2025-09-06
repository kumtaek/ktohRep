import sqlite3

conn = sqlite3.connect('project/sampleSrc/metadata.db')
cursor = conn.cursor()

# SQL 단위 수 확인
cursor.execute('SELECT COUNT(*) FROM sql_units')
sql_count = cursor.fetchone()[0]
print(f'SQL 단위 수: {sql_count}개')

# Origin별 SQL 단위 수 확인
cursor.execute('SELECT origin, COUNT(*) as count FROM sql_units GROUP BY origin ORDER BY origin')
origin_counts = cursor.fetchall()
print(f'\nOrigin별 SQL 단위 수:')
for oc in origin_counts:
    print(f'  {oc[0]}: {oc[1]}개')

# SQL 단위 샘플 확인
cursor.execute('SELECT origin, stmt_kind, stmt_id, normalized_fingerprint FROM sql_units LIMIT 20')
sqls = cursor.fetchall()
print(f'\nSQL 단위 샘플 (처음 20개):')
for i, sql in enumerate(sqls):
    print(f'{i+1}. {sql[0]} - {sql[1]} - {sql[2]} - {sql[3][:50]}...')

conn.close()


