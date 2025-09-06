#!/usr/bin/env python3
"""
AI 기반 소스코드 분석 리포트 생성기
사용법: python generate_ai_report.py <프로젝트_경로> [분석_유형] [모델_타입]
"""

import sys
import argparse
import logging
import yaml
from pathlib import Path
from datetime import datetime

# 상대 임포트
from utils.ai_analyzer import AIAnalyzer, AnalysisRequest
from utils.ai_report_generator import AIReportGenerator

def load_config(config_path: str = None) -> dict:
    """설정 파일 로드"""
    if config_path and Path(config_path).exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    # 기본 설정
    return {
        'local_ollama_url': 'http://localhost:11434',
        'remote_api_url': None,
        'remote_api_key': None
    }

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
        description='AI 기반 소스코드 분석 리포트 생성기',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python generate_ai_report.py ../project/sampleSrc
  python generate_ai_report.py ../project/sampleSrc erd local_gemma
  python generate_ai_report.py ../project/sampleSrc comprehensive remote_qwen
  python generate_ai_report.py ../project/sampleSrc --custom-prompt "보안 취약점에 집중해서 분석해주세요"
        """
    )
    
    parser.add_argument(
        '--project-name',
        help='분석할 프로젝트명 (예: sampleSrc)'
    )
    
    parser.add_argument(
        'analysis_type',
        nargs='?',
        choices=['erd', 'architecture', 'code_quality', 'security', 'comprehensive'],
        default='comprehensive',
        help='분석 유형 (기본값: comprehensive)'
    )
    
    parser.add_argument(
        'model_type',
        nargs='?',
        choices=['local_gemma', 'remote_qwen'],
        default='local_gemma',
        help='사용할 AI 모델 (기본값: local_gemma)'
    )
    
    parser.add_argument(
        '--config', '-c',
        help='설정 파일 경로 (기본값: ./config/ai_config.yaml)'
    )
    
    parser.add_argument(
        '--output-format',
        choices=['markdown', 'html', 'json'],
        default='markdown',
        help='출력 형식 (기본값: markdown)'
    )
    
    parser.add_argument(
        '--custom-prompt',
        help='사용자 정의 분석 프롬프트'
    )
    
    parser.add_argument(
        '--output-path',
        help='출력 파일 경로 (기본값: 프로젝트명/report/ai_analysis_yyyymmdd_hms.md)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='상세 로그 출력'
    )
    
    parser.add_argument(
        '--test-connection',
        action='store_true',
        help='AI 모델 연결 테스트만 실행'
    )
    
    args = parser.parse_args()
    
    # 로깅 설정
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        setup_logging()
    
    logger = logging.getLogger(__name__)
    
    try:
        # 설정 파일 로드
        config_path = args.config or "./config/ai_config.yaml"
        config = load_config(config_path)
        
        # AI 분석기 초기화
        analyzer = AIAnalyzer(config)
        
        # 연결 테스트 모드
        if args.test_connection:
            logger.info("AI 모델 연결 테스트 시작...")
            
            local_ok = analyzer.test_connection('local_gemma')
            remote_ok = analyzer.test_connection('remote_qwen')
            
            print("\n" + "=" * 50)
            print("🔍 AI 모델 연결 테스트 결과")
            print("=" * 50)
            print(f"🤖 로컬 Gemma (Ollama): {'✅ 연결됨' if local_ok else '❌ 연결 실패'}")
            print(f"🌐 원격 Qwen: {'✅ 연결됨' if remote_ok else '❌ 연결 실패'}")
            
            if not local_ok:
                print("\n💡 로컬 Gemma 연결 실패 시:")
                print("   1. Ollama 서비스가 실행 중인지 확인")
                print("   2. gemma3:1b 모델이 설치되어 있는지 확인")
                print("   3. http://localhost:11434 접근 가능한지 확인")
            
            if not remote_ok:
                print("\n💡 원격 Qwen 연결 실패 시:")
                print("   1. 설정 파일에 API URL과 키가 올바르게 설정되어 있는지 확인")
                print("   2. 네트워크 연결 상태 확인")
                print("   3. API 키의 유효성 확인")
            
            print("=" * 50)
            return 0
        
        # 프로젝트명이 없으면 오류
        if not args.project_name:
            logger.error("프로젝트명이 필요합니다.")
            parser.print_help()
            sys.exit(1)
        
        # 프로젝트 경로 설정
        project_path = Path(f"../project/{args.project_name}")
        if not project_path.exists():
            logger.error(f"프로젝트 경로가 존재하지 않습니다: {project_path}")
            sys.exit(1)
        
        if not project_path.is_dir():
            logger.error(f"프로젝트 경로는 디렉토리여야 합니다: {project_path}")
            sys.exit(1)
        
        # 출력 경로 설정
        if args.output_path:
            output_path = Path(args.output_path)
        else:
            # 프로젝트 지침에 따라 ./project/<프로젝트명>/report/ 폴더에 생성
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_dir = Path(f"../project/{args.project_name}/report")
            report_dir.mkdir(parents=True, exist_ok=True)
            output_path = report_dir / f"ai_analysis_{timestamp}.md"
        
        logger.info("=" * 60)
        logger.info("AI 기반 소스코드 분석 리포트 생성 시작")
        logger.info("=" * 60)
        logger.info(f"프로젝트 경로: {project_path}")
        logger.info(f"분석 유형: {args.analysis_type}")
        logger.info(f"AI 모델: {args.model_type}")
        logger.info(f"출력 형식: {args.output_format}")
        logger.info(f"출력 경로: {output_path}")
        
        # AI 분석 요청 생성
        request = AnalysisRequest(
            project_path=str(project_path),
            analysis_type=args.analysis_type,
            model_type=args.model_type,
            output_format=args.output_format,
            custom_prompt=args.custom_prompt
        )
        
        # 1단계: AI 분석 실행
        logger.info("1단계: AI 모델로 소스코드 분석 중...")
        result = analyzer.analyze_project(request)
        
        if not result.success:
            logger.error(f"AI 분석 실패: {result.error_message}")
            sys.exit(1)
        
        # 2단계: 리포트 생성
        logger.info("2단계: AI 분석 리포트 생성 중...")
        generator = AIReportGenerator()
        report_content = generator.generate_report(result, str(output_path))
        
        # 3단계: 완료 보고
        logger.info("3단계: AI 분석 리포트 생성 완료!")
        logger.info(f"생성된 리포트: {output_path}")
        logger.info(f"리포트 크기: {len(report_content):,} 문자")
        logger.info(f"AI 처리 시간: {result.processing_time:.2f}초")
        
        # 성공 메시지
        print("\n" + "=" * 60)
        print("🎉 AI 기반 소스코드 분석 리포트 생성 완료!")
        print("=" * 60)
        print(f"📁 프로젝트: {project_path.name}")
        print(f"🔍 분석 유형: {args.analysis_type}")
        print(f"🤖 사용 모델: {args.model_type}")
        print(f"📄 생성된 리포트: {output_path}")
        print(f"⏱️ AI 처리 시간: {result.processing_time:.2f}초")
        print(f"📊 프로젝트 정보: {result.metadata.get('project_info', {}).get('file_count', 0)}개 파일")
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
