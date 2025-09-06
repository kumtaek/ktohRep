import os
import re
import sqlite3

# 메타디비에서 추출된 SQL 단위 목록 확인
conn = sqlite3.connect('project/sampleSrc/metadata.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT su.origin, su.stmt_kind, su.stmt_id, f.path 
    FROM sql_units su 
    JOIN files f ON su.file_id = f.file_id 
    ORDER BY su.origin, f.path
""")
extracted_sqls = cursor.fetchall()

print("=== 메타디비에서 추출된 SQL 단위 목록 ===")
for sql in extracted_sqls:
    print(f"  {sql[0]} - {sql[1]} - {sql[2]} - {sql[3]}")

print(f"\n추출된 SQL 단위 수: {len(extracted_sqls)}개")

# 실제 파일에서 SQL 찾기
print(f"\n=== 실제 파일에서 SQL 찾기 ===")

# 1. MyBatis XML 파일에서 SQL 찾기
xml_files = []
for root, dirs, files in os.walk("project/sampleSrc/src"):
    for file in files:
        if file.endswith('.xml'):
            xml_files.append(os.path.join(root, file))

xml_sql_count = 0
for xml_file in xml_files:
    with open(xml_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # MyBatis SQL 태그 패턴
    sql_patterns = [
        r'<select[^>]*id\s*=\s*["\']([^"\']*)["\'][^>]*>(.*?)</select>',
        r'<insert[^>]*id\s*=\s*["\']([^"\']*)["\'][^>]*>(.*?)</insert>',
        r'<update[^>]*id\s*=\s*["\']([^"\']*)["\'][^>]*>(.*?)</update>',
        r'<delete[^>]*id\s*=\s*["\']([^"\']*)["\'][^>]*>(.*?)</delete>',
    ]
    
    file_sql_count = 0
    for pattern in sql_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
        for match in matches:
            sql_id = match.group(1)
            sql_content = match.group(2)
            if sql_content.strip():
                file_sql_count += 1
    
    if file_sql_count > 0:
        print(f"{os.path.basename(xml_file)}: {file_sql_count}개 SQL")
        xml_sql_count += file_sql_count

print(f"MyBatis XML SQL 수: {xml_sql_count}개")

# 2. Java 파일에서 SQL 찾기
java_files = []
for root, dirs, files in os.walk("project/sampleSrc/src"):
    for file in files:
        if file.endswith('.java'):
            java_files.append(os.path.join(root, file))

java_sql_count = 0
for java_file in java_files:
    with open(java_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Java SQL 패턴
    sql_patterns = [
        r'String\s+\w+\s*=\s*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|TRUNCATE|MERGE)[^"\']*)["\']',
        r'["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|TRUNCATE|MERGE)[^"\']*)["\']',
    ]
    
    file_sql_count = 0
    for pattern in sql_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
        for match in matches:
            sql_text = match.group(1)
            if sql_text and len(sql_text.strip()) > 10:
                file_sql_count += 1
    
    if file_sql_count > 0:
        print(f"{os.path.basename(java_file)}: {file_sql_count}개 SQL")
        java_sql_count += file_sql_count

print(f"Java SQL 수: {java_sql_count}개")
print(f"총 실제 SQL 수: {xml_sql_count + java_sql_count}개")
print(f"메타디비 추출 SQL 수: {len(extracted_sqls)}개")
print(f"차이: {(xml_sql_count + java_sql_count) - len(extracted_sqls)}개")

conn.close()


