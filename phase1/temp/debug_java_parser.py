import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from phase1.parsers.java.java_parser import JavaParser

# Java 파서 테스트
parser = JavaParser()

# 샘플 Java 파일 읽기
sample_file = "project/sampleSrc/src/main/java/com/example/controller/ProductController.java"
with open(sample_file, 'r', encoding='utf-8') as f:
    content = f.read()

# 파싱 실행
context = {'file_path': sample_file}
result = parser.parse_content(content, context)

print("=== Java 파서 결과 ===")
print(f"클래스 수: {len(result['classes'])}")
print(f"메서드 수: {len(result['methods'])}")

print("\n=== 클래스 목록 ===")
for i, cls in enumerate(result['classes']):
    print(f"{i+1}. {cls.get('name', 'Unknown')} - FQN: {cls.get('fqn', 'Unknown')}")

print("\n=== 메서드 목록 ===")
for i, method in enumerate(result['methods']):
    print(f"{i+1}. {method.get('name', 'Unknown')} - Owner: {method.get('owner_fqn', 'None')}")
