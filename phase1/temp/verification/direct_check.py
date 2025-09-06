#!/usr/bin/env python3
import sqlite3
import os

def check_current_state():
    db_path = '../project/sampleSrc/metadata.db'
    
    print("🔍 현재 메타디비 상태 확인")
    print("=" * 50)
    
    if not os.path.exists(db_path):
        print("❌ 메타디비가 존재하지 않습니다.")
        return
    
    size = os.path.getsize(db_path)
    print(f"📁 메타디비 크기: {size} bytes")
    
    if size == 0:
        print("❌ 메타디비가 비어있습니다.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 기본 통계
        cursor.execute('SELECT COUNT(*) FROM files')
        files_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM classes')
        classes_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM methods')
        methods_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM edges')
        edges_count = cursor.fetchone()[0]
        
        print(f"📊 Files: {files_count}")
        print(f"📊 Classes: {classes_count}")
        print(f"📊 Methods: {methods_count}")
        print(f"📊 Edges: {edges_count}")
        
        # Edge 상세 정보
        if edges_count > 0:
            print("\n🎯 Edge 상세 정보:")
            cursor.execute('SELECT edge_id, src_type, src_id, dst_type, dst_id, edge_kind, confidence FROM edges LIMIT 5')
            edges = cursor.fetchall()
            for edge_id, src_type, src_id, dst_type, dst_id, edge_kind, confidence in edges:
                print(f"  ID: {edge_id}, {src_type}:{src_id} -> {dst_type}:{dst_id} ({edge_kind}, conf: {confidence})")
        else:
            print("\n❌ Edge가 0개입니다.")
            
            # 클래스 정보 확인
            print("\n🔍 Service 클래스 정보:")
            cursor.execute('SELECT class_id, fqn, name FROM classes WHERE name LIKE "%Service%" ORDER BY name')
            service_classes = cursor.fetchall()
            print(f"Service 클래스 수: {len(service_classes)}")
            for class_id, fqn, name in service_classes:
                print(f"  - {name} (ID: {class_id}, FQN: {fqn})")
            
            # ListService 관련 클래스 확인
            print("\n🔍 ListService 관련 클래스:")
            cursor.execute('SELECT class_id, fqn, name FROM classes WHERE name LIKE "%ListService%" ORDER BY name')
            list_service_classes = cursor.fetchall()
            print(f"ListService 클래스 수: {len(list_service_classes)}")
            for class_id, fqn, name in list_service_classes:
                print(f"  - {name} (ID: {class_id}, FQN: {fqn})")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    check_current_state()




