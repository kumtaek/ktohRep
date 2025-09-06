import os
import re

# Java 파일에서 SQL 문자열 찾기
java_files = []
for root, dirs, files in os.walk("project/sampleSrc/src"):
    for file in files:
        if file.endswith('.java'):
            java_files.append(os.path.join(root, file))

print(f"Java 파일 수: {len(java_files)}")

total_sql_count = 0
for java_file in java_files:
    with open(java_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # SQL 패턴 찾기
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
                print(f"  {os.path.basename(java_file)}: {sql_text[:50]}...")
    
    if file_sql_count > 0:
        print(f"{os.path.basename(java_file)}: {file_sql_count}개 SQL")
        total_sql_count += file_sql_count

print(f"\n총 Java SQL 수: {total_sql_count}개")


