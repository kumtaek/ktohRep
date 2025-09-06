import sys
import asyncio
from pathlib import Path

# Add phase1 to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from phase1.parsers.java.java_parser import JavaParser

# JavaParser 인스턴스 생성
parser = JavaParser({})

print("=== JavaParser parse 메서드 테스트 ===")

# 간단한 Java 코드로 테스트
test_content = """
package com.example.service;

@Service
public class TestService {
    public void testMethod() {
        System.out.println("test");
    }
}
"""

async def test_parse():
    try:
        result = await parser.parse(test_content, "TestService.java")
        print(f"✅ parse 성공: {type(result)}")
        print(f"결과: {result}")
    except Exception as e:
        print(f"❌ parse 실패: {e}")
        import traceback
        traceback.print_exc()

# 비동기 함수 실행
asyncio.run(test_parse())




