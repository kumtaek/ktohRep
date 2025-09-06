#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
파서 통합 테스트 스크립트
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 패스에 추가
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

def test_java_parser():
    """Java 파서 테스트"""
    try:
        from parsers.java_parser import JavaParser
        
        # 간단한 설정
        config = {
            'java': {
                'enabled': True,
                'parser_type': 'javalang',
                'java_version': 8
            }
        }
        
        parser = JavaParser(config)
        print("✓ JavaParser 생성 성공")
        
        # 간단한 Java 코드로 테스트
        test_code = """
        public class TestClass {
            public void testMethod() {
                System.out.println("Hello World");
            }
        }
        """
        
        # parse 메서드 테스트
        result = parser._parse_java_content(test_code, "TestClass.java")
        print(f"✓ Java 파싱 성공: {len(result[0])} 클래스, {len(result[1])} 메서드")
        
        return True
        
    except Exception as e:
        print(f"✗ Java 파서 테스트 실패: {e}")
        return False

def test_jsp_parser():
    """JSP 파서 테스트"""
    try:
        from parsers.jsp_mybatis_parser import JspMybatisParser
        
        # 간단한 설정
        config = {
            'jsp': {
                'enabled': True,
                'parser_type': 'antlr'
            }
        }
        
        parser = JspMybatisParser(config)
        print("✓ JspMybatisParser 생성 성공")
        
        # 간단한 JSP 코드로 테스트
        test_code = """
        <%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
        <html>
        <body>
            <h1>Hello JSP</h1>
        </body>
        </html>
        """
        
        # parse 메서드 테스트
        result = parser._parse_jsp_content(test_code, "test.jsp")
        print(f"✓ JSP 파싱 성공: {len(result[0])} SQL 유닛")
        
        return True
        
    except Exception as e:
        print(f"✗ JSP 파서 테스트 실패: {e}")
        return False

def test_sql_parser():
    """SQL 파서 테스트"""
    try:
        from parsers.sql_parser import SqlParser
        
        # 간단한 설정
        config = {
            'sql': {
                'enabled': True,
                'parser_type': 'jsqlparser',
                'oracle_dialect': True
            }
        }
        
        parser = SqlParser(config)
        print("✓ SqlParser 생성 성공")
        
        # 간단한 SQL 코드로 테스트
        test_code = "SELECT * FROM users WHERE id = 1"
        
        # parse 메서드 테스트
        result = parser._parse_sql_content(test_code, "test.sql")
        print(f"✓ SQL 파싱 성공: {len(result[2])} 테이블, {len(result[3])} 컬럼")
        
        return True
        
    except Exception as e:
        print(f"✗ SQL 파서 테스트 실패: {e}")
        return False

def test_parser_factory():
    """파서 팩토리 테스트"""
    try:
        from parsers.parser_factory import ParserFactory
        
        # 간단한 설정
        config = {
            'oracle': {'enabled': True},
            'spring': {'enabled': True},
            'jpa': {'enabled': True},
            'mybatis': {'enabled': True}
        }
        
        factory = ParserFactory(config)
        print("✓ ParserFactory 생성 성공")
        
        # 사용 가능한 파서 확인
        available = factory.get_available_parsers()
        print(f"✓ 사용 가능한 파서: {list(available.keys())}")
        
        return True
        
    except Exception as e:
        print(f"✗ 파서 팩토리 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("=" * 50)
    print("파서 통합 테스트 시작")
    print("=" * 50)
    
    tests = [
        ("Java 파서", test_java_parser),
        ("JSP 파서", test_jsp_parser),
        ("SQL 파서", test_sql_parser),
        ("파서 팩토리", test_parser_factory)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name} 테스트 중...")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("테스트 결과 요약")
    print("=" * 50)
    
    success_count = 0
    for test_name, result in results:
        status = "✓ 성공" if result else "✗ 실패"
        print(f"{test_name}: {status}")
        if result:
            success_count += 1
    
    print(f"\n전체 테스트: {len(results)}개")
    print(f"성공: {success_count}개")
    print(f"실패: {len(results) - success_count}개")
    
    if success_count == len(results):
        print("\n🎉 모든 파서가 정상적으로 작동합니다!")
    else:
        print("\n⚠️  일부 파서에 문제가 있습니다.")

if __name__ == "__main__":
    main()
