import os
import glob

# 실제 파일 수 확인
src_files = glob.glob('project/sampleSrc/src/**/*', recursive=True)
src_files = [f for f in src_files if os.path.isfile(f)]
print(f'실제 파일 수: {len(src_files)}')
for f in sorted(src_files):
    print(f'  {f}')

# 메타디비의 파일 수 확인
import sqlite3
conn = sqlite3.connect('project/sampleSrc/metadata.db')
cursor = conn.cursor()

# 파일 테이블 구조 확인
cursor.execute("PRAGMA table_info(files)")
columns = cursor.fetchall()
print(f'\n파일 테이블 구조:')
for col in columns:
    print(f'  {col}')

# 파일 수 확인
cursor.execute("SELECT COUNT(*) FROM files")
file_count = cursor.fetchone()[0]
print(f'\n메타디비 파일 수: {file_count}')

# 파일 목록 확인
cursor.execute("SELECT * FROM files LIMIT 5")
files = cursor.fetchall()
print(f'\n파일 목록 (처음 5개):')
for f in files:
    print(f'  {f}')

conn.close()