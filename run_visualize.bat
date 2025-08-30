@echo off
setlocal

REM Activate the virtual environment
call "%~dp0venvSrcAnalyzer\Scripts\activate.bat"

REM Set PYTHONPATH for phase1 module imports (visualize may need access to phase1 modules)
set PYTHONPATH=%~dp0phase1

REM Execute the Python script, passing all arguments
python "%~dp0visualize\cli.py" %*

endlocal