#!/usr/bin/env python3
import sys
import os

# 경로 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def execute_main():
    try:
        # main.py의 SourceAnalyzer 클래스 직접 실행
        from main import SourceAnalyzer
        
        print("🚀 SourceAnalyzer 직접 실행")
        print("=" * 50)
        
        # SourceAnalyzer 인스턴스 생성
        analyzer = SourceAnalyzer()
        
        # 프로젝트 분석 실행
        analyzer.analyze_project('sampleSrc', clean=True, debug=True)
        
        print("✅ 분석 완료")
        
    except Exception as e:
        print(f"❌ 실행 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    execute_main()




