"""
Implicit JOIN 파싱 테스트
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def test_implicit_join():
    print("Implicit JOIN 파싱 테스트")
    print("-" * 50)
    
    try:
        from core.optimized_metadata_engine import OptimizedMetadataEngine
        from parsers.table_metadata_loader import TableMetadataLoader
        from parsers.mybatis_join_analyzer import MyBatisJoinAnalyzer
        
        # 메타데이터 엔진 초기화
        metadata_engine = OptimizedMetadataEngine(project_path="./project")
        project_id = metadata_engine.create_project("ImplicitJoinTest", "./project")
        print(f"프로젝트 생성: ID {project_id}")
        
        # 테이블 로더로 기본 테이블 생성
        table_loader = TableMetadataLoader(metadata_engine)
        csv_result = table_loader.load_tables_from_csv(project_id, "./sample_tables_no_fk.csv")
        
        if csv_result['success']:
            print(f"CSV 테이블 로드: {csv_result['table_count']}개")
            print(f"로드된 테이블: {list(csv_result['loaded_tables'].keys())}")
            
            # Implicit JOIN XML 파일 분석
            join_analyzer = MyBatisJoinAnalyzer(metadata_engine)
            xml_file = "./project/sampleSrc/src/main/resources/mybatis/mapper/ImplicitJoinMapper.xml"
            
            if Path(xml_file).exists():
                print(f"\nImplicit JOIN XML 파일 분석: {xml_file}")
                
                join_result = join_analyzer.analyze_mybatis_joins(
                    project_id, xml_file, csv_result['loaded_tables']
                )
                
                if join_result['success']:
                    print(f"\n발견된 JOIN: {len(join_result['joins_found'])}개")
                    print(f"생성된 더미 테이블: {len(join_result['dummy_tables_created'])}개")
                    
                    for i, join in enumerate(join_result['joins_found'], 1):
                        print(f"{i:2d}. {join['source_table']} --[{join['join_type']}]--> {join['target_table']}")
                        print(f"     조건: {join['join_condition']}")
                        print(f"     파일: {join['xml_file']}")
                        print()
                    
                    print("생성된 더미 테이블:")
                    for table_name, table_id in join_result['dummy_tables_created'].items():
                        print(f"  - {table_name} (ID: {table_id})")
                        
                else:
                    print(f"JOIN 분석 실패: {join_result.get('error', '알 수 없는 오류')}")
                    
            else:
                print(f"XML 파일을 찾을 수 없음: {xml_file}")
        else:
            print(f"CSV 로드 실패: {csv_result['error']}")
    
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_implicit_join()