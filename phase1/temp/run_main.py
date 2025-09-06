#!/usr/bin/env python3
import sys
import os
import subprocess

# 경로 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_main():
    try:
        # main.py 실행
        cmd = [
            sys.executable, 
            'main.py', 
            '--project-name', 'sampleSrc', 
            '--clean', 
            '--debug'
        ]
        
        print("🚀 main.py 실행 중...")
        print(f"명령어: {' '.join(cmd)}")
        
        # subprocess로 실행
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
        
        print("📤 표준 출력:")
        print(result.stdout)
        
        if result.stderr:
            print("📤 표준 에러:")
            print(result.stderr)
        
        print(f"📊 종료 코드: {result.returncode}")
        
    except Exception as e:
        print(f"❌ 실행 오류: {e}")

if __name__ == "__main__":
    run_main()




