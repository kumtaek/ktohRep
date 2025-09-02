@echo off
chcp 65001 >nul
REM Enhanced visualization generation script (analysis already completed)
REM Usage: run_enhanced_visualize_only.bat [project_name]

setlocal enabledelayedexpansion

set PROJECT_NAME=%1
if "%PROJECT_NAME%"=="" set PROJECT_NAME=sampleSrc

echo ========================================
echo Enhanced Visualization Generation (based on analysis data)
echo ========================================
echo Project Name: %PROJECT_NAME%
echo Start Time: %date% %time%
echo ========================================

REM 1. Basic visualization generation
echo.
echo [1/3] Basic visualization generation...
echo  Multiple visualization types will be generated sequentially. This may take some time...
echo.
echo  Dependency graph generation...
call venvSrcAnalyzer\Scripts\python.exe -m visualize graph --project-name %PROJECT_NAME% --export-html "" --export-mermaid ""
echo.
echo  ERD generation...
call venvSrcAnalyzer\Scripts\python.exe -m visualize erd --project-name %PROJECT_NAME% --export-html "" --export-mermaid ""
echo.
echo  Component diagram generation...
call venvSrcAnalyzer\Scripts\python.exe -m visualize component --project-name %PROJECT_NAME% --export-html "" --export-mermaid ""
echo.
echo  Class diagram generation...
call venvSrcAnalyzer\Scripts\python.exe -m visualize class --project-name %PROJECT_NAME% --export-html "" --export-mermaid ""
echo.
echo  Relatedness analysis... (Takes longest due to LLM processing)
call venvSrcAnalyzer\Scripts\python.exe -m visualize relatedness --project-name %PROJECT_NAME% --export-html "" --export-mermaid ""
if !errorlevel! neq 0 (
    echo ERROR: Basic visualization generation failed
    goto :error
)
echo  Basic visualization completed

REM 2. Enhanced ERD generation
echo.
echo [2/3] Enhanced ERD generation...
call venvSrcAnalyzer\Scripts\python.exe generate_enhanced_erd.py --project-name %PROJECT_NAME%

REM 3. Sequence diagram generation
echo.
echo [3/3] Sequence diagram generation...
call venvSrcAnalyzer\Scripts\python.exe -m visualize sequence --project-name %PROJECT_NAME% --depth 2 --max-nodes 50
if !errorlevel! neq 0 (
    echo WARNING: Sequence diagram generation failed
)
echo  Sequence diagram completed

REM Completion report
echo.
echo ========================================
echo  Enhanced Visualization Generation Completed!
echo ========================================
echo Complete Time: %date% %time%
echo.
echo  Generated file location:
dir /b output\%PROJECT_NAME%\visualize\*.html 2>nul
echo.
echo  New features:
echo    • erd_enhanced.html: Column detail tooltips
echo    • Overlap prevention layout
echo    • 3 layout algorithms (Force/Hierarchical/Grid)
echo    • Enhanced interaction (zoom, pan, search)
echo.
echo  Usage:
echo    1. Open erd_enhanced.html in browser
echo    2. Mouse over tables for detailed info
echo    3. Use layout buttons for optimal arrangement
echo    4. Search table names in search box
goto :end

:error
echo.
echo  Error occurred
echo Check if existing analysis data exists.
echo If not, run run_complete_analysis.bat first.
exit /b 1

:end
echo.