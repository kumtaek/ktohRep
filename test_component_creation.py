"""
컴포넌트 생성 테스트
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def test_component_creation():
    print("컴포넌트 생성 테스트")
    print("-" * 50)
    
    try:
        from core.optimized_metadata_engine import OptimizedMetadataEngine
        
        # 메타데이터 엔진 초기화
        metadata_engine = OptimizedMetadataEngine(project_path="./project")
        project_id = metadata_engine.create_project("ComponentTest", "./project")
        print(f"프로젝트 생성: ID {project_id}")
        
        # 테이블 컴포넌트 직접 추가 테스트
        table_component_id = metadata_engine.add_component(
            project_id=project_id,
            file_id=None,
            component_name="test_table",
            component_type='table',
            line_start=None,
            line_end=None
        )
        
        print(f"테이블 컴포넌트 ID: {table_component_id}")
        print(f"타입: {type(table_component_id)}")
        
        if table_component_id:
            print("컴포넌트 생성 성공!")
        else:
            print("컴포넌트 생성 실패!")
            
        # 중복 생성 테스트
        table_component_id2 = metadata_engine.add_component(
            project_id=project_id,
            file_id=None,
            component_name="test_table",
            component_type='table',
            line_start=None,
            line_end=None
        )
        
        print(f"중복 테이블 컴포넌트 ID: {table_component_id2}")
        print(f"동일한 ID인가: {table_component_id == table_component_id2}")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_component_creation()