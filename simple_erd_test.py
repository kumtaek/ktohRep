"""
간단한 ERD 생성 테스트
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def simple_test():
    print("=== 간단한 ERD 생성 테스트 ===\n")
    
    try:
        # 메타데이터 엔진 초기화
        from core.optimized_metadata_engine import OptimizedMetadataEngine
        metadata_engine = OptimizedMetadataEngine(project_path="./project")
        project_id = metadata_engine.create_project("SimpleERD", "./project")
        print(f"프로젝트 생성: ID {project_id}")
        
        # CSV 테이블 로더 테스트
        from parsers.table_metadata_loader import TableMetadataLoader
        table_loader = TableMetadataLoader(metadata_engine)
        
        csv_result = table_loader.load_tables_from_csv(project_id, "./sample_tables.csv")
        print(f"CSV 로드: {csv_result['success']}")
        
        if csv_result['success']:
            print(f"로드된 테이블: {csv_result['table_count']}개")
            print(f"로드된 컬럼: {csv_result['column_count']}개")
            
            # 외래키 컬럼 확인
            fk_columns = [col for col in csv_result['loaded_columns'] if col['is_foreign_key']]
            print(f"외래키 컬럼: {len(fk_columns)}개")
            for fk_col in fk_columns:
                print(f"  - {fk_col['table_name']}.{fk_col['column_name']} -> {fk_col['foreign_table']}.{fk_col['foreign_column']}")
            
            # 외래키 관계 생성
            fk_result = table_loader.create_foreign_key_relationships(
                project_id, csv_result['loaded_tables'], csv_result['loaded_columns']
            )
            print(f"외래키 관계 생성 결과: {fk_result['success']}")
            print(f"외래키 관계: {fk_result.get('relationship_count', 0)}개")
            if not fk_result['success']:
                print(f"외래키 생성 오류: {fk_result.get('error', '알 수 없는 오류')}")
            
            # 간단한 ERD 텍스트 생성
            print("\n=== 생성된 테이블 구조 ===")
            for table_name in csv_result['loaded_tables'].keys():
                print(f"테이블: {table_name}")
            
            print("\n=== 외래키 관계 ===")
            for rel in fk_result.get('relationships_created', []):
                print(f"{rel['source_table']}.{rel['source_column']} -> {rel['target_table']}.{rel['target_column']}")
        
        print("\n테스트 완료!")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_test()