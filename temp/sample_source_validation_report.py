#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from typing import List, Dict, Any

def validate_sample_source():
    """샘플 소스 검증 및 문제점 분석"""
    
    print("=== 샘플 소스 검증 리포트 ===")
    
    # 검증할 파일들
    java_files = [
        "./project/sampleSrc/src/main/java/com/example/controller/OrderController.java",
        "./project/sampleSrc/src/main/java/com/example/mapper/UserMapper.java", 
        "./project/sampleSrc/src/main/java/com/example/service/UserService.java"
    ]
    
    xml_files = [
        "./project/sampleSrc/src/main/resources/mybatis/UserMapper.xml"
    ]
    
    jsp_files = [
        "./project/sampleSrc/src/main/webapp/WEB-INF/jsp/user/userList.jsp"
    ]
    
    issues = []
    
    # Java 파일 검증
    print("\n=== Java 파일 검증 ===")
    for file_path in java_files:
        if os.path.exists(file_path):
            issues.extend(validate_java_file(file_path))
    
    # XML 파일 검증
    print("\n=== XML 파일 검증 ===")
    for file_path in xml_files:
        if os.path.exists(file_path):
            issues.extend(validate_xml_file(file_path))
    
    # JSP 파일 검증
    print("\n=== JSP 파일 검증 ===")
    for file_path in jsp_files:
        if os.path.exists(file_path):
            issues.extend(validate_jsp_file(file_path))
    
    # 문제점 요약
    print("\n=== 문제점 요약 ===")
    if issues:
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
    else:
        print("문제점이 발견되지 않았습니다.")
    
    return issues

def validate_java_file(file_path: str) -> List[str]:
    """Java 파일 검증"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"\n파일: {file_path}")
        
        # Import 문 검증
        import_lines = re.findall(r'^import\s+([^;]+);', content, re.MULTILINE)
        print(f"Import 개수: {len(import_lines)}")
        
        # 클래스 선언 검증
        class_declarations = re.findall(r'class\s+(\w+)', content)
        print(f"클래스: {class_declarations}")
        
        # 메소드 선언 검증
        method_declarations = re.findall(r'(?:public|private|protected)\s+(?:static\s+)?(?:[\w<>\[\],\s?&\.]+\s+)?(\w+)\s*\([^)]*\)', content)
        print(f"메소드: {method_declarations}")
        
        # SQL 문자열 검증
        sql_strings = re.findall(r'["\']([^"\']*(?:SELECT|FROM|WHERE|JOIN|UPDATE|INSERT|DELETE|CREATE|ALTER|DROP|TRUNCATE|MERGE)[^"\']*)["\']', content, re.IGNORECASE)
        print(f"SQL 문자열: {len(sql_strings)}개")
        
        # 문제점 검출
        if 'ResponseEntity' in content and 'import org.springframework.http.ResponseEntity' not in content:
            issues.append(f"{file_path}: ResponseEntity import 누락")
        
        if 'Order' in content and 'import.*Order' not in content:
            issues.append(f"{file_path}: Order 클래스 import 누락")
        
        if 'User' in content and 'import.*User' not in content:
            issues.append(f"{file_path}: User 클래스 import 누락")
        
        # SQL Injection 취약점 검출
        if 'String sql = "SELECT * FROM' in content:
            issues.append(f"{file_path}: SQL Injection 취약점 발견")
        
    except Exception as e:
        issues.append(f"{file_path}: 파일 읽기 오류 - {e}")
    
    return issues

def validate_xml_file(file_path: str) -> List[str]:
    """XML 파일 검증"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"\n파일: {file_path}")
        
        # XML 선언 검증
        if not content.strip().startswith('<?xml'):
            issues.append(f"{file_path}: XML 선언 누락")
        
        # DOCTYPE 검증
        if '<!DOCTYPE' not in content:
            issues.append(f"{file_path}: DOCTYPE 선언 누락")
        
        # SQL 쿼리 검증
        select_queries = re.findall(r'<select[^>]*>.*?</select>', content, re.DOTALL | re.IGNORECASE)
        print(f"SELECT 쿼리: {len(select_queries)}개")
        
        insert_queries = re.findall(r'<insert[^>]*>.*?</insert>', content, re.DOTALL | re.IGNORECASE)
        print(f"INSERT 쿼리: {len(insert_queries)}개")
        
        update_queries = re.findall(r'<update[^>]*>.*?</update>', content, re.DOTALL | re.IGNORECASE)
        print(f"UPDATE 쿼리: {len(update_queries)}개")
        
        delete_queries = re.findall(r'<delete[^>]*>.*?</delete>', content, re.DOTALL | re.IGNORECASE)
        print(f"DELETE 쿼리: {len(delete_queries)}개")
        
    except Exception as e:
        issues.append(f"{file_path}: 파일 읽기 오류 - {e}")
    
    return issues

def validate_jsp_file(file_path: str) -> List[str]:
    """JSP 파일 검증"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"\n파일: {file_path}")
        
        # JSP 지시어 검증
        page_directives = re.findall(r'<%@\s+page[^%]*%>', content, re.IGNORECASE)
        print(f"Page 지시어: {len(page_directives)}개")
        
        # 태그라이브러리 검증
        taglib_directives = re.findall(r'<%@\s+taglib[^%]*%>', content, re.IGNORECASE)
        print(f"Taglib 지시어: {len(taglib_directives)}개")
        
        # 스크립틀릿 검증
        scriptlets = re.findall(r'<%[^%]*%>', content)
        print(f"스크립틀릿: {len(scriptlets)}개")
        
        # JSTL 태그 검증
        jstl_tags = re.findall(r'<c:[^>]*>', content)
        print(f"JSTL 태그: {len(jstl_tags)}개")
        
        # SQL Injection 취약점 검출
        if 'String dynamicSql = "SELECT * FROM' in content:
            issues.append(f"{file_path}: SQL Injection 취약점 발견")
        
    except Exception as e:
        issues.append(f"{file_path}: 파일 읽기 오류 - {e}")
    
    return issues

if __name__ == "__main__":
    validate_sample_source()




