#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from parsers.optimized_java_parser import OptimizedJavaParser
from core.optimized_metadata_engine import OptimizedMetadataEngine
import sqlite3

def test_step_by_step():
    """단계별 관계 생성 테스트"""
    print("=== 단계별 관계 생성 테스트 ===")
    
    # 1. 메타데이터 엔진 초기화
    print("1. 메타데이터 엔진 초기화...")
    engine = OptimizedMetadataEngine()
    parser = OptimizedJavaParser(engine)
    
    # 2. 간단한 테스트 코드
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
    
    # 3. 파일 파싱
    print("2. 파일 파싱...")
    result = parser.parse_file('test.java', test_content)
    print(f"Parse success: {result.get('success')}")
    
    if not result.get('success'):
        print(f"Parse error: {result.get('error')}")
        return
    
    # 4. 구조 정보 확인
    print("3. 구조 정보 확인...")
    structure_info = result.get('structure_info', {})
    classes = structure_info.get('classes', [])
    print(f"Classes found: {len(classes)}")
    
    for cls in classes:
        print(f"  - {cls['name']}: extends={cls.get('extends')}, implements={cls.get('implements')}")
        print(f"    imports={cls.get('imports', [])}")
        print(f"    annotations={cls.get('annotations', [])}")
    
    # 5. 컴포넌트 ID 확인
    print("4. 컴포넌트 ID 확인...")
    component_ids = result.get('component_ids', {})
    print(f"Component IDs: {list(component_ids.keys())}")
    
    # 6. 수동으로 관계 생성 테스트
    print("5. 수동 관계 생성 테스트...")
    project_id = 1
    
    # extends 관계 테스트
    for cls in classes:
        if cls.get('extends'):
            src_id = component_ids.get(cls['name'])
            dst_id = component_ids.get(cls['extends'])
            print(f"  extends test: {cls['name']} -> {cls['extends']}")
            print(f"    src_id: {src_id}, dst_id: {dst_id}")
            
            if src_id and dst_id:
                try:
                    engine.add_relationship(project_id, src_id, dst_id, 'extends', 0.9)
                    print(f"    extends relationship added successfully")
                except Exception as e:
                    print(f"    extends relationship error: {e}")
    
    # 7. 관계 확인
    print("6. 관계 확인...")
    with sqlite3.connect(engine.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM relationships")
        count = cursor.fetchone()[0]
        print(f"Total relationships: {count}")
        
        if count > 0:
            cursor.execute("SELECT * FROM relationships")
            relationships = cursor.fetchall()
            for rel in relationships:
                print(f"  Relationship: {rel}")

if __name__ == "__main__":
    test_step_by_step()
