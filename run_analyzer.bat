@echo off
setlocal

call "%~dp0venvSrcAnalyzer\Scripts\activate.bat"

set "PYTHONPATH=%~dp0"

python.exe "%~dp0phase1\main.py" %*

endlocal