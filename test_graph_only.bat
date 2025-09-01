@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo 🧪 의존성 그래프 단독 테스트
echo ========================================
echo 시작시간: %date% %time%
echo.

echo 📊 의존성 그래프 생성 중... (디버그 모드)
echo ⏰ 최대 2분 후 타임아웃 됩니다
echo.

REM 디버그 모드로 실행 (-vv = 최대 상세 로그)
timeout /t 120 /nobreak & call venvSrcAnalyzer\Scripts\python.exe -m visualize graph --project-name sampleSrc --export-html "" -vv

echo.
echo 완료시간: %date% %time%
pause