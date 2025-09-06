#!/usr/bin/env python3
"""
Java 프로젝트 계층도 분석 리포트 생성기
사용법: python generate_hierarchy_report.py <프로젝트_경로> [출력_경로]
"""

import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

# 상대 임포트
from utils.hierarchy_analyzer import JavaHierarchyAnalyzer
from utils.report_generator import HierarchyReportGenerator

def setup_logging():
    """로깅 설정"""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description='Java 프로젝트 계층도 분석 리포트 생성기',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python generate_hierarchy_report.py ../project/sampleSrc
  python generate_hierarchy_report.py ../project/sampleSrc ../output/hierarchy_report.md
        """
    )
    
    parser.add_argument(
        '--project-name',
        required=True,
        help='분석할 프로젝트명 (예: sampleSrc)'
    )
    
    parser.add_argument(
        '--output',
        help='출력 파일 경로 (기본값: 프로젝트명_계층도분석리포트_yyyymmdd_hms.md)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='상세 로그 출력'
    )
    
    parser.add_argument(
        '--top-n',
        type=int,
        help='계층별 표시할 최대 항목 수 (예: --top-n 5)'
    )
    
    args = parser.parse_args()
    
    # 로깅 설정
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        setup_logging()
    
    logger = logging.getLogger(__name__)
    
    try:
        # 프로젝트 경로 설정
        project_path = Path(f"../project/{args.project_name}")
        if not project_path.exists():
            logger.error(f"프로젝트 경로가 존재하지 않습니다: {project_path}")
            sys.exit(1)
        
        if not project_path.is_dir():
            logger.error(f"프로젝트 경로는 디렉토리여야 합니다: {project_path}")
            sys.exit(1)
        
        # 출력 경로 설정
        if args.output:
            output_path = Path(args.output)
        else:
            # 프로젝트 지침에 따라 ./project/<프로젝트명>/report/ 폴더에 생성
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_dir = Path(f"../project/{args.project_name}/report")
            report_dir.mkdir(parents=True, exist_ok=True)
            output_path = report_dir / f"계층도분석리포트_{timestamp}.md"
        
        logger.info("=" * 60)
        logger.info("Java 프로젝트 계층도 분석 리포트 생성 시작")
        logger.info("=" * 60)
        logger.info(f"프로젝트 경로: {project_path}")
        logger.info(f"출력 경로: {output_path}")
        
        # 1단계: 프로젝트 분석
        logger.info("1단계: 프로젝트 구조 분석 중...")
        analyzer = JavaHierarchyAnalyzer(str(project_path))
        project_structure = analyzer.analyze_project()
        
        # 분석 결과 요약 출력
        summary = analyzer.generate_summary(project_structure)
        logger.info("프로젝트 분석 완료:")
        logger.info(f"  - 총 패키지 수: {summary['package_count']}개")
        logger.info(f"  - 총 클래스 수: {summary['total_classes']}개")
        logger.info(f"  - 총 파일 수: {summary['total_files']}개")
        logger.info(f"  - 총 라인 수: {summary['total_lines']:,}줄")
        
        # 2단계: 리포트 생성
        logger.info("2단계: 마크다운 리포트 생성 중...")
        generator = HierarchyReportGenerator()
        report_content = generator.generate_report(project_structure, str(output_path), args.top_n)
        
        # 3단계: 완료 보고
        logger.info("3단계: 리포트 생성 완료!")
        logger.info(f"생성된 리포트: {output_path}")
        logger.info(f"리포트 크기: {len(report_content):,} 문자")
        
        # 성공 메시지
        print("\n" + "=" * 60)
        print("🎉 계층도 분석 리포트 생성 완료!")
        print("=" * 60)
        print(f"📁 프로젝트: {project_path.name}")
        print(f"📊 분석 결과: {summary['total_classes']}개 클래스, {summary['total_lines']:,}줄")
        print(f"📄 생성된 리포트: {output_path}")
        print(f"⏱️ 분석 소요 시간: {datetime.now() - project_structure.analysis_time}")
        print("=" * 60)
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("사용자에 의해 중단되었습니다.")
        return 1
        
    except Exception as e:
        logger.error(f"오류가 발생했습니다: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
