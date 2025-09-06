import os
import re

# Java 파일에서 메서드 추출 패턴 테스트
java_files = []
for root, dirs, files in os.walk("project/sampleSrc/src"):
    for file in files:
        if file.endswith('.java'):
            java_files.append(os.path.join(root, file))

print("=== 메서드 추출 패턴 분석 ===")

for java_file in java_files:
    with open(java_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"\n--- {os.path.basename(java_file)} ---")
    
    # 현재 파서 패턴
    current_patterns = [
        r'(?:@\w+(?:\([^)]*\))?\s*)*public\s+(\w+)\s*\(([^)]*)\)\s*\{',
        r'(?:@\w+(?:\([^)]*\))?\s*)*public\s+(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?(\w+(?:<[^>]*>)?)\s+(\w+)\s*\(([^)]*)\)\s*\{[^}]{20,}',
    ]
    
    # 더 포괄적인 패턴
    comprehensive_patterns = [
        r'(?:@\w+(?:\([^)]*\))?\s*)*public\s+(\w+)\s*\(([^)]*)\)\s*\{',
        r'(?:@\w+(?:\([^)]*\))?\s*)*public\s+(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?(\w+(?:<[^>]*>)?)\s+(\w+)\s*\(([^)]*)\)\s*\{[^}]{10,}',
        r'(?:@\w+(?:\([^)]*\))?\s*)*private\s+(?:static\s+)?(?:final\s+)?(\w+(?:<[^>]*>)?)\s+(\w+)\s*\(([^)]*)\)\s*\{[^}]{10,}',
        r'(?:@\w+(?:\([^)]*\))?\s*)*protected\s+(?:static\s+)?(?:final\s+)?(\w+(?:<[^>]*>)?)\s+(\w+)\s*\(([^)]*)\)\s*\{[^}]{10,}',
    ]
    
    current_count = 0
    comprehensive_count = 0
    
    print("현재 패턴으로 추출된 메서드:")
    for i, pattern in enumerate(current_patterns):
        matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
        for match in matches:
            if i == 0:  # 생성자 패턴
                method_name = match.group(1)
                parameters = match.group(2)
            else:  # 메서드 패턴
                method_name = match.group(2)
                parameters = match.group(3)
            current_count += 1
            print(f"  - {method_name}({parameters})")
    
    print(f"현재 패턴 총 개수: {current_count}")
    
    print("\n포괄적 패턴으로 추출된 메서드:")
    for i, pattern in enumerate(comprehensive_patterns):
        matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
        for match in matches:
            if i == 0:  # 생성자 패턴
                method_name = match.group(1)
                parameters = match.group(2)
            else:  # 메서드 패턴
                method_name = match.group(2)
                parameters = match.group(3)
            comprehensive_count += 1
            print(f"  - {method_name}({parameters})")
    
    print(f"포괄적 패턴 총 개수: {comprehensive_count}")
    print(f"차이: {comprehensive_count - current_count}개")


