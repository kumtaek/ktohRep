import re

# 테스트할 getter/setter
content = 'public String getProductId() { return productId; }'
print(f"테스트 내용: {content}")

# 현재 패턴 (50자 이상)
pattern = r'public\s+(\w+(?:<[^>]*>)?)\s+(\w+)\s*\(([^)]*)\)\s*\{[^}]{50,}'
match = re.search(pattern, content)
print(f"50자 이상 패턴 매치: {match is not None}")

# 본문 길이 계산
body_start = content.find('{')
body_end = content.find('}')
if body_start != -1 and body_end != -1:
    body = content[body_start+1:body_end]
    print(f"본문: '{body}'")
    print(f"본문 길이: {len(body)}자")

# 20자 이상 패턴으로 테스트
pattern20 = r'public\s+(\w+(?:<[^>]*>)?)\s+(\w+)\s*\(([^)]*)\)\s*\{[^}]{20,}'
match20 = re.search(pattern20, content)
print(f"20자 이상 패턴 매치: {match20 is not None}")


