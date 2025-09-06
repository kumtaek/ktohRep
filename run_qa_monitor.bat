@echo off
chcp 65001 > nul
echo ============================================
echo Q&A 자동 모니터링 시스템 시작
echo ============================================
echo.

:: 가상환경 활성화
if exist "venvSrcAnalyzer\Scripts\activate.bat" (
    echo [INFO] 가상환경 활성화 중...
    call "venvSrcAnalyzer\Scripts\activate.bat"
) else (
    echo [WARNING] 가상환경을 찾을 수 없습니다. 시스템 Python 사용
)

echo.
echo [INFO] Python 버전 확인:
python --version
echo.

:: Dev.Report 디렉토리 확인/생성
if not exist "Dev.Report" (
    echo [INFO] Dev.Report 디렉토리 생성 중...
    mkdir "Dev.Report"
)

echo [INFO] 현재 시간: %date% %time%
echo [INFO] 모니터링 대상: .\Dev.Report\Q_*.md
echo [INFO] 체크 간격: 5분 (300초)
echo.
echo [시작] Q&A 모니터링을 시작합니다...
echo [종료] Ctrl+C로 중단할 수 있습니다.
echo ============================================
echo.

:: Python 스크립트 실행
python qa_monitor.py --interval 300 --dev-report-dir "./Dev.Report"

echo.
echo ============================================
echo Q&A 모니터링이 종료되었습니다.
echo ============================================
pause