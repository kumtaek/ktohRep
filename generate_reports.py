"""
아키텍처 분석서 및 ERD 리포트 통합 생성기
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def generate_all_reports():
    print("SourceAnalyzer 통합 리포트 생성기")
    print("=" * 60)
    
    try:
        from core.optimized_metadata_engine import OptimizedMetadataEngine
        from parsers.enhanced_relationship_extractor import EnhancedRelationshipExtractor
        from parsers.architecture_analyzer import ArchitectureAnalyzer
        from parsers.table_metadata_loader import TableMetadataLoader
        from parsers.mybatis_join_analyzer import MyBatisJoinAnalyzer
        from parsers.visual_architecture_reporter import VisualArchitectureReporter
        from parsers.mermaid_architecture_reporter import MermaidArchitectureReporter
        import glob
        import sqlite3
        
        # 메타데이터 엔진 초기화
        print("메타데이터 엔진 초기화 중...")
        metadata_engine = OptimizedMetadataEngine(project_path="./project")
        project_id = metadata_engine.create_project("ReportGeneration", "./project")
        
        # 1단계: 모든 메타데이터 수집
        print("\n1단계: 메타데이터 수집")
        print("-" * 40)
        
        # CSV 테이블 로드
        table_loader = TableMetadataLoader(metadata_engine)
        csv_result = table_loader.load_tables_from_csv(project_id, "./sample_tables_no_fk.csv")
        print(f"CSV 테이블: {csv_result.get('table_count', 0)}개")
        
        # MyBatis JOIN 관계 분석
        join_analyzer = MyBatisJoinAnalyzer(metadata_engine)
        xml_directory = "./project/sampleSrc/src/main/resources/mybatis/mapper"
        join_result = join_analyzer.analyze_multiple_mybatis_files(
            project_id, xml_directory, csv_result.get('loaded_tables', {})
        )
        print(f"JOIN 관계: {join_result.get('join_count', 0)}개")
        
        # Java 소스코드 관계 추출
        relationship_extractor = EnhancedRelationshipExtractor(metadata_engine)
        java_files = glob.glob("./project/sampleSrc/src/main/java/**/*.java", recursive=True)
        java_result = relationship_extractor.extract_relationships_from_java(project_id, java_files)
        print(f"Java 파일: {len(java_files)}개 분석 완료")
        
        # 비즈니스 태그 생성
        relationship_extractor.add_business_tags_from_analysis(project_id)
        print("비즈니스 태그 생성 완료")
        
        # 2단계: ERD 생성
        print("\n2단계: ERD 리포트 생성")
        print("-" * 40)
        
        erd_report = generate_erd_report(metadata_engine, project_id)
        print("ERD 리포트 생성 완료")
        
        # 3단계: 아키텍처 분석서 생성
        print("\n3단계: 아키텍처 분석서 생성")
        print("-" * 40)
        
        architecture_analyzer = ArchitectureAnalyzer(metadata_engine)
        analysis_result = architecture_analyzer.analyze_project_architecture(project_id)
        
        if analysis_result['success']:
            architecture_report = architecture_analyzer.generate_architecture_report(analysis_result)
            print("아키텍처 분석서 생성 완료")
        else:
            architecture_report = f"아키텍처 분석 실패: {analysis_result.get('error', '알 수 없는 오류')}"
        
        # 시각적 아키텍처 리포트 생성
        visual_reporter = VisualArchitectureReporter(metadata_engine)
        visual_architecture_report = visual_reporter.generate_visual_report(project_id)
        print("시각적 아키텍처 리포트 생성 완료")
        
        # HTML 아키텍처 리포트 생성
        mermaid_reporter = MermaidArchitectureReporter(metadata_engine)
        html_report_path = mermaid_reporter.generate_html_report(project_id)
        print(f"HTML 아키텍처 리포트 생성 완료: {html_report_path}")
        
        # 4단계: 통합 리포트 출력
        print("\n" + "=" * 80)
        print("통합 분석 리포트")
        print("=" * 80)
        
        print("\n" + "=" * 40)
        print("1. ERD (Entity Relationship Diagram)")
        print("=" * 40)
        print(erd_report)
        
        print("\n" + "=" * 40) 
        print("2. 시스템 아키텍처 분석 (기본)")
        print("=" * 40)
        print(architecture_report)
        
        print("\n" + "=" * 40) 
        print("3. 시스템 아키텍처 분석 (시각적)")
        print("=" * 40)
        print(visual_architecture_report)
        
        # 5단계: 파일로 저장 (선택사항)
        save_to_files = input("\n리포트를 파일로 저장하시겠습니까? (y/n): ").lower().strip()
        if save_to_files == 'y':
            save_reports_to_files(erd_report, architecture_report, visual_architecture_report)
            print("리포트 파일 저장 완료!")
        
        print(f"\n리포트 생성 완료!")
        print(f"   - 테이블: {csv_result.get('table_count', 0)}개")
        print(f"   - JOIN 관계: {join_result.get('join_count', 0)}개")
        print(f"   - Java 관계: {sum(java_result.get('summary', {}).values())}개")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

def generate_erd_report(metadata_engine, project_id):
    """ERD 리포트 생성"""
    import sqlite3
    
    try:
        db_path = metadata_engine.db_path
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # 테이블 조회
            cursor.execute("""
                SELECT component_name, component_type
                FROM components
                WHERE project_id = ? AND component_type IN ('table', 'table_dummy')
                ORDER BY component_type, component_name
            """, (project_id,))
            
            tables = cursor.fetchall()
            real_tables = [t for t in tables if t[1] == 'table']
            dummy_tables = [t for t in tables if t[1] == 'table_dummy']
            
            # 관계 조회
            cursor.execute("""
                SELECT r.relationship_type, 
                       c1.component_name as source_table, 
                       c2.component_name as target_table,
                       r.confidence
                FROM relationships r
                JOIN components c1 ON r.src_component_id = c1.component_id
                JOIN components c2 ON r.dst_component_id = c2.component_id
                WHERE r.project_id = ? AND r.relationship_type IN ('join', 'foreign_key')
                ORDER BY r.relationship_type, c1.component_name
            """, (project_id,))
            
            relationships = cursor.fetchall()
            join_rels = [r for r in relationships if r[0] == 'join']
            fk_rels = [r for r in relationships if r[0] == 'foreign_key']
        
        # ERD 리포트 작성
        report_lines = []
        report_lines.append("ERD - Entity Relationship Diagram")
        report_lines.append("=" * 50)
        
        # 테이블 목록
        report_lines.append(f"\n[테이블 목록] - 총 {len(tables)}개")
        
        if real_tables:
            report_lines.append(f"  실제 테이블 ({len(real_tables)}개):")
            for table_name, _ in real_tables:
                report_lines.append(f"    - {table_name}")
        
        if dummy_tables:
            report_lines.append(f"  참조 테이블 ({len(dummy_tables)}개):")
            for table_name, _ in dummy_tables:
                report_lines.append(f"    - {table_name} [더미]")
        
        # 관계 다이어그램
        report_lines.append(f"\n[관계 다이어그램] - 총 {len(relationships)}개")
        
        if join_rels:
            report_lines.append(f"  JOIN 관계 ({len(join_rels)}개):")
            for _, source, target, confidence in join_rels:
                conf_str = f" (신뢰도: {confidence})" if confidence < 1.0 else ""
                report_lines.append(f"    {source} --JOIN--> {target}{conf_str}")
        
        if fk_rels:
            report_lines.append(f"  외래키 관계 ({len(fk_rels)}개):")
            for _, source, target, confidence in fk_rels:
                conf_str = f" (신뢰도: {confidence})" if confidence < 1.0 else ""
                report_lines.append(f"    {source} --FK--> {target}{conf_str}")
        
        # 요약 통계
        report_lines.append(f"\n[요약]")
        report_lines.append(f"  - 실제 테이블: {len(real_tables)}개 (CSV 로드)")
        report_lines.append(f"  - 참조 테이블: {len(dummy_tables)}개 (MyBatis 분석)")
        report_lines.append(f"  - JOIN 관계: {len(join_rels)}개")
        report_lines.append(f"  - 외래키 관계: {len(fk_rels)}개")
        
        return "\n".join(report_lines)
        
    except Exception as e:
        return f"ERD 생성 실패: {e}"

def save_reports_to_files(erd_report, architecture_report, visual_architecture_report=None):
    """리포트를 파일로 저장"""
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # ERD 리포트 저장
    erd_filename = f"ERD_Report_{timestamp}.txt"
    with open(erd_filename, 'w', encoding='utf-8') as f:
        f.write(erd_report)
    print(f"ERD 리포트 저장: {erd_filename}")
    
    # 아키텍처 리포트 저장 (기본)
    arch_filename = f"Architecture_Report_{timestamp}.txt"
    with open(arch_filename, 'w', encoding='utf-8') as f:
        f.write(architecture_report)
    print(f"아키텍처 리포트 저장: {arch_filename}")
    
    # 시각적 아키텍처 리포트 저장
    if visual_architecture_report:
        visual_arch_filename = f"Visual_Architecture_Report_{timestamp}.txt"
        with open(visual_arch_filename, 'w', encoding='utf-8') as f:
            f.write(visual_architecture_report)
        print(f"시각적 아키텍처 리포트 저장: {visual_arch_filename}")
    
    # 통합 리포트 저장
    combined_filename = f"Combined_Report_{timestamp}.txt"
    with open(combined_filename, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("SourceAnalyzer 통합 분석 리포트\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("=" * 40 + "\n")
        f.write("1. ERD (Entity Relationship Diagram)\n")
        f.write("=" * 40 + "\n")
        f.write(erd_report + "\n\n")
        
        f.write("=" * 40 + "\n")
        f.write("2. 시스템 아키텍처 분석 (기본)\n")
        f.write("=" * 40 + "\n")
        f.write(architecture_report + "\n\n")
        
        if visual_architecture_report:
            f.write("=" * 40 + "\n")
            f.write("3. 시스템 아키텍처 분석 (시각적)\n")
            f.write("=" * 40 + "\n")
            f.write(visual_architecture_report + "\n")
    print(f"통합 리포트 저장: {combined_filename}")

if __name__ == "__main__":
    generate_all_reports()