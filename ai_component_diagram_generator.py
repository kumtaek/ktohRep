#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 컴포넌트 다이어그램 생성기
LLM을 이용하여 프로젝트 소스를 분석하고 컴포넌트 다이어그램을 생성합니다.
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.ai_component_analyzer import AIComponentAnalyzer

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description='AI 컴포넌트 다이어그램 생성기')
    parser.add_argument('--project-path', '-p', 
                       default='../project/sampleSrc',
                       help='분석할 프로젝트 경로 (기본값: ../project/sampleSrc)')
    parser.add_argument('--output-path', '-o',
                       help='출력 파일 경로 (기본값: ../project/<프로젝트명>/report/)')
    parser.add_argument('--config', '-c',
                       default='config/ai_config.yaml',
                       help='AI 설정 파일 경로 (기본값: config/ai_config.yaml)')
    
    args = parser.parse_args()
    
    # 프로젝트 경로 검증
    if not os.path.exists(args.project_path):
        print(f"오류: 프로젝트 경로가 존재하지 않습니다: {args.project_path}")
        sys.exit(1)
    
    # 출력 경로 설정
    if args.output_path:
        output_dir = args.output_path
    else:
        project_name = os.path.basename(args.project_path)
        output_dir = f"../project/{project_name}/report"
    
    # 출력 디렉토리 생성
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        print("=" * 60)
        print("AI 컴포넌트 다이어그램 생성기 시작")
        print("=" * 60)
        
        # AI 분석기 초기화
        print(f"AI 설정 파일: {args.config}")
        analyzer = AIComponentAnalyzer(args.config)
        
        # 컴포넌트 다이어그램 생성
        print(f"프로젝트 분석: {args.project_path}")
        component_diagram = analyzer.generate_component_diagram(args.project_path)
        
        if not component_diagram:
            print("오류: 컴포넌트 다이어그램 생성 실패")
            sys.exit(1)
        
        # 파일명 생성 (타임스탬프 포함)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = os.path.basename(args.project_path)
        filename = f"AI_컴포넌트다이어그램_{timestamp}.md"
        output_file = os.path.join(output_dir, filename)
        
        # 파일 저장
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(component_diagram)
        
        print(f"컴포넌트 다이어그램 생성 완료: {output_file}")
        print("=" * 60)
        
        # 생성된 내용 미리보기
        print("생성된 내용 미리보기:")
        print("-" * 40)
        lines = component_diagram.split('\n')
        for i, line in enumerate(lines[:20]):  # 처음 20줄만 출력
            print(line)
        if len(lines) > 20:
            print(f"... (총 {len(lines)}줄 중 20줄만 표시)")
        print("-" * 40)
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

