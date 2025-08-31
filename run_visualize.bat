@echo off
setlocal

REM Activate the virtual environment
call "%~dp0venvSrcAnalyzer\Scripts\activate.bat"

REM Set project root to PYTHONPATH to handle all imports correctly
set PYTHONPATH=%~dp0

REM Execute the visualize module, passing all arguments
python -m visualize.cli %*

endlocal