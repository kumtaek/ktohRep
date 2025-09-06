import os
import re

# Java 파일에서 getter/setter 제외 로직 테스트
java_files = []
for root, dirs, files in os.walk("project/sampleSrc/src"):
    for file in files:
        if file.endswith('.java'):
            java_files.append(os.path.join(root, file))

print("=== Getter/Setter 제외 로직 테스트 ===")

for java_file in java_files:
    with open(java_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"\n--- {os.path.basename(java_file)} ---")
    
    # 메서드 패턴
    method_patterns = [
        r'(?:@\w+(?:\([^)]*\))?\s*)*public\s+(\w+)\s*\(([^)]*)\)\s*\{',
        r'(?:@\w+(?:\([^)]*\))?\s*)*public\s+(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?(\w+(?:<[^>]*>)?)\s+(\w+)\s*\(([^)]*)\)\s*\{[^}]{30,}',
    ]
    
    all_methods = []
    for i, pattern in enumerate(method_patterns):
        matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
        for match in matches:
            if i == 0:  # 생성자 패턴
                method_name = match.group(1)
                parameters = match.group(2)
                return_type = None
            else:  # 메서드 패턴
                return_type = match.group(1)
                method_name = match.group(2)
                parameters = match.group(3)
            
            # 매개변수 파싱
            param_list = []
            if parameters and parameters.strip():
                param_parts = [p.strip() for p in parameters.split(',')]
                for param in param_parts:
                    if param:
                        param_list.append(param)
            
            all_methods.append({
                'name': method_name,
                'return_type': return_type,
                'parameters': param_list,
                'param_count': len(param_list)
            })
    
    print(f"추출된 메서드 수: {len(all_methods)}개")
    
    # Getter/Setter 제외 로직 테스트
    excluded_count = 0
    included_count = 0
    
    for method in all_methods:
        method_name = method['name']
        param_count = method['param_count']
        
        # 현재 제외 로직
        if (method_name.startswith('get') and param_count == 0) or \
           (method_name.startswith('set') and param_count == 1):
            excluded_count += 1
            print(f"  제외됨: {method_name}({param_count}개 매개변수)")
        else:
            included_count += 1
            print(f"  포함됨: {method_name}({param_count}개 매개변수)")
    
    print(f"제외된 메서드: {excluded_count}개")
    print(f"포함된 메서드: {included_count}개")


