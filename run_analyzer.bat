@echo off
REM SourceAnalyzer 실행 배치 파일
REM phase1 디렉토리에서 main.py를 실행합니다

setlocal
set PYTHONPATH=%~dp0phase1
cd /d "%~dp0phase1"
python main.py %*
exit /b %ERRORLEVEL%