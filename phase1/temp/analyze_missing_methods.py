import os
import re
import sqlite3

# 메타디비에서 추출된 메서드 목록 확인
conn = sqlite3.connect('project/sampleSrc/metadata.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT m.name, m.parameters, f.path 
    FROM methods m 
    JOIN classes c ON m.class_id = c.class_id
    JOIN files f ON c.file_id = f.file_id 
    WHERE f.path LIKE '%.java'
    ORDER BY f.path, m.name
""")
extracted_methods = cursor.fetchall()

print("=== 메타디비에서 추출된 메서드 목록 ===")
for method in extracted_methods:
    print(f"  {method[2]} -> {method[0]}({method[1]})")

print(f"\n추출된 메서드 수: {len(extracted_methods)}개")

# 실제 Java 파일에서 메서드 찾기
java_files = []
for root, dirs, files in os.walk("project/sampleSrc/src"):
    for file in files:
        if file.endswith('.java'):
            java_files.append(os.path.join(root, file))

print(f"\n=== 실제 Java 파일에서 메서드 찾기 ===")
total_actual_methods = 0

for java_file in java_files:
    with open(java_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 메서드 패턴 (현재 파서와 동일)
    method_patterns = [
        r'(?:@\w+(?:\([^)]*\))?\s*)*public\s+(\w+)\s*\(([^)]*)\)\s*\{',
        r'(?:@\w+(?:\([^)]*\))?\s*)*public\s+(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?(\w+(?:<[^>]*>)?)\s+(\w+)\s*\(([^)]*)\)\s*\{[^}]{20,}',
    ]
    
    file_methods = []
    for i, pattern in enumerate(method_patterns):
        matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
        for match in matches:
            if i == 0:  # 생성자 패턴
                method_name = match.group(1)
                parameters = match.group(2)
            else:  # 메서드 패턴
                method_name = match.group(2)
                parameters = match.group(3)
            
            file_methods.append(f"{method_name}({parameters})")
    
    if file_methods:
        print(f"{os.path.basename(java_file)}: {len(file_methods)}개")
        for method in file_methods:
            print(f"  - {method}")
        total_actual_methods += len(file_methods)

print(f"\n실제 Java 파일의 메서드 수: {total_actual_methods}개")
print(f"메타디비 추출 메서드 수: {len(extracted_methods)}개")
print(f"차이: {total_actual_methods - len(extracted_methods)}개")

conn.close()
