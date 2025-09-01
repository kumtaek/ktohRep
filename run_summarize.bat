@echo off
REM =====================================================
REM LLM 기반 소스코드 요약 생성 스크립트
REM 분석된 소스코드를 LLM을 사용해 자연어로 요약
REM 사용법: run_summarize.bat <project_name> [--debug]
REM =====================================================

REM UTF-8 인코딩 설정
chcp 65001 > nul
setlocal

REM Python 가상환경 존재 여부 확인
if not exist "venvSrcAnalyzer" (
    echo 가상환경 'venvSrcAnalyzer'을 찾을 수 없습니다.
    echo 먼저 설정을 완료해주세요.
    pause
    exit /b 1
)

REM Python 가상환경 활성화
call venvSrcAnalyzer\Scripts\activate.bat

REM 디버그 모드 확인 및 실행
if "%2"=="--debug" (
    REM 디버그 모드로 LLM 요약 실행 (배치 크기 1, 디버그 출력)
    python.exe phase1/tools/llm_analyzer.py summarize --project-name %1 --batch-size 1 --debug
) else (
    REM 일반 모드로 LLM 요약 실행 (배치 크기 1)
    python.exe phase1/tools/llm_analyzer.py summarize --project-name %1 --batch-size 1
)
