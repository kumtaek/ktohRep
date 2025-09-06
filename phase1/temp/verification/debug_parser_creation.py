import sys
from pathlib import Path

# Add phase1 to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from parsers.parser_factory import ParserFactory

# 파서 팩토리 생성
config = {}
factory = ParserFactory(config)

print("=== 파서 생성 디버깅 ===")

# Java 파서 생성
java_parser = factory.get_parser('java', 'source')
print(f"Java 파서 타입: {type(java_parser)}")
print(f"Java 파서: {java_parser}")

if java_parser:
    print(f"parse_file 메서드 존재: {hasattr(java_parser, 'parse_file')}")
    if hasattr(java_parser, 'parse_file'):
        import inspect
        sig = inspect.signature(java_parser.parse_file)
        print(f"parse_file 시그니처: {sig}")
        
        # parse_file이 async인지 확인
        if inspect.iscoroutinefunction(java_parser.parse_file):
            print("✅ parse_file은 async 함수입니다")
        else:
            print("❌ parse_file은 동기 함수입니다")

# 파서 팩토리의 _parsers 확인
print(f"\n등록된 파서들: {factory._parsers}")
print(f"Java 파서 클래스: {factory._parsers.get('java', {}).get('source')}")




