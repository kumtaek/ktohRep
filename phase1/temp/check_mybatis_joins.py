import os
import re

# MyBatis XML 파일에서 JOIN 쿼리 찾기
xml_files = []
for root, dirs, files in os.walk("project/sampleSrc/src"):
    for file in files:
        if file.endswith('.xml'):
            xml_files.append(os.path.join(root, file))

print(f"MyBatis XML 파일 수: {len(xml_files)}")

total_join_count = 0
for xml_file in xml_files:
    with open(xml_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # JOIN 패턴 찾기
    join_patterns = [
        r'JOIN\s+(\w+)\s+ON\s+([^,\s]+)\s*=\s*([^,\s]+)',
        r'INNER\s+JOIN\s+(\w+)\s+ON\s+([^,\s]+)\s*=\s*([^,\s]+)',
        r'LEFT\s+JOIN\s+(\w+)\s+ON\s+([^,\s]+)\s*=\s*([^,\s]+)',
        r'RIGHT\s+JOIN\s+(\w+)\s+ON\s+([^,\s]+)\s*=\s*([^,\s]+)',
        r'OUTER\s+JOIN\s+(\w+)\s+ON\s+([^,\s]+)\s*=\s*([^,\s]+)',
    ]
    
    file_join_count = 0
    for pattern in join_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            table = match.group(1)
            left_col = match.group(2)
            right_col = match.group(3)
            file_join_count += 1
            print(f"  {os.path.basename(xml_file)}: {table} ON {left_col}={right_col}")
    
    if file_join_count > 0:
        print(f"{os.path.basename(xml_file)}: {file_join_count}개 JOIN")
        total_join_count += file_join_count

print(f"\n총 JOIN 수: {total_join_count}개")


