import sqlite3

conn = sqlite3.connect('../project/sampleSrc/metadata.db')
cursor = conn.cursor()

# 테이블 목록 확인
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print('테이블 목록:', tables)

# sql_units 테이블이 있으면 분석
if 'sql_units' in tables:
    cursor.execute('SELECT origin, stmt_kind, COUNT(*) FROM sql_units GROUP BY origin, stmt_kind')
    results = cursor.fetchall()
    print('SQL Units 분석:')
    for row in results:
        print(f'  {row[0]} - {row[1]}: {row[2]}개')
else:
    print('sql_units 테이블이 없습니다.')

conn.close()
