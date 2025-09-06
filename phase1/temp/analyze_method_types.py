import sqlite3

conn = sqlite3.connect('project/sampleSrc/metadata.db')
cursor = conn.cursor()

# 메서드 타입별 상세 분석
cursor.execute('SELECT name, parameters FROM methods')
methods = cursor.fetchall()

getter_count = 0
setter_count = 0
constructor_count = 0
business_count = 0

print("=== 메서드 타입별 분석 ===")
for method in methods:
    name = method[0]
    params = method[1]
    
    if name.startswith('get') and params == '':
        getter_count += 1
    elif name.startswith('set') and params != '':
        setter_count += 1
    elif name in ['Product', 'User']:
        constructor_count += 1
    else:
        business_count += 1

print(f"Getter 메서드: {getter_count}개")
print(f"Setter 메서드: {setter_count}개")
print(f"생성자: {constructor_count}개")
print(f"비즈니스 메서드: {business_count}개")
print(f"총 메서드: {len(methods)}개")

# 예상 40개에 맞추려면 어떤 메서드들을 제외해야 하는지 분석
print(f"\n=== 40개 목표 달성을 위한 제외 대상 ===")
print(f"Getter 제외 시: {len(methods) - getter_count}개")
print(f"Setter 제외 시: {len(methods) - setter_count}개")
print(f"Getter+Setter 제외 시: {len(methods) - getter_count - setter_count}개")

conn.close()


