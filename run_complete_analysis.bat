@echo off
REM SourceAnalyzer ���� �м� �� �ð�ȭ ���� ��ũ��Ʈ
REM ����: run_complete_analysis.bat [������Ʈ��] [�ҽ����]

setlocal enabledelayedexpansion

REM �⺻�� ����
set PROJECT_NAME=%1
set SOURCE_PATH=%2

if "%PROJECT_NAME%"=="" set PROJECT_NAME=sampleSrc
if "%SOURCE_PATH%"=="" set SOURCE_PATH=testcase\sampleSrc

echo ========================================
echo SourceAnalyzer ���� �м� �� �ð�ȭ ����
echo ========================================
echo ������Ʈ��: %PROJECT_NAME%
echo �ҽ����: %SOURCE_PATH%
echo ���۽ð�: %date% %time%
echo ========================================

REM 1. �⺻ �м� ����
echo.
echo [1/7] �⺻ �ҽ� �м� ����...
call run_analyzer.bat --project-name %PROJECT_NAME%
if !errorlevel! neq 0 (
    echo ERROR: �⺻ �м� ����
    goto :error
)
echo  �⺻ �м� �Ϸ�

REM 2. ���輺 ���
echo.
echo [2/7] ���輺 ���� ��� ��...
call venvSrcAnalyzer\Scripts\python.exe phase1\scripts\calculate_relatedness.py --project-name %PROJECT_NAME%
if !errorlevel! neq 0 (
    echo ERROR: ���輺 ��� ����
    goto :error
)
echo  ���輺 ��� �Ϸ�

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

REM 5. �⺻ �ð�ȭ ���� (ERD, ������ �׷���, ������Ʈ)
echo.
echo [5/7] �⺻ �ð�ȭ ���� ��...
call venvSrcAnalyzer\Scripts\python.exe -m visualize all --project-name %PROJECT_NAME% --export-html "" --export-mermaid ""
if !errorlevel! neq 0 (
    echo ERROR: �⺻ �ð�ȭ ���� ����
    goto :error
)
echo  �⺻ �ð�ȭ �Ϸ�

goto end




REM 6. ���� ERD ���� (���ο� ���)
echo.
echo [6/7] ���� ERD ���� ��...
call venvSrcAnalyzer\Scripts\python.exe -c "
from visualize.builders.erd_enhanced import build_enhanced_erd_json
from visualize.renderers.enhanced_renderer_factory import EnhancedVisualizationFactory
import yaml
import json
from pathlib import Path

# ���� �ε�
config_path = Path('config/config.yaml')
config = {}
if config_path.exists():
    with open(config_path, 'r', encoding='utf-8') as f:
        raw = f.read().replace('{project_name}', '%PROJECT_NAME%')
        config = yaml.safe_load(raw) or {}

# ERD ������ ����
data = build_enhanced_erd_json(config, 1, '%PROJECT_NAME%')

# ���� �������� HTML ����
factory = EnhancedVisualizationFactory()
html = factory.create_enhanced_erd(data)

# ��� ���丮 ���� �� ���� ����
output_dir = Path('output/%PROJECT_NAME%/visualize')
output_dir.mkdir(parents=True, exist_ok=True)

with open(output_dir / 'erd_enhanced.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(' ���� ERD ���� �Ϸ�: ' + str(output_dir / 'erd_enhanced.html'))
"
if !errorlevel! neq 0 (
    echo WARNING: ���� ERD ���� ����, �⺻ ERD ���
)

REM 7. ������ ���̾�׷� ���� (�ֿ� �޼����)
echo.
echo [7/7] ������ ���̾�׷� ���� ��...
call venvSrcAnalyzer\Scripts\python.exe -m visualize sequence --project-name %PROJECT_NAME% --depth 3
if !errorlevel! neq 0 (
    echo WARNING: ������ ���̾�׷� ���� ����
)
echo  ������ ���̾�׷� �Ϸ�

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