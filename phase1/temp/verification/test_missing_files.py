import sys
import os
from pathlib import Path

# Add phase1 to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from parsers.java_parser import JavaParser

# 누락된 파일들 테스트
missing_files = [
    '../project/sampleSrc/src/main/java/com/example/service/OrderService.java',
    '../project/sampleSrc/src/main/java/com/example/service/UserService.java', 
    '../project/sampleSrc/src/main/java/com/example/service/ProductService.java',
    '../project/sampleSrc/src/main/java/com/example/service/VulnerabilityTestService.java'
]

parser = JavaParser({})

for file_path in missing_files:
    if os.path.exists(file_path):
        print(f'\n=== {file_path.split("/")[-1]} 테스트 ===')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import asyncio
            classes, methods, edges = asyncio.run(parser.parse_file(file_path, content))
            
            print(f'  클래스 수: {len(classes)}')
            print(f'  메소드 수: {len(methods)}')
            print(f'  엣지 수: {len(edges)}')
            
            if classes:
                for cls in classes:
                    print(f'    클래스: {cls.name}')
            
            if methods:
                for method in methods[:3]:  # 처음 3개만
                    print(f'    메소드: {method.name}')
                    
        except Exception as e:
            print(f'  ❌ 파싱 실패: {e}')
    else:
        print(f'❌ 파일 없음: {file_path}')
