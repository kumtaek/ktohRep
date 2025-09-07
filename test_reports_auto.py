"""
아키텍처 분석서 및 ERD 리포트 자동 생성 테스트
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def test_reports_auto():
    print("SourceAnalyzer 통합 리포트 생성기 (자동 저장)")
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
        project_id = metadata_engine.create_project("AutoReportGeneration", "./project")
        
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
        
        from generate_reports import generate_erd_report
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
        
        # 4단계: 파일로 자동 저장
        print("\n4단계: 리포트 파일 저장")
        print("-" * 40)
        
        from generate_reports import save_reports_to_files
        save_reports_to_files(erd_report, architecture_report, visual_architecture_report)
        print("리포트 파일 저장 완료!")
        
        print(f"\n리포트 생성 완료!")
        print(f"   - 테이블: {csv_result.get('table_count', 0)}개")
        print(f"   - JOIN 관계: {join_result.get('join_count', 0)}개")
        print(f"   - Java 관계: {sum(java_result.get('summary', {}).values())}개")
        
        # 5단계: 생성된 파일 목록 확인
        print("\n5단계: 생성된 파일 확인")
        print("-" * 40)
        import os
        from datetime import datetime
        
        # 현재 시각의 타임스탬프로 파일 찾기
        current_time = datetime.now().strftime("%Y%m%d")
        files = [f for f in os.listdir('.') if f.startswith(('ERD_Report_', 'Architecture_Report_', 'Visual_Architecture_Report_', 'Combined_Report_')) and current_time in f]
        
        # HTML 파일도 확인
        html_files = []
        report_dir = "./project/sampleSrc/report"
        if os.path.exists(report_dir):
            html_files = [f for f in os.listdir(report_dir) if f.startswith('architecture_mermaid_') and f.endswith('.html') and current_time in f]
        
        for file in sorted(files):
            file_size = os.path.getsize(file)
            print(f"   생성된 파일: {file} ({file_size} bytes)")
        
        for file in sorted(html_files):
            file_size = os.path.getsize(os.path.join(report_dir, file))
            print(f"   생성된 HTML 파일: {file} ({file_size} bytes)")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_reports_auto()