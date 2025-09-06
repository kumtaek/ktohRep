@echo off
chcp 65001 > nul
rem SETLOCAL

REM --- Start ---
SET PROJECT_NAME=%1
SET PYTHON_EXE=python
SET SCRIPT_DIR=E:\SourceAnalyzer.git
SET OUTPUT_DIR=%SCRIPT_DIR%\output\%PROJECT_NAME%
SET BATCH_SIZE=10

REM --- Project name validation ---
IF "%PROJECT_NAME%"=="" (
    ECHO Error: PROJECT_NAME must be specified as the project name to execute.
    GOTO :EOF
)

REM --- Create output directory ---
IF NOT EXIST "%OUTPUT_DIR%" (
    MKDIR "%OUTPUT_DIR%"
    IF %ERRORLEVEL% NEQ 0 (
        ECHO Error: Failed to create output directory - %OUTPUT_DIR%
        GOTO :EOF
    )
)

ECHO ==================================================
ECHO SourceAnalyzer Complete Analysis Start: %PROJECT_NAME%
ECHO ==================================================

REM --- 1. LLM-based analysis and enhancement ---
ECHO.
ECHO --- 1.1. Code summarization and analysis ---
%PYTHON_EXE% "%SCRIPT_DIR%\phase1\tools\llm_analyzer.py" summarize --project-name %PROJECT_NAME% --batch-size %BATCH_SIZE%
IF %ERRORLEVEL% NEQ 0 (
    ECHO Error: Code summarization and analysis failed.
    GOTO :EOF
)
ECHO Code summarization and analysis completed.

ECHO.
ECHO --- 1.2. Database comment enhancement ---
%PYTHON_EXE% "%SCRIPT_DIR%\phase1\tools\llm_analyzer.py" enhance-db --project-name %PROJECT_NAME% --batch-size %BATCH_SIZE%
IF %ERRORLEVEL% NEQ 0 (
    ECHO Error: Database comment enhancement failed.
    GOTO :EOF
)
ECHO Database comment enhancement completed.

ECHO.
ECHO --- 1.3. SQL join relationship analysis ---
%PYTHON_EXE% "%SCRIPT_DIR%\phase1\tools\llm_analyzer.py" analyze-joins --project-name %PROJECT_NAME% --batch-size %BATCH_SIZE%
IF %ERRORLEVEL% NEQ 0 (
    ECHO Error: SQL join relationship analysis failed.
    GOTO :EOF
)
ECHO SQL join relationship analysis completed.

REM --- 2. Report generation ---
ECHO.
ECHO --- 2.1. Table specification generation ---
%PYTHON_EXE% "%SCRIPT_DIR%\phase1\tools\llm_analyzer.py" table-spec --project-name %PROJECT_NAME% --output "%OUTPUT_DIR%\table_specification.md"
IF %ERRORLEVEL% NEQ 0 (
    ECHO Error: Table specification generation failed.
    GOTO :EOF
)
ECHO Table specification generation completed: "%OUTPUT_DIR%\table_specification.md"

ECHO.
ECHO --- 2.2. Source code specification generation ---
%PYTHON_EXE% "%SCRIPT_DIR%\phase1\tools\llm_analyzer.py" source-spec --project-name %PROJECT_NAME% --output "%OUTPUT_DIR%\source_specification.md"
IF %ERRORLEVEL% NEQ 0 (
    ECHO Error: Source code specification generation failed.
    GOTO :EOF
)
ECHO Source code specification generation completed: "%OUTPUT_DIR%\source_specification.md"

REM --- 3. Visualization generation ---
ECHO.
ECHO --- 3.1. Code sequence diagram generation (enhanced version) ---
REM Use visualize/cli.py generate-sequence-diagrams command
%PYTHON_EXE% "%SCRIPT_DIR%\visualize\cli.py" generate-sequence-diagrams --project-name %PROJECT_NAME% --max-diagrams 5 --depth 3 --max-nodes 50 --output-dir "%OUTPUT_DIR%"
IF %ERRORLEVEL% NEQ 0 (
    ECHO Error: Code sequence diagram generation failed. Please check visualize/cli.py log.
)
ECHO Code sequence diagram generation completed.

ECHO.
ECHO ==================================================
ECHO SourceAnalyzer Complete Analysis Finished.
ECHO Results can be found in: %OUTPUT_DIR%
ECHO ==================================================

rem ENDLOCAL