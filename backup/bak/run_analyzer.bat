@echo off
REM =====================================================
REM Source analyzer execution script
REM Main script for analyzing project source code and generating metadata
REM Usage: run_analyzer.bat <project_name> [options]
REM =====================================================

REM UTF-8 encoding setting
chcp 65001 >nul
setlocal

REM Activate Python virtual environment
call "%~dp0venvSrcAnalyzer\Scripts\activate.bat"

REM Add project root to Python path
set "PYTHONPATH=%~dp0"

REM Execute main analysis script
python.exe "%~dp0phase1\main.py" --project-name %1 %*

endlocal