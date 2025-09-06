#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
컴포넌트 다이어그램 보고서 생성기
메타정보를 기반으로 프로젝트 컴포넌트 구조를 분석하여 마크다운 보고서를 생성합니다.
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
import logging

# 현재 스크립트의 디렉토리를 Python 경로에 추가
script_dir = Path(__file__).parent
sys.path.append(str(script_dir))

from utils.component_analyzer import ComponentAnalyzer
from utils.component_report_generator import ComponentReportGenerator

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='컴포넌트 명세서 생성기')
    parser.add_argument('--project-name', required=True, help='분석할 프로젝트명 (예: sampleSrc)')
    parser.add_argument('--output', help='출력 파일 경로 (기본값: 프로젝트/report/컴포넌트명세서_YYYYMMDD_HHMMSS.md)')
    parser.add_argument('--top-n', type=int, help='계층별 표시할 최대 항목 수 (예: --top-n 5)')
    
    args = parser.parse_args()
    
    try:
        # 프로젝트 경로 설정
        project_path = f"../project/{args.project_name}"
        
        if not os.path.exists(project_path):
            logger.error(f"프로젝트 경로가 존재하지 않습니다: {project_path}")
            sys.exit(1)
        
        # 출력 파일 경로 설정
        if args.output:
            output_path = args.output
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"{project_path}/report/컴포넌트명세서_{timestamp}.md"
        
        # 출력 디렉토리 생성
        output_dir = Path(output_path).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"컴포넌트 분석 시작: {args.project_name}")
        logger.info(f"프로젝트 경로: {project_path}")
        logger.info(f"출력 파일: {output_path}")
        
        # 컴포넌트 분석
        analyzer = ComponentAnalyzer(project_path)
        project_structure = analyzer.analyze_components()
        
        # 보고서 생성
        report_generator = ComponentReportGenerator()
        report_content = report_generator.generate_report(project_structure, args.top_n)
        
        # 파일 저장
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        logger.info(f"컴포넌트 보고서 생성 완료: {len(report_content)} 문자")
        logger.info(f"출력 파일: {output_path}")
        
        # 생성된 파일 정보 출력
        print(f"\n✅ 컴포넌트 명세서 생성 완료!")
        print(f"📁 파일: {output_path}")
        print(f"📊 컴포넌트 수: {project_structure.total_components}개")
        print(f"🏗️ 계층 수: {len(project_structure.layers)}개")
        print(f"📝 파일 크기: {len(report_content):,} 문자")
        
    except Exception as e:
        logger.error(f"오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
