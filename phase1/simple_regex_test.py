import re

# 테스트할 SQL
sql = "LEFT JOIN categories c ON p.category_id = c.id"

# JOIN 패턴
pattern = r'LEFT\s+JOIN\s+(\w+)\s+(\w+)\s+ON\s+(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)'

print(f"테스트 SQL: {sql}")
print(f"패턴: {pattern}")

# 매치 테스트
matches = list(re.finditer(pattern, sql, re.IGNORECASE))
print(f"매치 수: {len(matches)}")

for i, match in enumerate(matches):
    groups = match.groups()
    print(f"매치 {i+1}: 그룹 수 {len(groups)}, 내용 {groups}")
