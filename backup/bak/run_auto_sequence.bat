@echo off
REM Auto-generate sequence diagrams without manual parameters

setlocal enabledelayedexpansion

set PROJECT_NAME=%1
if "%PROJECT_NAME%"=="" set PROJECT_NAME=sampleSrc

echo =================================
echo Auto Sequence Diagram Generation
echo Project: %PROJECT_NAME%
echo =================================

python auto_sequence_runner.py --project-name %PROJECT_NAME%

if errorlevel 1 (
    echo Failed to generate sequence diagrams
    pause
    exit /b 1
)

echo.
echo Sequence diagram generation completed successfully!
