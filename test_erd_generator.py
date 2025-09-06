"""
ERD 생성기 테스트 스크립트
CSV와 MyBatis XML을 통합하여 완전한 ERD를 생성하는 테스트
"""
import sys
import logging
from pathlib import Path

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(str(Path(__file__).parent))

from core.optimized_metadata_engine import OptimizedMetadataEngine
from parsers.erd_generator import ERDGenerator

def setup_logging():
    """로깅 설정"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('erd_generation.log', encoding='utf-8')
        ]
    )

def test_erd_generation():
    """ERD 생성 테스트"""
    print("=== ERD 생성기 테스트 ===\n")
    
    try:
        # 1. 메타데이터 엔진 초기화
        print("1단계: 메타데이터 엔진 초기화...")
        metadata_engine = OptimizedMetadataEngine(project_path="./project")
        
        # 2. ERD 생성기 초기화
        print("2단계: ERD 생성기 초기화...")
        erd_generator = ERDGenerator(metadata_engine)
        
        # 3. 프로젝트 생성
        print("3단계: 프로젝트 생성...")
        project_name = "SampleECommerce_ERD"
        project_id = metadata_engine.create_project(project_name, "./project")
        print(f"프로젝트 생성 완료: {project_name} (ID: {project_id})")
        
        # 4. ERD 생성 실행
        print("4단계: ERD 생성 실행...")
        csv_file_path = "./sample_tables.csv"
        mybatis_xml_directory = "./project/sampleSrc/src/main/resources/mybatis/mapper"
        
        # 파일 존재 확인
        if not Path(csv_file_path).exists():
            print(f"❌ CSV 파일이 존재하지 않음: {csv_file_path}")
            return
            
        if not Path(mybatis_xml_directory).exists():
            print(f"❌ MyBatis XML 디렉토리가 존재하지 않음: {mybatis_xml_directory}")
            return
        
        # ERD 생성
        erd_result = erd_generator.generate_complete_erd(
            project_id=project_id,
            project_name=project_name,
            csv_file_path=csv_file_path,
            mybatis_xml_directory=mybatis_xml_directory
        )
        
        # 5. 결과 출력
        if erd_result['success']:
            print("✅ ERD 생성 성공!")
            
            # 통계 출력
            stats = erd_result['statistics']
            print(f"\n📊 ERD 통계:")
            print(f"  - 총 테이블: {stats['total_tables']}개")
            print(f"    └─ CSV 테이블: {stats['csv_tables']}개")
            print(f"    └─ 더미 테이블: {stats['dummy_tables']}개")
            print(f"  - 총 관계: {stats['total_relationships']}개")
            print(f"    └─ 외래키 관계: {stats['foreign_key_relationships']}개")
            print(f"    └─ JOIN 관계: {stats['join_relationships']}개")
            print(f"  - 총 컬럼: {stats['total_columns']}개")
            
            # 텍스트 ERD 출력
            print(f"\n📋 생성된 ERD:")
            print("=" * 80)
            print(erd_result['text_erd'])
            print("=" * 80)
            
            # 파일로 저장
            output_file = f"./docs/{project_name}_ERD.md"
            Path(output_file).parent.mkdir(exist_ok=True)
            
            if erd_generator.save_erd_to_file(erd_result, output_file):
                print(f"\n💾 ERD 파일 저장 완료: {output_file}")
            
            # 상세 분석 결과 출력
            print(f"\n🔍 상세 분석 결과:")
            
            # CSV 결과
            csv_result = erd_result['csv_result']
            print(f"CSV 처리 결과:")
            print(f"  - 성공: {csv_result['success']}")
            print(f"  - 테이블 수: {csv_result.get('table_count', 0)}개")
            print(f"  - 컬럼 수: {csv_result.get('column_count', 0)}개")
            
            # 외래키 결과
            fk_result = erd_result['fk_result']
            print(f"외래키 처리 결과:")
            print(f"  - 성공: {fk_result.get('success', False)}")
            print(f"  - 외래키 관계: {fk_result.get('relationship_count', 0)}개")
            print(f"  - 더미 테이블: {fk_result.get('dummy_table_count', 0)}개")
            
            # JOIN 결과
            join_result = erd_result['join_result']
            print(f"JOIN 분석 결과:")
            print(f"  - 성공: {join_result.get('success', False)}")
            print(f"  - JOIN 관계: {join_result.get('join_count', 0)}개")
            print(f"  - 분석된 파일: {join_result.get('file_count', 0)}개")
            print(f"  - 더미 테이블: {join_result.get('dummy_table_count', 0)}개")
            
            if join_result.get('joins_found'):
                print(f"\n발견된 JOIN 관계:")
                for join_rel in join_result['joins_found'][:5]:  # 상위 5개만 출력
                    print(f"  - {join_rel['source_table']} {join_rel['join_type']} JOIN {join_rel['target_table']}")
                    if len(join_result['joins_found']) > 5:
                        print(f"  ... 외 {len(join_result['joins_found']) - 5}개")
                        break
            
        else:
            print(f"❌ ERD 생성 실패: {erd_result['error']}")
            print(f"실패 단계: {erd_result.get('stage', 'unknown')}")
    
    except Exception as e:
        print(f"❌ 테스트 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()

def test_components_separately():
    """개별 컴포넌트 테스트"""
    print("\n=== 개별 컴포넌트 테스트 ===\n")
    
    try:
        metadata_engine = OptimizedMetadataEngine(project_path="./project")
        project_id = metadata_engine.create_project("ComponentTest", "./project")
        
        # 1. CSV 로더 테스트
        print("1. CSV 테이블 로더 테스트...")
        from parsers.table_metadata_loader import TableMetadataLoader
        table_loader = TableMetadataLoader(metadata_engine)
        
        csv_result = table_loader.load_tables_from_csv(project_id, "./sample_tables.csv")
        print(f"CSV 로드 결과: {csv_result['success']}")
        if csv_result['success']:
            print(f"  - 로드된 테이블: {csv_result['table_count']}개")
        
        # 2. MyBatis JOIN 분석 테스트
        print("\n2. MyBatis JOIN 분석 테스트...")
        from parsers.mybatis_join_analyzer import MyBatisJoinAnalyzer
        join_analyzer = MyBatisJoinAnalyzer(metadata_engine)
        
        xml_directory = "./project/sampleSrc/src/main/resources/mybatis/mapper"
        if Path(xml_directory).exists():
            join_result = join_analyzer.analyze_multiple_mybatis_files(
                project_id, xml_directory, csv_result.get('loaded_tables', {})
            )
            print(f"JOIN 분석 결과: {join_result['success']}")
            if join_result['success']:
                print(f"  - 발견된 JOIN: {join_result['join_count']}개")
                print(f"  - 처리된 파일: {join_result['file_count']}개")
        else:
            print(f"  - MyBatis XML 디렉토리 없음: {xml_directory}")
        
        print("\n개별 컴포넌트 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 개별 테스트 실패: {e}")

if __name__ == "__main__":
    # 로깅 설정
    setup_logging()
    
    print("ERD 생성기 테스트를 시작합니다...\n")
    
    # 메인 ERD 생성 테스트
    test_erd_generation()
    
    # 개별 컴포넌트 테스트
    test_components_separately()
    
    print("\n테스트 완료!")