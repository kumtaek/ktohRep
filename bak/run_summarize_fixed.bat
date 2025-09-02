@echo off
REM =====================================================
REM LLM-based source code summarization script
REM Summarize analyzed source code using LLM in natural language
REM Usage: run_summarize.bat <project_name> [--debug]
REM =====================================================

REM UTF-8 encoding setting
REM chcp 65001 > nul
setlocal

REM Check if virtual environment exists
if not exist "venvSrcAnalyzer" (
    echo Virtual environment 'venvSrcAnalyzer' not found.
    echo Please complete setup first.
    pause
    exit /b 1
)

REM Activate Python virtual environment
call venvSrcAnalyzer\Scripts\activate

REM Check debug mode and execute
if "%2"=="--debug" (
    REM Execute LLM summary in debug mode (batch size 1, debug output)
    python.exe phase1/tools/llm_analyzer.py summarize --project-name %1 --batch-size 1 --debug
) else (
    REM Execute LLM summary in normal mode (batch size 1)
    python.exe phase1/tools/llm_analyzer.py summarize --project-name %1 --batch-size 1
)

endlocak