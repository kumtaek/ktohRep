#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from parsers.optimized_java_parser import OptimizedJavaParser
from core.optimized_metadata_engine import OptimizedMetadataEngine

def test_relationship_generation():
    """관계 생성 테스트"""
    print("=== 관계 생성 디버그 테스트 ===")
    
    # 메타데이터 엔진 초기화
    engine = OptimizedMetadataEngine()
    parser = OptimizedJavaParser(engine)
    
    # 간단한 테스트 코드
    test_content = '''
package com.example;
import com.example.model.User;
import com.example.service.UserService;

@Service
public class UserController {
    @Autowired
    private UserService userService;
    
    public User getUserById(Long id) {
        return userService.getUserById(id);
    }
}
'''
    
    print("1. 파일 파싱 테스트...")
    result = parser.parse_file('test.java', test_content)
    print(f"Parse result: {result}")
    
    if result.get('success'):
        print("2. 구조 정보 확인...")
        structure_info = result.get('structure_info', {})
        print(f"Classes: {structure_info.get('classes', [])}")
        print(f"Imports: {structure_info.get('imports', [])}")
        
        print("3. 컴포넌트 ID 확인...")
        component_ids = result.get('component_ids', {})
        print(f"Component IDs: {component_ids}")
        
        print("4. 관계 생성 테스트...")
        project_id = 1
        parser._add_basic_relationships(project_id, structure_info, component_ids)
        
        print("5. 관계 확인...")
        import sqlite3
        with sqlite3.connect(engine.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM relationships")
            count = cursor.fetchone()[0]
            print(f"Relationships count: {count}")
            
            if count > 0:
                cursor.execute("SELECT * FROM relationships LIMIT 5")
                relationships = cursor.fetchall()
                print(f"Sample relationships: {relationships}")

if __name__ == "__main__":
    test_relationship_generation()
