@echo off
chcp 65001 > nul
setlocal

REM Check if virtual environment exists
if not exist "venvSrcAnalyzer" (
    echo Virtual environment 'venvSrcAnalyzer' not found.
    echo Please run setup first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venvSrcAnalyzer\Scripts\activate.bat

if "%2"=="--debug" (
    python.exe phase1/tools/llm_analyzer.py summarize --project-name %1 --batch-size 1 --debug
) else (
    python.exe phase1/tools/llm_analyzer.py summarize --project-name %1 --batch-size 1
)
