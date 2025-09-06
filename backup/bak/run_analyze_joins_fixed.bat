@echo off
REM =====================================================
REM Database join relationship analysis script
REM Analyze join relationships between tables using LLM
REM Usage: run_analyze_joins.bat <project_name> [--debug]
REM =====================================================

REM UTF-8 encoding setting
chcp 65001 > nul
setlocal

REM Check if virtual environment exists
if not exist "venvSrcAnalyzer" (
    echo Virtual environment 'venvSrcAnalyzer' not found.
    echo Please complete setup first.
    pause
    exit /b 1
)

REM Activate Python virtual environment
call venvSrcAnalyzer\Scripts\activate.bat

REM Check debug mode and execute join analysis
if "%2"=="--debug" (
    REM Execute join analysis in debug mode (batch size 2, debug output)
    python.exe phase1/tools/llm_analyzer.py analyze-joins --project-name %1 --batch-size 2 --debug
) else (
    REM Execute join analysis in normal mode (batch size 2)
    python.exe phase1/tools/llm_analyzer.py analyze-joins --project-name %1 --batch-size 2
)