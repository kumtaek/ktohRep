import sys
import os
sys.path.append('phase1')

# 상대 import 문제 해결을 위해 phase1을 현재 디렉토리로 설정
os.chdir('phase1')

from main import SourceAnalyzer
import yaml
import asyncio

# 설정 로드
with open('config/config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 분석기 생성 및 실행
analyzer = SourceAnalyzer(config)
asyncio.run(analyzer.analyze_project('sampleSrc'))

