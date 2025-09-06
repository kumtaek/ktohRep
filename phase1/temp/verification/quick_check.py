import sqlite3
import os

# 메타디비 경로 확인
db_path = '../project/sampleSrc/metadata.db'
if os.path.exists(db_path):
    print(f"✅ 메타디비 존재: {db_path}")
    
    # 파일 크기 확인
    size = os.path.getsize(db_path)
    print(f"📁 파일 크기: {size} bytes")
    
    if size > 0:
        # 메타디비 연결
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 기본 통계
        cursor.execute('SELECT COUNT(*) FROM edges')
        edges_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM classes')
        classes_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM methods')
        methods_count = cursor.fetchone()[0]
        
        print(f'📊 Classes: {classes_count}')
        print(f'📊 Methods: {methods_count}')
        print(f'📊 Edges: {edges_count}')
        
        # Edge 상세 정보
        if edges_count > 0:
            print('\n🎯 Edge 상세 정보:')
            cursor.execute('SELECT edge_id, src_type, src_id, dst_type, dst_id, edge_kind, confidence FROM edges LIMIT 3')
            edges = cursor.fetchall()
            for edge_id, src_type, src_id, dst_type, dst_id, edge_kind, confidence in edges:
                print(f'  ID: {edge_id}, {src_type}:{src_id} -> {dst_type}:{dst_id} ({edge_kind}, conf: {confidence})')
        else:
            print('\n❌ Edge가 여전히 0개입니다.')
        
        conn.close()
    else:
        print("❌ 메타디비가 0바이트입니다.")
else:
    print(f"❌ 메타디비가 존재하지 않습니다: {db_path}")




