import os
import re

# Product.java 파일에서 메서드 추출 디버깅
java_file = "project/sampleSrc/src/main/java/com/example/model/Product.java"
with open(java_file, 'r', encoding='utf-8') as f:
    content = f.read()

print("=== Product.java 메서드 추출 디버깅 ===")

# 현재 파서 패턴
method_patterns = [
    r'(?:@\w+(?:\([^)]*\))?\s*)*public\s+(\w+)\s*\(([^)]*)\)\s*\{[^}]{30,}',
    r'(?:@\w+(?:\([^)]*\))?\s*)*public\s+(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?(\w+(?:<[^>]*>)?)\s+(\w+)\s*\(([^)]*)\)\s*\{[^}]{50,}',
]

all_methods = []
for i, pattern in enumerate(method_patterns):
    print(f"\n패턴 {i+1}: {pattern}")
    matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
    for match in matches:
        if i == 0:  # 생성자 패턴
            method_name = match.group(1)
            parameters = match.group(2)
        else:  # 메서드 패턴
            method_name = match.group(2)
            parameters = match.group(3)
        
        print(f"  추출됨: {method_name}({parameters})")
        
        # getter/setter 체크
        if method_name.startswith('get') or method_name.startswith('set'):
            print(f"    -> getter/setter로 제외되어야 함")
        else:
            print(f"    -> 비즈니스 메서드로 포함")
            all_methods.append(method_name)

print(f"\n최종 포함될 메서드: {len(all_methods)}개")
for method in all_methods:
    print(f"  - {method}")


