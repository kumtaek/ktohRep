"""
데이터베이스 초기화 테스트
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def test_db_init():
    print("데이터베이스 초기화 테스트")
    print("-" * 40)
    
    try:
        from core.optimized_metadata_engine import OptimizedMetadataEngine
        import sqlite3
        
        # 메타데이터 엔진 초기화
        metadata_engine = OptimizedMetadataEngine(project_path="./project")
        print(f"DB 경로: {metadata_engine.db_path}")
        
        # 데이터베이스 테이블 확인
        with sqlite3.connect(metadata_engine.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            print(f"존재하는 테이블: {len(tables)}개")
            for table in tables:
                print(f"  - {table[0]}")
                
        # 프로젝트 생성 테스트
        project_id = metadata_engine.create_project("DBTestProject", "./project")
        print(f"프로젝트 생성: ID {project_id}")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_db_init()