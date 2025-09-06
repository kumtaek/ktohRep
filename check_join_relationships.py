"""
JOIN 관계가 메타DB에 제대로 저장되는지 확인하는 테스트
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def check_join_storage():
    print("JOIN 관계 메타DB 저장 테스트")
    print("-" * 50)
    
    try:
        from core.optimized_metadata_engine import OptimizedMetadataEngine
        from parsers.table_metadata_loader import TableMetadataLoader
        from parsers.mybatis_join_analyzer import MyBatisJoinAnalyzer
        
        # 메타데이터 엔진 초기화
        metadata_engine = OptimizedMetadataEngine(project_path="./project")
        project_id = metadata_engine.create_project("JoinTest", "./project")
        print(f"프로젝트 생성: ID {project_id}")
        
        # 테이블 로더로 기본 테이블만 생성 (외래키 없음)
        table_loader = TableMetadataLoader(metadata_engine)
        csv_result = table_loader.load_tables_from_csv(project_id, "./sample_tables_no_fk.csv")
        
        if csv_result['success']:
            print(f"CSV 테이블 로드: {csv_result['table_count']}개")
            
            # MyBatis JOIN 분석
            join_analyzer = MyBatisJoinAnalyzer(metadata_engine)
            xml_directory = "./project/sampleSrc/src/main/resources/mybatis/mapper"
            
            if Path(xml_directory).exists():
                join_result = join_analyzer.analyze_multiple_mybatis_files(
                    project_id, xml_directory, csv_result['loaded_tables']
                )
                
                if join_result['success']:
                    print(f"JOIN 관계 분석: {join_result['join_count']}개 발견")
                    
                    # 실제 메타DB에서 관계 조회
                    print("\n메타DB에 저장된 관계 확인:")
                    import sqlite3
                    
                    db_path = "./project/metadata_optimized.db"
                    if Path(db_path).exists():
                        conn = sqlite3.connect(db_path)
                        cursor = conn.cursor()
                        
                        # 저장된 관계 조회
                        cursor.execute("""
                            SELECT r.relationship_type, 
                                   c1.component_name as source_table, 
                                   c2.component_name as target_table,
                                   r.confidence
                            FROM relationships r
                            JOIN components c1 ON r.src_component_id = c1.component_id
                            JOIN components c2 ON r.dst_component_id = c2.component_id
                            WHERE r.project_id = ?
                            ORDER BY r.relationship_type, c1.component_name
                        """, (project_id,))
                        
                        relationships = cursor.fetchall()
                        
                        if relationships:
                            print(f"저장된 관계: {len(relationships)}개")
                            for rel_type, source, target, confidence in relationships:
                                print(f"  - {source} --[{rel_type}]-> {target} (신뢰도: {confidence})")
                        else:
                            print("저장된 관계가 없습니다.")
                        
                        # 테이블 정보도 확인
                        cursor.execute("""
                            SELECT component_name, component_type
                            FROM components
                            WHERE project_id = ? AND component_type IN ('table', 'table_dummy')
                            ORDER BY component_type, component_name
                        """, (project_id,))
                        
                        tables = cursor.fetchall()
                        print(f"\n저장된 테이블: {len(tables)}개")
                        for table_name, table_type in tables:
                            marker = "[더미]" if table_type == 'table_dummy' else ""
                            print(f"  - {table_name} {marker}")
                        
                        conn.close()
                        
                        # 성공적으로 저장되었는지 확인
                        if relationships:
                            print(f"\n결론: JOIN 관계가 메타DB에 성공적으로 저장되었습니다!")
                            
                            # ERD 텍스트 간단히 출력
                            print(f"\n간단한 ERD:")
                            print("-" * 30)
                            
                            # 관계별 그룹화
                            for rel_type, source, target, confidence in relationships:
                                print(f"{source} --> {target} ({rel_type})")
                            
                        else:
                            print(f"\n결론: JOIN 관계가 메타DB에 저장되지 않았습니다.")
                            
                    else:
                        print(f"메타DB 파일을 찾을 수 없음: {db_path}")
                else:
                    print(f"JOIN 분석 실패: {join_result['error']}")
            else:
                print(f"MyBatis XML 디렉토리 없음: {xml_directory}")
        else:
            print(f"CSV 로드 실패: {csv_result['error']}")
    
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_join_storage()