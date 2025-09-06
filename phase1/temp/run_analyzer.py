#!/usr/bin/env python3
import sys
import os

# 경로 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_analyzer():
    try:
        print("🚀 SourceAnalyzer 직접 실행 시작")
        print("=" * 60)
        
        # main.py의 SourceAnalyzer 클래스 직접 실행
        from main import SourceAnalyzer
        
        # SourceAnalyzer 인스턴스 생성 (필요한 인자 추가)
        global_config_path = '../config/global_config.yaml'
        phase_config_path = 'config/config.yaml'
        analyzer = SourceAnalyzer(global_config_path, phase_config_path)
        
        print("📋 프로젝트 분석 시작: sampleSrc")
        print("🧹 Clean 모드: True")
        print("🐛 Debug 모드: True")
        print("-" * 60)
        
        # 프로젝트 분석 실행
        import asyncio
        # 절대 경로 사용
        project_root = os.path.abspath('../project/sampleSrc')
        print(f"📁 프로젝트 루트: {project_root}")
        print(f"📁 프로젝트명: sampleSrc")
        asyncio.run(analyzer.analyze_project(project_root, 'sampleSrc', incremental=False))
        
        print("-" * 60)
        print("✅ 분석 완료!")
        
    except Exception as e:
        print(f"❌ 실행 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_analyzer()
