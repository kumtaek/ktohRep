import sys
import os
sys.path.append('phase1')

from parsers.java.java_parser import JavaParser
import yaml

# 설정 로드
with open('phase1/config/config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# Java 파서 생성
parser = JavaParser(config)
print(f"파서 생성 성공: {type(parser).__name__}")

# UserController.java 파일 읽기
file_path = 'project/sampleSrc/src/main/java/com/example/controller/UserController.java'
with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

print(f"파일 읽기 성공: {len(content)} 문자")

# parse_content 메서드 테스트
context = {'file_path': file_path}
try:
    result = parser.parse_content(content, context)
    print(f"파싱 결과 타입: {type(result)}")
    print(f"파싱 결과 키: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
    
    if isinstance(result, dict):
        print(f"클래스 수: {len(result.get('classes', []))}")
        print(f"메소드 수: {len(result.get('methods', []))}")
        print(f"SQL Units 수: {len(result.get('sql_units', []))}")
        
        # 클래스 상세 정보
        classes = result.get('classes', [])
        for i, cls in enumerate(classes):
            print(f"클래스 {i+1}: {cls}")
            
except Exception as e:
    print(f"파싱 실패: {e}")
    import traceback
    traceback.print_exc()

