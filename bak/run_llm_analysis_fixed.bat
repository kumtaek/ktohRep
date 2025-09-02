@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

echo ====================================
echo   LLM Analysis Tool for SourceAnalyzer
echo ====================================
echo.

REM Get project name from command line or prompt
set PROJECT_NAME=%1
echo "%PROJECT_NAME%"

if "%PROJECT_NAME%"=="" (
    set /p PROJECT_NAME="Enter project name (default: sampleSrc): "
    if "!PROJECT_NAME!"=="" set PROJECT_NAME=sampleSrc
)

REM Get operation type from command line or prompt
set OPERATION=%2
echo "%OPERATION%"

if "%OPERATION%"=="1" set OPERATION=summarize
if "%OPERATION%"=="2" set OPERATION=enhance-db
if "%OPERATION%"=="3" set OPERATION=table-spec
if "%OPERATION%"=="4" set OPERATION=full-analysis

set OPERATION=table-spec

echo.
echo Project Name: %PROJECT_NAME%
echo Operation: %OPERATION%
echo.

REM Check if virtual environment exists
if not exist "venvSrcAnalyzer" (
    echo Virtual environment 'venvSrcAnalyzer' not found.
    echo Please run setup first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venvSrcAnalyzer\Scripts\activate.bat

REM Check if Ollama is running (optional check)
echo Checking Ollama availability...
curl -s http://localhost:11434/api/tags > nul 2>&1
if errorlevel 1 (
    echo Warning: Ollama may not be running at localhost:11434
    echo Make sure Ollama is started with gemma3:1b model available
    echo.
)

REM Run the LLM analysis
echo Starting LLM analysis...
echo Command: python phase1/tools/llm_analyzer.py %OPERATION% --project-name %PROJECT_NAME%
echo.

python phase1/tools/llm_analyzer.py %OPERATION% --project-name %PROJECT_NAME%

REM Check result
if errorlevel 1 (
    echo.
    echo LLM analysis failed. Check the error messages above.
    echo.
    echo Common issues:
    echo   - Ollama is not running: Start Ollama service
    echo   - Model not available: Run 'ollama pull gemma3:1b'
    echo   - Database not initialized: Run analyzer first
    echo   - Project not found: Check project name
) else (
    echo.
    echo LLM analysis completed successfully!
    echo.
    if "%OPERATION%"=="table-spec" (
        echo Table specification saved to: output/%PROJECT_NAME%/table_specification.md
    )
    if "%OPERATION%"=="full-analysis" (
        echo Table specification saved to: output/%PROJECT_NAME%/table_specification.md
        echo Analysis results are now available in the visualization system
    )
)

echo.