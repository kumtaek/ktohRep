#!/bin/bash
# SourceAnalyzer 실행 스크립트
# PYTHONPATH를 설정하여 phase1/main.py를 실행합니다

# 스크립트가 위치한 디렉토리를 기준으로 경로 설정
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PHASE1_DIR="$SCRIPT_DIR/phase1"

# PYTHONPATH 설정하고 phase1 디렉토리로 이동하여 실행
export PYTHONPATH="$PHASE1_DIR"
cd "$PHASE1_DIR"
python main.py "$@"