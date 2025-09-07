"""
아키텍처 전용 HTML 리포트 생성 스크립트
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def generate_architecture_html_only():
    print("아키텍처 HTML 리포트 생성기")
    print("=" * 50)
    
    try:
        from core.optimized_metadata_engine import OptimizedMetadataEngine
        from parsers.enhanced_relationship_extractor import EnhancedRelationshipExtractor
        from parsers.table_metadata_loader import TableMetadataLoader
        from parsers.mybatis_join_analyzer import MyBatisJoinAnalyzer
        from parsers.mermaid_html_reporter import MermaidHTMLReporter
        import glob
        
        # 메타데이터 엔진 초기화
        print("메타데이터 엔진 초기화 중...")
        metadata_engine = OptimizedMetadataEngine(project_path="./project")
        project_id = metadata_engine.create_project("ArchHtmlGeneration", "./project")
        
        # 1단계: 전체 메타데이터 수집
        print("\n1단계: 메타데이터 수집")
        print("-" * 30)
        
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
        
        # 2단계: 아키텍처 HTML 리포트 생성
        print("\n2단계: 아키텍처 HTML 리포트 생성")
        print("-" * 30)
        
        html_reporter = MermaidHTMLReporter(metadata_engine)
        html_file_path = html_reporter.generate_architecture_html(project_id)
        
        print("[OK] 아키텍처 HTML 리포트 생성 완료!")
        print(f"   파일 위치: {html_file_path}")
        print(f"   테이블: {csv_result.get('table_count', 0)}개")
        print(f"   JOIN 관계: {join_result.get('join_count', 0)}개")
        print(f"   Java 관계: {sum(java_result.get('summary', {}).values())}개")
        
        # 파일 크기 확인
        import os
        if os.path.exists(html_file_path):
            file_size = os.path.getsize(html_file_path)
            print(f"   파일 크기: {file_size:,} bytes")
        
        print(f"\n브라우저에서 확인: file:///{os.path.abspath(html_file_path)}")
        
    except Exception as e:
        print(f"[ERROR] 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_architecture_html_only()