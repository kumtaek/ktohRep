@echo off
REM =====================================================
REM Source analysis result visualization generation script
REM Generate ERD, class diagrams, dependency graphs, etc.
REM Usage: run_visualize.bat <diagram_type> <project_name> [options]
REM =====================================================

REM UTF-8 encoding setting
chcp 65001 >nul
setlocal enabledelayedexpansion

echo =========================================
echo  SourceAnalyzer Visualization Tool
echo =========================================
echo Project: %1
echo Start Time: %date% %time%
echo =========================================
echo.

REM Activate Python virtual environment
echo [1/3] Activating virtual environment...
call "%~dp0venvSrcAnalyzer\Scripts\activate.bat"
echo Virtual environment activated
echo.

REM Add project root to Python path to prevent import errors
echo [2/3] Setting up environment...
set PYTHONPATH=%~dp0
echo Environment setup completed
echo.

REM Execute visualization module, passing all arguments
echo [3/3] Starting visualization generation...
echo LLM processing may take a long time. Please wait...
echo Processing... (Ctrl+C to abort)
echo.

python -m visualize.cli %1 --project-name %2 %*

if !errorlevel! equ 0 (
    echo.
    echo Visualization generation completed!
    echo Completion Time: %date% %time%
) else (
    echo.
    echo Visualization generation failed (Error code: !errorlevel!)
)

endlocal