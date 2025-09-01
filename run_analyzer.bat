@echo off
REM =====================================================
REM 소스 분석기 실행 스크립트
REM 프로젝트 소스코드를 분석하고 메타데이터를 생성하는 메인 스크립트
REM 사용법: run_analyzer.bat <project_name> [options]
REM =====================================================

REM UTF-8 인코딩 설정
chcp 65001 >nul
setlocal

REM Python 가상환경 활성화
call "%~dp0venvSrcAnalyzer\Scripts\activate.bat"

REM 프로젝트 루트를 Python 경로에 추가
set "PYTHONPATH=%~dp0"

REM 메인 분석 스크립트 실행
python.exe "%~dp0phase1\main.py" --project-name %1 %*

endlocal