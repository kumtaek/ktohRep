@echo off
REM ================================================================
REM Source Analyzer - Relationship Information Generation Batch File
REM ================================================================
REM This script generates visualizations including all relationship information for the project.
REM 
REM Usage:
REM   run_relationships.bat --project-name [project_name]
REM
REM Examples:
REM   run_relationships.bat --project-name sampleSrc
REM   run_relationships.bat --project-name myProject
REM ================================================================

setlocal enabledelayedexpansion

REM Set project name (default: sampleSrc)
set PROJECT_NAME=%1

:start_analysis

echo ================================================================
echo Source Analyzer - Relationship Information Generation Start
echo Project: %PROJECT_NAME%
echo Time: %date% %time%
echo ================================================================

REM Activate Python virtual environment
if exist "venvSrcAnalyzer\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment...
    call venvSrcAnalyzer\Scripts\activate.bat
) else (
    echo [WARNING] Virtual environment not found. Using system Python.
)

echo.
echo [1/5] ERD diagram generation (table relationships)...
python -m visualize.cli erd --project-name %PROJECT_NAME% --export-html --export-mermaid
if errorlevel 1 (
    echo [ERROR] ERD generation failed
    goto :error
)

echo.
echo [2/5] Dependency graph generation (code relationships)...
python -m visualize.cli graph --project-name %PROJECT_NAME% --export-html --export-mermaid
if errorlevel 1 (
    echo [ERROR] Dependency graph generation failed
    goto :error
)

echo.
echo [3/5] Class diagram generation (class relationships)...
python -m visualize.cli class --project-name %PROJECT_NAME% --export-html --export-mermaid
if errorlevel 1 (
    echo [ERROR] Class diagram generation failed
    goto :error
)

echo.
echo [4/5] Component diagram generation (component relationships)...
python -m visualize.cli component --project-name %PROJECT_NAME% --export-html --export-mermaid
if errorlevel 1 (
    echo [ERROR] Component diagram generation failed
    goto :error
)

echo.
echo [5/5] Relatedness graph generation (overall relationships)...
python -m visualize.cli relatedness --project-name %PROJECT_NAME% --export-html --min-score 0.3
if errorlevel 1 (
    echo [ERROR] Relatedness graph generation failed
    goto :error
)

echo.
echo ================================================================
echo Relationship information generation completed!
echo.
echo Generated file location: .\output\%PROJECT_NAME%\visualize\
echo   - graph.html      : Dependency graph (code relationships)
echo   - erd.html        : Entity relationship diagram (table relationships)
echo   - class.html      : Class diagram (class inheritance/implementation relationships)
echo   - component.html  : Component diagram (module relationships)
echo   - relatedness.html: Relatedness graph (overall associative relationships)
echo   - *.md            : Mermaid diagrams
echo.
echo Open HTML files in web browser to check interactive visualizations.
echo ================================================================
goto :end

:error
echo.
echo ================================================================
echo [ERROR] Error occurred during relationship information generation
echo Please check if project analysis is completed:
echo   .\run_analyzer.bat --project-name %PROJECT_NAME%
echo ================================================================
exit /b 1

:end
endlocal