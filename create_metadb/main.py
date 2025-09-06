"""
Create MetaDB 메인 엔트리 포인트

신규입사자 지원을 위한 최적화된 메타정보 생성 시스템의 메인 실행 파일입니다.
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# create_metadb 루트를 Python 경로에 추가
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# 상대 import 문제 해결을 위한 모듈 경로 설정
import create_metadb.core.metadata_engine as metadata_engine
import create_metadb.config as config_module

def setup_logging(verbose: bool = False):
    """로깅 설정"""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/create_metadb.log', encoding='utf-8')
        ]
    )

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description='Create MetaDB - 신규입사자 지원을 위한 최적화된 메타정보 생성 시스템'
    )
    
    parser.add_argument(
        '--project-name', 
        required=True,
        help='프로젝트명 (예: sampleSrc)'
    )
    
    parser.add_argument(
        '--clean',
        action='store_true',
        help='메타DB 전체 초기화 (초기화만 하고 종료)'
    )
    
    parser.add_argument(
        '--del-clear',
        action='store_true',
        help='삭제된 데이터만 정리 (del_yn=\'Y\' 건만 삭제, 삭제만 하고 종료)'
    )
    
    parser.add_argument(
        '--enable-llm',
        action='store_true',
        help='LLM 요약 생성 활성화'
    )
    
    parser.add_argument(
        '--enhance-sql-analysis',
        action='store_true',
        help='SQL 조인 분석 강화'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='상세 로그 출력'
    )
    
    parser.add_argument(
        '--compare',
        action='store_true',
        help='기존 시스템과 비교'
    )
    
    args = parser.parse_args()
    
    # 로깅 설정
    setup_logging(args.verbose)
    logger = logging.getLogger('CreateMetaDB')
    
    try:
        logger.info(f"Create MetaDB 시작: {args.project_name}")
        
        # 환경 변수 설정
        os.environ['CREATE_METADB_PATH'] = str(current_dir)
        
        # 설정 로드
        config = config_module.load_config()
        
        # LLM 설정 업데이트
        if args.enable_llm:
            config['llm']['enabled'] = True
            logger.info("LLM 기능 활성화")
        
        # SQL 분석 강화 설정
        if args.enhance_sql_analysis:
            config['sql_analysis']['use_llm_for_complex_queries'] = True
            logger.info("SQL 조인 분석 강화 활성화")
        
        # 메타정보 엔진 초기화
        engine = metadata_engine.MetadataEngine(args.project_name)
        
        # 실행 모드에 따른 처리
        if args.clean:
            logger.info("메타DB 전체 초기화 모드")
            result = engine.generate_metadata(clean_mode=True)
            print(f"✅ {result['message']}")
            
        elif args.del_clear:
            logger.info("삭제된 데이터 정리 모드")
            result = engine.generate_metadata(del_clear_mode=True)
            print(f"✅ {result['message']}")
            
        else:
            logger.info("메타정보 생성 모드")
            result = engine.generate_metadata()
            
            if result['status'] == 'success':
                stats = result['stats']
                print(f"✅ 메타정보 생성 완료!")
                print(f"   📁 처리된 파일: {stats.get('processed_files', 0)}개")
                print(f"   📦 생성된 청크: {stats.get('chunks_created', 0)}개")
                print(f"   🔗 생성된 관계: {stats.get('relationships_created', 0)}개")
                print(f"   🏷️ 비즈니스 분류: {stats.get('business_classifications', 0)}개")
                print(f"   🤖 LLM 요약: {stats.get('llm_summaries', 0)}개")
                
                if stats.get('deleted_files', 0) > 0:
                    print(f"   🗑️ 삭제된 파일: {stats['deleted_files']}개")
                    
            elif result['status'] == 'no_changes':
                print(f"ℹ️ {result['message']}")
            else:
                print(f"❌ 오류: {result.get('message', '알 수 없는 오류')}")
        
        # 기존 시스템과 비교 (옵션)
        if args.compare:
            logger.info("기존 시스템과 비교 분석")
            # TODO: 기존 phase1 시스템과 비교 로직 구현
            print("📊 기존 시스템과 비교 분석은 추후 구현 예정입니다.")
        
        logger.info("Create MetaDB 완료")
        
    except KeyboardInterrupt:
        logger.info("사용자에 의해 중단됨")
        print("❌ 사용자에 의해 중단되었습니다.")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"실행 중 오류 발생: {e}")
        print(f"❌ 오류 발생: {e}")
        sys.exit(1)
    
    finally:
        # 리소스 정리
        if 'engine' in locals():
            engine.db_manager.disconnect()

if __name__ == '__main__':
    main()
