"""
단일 MyBatis XML 파일로 JOIN 관계 추출 테스트
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def test_single_xml():
    print("단일 MyBatis XML JOIN 분석 테스트")
    print("-" * 50)
    
    try:
        from core.optimized_metadata_engine import OptimizedMetadataEngine
        from parsers.table_metadata_loader import TableMetadataLoader
        from parsers.mybatis_join_analyzer import MyBatisJoinAnalyzer
        
        # 메타데이터 엔진 초기화
        metadata_engine = OptimizedMetadataEngine(project_path="./project")
        project_id = metadata_engine.create_project("SingleXmlTest", "./project")
        print(f"프로젝트 생성: ID {project_id}")
        
        # 테이블 로더로 기본 테이블 생성
        table_loader = TableMetadataLoader(metadata_engine)
        csv_result = table_loader.load_tables_from_csv(project_id, "./sample_tables_no_fk.csv")
        
        if csv_result['success']:
            print(f"CSV 테이블 로드: {csv_result['table_count']}개")
            print(f"로드된 테이블: {list(csv_result['loaded_tables'].keys())}")
            
            # 단일 XML 파일 분석 (JOIN이 있는 파일)
            join_analyzer = MyBatisJoinAnalyzer(metadata_engine)
            xml_file = "./project/sampleSrc/src/main/resources/mybatis/mapper/MixedErrorMapper.xml"
            
            if Path(xml_file).exists():
                print(f"\nXML 파일 분석: {xml_file}")
                
                join_result = join_analyzer.analyze_mybatis_joins(
                    project_id, xml_file, csv_result['loaded_tables']
                )
                
                print(f"분석 결과: {join_result}")
                
                if join_result['success']:
                    print(f"발견된 JOIN: {len(join_result['joins_found'])}개")
                    for join in join_result['joins_found']:
                        print(f"  - {join['source_table']} --[{join['join_type']}]--> {join['target_table']}")
                        print(f"    조건: {join['join_condition']}")
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
    test_single_xml()