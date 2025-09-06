"""
최종 ERD 생성 테스트 - CSV + MyBatis Implicit/Explicit JOIN 통합
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def test_final_erd():
    print("최종 ERD 생성 테스트")
    print("=" * 60)
    
    try:
        from core.optimized_metadata_engine import OptimizedMetadataEngine
        from parsers.table_metadata_loader import TableMetadataLoader
        from parsers.mybatis_join_analyzer import MyBatisJoinAnalyzer
        import sqlite3
        
        # 메타데이터 엔진 초기화
        metadata_engine = OptimizedMetadataEngine(project_path="./project")
        project_id = metadata_engine.create_project("FinalERDTest", "./project")
        print(f"프로젝트 생성: ID {project_id}")
        
        # 1단계: CSV에서 테이블 구조 로드
        print("\n1단계: CSV 테이블 구조 로딩")
        print("-" * 40)
        table_loader = TableMetadataLoader(metadata_engine)
        csv_result = table_loader.load_tables_from_csv(project_id, "./sample_tables_no_fk.csv")
        
        if csv_result['success']:
            print(f"OK CSV 테이블 {csv_result['table_count']}개 로드 완료")
            for table_name in csv_result['loaded_tables'].keys():
                print(f"  - {table_name}")
        
        # 2단계: MyBatis XML에서 JOIN 관계 추출
        print("\n2단계: MyBatis JOIN 관계 분석")
        print("-" * 40)
        join_analyzer = MyBatisJoinAnalyzer(metadata_engine)
        xml_directory = "./project/sampleSrc/src/main/resources/mybatis/mapper"
        
        # 여러 XML 파일 분석
        join_result = join_analyzer.analyze_multiple_mybatis_files(
            project_id, xml_directory, csv_result['loaded_tables']
        )
        
        if join_result['success']:
            print(f"OK JOIN 관계 {join_result['join_count']}개 발견")
            print(f"OK 더미 테이블 {join_result['dummy_table_count']}개 생성")
        
        # 3단계: 메타DB에서 최종 ERD 정보 조회
        print("\n3단계: 메타DB 조회 및 ERD 생성")  
        print("-" * 40)
        
        db_path = metadata_engine.db_path
        print(f"메타DB 경로: {db_path}")
        if Path(db_path).exists():
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # 전체 테이블 조회
            cursor.execute("""
                SELECT component_name, component_type
                FROM components
                WHERE project_id = ? AND component_type IN ('table', 'table_dummy')
                ORDER BY component_type, component_name
            """, (project_id,))
            
            tables = cursor.fetchall()
            print(f"총 테이블: {len(tables)}개")
            
            real_tables = [t for t in tables if t[1] == 'table']
            dummy_tables = [t for t in tables if t[1] == 'table_dummy']
            
            print(f"  실제 테이블: {len(real_tables)}개")
            for table_name, _ in real_tables:
                print(f"    - {table_name}")
                
            print(f"  더미 테이블: {len(dummy_tables)}개") 
            for table_name, _ in dummy_tables:
                print(f"    - {table_name} [더미]")
            
            # 관계 조회
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
            print(f"\n관계: {len(relationships)}개")
            
            # 관계 타입별 분류
            join_rels = [r for r in relationships if r[0] == 'join']
            fk_rels = [r for r in relationships if r[0] == 'foreign_key']
            
            print(f"  JOIN 관계: {len(join_rels)}개")
            for rel_type, source, target, confidence in join_rels:
                print(f"    {source} ──JOIN──> {target} (신뢰도: {confidence})")
            
            if fk_rels:
                print(f"  외래키 관계: {len(fk_rels)}개")
                for rel_type, source, target, confidence in fk_rels:
                    print(f"    {source} ──FK──> {target} (신뢰도: {confidence})")
            
            conn.close()
            
            # 4단계: 최종 ERD 다이어그램 생성
            print("\n4단계: 최종 ERD 다이어그램")
            print("=" * 60)
            
            print("```")
            print("ERD - SourceAnalyzer 프로젝트 테이블 관계도")
            print("=" * 50)
            
            # 테이블 목록
            print("\n[테이블 목록]")
            for table_name, table_type in tables:
                marker = "[더미]" if table_type == 'table_dummy' else ""
                print(f"  {table_name} {marker}")
            
            # 관계 다이어그램
            print(f"\n[관계 다이어그램]")
            for rel_type, source, target, confidence in relationships:
                arrow = "──FK──>" if rel_type == 'foreign_key' else "──JOIN──>"
                print(f"  {source} {arrow} {target}")
            
            print("```")
            
            # 통계 요약
            print(f"\n[결과] ERD 생성 완료!")
            print(f"   - 실제 테이블: {len(real_tables)}개 (CSV 로드)")
            print(f"   - 더미 테이블: {len(dummy_tables)}개 (XML 참조)")
            print(f"   - 총 관계: {len(relationships)}개")
            print(f"     * JOIN 관계: {len(join_rels)}개 (MyBatis XML 분석)")
            print(f"     * 외래키 관계: {len(fk_rels)}개 (CSV 메타데이터)")
                
        else:
            print(f"메타DB 파일을 찾을 수 없음: {db_path}")
            
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_final_erd()