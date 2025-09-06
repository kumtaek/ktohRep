"""
Implicit JOIN 파싱 상세 디버깅
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def test_implicit_join_debug():
    print("Implicit JOIN 파싱 상세 디버깅")
    print("-" * 50)
    
    try:
        from core.optimized_metadata_engine import OptimizedMetadataEngine
        from parsers.table_metadata_loader import TableMetadataLoader
        from parsers.mybatis_join_analyzer import MyBatisJoinAnalyzer
        import logging
        
        # 로깅 설정
        logging.basicConfig(level=logging.DEBUG)
        
        # 메타데이터 엔진 초기화
        metadata_engine = OptimizedMetadataEngine(project_path="./project")
        project_id = metadata_engine.create_project("ImplicitJoinDebugTest", "./project")
        print(f"프로젝트 생성: ID {project_id}")
        
        # 테이블 로더로 기본 테이블 생성
        table_loader = TableMetadataLoader(metadata_engine)
        csv_result = table_loader.load_tables_from_csv(project_id, "./sample_tables_no_fk.csv")
        
        if csv_result['success']:
            print(f"CSV 테이블 로드: {csv_result['table_count']}개")
            print(f"로드된 테이블: {list(csv_result['loaded_tables'].keys())}")
            
            # 단일 쿼리만 테스트 - getUsersWithTypes
            join_analyzer = MyBatisJoinAnalyzer(metadata_engine)
            
            # 직접 SQL 텍스트로 테스트
            sql_text = """
                SELECT u.id, u.name, u.email, ut.type_name
                FROM users u, user_types ut
                WHERE u.type_id = ut.id
                ORDER BY u.name
            """
            
            print(f"\n테스트 SQL:")
            print(sql_text)
            
            # JOIN 관계 추출 테스트
            joins = join_analyzer._extract_join_relationships(sql_text)
            print(f"\n추출된 JOIN: {len(joins)}개")
            
            for i, join in enumerate(joins, 1):
                print(f"{i}. {join['source_table']} --[{join['join_type']}]--> {join['target_table']}")
                print(f"   조건: {join['join_condition']}")
                print(f"   별칭: {join['target_alias']}")
                
                # 실제 메타데이터 엔진에 저장 시도
                source_table_id = csv_result['loaded_tables'].get(join['source_table'])
                target_table_id = csv_result['loaded_tables'].get(join['target_table'])
                
                print(f"   소스 테이블 ID: {source_table_id}")
                print(f"   타겟 테이블 ID: {target_table_id}")
                
                if not target_table_id:
                    print(f"   타겟 테이블이 CSV에 없음 - 더미 테이블 생성 필요")
                    target_table_id = join_analyzer._get_or_create_table(
                        project_id, join['target_table'], csv_result['loaded_tables'], {}
                    )
                    print(f"   생성된 더미 테이블 ID: {target_table_id}")
                
                if source_table_id and target_table_id:
                    try:
                        print(f"   관계 저장 시도...")
                        metadata_engine.add_relationship(
                            project_id=project_id,
                            src_component_id=source_table_id,
                            dst_component_id=target_table_id,
                            relationship_type='join',
                            confidence=0.9
                        )
                        print(f"   관계 저장 성공!")
                    except Exception as e:
                        print(f"   관계 저장 실패: {e}")
                else:
                    print(f"   테이블 ID가 없어서 관계 저장 불가")
                print()
                
        else:
            print(f"CSV 로드 실패: {csv_result['error']}")
    
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_implicit_join_debug()