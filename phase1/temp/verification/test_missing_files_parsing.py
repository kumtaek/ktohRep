import sys
import os
from pathlib import Path

# Add phase1 to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from phase1.parsers.java_parser import JavaParser

# 누락된 파일들 테스트
missing_files = [
    '../project/sampleSrc/src/main/java/com/example/integrated/VulnerabilityTestService.java',
    '../project/sampleSrc/src/main/java/com/example/service/OrderService.java',
    '../project/sampleSrc/src/main/java/com/example/service/UserService.java', 
    '../project/sampleSrc/src/main/java/com/example/service/ProductService.java'
]

parser = JavaParser({})

for file_path in missing_files:
    if os.path.exists(file_path):
        print(f'\n=== {file_path.split("/")[-1]} 파싱 테스트 ===')
        try:
            # 파일 내용 확인
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f'  파일 크기: {len(content)} bytes')
            print(f'  첫 100자: {content[:100]}...')
            
            # 파싱 시도
            result = parser.parse_file(file_path, 1)  # project_id = 1
            
            if isinstance(result, tuple) and len(result) == 4:
                file_obj, classes, methods, edges = result
                print(f'  ✅ 파싱 성공')
                print(f'    클래스 수: {len(classes)}')
                print(f'    메소드 수: {len(methods)}')
                print(f'    엣지 수: {len(edges)}')
                
                if classes:
                    for cls in classes:
                        print(f'      클래스: {cls.name} (FQN: {getattr(cls, "fqn", "N/A")})')
                
                if methods:
                    for method in methods[:3]:  # 처음 3개만
                        print(f'      메소드: {method.name}')
            else:
                print(f'  ❌ 예상과 다른 결과 형식: {type(result)}')
                print(f'  결과: {result}')
                    
        except Exception as e:
            print(f'  ❌ 파싱 실패: {e}')
            import traceback
            traceback.print_exc()
    else:
        print(f'❌ 파일 없음: {file_path}')

