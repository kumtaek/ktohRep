import sqlite3

conn = sqlite3.connect('project/sampleSrc/metadata.db')
cursor = conn.cursor()

# 메서드 수 확인
cursor.execute('SELECT COUNT(*) FROM methods')
method_count = cursor.fetchone()[0]
print(f'메서드 수: {method_count}개')

# 메서드 샘플 확인
cursor.execute('SELECT name, parameters, modifiers FROM methods LIMIT 20')
methods = cursor.fetchall()
print(f'\n메서드 샘플 (처음 20개):')
for i, method in enumerate(methods):
    print(f'{i+1}. {method[0]}({method[1]}) - {method[2]}')

conn.close()


