import os
import re

# Java 파일에서 SQL 추출 패턴 테스트
java_files = []
for root, dirs, files in os.walk("project/sampleSrc/src"):
    for file in files:
        if file.endswith('.java'):
            java_files.append(os.path.join(root, file))

print("=== Java SQL 추출 패턴 분석 ===")

for java_file in java_files:
    with open(java_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"\n--- {os.path.basename(java_file)} ---")
    
    # 현재 파서 패턴
    current_patterns = [
        r'String\s+\w+\s*=\s*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|TRUNCATE|MERGE)[^"\']*)["\']',
        r'["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|TRUNCATE|MERGE)[^"\']*)["\']',
        r'StringBuilder\s*\([^)]*\)\s*\.append\s*\(\s*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|TRUNCATE|MERGE)[^"\']*)["\']',
        r'["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|TRUNCATE|MERGE)[^"\']*(?:\s*\+\s*["\'][^"\']*["\'])*)["\']',
    ]
    
    # 더 포괄적인 패턴
    comprehensive_patterns = [
        r'String\s+\w+\s*=\s*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|TRUNCATE|MERGE)[^"\']*)["\']',
        r'["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|TRUNCATE|MERGE)[^"\']*)["\']',
        r'StringBuilder\s*\([^)]*\)\s*\.append\s*\(\s*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|TRUNCATE|MERGE)[^"\']*)["\']',
        r'["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|TRUNCATE|MERGE)[^"\']*(?:\s*\+\s*["\'][^"\']*["\'])*)["\']',
        # 추가 패턴들
        r'=\s*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|TRUNCATE|MERGE)[^"\']*)["\']',
        r'\+=\s*["\']([^"\']*(?:SELECT|INSERT|UPDATE|DELETE|TRUNCATE|MERGE)[^"\']*)["\']',
    ]
    
    current_count = 0
    comprehensive_count = 0
    
    print("현재 패턴으로 추출된 SQL:")
    for i, pattern in enumerate(current_patterns):
        matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
        for match in matches:
            sql_text = match.group(1)
            if sql_text and len(sql_text.strip()) > 10:
                current_count += 1
                print(f"  - {sql_text[:50]}...")
    
    print(f"현재 패턴 총 개수: {current_count}")
    
    print("\n포괄적 패턴으로 추출된 SQL:")
    for i, pattern in enumerate(comprehensive_patterns):
        matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
        for match in matches:
            sql_text = match.group(1)
            if sql_text and len(sql_text.strip()) > 10:
                comprehensive_count += 1
                print(f"  - {sql_text[:50]}...")
    
    print(f"포괄적 패턴 총 개수: {comprehensive_count}")
    print(f"차이: {comprehensive_count - current_count}개")


