import sqlite3

# 메타디비에서 추출된 메서드 상세 분석
conn = sqlite3.connect('project/sampleSrc/metadata.db')
cursor = conn.cursor()

# 메서드별 상세 정보 조회
cursor.execute("""
    SELECT m.name, m.parameters, m.modifiers, f.path, c.name as class_name
    FROM methods m 
    JOIN classes c ON m.class_id = c.class_id
    JOIN files f ON c.file_id = f.file_id 
    WHERE f.path LIKE '%.java'
    ORDER BY f.path, c.name, m.name
""")
methods = cursor.fetchall()

print("=== 추출된 메서드 상세 분석 ===")
print(f"총 메서드 수: {len(methods)}개")

# 파일별 메서드 수 분석
file_methods = {}
for method in methods:
    file_path = method[3]
    if file_path not in file_methods:
        file_methods[file_path] = []
    file_methods[file_path].append(method)

print("\n=== 파일별 메서드 수 ===")
for file_path, methods_in_file in file_methods.items():
    print(f"{file_path}: {len(methods_in_file)}개")
    # 각 파일의 메서드 목록 출력 (처음 10개만)
    for i, method in enumerate(methods_in_file[:10]):
        print(f"  - {method[4]}.{method[0]}({method[1]}) - {method[2]}")
    if len(methods_in_file) > 10:
        print(f"  ... 외 {len(methods_in_file) - 10}개")

# 메서드 타입별 분석
print("\n=== 메서드 타입별 분석 ===")
getter_count = 0
setter_count = 0
constructor_count = 0
other_count = 0

for method in methods:
    method_name = method[0]
    if method_name.startswith('get'):
        getter_count += 1
    elif method_name.startswith('set'):
        setter_count += 1
    elif method_name in ['Product', 'User']:  # 생성자
        constructor_count += 1
    else:
        other_count += 1

print(f"Getter 메서드: {getter_count}개")
print(f"Setter 메서드: {setter_count}개") 
print(f"생성자: {constructor_count}개")
print(f"기타 메서드: {other_count}개")

conn.close()


