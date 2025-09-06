import sqlite3

# 메타디비에서 에지/조인 정보 확인
conn = sqlite3.connect('project/sampleSrc/metadata.db')
cursor = conn.cursor()

# 에지 수 확인
cursor.execute("SELECT COUNT(*) FROM edges")
edge_count = cursor.fetchone()[0]
print(f'메타디비 에지 수: {edge_count}')

# 조인 수 확인
cursor.execute("SELECT COUNT(*) FROM joins")
join_count = cursor.fetchone()[0]
print(f'메타디비 조인 수: {join_count}')

# 에지 테이블 구조 확인
cursor.execute("PRAGMA table_info(edges)")
edge_columns = cursor.fetchall()
print(f'\n에지 테이블 구조:')
for col in edge_columns:
    print(f'  {col}')

# 조인 테이블 구조 확인
cursor.execute("PRAGMA table_info(joins)")
join_columns = cursor.fetchall()
print(f'\n조인 테이블 구조:')
for col in join_columns:
    print(f'  {col}')

conn.close()




