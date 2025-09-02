@echo off
chcp 65001 >nul
REM SourceAnalyzer Complete Analysis and Visualization Script
REM Usage: run_complete_analysis.bat [project_name] [source_path]

setlocal enabledelayedexpansion

REM Default settings
set PROJECT_NAME=%1
set SOURCE_PATH=%2

if "%PROJECT_NAME%"=="" set PROJECT_NAME=sampleSrc
if "%SOURCE_PATH%"=="" set SOURCE_PATH=testcase\sampleSrc

echo ========================================
echo SourceAnalyzer Complete Analysis and Visualization
echo ========================================
echo Project Name: %PROJECT_NAME%
echo Source Path: %SOURCE_PATH%
echo Start Time: %date% %time%
echo ========================================

REM 1. Basic analysis start
echo.
echo [1/7] Basic source analysis...
call run_analyzer.bat --project-name %PROJECT_NAME%
if !errorlevel! neq 0 (
    echo ERROR: Basic analysis failed
    goto :error
)
echo  Basic analysis completed

REM 2. Relatedness calculation
echo.
echo [2/7] Relatedness calculation...
call venvSrcAnalyzer\Scripts\python.exe phase1\scripts\calculate_relatedness.py --project-name %PROJECT_NAME%
if !errorlevel! neq 0 (
    echo ERROR: Relatedness calculation failed
    goto :error
)
echo  Relatedness calculation completed

rem    echo.REM 3. LLM ��� �� ��ȭ
rem    echo.
rem    echo [3/7] LLM ��� �� ��Ÿ������ ��ȭ ��... summarize
rem    call "venvSrcAnalyzer\Scripts\python.exe" phase1/tools/llm_analyzer.py summarize --project-name %PROJECT_NAME% --batch-size 3
rem    if !errorlevel! neq 0 (
rem        echo WARNING: LLM ��� ���� (���û���)
rem    )
rem    
rem    echo.
rem    echo. ��Ÿ������ ��ȭ - enhance-db
rem    call "venvSrcAnalyzer\Scripts\python.exe" phase1/tools/llm_analyzer.py enhance-db --project-name %PROJECT_NAME% --batch-size 3
rem    if !errorlevel! neq 0 (
rem        echo WARNING: ��Ÿ������ ��ȭ ���� (���û���)
rem    )
rem    echo  LLM ó�� �Ϸ�
rem    
rem    echo.
rem    echo.
rem    echo.REM 4. ���� �м�
rem    echo.
rem    echo [4/7] SQL ���� ���� �м� ��...
rem    call "venvSrcAnalyzer\Scripts\python.exe" phase1/tools/llm_analyzer.py analyze-joins --project-name %PROJECT_NAME% --batch-size 2
rem    if !errorlevel! neq 0 (
rem        echo WARNING: ���� �м� ���� (���û���)
rem    )
rem    echo  ���� �м� �Ϸ�

call run_llm_analysis.bat %PROJECT_NAME%

REM 5. Basic visualization generation (ERD, dependency graph, component)
echo.
echo [5/7] Basic visualization generation...
call venvSrcAnalyzer\Scripts\python.exe -m visualize all --project-name %PROJECT_NAME% --export-html "" --export-mermaid ""
if !errorlevel! neq 0 (
    echo ERROR: Basic visualization generation failed
    goto :error
)
echo  Basic visualization completed

goto end




REM 6. Enhanced ERD generation (new feature)
echo.
echo [6/7] Enhanced ERD generation...
call venvSrcAnalyzer\Scripts\python.exe -c "
from visualize.builders.erd_enhanced import build_enhanced_erd_json
from visualize.renderers.enhanced_renderer_factory import EnhancedVisualizationFactory
import yaml
import json
from pathlib import Path

# Config loading
config_path = Path('config/config.yaml')
config = {}
if config_path.exists():
    with open(config_path, 'r', encoding='utf-8') as f:
        raw = f.read().replace('{project_name}', '%PROJECT_NAME%')
        config = yaml.safe_load(raw) or {}

# ERD data generation
data = build_enhanced_erd_json(config, 1, '%PROJECT_NAME%')

# Enhanced renderer HTML generation
factory = EnhancedVisualizationFactory()
html = factory.create_enhanced_erd(data)

# Output directory creation and file write
output_dir = Path('output/%PROJECT_NAME%/visualize')
output_dir.mkdir(parents=True, exist_ok=True)

with open(output_dir / 'erd_enhanced.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(' Enhanced ERD generation completed: ' + str(output_dir / 'erd_enhanced.html'))
"
if !errorlevel! neq 0 (
    echo WARNING: Enhanced ERD generation failed, using basic ERD
)

REM 7. Sequence diagram generation (main methods)
echo.
echo [7/7] Sequence diagram generation...
call venvSrcAnalyzer\Scripts\python.exe -m visualize sequence --project-name %PROJECT_NAME% --depth 3
if !errorlevel! neq 0 (
    echo WARNING: Sequence diagram generation failed
)
echo  Sequence diagram completed

REM �Ϸ� ������ ����
echo.
echo ========================================
echo  ��� �м� �� �ð�ȭ �Ϸ�!
echo ========================================
echo �Ϸ�ð�: %date% %time%
echo.
echo  ������ ���ϵ�:
echo    output\%PROJECT_NAME%\visualize\
echo    ������ graph.html              (������ �׷���)
echo    ������ erd.html               (�⺻ ERD)
echo    ������ erd_enhanced.html      (���� ERD - ���ο�!)
echo    ������ components.html        (������Ʈ ���̾�׷�)
echo    ������ class.html            (Ŭ���� ���̾�׷�)
echo    ������ relatedness.html      (���輺 �׷���)
echo    ������ *_sequence.html       (������ ���̾�׷���)
echo.
echo  ��õ Ȯ�� ����:
echo    1. erd_enhanced.html      (�÷� ����, ��ħ ����)
echo    2. graph.html            (��ü ������ ����)
echo    3. components.html       (������Ʈ�� ����)
echo    4. relatedness.html      (���輺 �м�)
echo.
echo  ���������� ���ϵ��� ���� Ȯ���غ�����!
goto :end

:error
echo.
echo  ���� �߻����� ��ũ��Ʈ�� �ߴܵǾ����ϴ�.
echo �α׸� Ȯ���ϰ� ������ �ذ��� �� �ٽ� �������ּ���.
exit /b 1

:end
echo.