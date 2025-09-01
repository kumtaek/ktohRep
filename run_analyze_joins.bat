@echo off
REM =====================================================
REM 데이터베이스 조인 관계 분석 스크립트
REM 테이블 간의 조인 관계를 LLM을 통해 분석
REM 사용법: run_analyze_joins.bat <project_name> [--debug]
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

REM 디버그 모드 확인 및 조인 분석 실행
if "%2"=="--debug" (
    REM 디버그 모드로 조인 분석 실행 (배치 크기 2, 디버그 출력)
    python.exe phase1/tools/llm_analyzer.py analyze-joins --project-name %1 --batch-size 2 --debug
) else (
    REM 일반 모드로 조인 분석 실행 (배치 크기 2)
    python.exe phase1/tools/llm_analyzer.py analyze-joins --project-name %1 --batch-size 2
)
