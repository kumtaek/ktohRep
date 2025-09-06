import sys
from pathlib import Path

# Add phase1 to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from parsers.java.java_parser import JavaParser
import inspect

# JavaParser 인스턴스 생성
parser = JavaParser({})

print("=== JavaParser 메서드 확인 ===")

# 모든 메서드 확인
methods = [method for method in dir(parser) if not method.startswith('_')]
print(f"사용 가능한 메서드들: {methods}")

# parse 관련 메서드 확인
parse_methods = [method for method in methods if 'parse' in method.lower()]
print(f"parse 관련 메서드들: {parse_methods}")

# 각 메서드의 시그니처 확인
for method_name in parse_methods:
    method = getattr(parser, method_name)
    if callable(method):
        sig = inspect.signature(method)
        is_async = inspect.iscoroutinefunction(method)
        print(f"  {method_name}: {sig} {'(async)' if is_async else '(sync)'}")

# BaseParser에서 상속받은 메서드 확인
from parsers.common.base_parser import BaseParser
base_methods = [method for method in dir(BaseParser) if not method.startswith('_')]
print(f"\nBaseParser 메서드들: {base_methods}")

# BaseParser의 parse_file 메서드 확인
if hasattr(BaseParser, 'parse_file'):
    base_parse_file = getattr(BaseParser, 'parse_file')
    sig = inspect.signature(base_parse_file)
    is_async = inspect.iscoroutinefunction(base_parse_file)
    print(f"BaseParser.parse_file: {sig} {'(async)' if is_async else '(sync)'}")
else:
    print("BaseParser에 parse_file 메서드가 없습니다")




