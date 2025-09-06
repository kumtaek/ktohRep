#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 기반 컴포넌트 다이어그램 생성 메인 스크립트
- sampleSrc 프로젝트 분석
- AI를 활용한 컴포넌트 분석
- 마크다운 형식의 상세한 다이어그램 생성
"""

import os
import sys
import logging
from pathlib import Path

# 현재 스크립트의 디렉토리를 Python 경로에 추가
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from ai_component_diagram_generator import AIComponentDiagramGenerator

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('../logs/ai_component_diagram.log', encoding='utf-8')
    ]
)

# 모든 로거의 레벨을 DEBUG로 설정
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger('ai_component_analyzer').setLevel(logging.DEBUG)
logging.getLogger('ai_model_client').setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI 기반 컴포넌트 다이어그램 생성기')
    parser.add_argument('--project-name', required=True, help='분석할 프로젝트명 (예: sampleSrc)')
    parser.add_argument('--output', help='출력 디렉토리 (기본값: 프로젝트/report)')
    
    args = parser.parse_args()
    
    try:
        # 프로젝트 경로 설정 (동적)
        project_path = f"../project/{args.project_name}"
        
        logger.info("=" * 60)
        logger.info("AI 기반 컴포넌트 다이어그램 생성 시작")
        logger.info("=" * 60)
        
        # 프로젝트 경로 확인
        if not Path(project_path).exists():
            logger.error(f"프로젝트 경로가 존재하지 않습니다: {project_path}")
            logger.error(f"사용 가능한 프로젝트: {list(Path('../project').glob('*'))}")
            return
        
        logger.info(f"분석 대상 프로젝트: {project_path}")
        
        # AI 컴포넌트 다이어그램 생성기 초기화
        generator = AIComponentDiagramGenerator(project_path)
        
        # 다이어그램 생성
        logger.info("컴포넌트 다이어그램 생성 중...")
        output_file = generator.generate_diagram()
        
        logger.info("=" * 60)
        logger.info("✅ AI 컴포넌트 다이어그램 생성 완료!")
        logger.info(f"📁 출력 파일: {output_file}")
        logger.info("=" * 60)
        
        # 생성된 파일 정보 출력
        output_path = Path(output_file)
        if output_path.exists():
            file_size = output_path.stat().st_size
            logger.info(f"📊 파일 크기: {file_size:,} bytes")
            
            # 파일 내용 미리보기
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                logger.info(f"📝 총 라인 수: {len(lines)}줄")
                
                # 주요 섹션 확인
                sections = [line for line in lines if line.startswith('#')]
                logger.info(f"📋 주요 섹션: {len(sections)}개")
                for section in sections[:5]:  # 최대 5개
                    logger.info(f"  - {section}")
        
        print("\n" + "=" * 60)
        print("🎉 AI 컴포넌트 다이어그램 생성이 완료되었습니다!")
        print(f"📁 결과 파일: {output_file}")
        print("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ 다이어그램 생성 실패: {e}")
        logger.exception("상세 오류 정보:")
        raise

if __name__ == "__main__":
    main()
