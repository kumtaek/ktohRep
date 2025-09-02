@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
REM Quick demo script - Complete functionality demonstration with sampleSrc project
REM Usage: run_quick_demo.bat

echo ========================================
echo  SourceAnalyzer Enhanced Visualization Demo
echo ========================================
echo Project: sampleSrc (test case)
echo Start Time: %date% %time%
echo ========================================

REM 1. Environment check
echo.
echo [Environment Check] Verifying required files...
if not exist "testcase\sampleSrc" (
    echo  testcase\sampleSrc directory not found.
    echo    Sample source code is required.
    goto :error
)

if not exist "venvSrcAnalyzer\Scripts\python.exe" (
    echo  Python virtual environment not configured.
    echo    Please run setup_venv.bat first.
    goto :error
)

if not exist "config\config.yaml" (
    echo  config.yaml file not found.
    goto :error
)

echo  Environment check completed

REM 2. Basic analysis (quick version)
echo.
echo [1/4] Basic source analysis...
call run_complete_analysis.bat sampleSrc

if !errorlevel! neq 0 (
    echo ERROR: Analysis failed
    goto :error
)
echo  Basic analysis completed

REM 3. Enhanced visualization generation
echo.
echo [3/4] Enhanced visualization generation...
call run_enhanced_visualize_only_fixed.bat sampleSrc
if !errorlevel! neq 0 (
    echo ERROR: Visualization generation failed
    goto :error
)

REM 4. Source specification output
echo.
echo [4/4] Source specification generation...
call venvSrcAnalyzer\Scripts\python.exe phase1\tools\llm_analyzer.py source-spec --project-name sampleSrc --output

set OUTPUT_DIR=output\sampleSrc\visualize

echo.
echo ========================================
echo  Demo Completed!
echo ========================================
echo Complete Time: %date% %time%
echo.
echo Generated Files:
if exist "%OUTPUT_DIR%" (
    dir /b "%OUTPUT_DIR%\*.html"
) else (
    echo Output directory not found.
)
echo.
echo Try New Features:
echo    1. Mouse over table = Column detail tooltip
echo    2. Top-right layout button = Force/Dagre switch
echo    3. Search box with table name = Filtering
echo    4. Mouse wheel = Zoom in/out
echo    5. Drag = Move screen
echo.
echo Compare:
echo    - erd_enhanced.html (new enhanced version)
echo    - erd.html (original version)
echo.
echo Please check the differences and provide feedback! 
goto :end

:error
echo.
echo Demo execution failed
echo Please check the following:
echo    1. testcase\sampleSrc directory exists
echo    2. venvSrcAnalyzer virtual environment setup
echo    3. config\config.yaml file exists
echo.
echo Solution:
echo    1. Run setup_venv.bat
echo    2. Check config.yaml settings
echo    3. Prepare sample source code
exit /b 1

:end