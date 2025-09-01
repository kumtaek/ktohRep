@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo 🎨 SourceAnalyzer 시각화 도구 실행
echo ========================================
echo 프로젝트: %*
echo 시작시간: %date% %time%
echo ========================================
echo.

REM Activate the virtual environment
echo [1/3] 가상환경 활성화 중...
call "%~dp0venvSrcAnalyzer\Scripts\activate.bat"
echo ✅ 가상환경 활성화 완료
echo.

REM Set project root to PYTHONPATH to handle all imports correctly
echo [2/3] 환경 설정 중...
set PYTHONPATH=%~dp0
echo ✅ 환경 설정 완료
echo.

REM Execute the visualize module, passing all arguments
echo [3/3] 시각화 생성 시작...
echo 📝 LLM 처리로 인해 시간이 오래 걸릴 수 있습니다. 잠시만 기다려주세요...
echo ⏳ 진행 중... (Ctrl+C로 중단 가능)
echo.

python -m visualize.cli %*

if !errorlevel! equ 0 (
    echo.
    echo ✅ 시각화 생성 완료!
    echo 완료시간: %date% %time%
) else (
    echo.
    echo ❌ 시각화 생성 실패 (오류코드: !errorlevel!)
)

endlocal