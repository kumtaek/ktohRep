"""
아키텍처 분석기 종합 테스트
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def test_architecture_analysis():
    print("시스템 아키텍처 분석 테스트")
    print("=" * 60)
    
    try:
        from core.optimized_metadata_engine import OptimizedMetadataEngine
        from parsers.enhanced_relationship_extractor import EnhancedRelationshipExtractor
        from parsers.architecture_analyzer import ArchitectureAnalyzer
        from parsers.table_metadata_loader import TableMetadataLoader
        from parsers.mybatis_join_analyzer import MyBatisJoinAnalyzer
        import glob
        
        # 1단계: 메타데이터 엔진 초기화
        print("1단계: 메타데이터 엔진 초기화")
        print("-" * 40)
        metadata_engine = OptimizedMetadataEngine(project_path="./project")
        project_id = metadata_engine.create_project("ArchitectureAnalysisTest", "./project")
        print(f"프로젝트 생성: ID {project_id}")
        
        # 2단계: 테이블 메타데이터 로드 (기존 데이터)
        print("\n2단계: 데이터베이스 테이블 메타데이터 로드")
        print("-" * 40)
        table_loader = TableMetadataLoader(metadata_engine)
        csv_result = table_loader.load_tables_from_csv(project_id, "./sample_tables_no_fk.csv")
        
        if csv_result['success']:
            print(f"OK CSV 테이블 {csv_result['table_count']}개 로드")
        
        # 3단계: MyBatis JOIN 관계 분석 (기존 데이터)
        print("\n3단계: MyBatis JOIN 관계 분석")
        print("-" * 40)
        join_analyzer = MyBatisJoinAnalyzer(metadata_engine)
        xml_directory = "./project/sampleSrc/src/main/resources/mybatis/mapper"
        
        join_result = join_analyzer.analyze_multiple_mybatis_files(
            project_id, xml_directory, csv_result['loaded_tables']
        )
        
        if join_result['success']:
            print(f"OK JOIN 관계 {join_result['join_count']}개 발견")
        
        # 4단계: Java 소스코드에서 관계 추출 (새로운 데이터)
        print("\n4단계: Java 소스코드 관계 추출")
        print("-" * 40)
        relationship_extractor = EnhancedRelationshipExtractor(metadata_engine)
        
        # Java 파일 목록 수집
        java_files = glob.glob("./project/sampleSrc/src/main/java/**/*.java", recursive=True)
        print(f"Java 파일 {len(java_files)}개 발견")
        
        # 관계 추출
        java_result = relationship_extractor.extract_relationships_from_java(project_id, java_files)
        
        if java_result['success']:
            print("OK Java 코드 관계 추출 완료")
            for rel_type, count in java_result['summary'].items():
                if count > 0:
                    print(f"    - {rel_type}: {count}개")
        
        # 5단계: 비즈니스 태그 자동 생성
        print("\n5단계: 비즈니스 태그 자동 생성")
        print("-" * 40)
        relationship_extractor.add_business_tags_from_analysis(project_id)
        print("OK 컴포넌트 이름 기반 비즈니스 태그 생성 완료")
        
        # 6단계: 아키텍처 분석 실행
        print("\n6단계: 아키텍처 분석 실행")
        print("-" * 40)
        architecture_analyzer = ArchitectureAnalyzer(metadata_engine)
        analysis_result = architecture_analyzer.analyze_project_architecture(project_id)
        
        if analysis_result['success']:
            print("OK 아키텍처 분석 완료")
            
            # 7단계: 텍스트 리포트 생성
            print("\n7단계: 아키텍처 리포트 생성")
            print("=" * 60)
            
            report = architecture_analyzer.generate_architecture_report(analysis_result)
            print(report)
            
        else:
            print(f"아키텍처 분석 실패: {analysis_result['error']}")
            
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_architecture_analysis()