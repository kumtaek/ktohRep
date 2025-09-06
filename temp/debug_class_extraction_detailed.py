import sys
import os
sys.path.append('phase1')

from parsers.java.java_parser import JavaParser
import yaml
import re

# 설정 로드
with open('phase1/config/config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# Java 파서 생성
parser = JavaParser(config)

# UserController.java 파일 읽기
file_path = 'project/sampleSrc/src/main/java/com/example/controller/UserController.java'
with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

print("=== Java 파서 클래스 추출 디버깅 ===")
print(f"파일: {file_path}")
print(f"내용 길이: {len(content)} 문자")
print()

# 1. 파서의 fallback 패턴 확인
print("1. Fallback 패턴 확인:")
fallback_pattern = parser.fallback_patterns['class_declaration']
print(f"패턴: {fallback_pattern.pattern}")
print()

# 2. 실제 파일 내용에서 클래스 선언 부분 찾기
print("2. 파일 내용에서 클래스 선언 부분:")
lines = content.split('\n')
for i, line in enumerate(lines, 1):
    if 'class' in line and ('public' in line or '@' in line):
        print(f"라인 {i}: {line.strip()}")
print()

# 3. 정규화된 내용으로 테스트
print("3. 정규화된 내용으로 테스트:")
normalized_content = parser._normalize_content(content)
print(f"정규화 후 길이: {len(normalized_content)} 문자")

# 정규화된 내용에서 클래스 선언 찾기
matches = fallback_pattern.finditer(normalized_content)
match_count = 0
for match in matches:
    match_count += 1
    print(f"매치 {match_count}: {match.group(0)}")
    print(f"  클래스명: {match.group(1)}")
    print(f"  extends: {match.group(2) if match.group(2) else 'None'}")
    print(f"  implements: {match.group(3) if match.group(3) else 'None'}")
    print()

if match_count == 0:
    print("❌ 정규화된 내용에서도 클래스를 찾을 수 없습니다.")
    print()
    print("4. 정규화 과정 확인:")
    print("원본 내용 (클래스 선언 부분):")
    for i, line in enumerate(lines, 1):
        if 'class' in line:
            print(f"라인 {i}: {repr(line)}")
    print()
    print("정규화된 내용 (클래스 선언 부분):")
    normalized_lines = normalized_content.split('\n')
    for i, line in enumerate(normalized_lines, 1):
        if 'class' in line:
            print(f"라인 {i}: {repr(line)}")
else:
    print(f"✅ 정규화된 내용에서 {match_count}개 클래스 발견")

# 5. _extract_classes 메서드 직접 테스트
print("\n5. _extract_classes 메서드 직접 테스트:")
try:
    classes = parser._extract_classes(normalized_content)
    print(f"추출된 클래스 수: {len(classes)}")
    for i, cls in enumerate(classes):
        print(f"클래스 {i+1}: {cls}")
except Exception as e:
    print(f"❌ _extract_classes 실행 실패: {e}")
    import traceback
    traceback.print_exc()

