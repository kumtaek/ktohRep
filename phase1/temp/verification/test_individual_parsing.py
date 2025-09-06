import sys
import os
import asyncio
from pathlib import Path

# Add phase1 to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from phase1.parsers.java_parser import JavaParser

# 누락된 파일들 테스트
missing_files = [
    '../project/sampleSrc/src/main/java/com/example/service/OrderService.java',
    '../project/sampleSrc/src/main/java/com/example/service/UserService.java', 
    '../project/sampleSrc/src/main/java/com/example/service/ProductService.java'
]

parser = JavaParser({})

async def test_file_parsing():
    for file_path in missing_files:
        if os.path.exists(file_path):
            print(f'\n=== {file_path.split("/")[-1]} 테스트 ===')
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                result = await parser.parse_file(file_path, content)
                
                # 결과가 3개 튜플인지 확인
                if isinstance(result, tuple) and len(result) == 3:
                    classes, methods, edges = result
                    print(f'  클래스 수: {len(classes)}')
                    print(f'  메소드 수: {len(methods)}')
                    print(f'  엣지 수: {len(edges)}')
                    
                    if classes:
                        for cls in classes:
                            print(f'    클래스: {cls.name}')
                    
                    if methods:
                        for method in methods[:3]:  # 처음 3개만
                            print(f'    메소드: {method.name}')
                else:
                    print(f'  ❌ 예상과 다른 결과 형식: {type(result)}')
                    print(f'  결과: {result}')
                    
            except Exception as e:
                print(f'  ❌ 파싱 실패: {e}')
                import traceback
                traceback.print_exc()
        else:
            print(f'❌ 파일 없음: {file_path}')

# 비동기 함수 실행
asyncio.run(test_file_parsing())

