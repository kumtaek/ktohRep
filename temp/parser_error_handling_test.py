#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import yaml
sys.path.append('.')

from parsers.java.java_parser import JavaParser
from parsers.mybatis.mybatis_parser import MyBatisParser
from parsers.jsp.jsp_parser import JSPParser

def test_parser_error_handling():
    """파서의 오류 처리 방식 테스트"""
    
    print("=== 파서 오류 처리 분석 ===")
    
    # Config 로드
    config_path = "config/config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 1. Java 파서 오류 처리 테스트
    print("\n=== Java 파서 오류 처리 테스트 ===")
    test_java_parser_error_handling(config)
    
    # 2. MyBatis 파서 오류 처리 테스트
    print("\n=== MyBatis 파서 오류 처리 테스트 ===")
    test_mybatis_parser_error_handling(config)
    
    # 3. JSP 파서 오류 처리 테스트
    print("\n=== JSP 파서 오류 처리 테스트 ===")
    test_jsp_parser_error_handling(config)

def test_java_parser_error_handling(config):
    """Java 파서의 오류 처리 테스트"""
    
    java_parser = JavaParser(config)
    
    # 오류가 있는 Java 코드 샘플들
    error_samples = [
        {
            'name': 'Import 누락',
            'code': '''
package com.example;
// import 누락
public class TestController {
    public ResponseEntity<String> test() {
        return ResponseEntity.ok("test");
    }
}
'''
        },
        {
            'name': 'SQL Injection 패턴',
            'code': '''
package com.example;
public class TestService {
    public void vulnerableMethod(String userInput) {
        String sql = "SELECT * FROM users WHERE name = '" + userInput + "'";
        // SQL Injection 취약점
    }
}
'''
        },
        {
            'name': '문법 오류',
            'code': '''
package com.example;
public class TestClass {
    public void testMethod() {
        // 문법 오류: 세미콜론 누락
        String test = "hello"
        return test;
    }
}
'''
        },
        {
            'name': '정상 코드',
            'code': '''
package com.example;
import org.springframework.http.ResponseEntity;
public class TestController {
    public ResponseEntity<String> test() {
        return ResponseEntity.ok("test");
    }
}
'''
        }
    ]
    
    for sample in error_samples:
        print(f"\n--- {sample['name']} ---")
        try:
            result = java_parser.parse_content(sample['code'], "test.java")
            print(f"파싱 성공: {type(result)}")
            print(f"메소드 개수: {len(result.get('methods', []))}")
            print(f"클래스 개수: {len(result.get('classes', []))}")
            print(f"SQL 유닛 개수: {len(result.get('sql_units', []))}")
            print(f"어노테이션 개수: {len(result.get('annotations', []))}")
            
            # SQL Injection 패턴 감지
            if 'sql_units' in result and result['sql_units']:
                for sql_unit in result['sql_units']:
                    if 'sql_content' in sql_unit:
                        sql_content = sql_unit['sql_content']
                        if "'" in sql_content and '+' in sql_content:
                            print(f"⚠️  SQL Injection 패턴 감지: {sql_content[:50]}...")
                            
        except Exception as e:
            print(f"파싱 실패: {e}")

def test_mybatis_parser_error_handling(config):
    """MyBatis 파서의 오류 처리 테스트"""
    
    mybatis_parser = MyBatisParser(config)
    
    # 오류가 있는 XML 코드 샘플들
    error_samples = [
        {
            'name': 'XML 문법 오류',
            'code': '''
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.example.mapper.UserMapper">
    <select id="selectUser" resultType="User">
        SELECT * FROM users WHERE id = #{id}
    <!-- 닫는 태그 누락 -->
</mapper>
'''
        },
        {
            'name': 'SQL Injection 패턴',
            'code': '''
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.example.mapper.UserMapper">
    <select id="vulnerableSelect" resultType="User">
        SELECT * FROM users WHERE name = '${name}'
    </select>
</mapper>
'''
        },
        {
            'name': '정상 XML',
            'code': '''
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" "http://mybatis.org/dtd/mybatis-3-mapper.dtd">
<mapper namespace="com.example.mapper.UserMapper">
    <select id="selectUser" resultType="User">
        SELECT * FROM users WHERE id = #{id}
    </select>
</mapper>
'''
        }
    ]
    
    for sample in error_samples:
        print(f"\n--- {sample['name']} ---")
        try:
            result = mybatis_parser.parse_content(sample['code'], "test.xml")
            print(f"파싱 성공: {type(result)}")
            print(f"SQL 쿼리 개수: {len(result.get('sql_queries', []))}")
            print(f"매퍼 개수: {len(result.get('mappers', []))}")
            
            # SQL Injection 패턴 감지
            if 'sql_queries' in result and result['sql_queries']:
                for query in result['sql_queries']:
                    if 'sql_content' in query:
                        sql_content = query['sql_content']
                        if '${' in sql_content:
                            print(f"⚠️  SQL Injection 패턴 감지: ${sql_content[:50]}...")
                            
        except Exception as e:
            print(f"파싱 실패: {e}")

def test_jsp_parser_error_handling(config):
    """JSP 파서의 오류 처리 테스트"""
    
    jsp_parser = JSPParser(config)
    
    # 오류가 있는 JSP 코드 샘플들
    error_samples = [
        {
            'name': 'SQL Injection 패턴',
            'code': '''
<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%
    String userInput = request.getParameter("name");
    String sql = "SELECT * FROM users WHERE name = '" + userInput + "'";
%>
<html>
<body>
    <h1>Vulnerable JSP</h1>
</body>
</html>
'''
        },
        {
            'name': '문법 오류',
            'code': '''
<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%
    String test = "hello"
    // 세미콜론 누락
%>
<html>
<body>
    <h1>Error JSP</h1>
</body>
</html>
'''
        },
        {
            'name': '정상 JSP',
            'code': '''
<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<%@ taglib prefix="c" uri="http://java.sun.com/jsp/jstl/core" %>
<html>
<body>
    <h1>Hello World</h1>
    <c:forEach var="item" items="${list}">
        <p>${item}</p>
    </c:forEach>
</body>
</html>
'''
        }
    ]
    
    for sample in error_samples:
        print(f"\n--- {sample['name']} ---")
        try:
            result = jsp_parser.parse_content(sample['code'], "test.jsp")
            print(f"파싱 성공: {type(result)}")
            print(f"스크립틀릿 개수: {len(result.get('scriptlets', []))}")
            print(f"JSTL 태그 개수: {len(result.get('jstl_tags', []))}")
            print(f"SQL 문자열 개수: {len(result.get('sql_strings', []))}")
            
            # SQL Injection 패턴 감지
            if 'sql_strings' in result and result['sql_strings']:
                for sql_string in result['sql_strings']:
                    if 'content' in sql_string:
                        sql_content = sql_string['content']
                        if "'" in sql_content and '+' in sql_content:
                            print(f"⚠️  SQL Injection 패턴 감지: {sql_content[:50]}...")
                            
        except Exception as e:
            print(f"파싱 실패: {e}")

if __name__ == "__main__":
    test_parser_error_handling()




