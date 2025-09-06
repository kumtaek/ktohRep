@echo off
chcp 65001 > nul
title Q&A 자동 모니터링 시스템

echo.
echo ╔══════════════════════════════════════════════════╗
echo ║              Q&A 자동 모니터링 시스템             ║  
echo ║                    v1.0                         ║
echo ╚══════════════════════════════════════════════════╝
echo.

:: 현재 디렉토리 확인
echo [INFO] 현재 작업 디렉토리: %CD%
echo.

:: 가상환경 확인 및 활성화
if exist "venvSrcAnalyzer\Scripts\activate.bat" (
    echo [INFO] 가상환경 활성화 중...
    call "venvSrcAnalyzer\Scripts\activate.bat"
    echo [SUCCESS] 가상환경 활성화 완료
) else (
    echo [WARNING] 가상환경을 찾을 수 없습니다.
    echo [INFO] 시스템 Python을 사용합니다.
)

echo.

:: Python 및 필수 모듈 확인
echo [INFO] 환경 확인 중...
python --version
echo.

:: Dev.Report 디렉토리 확인
if not exist "Dev.Report" (
    echo [INFO] Dev.Report 디렉토리를 생성합니다...
    mkdir "Dev.Report"
    echo [SUCCESS] Dev.Report 디렉토리 생성 완료
)

echo [INFO] 모니터링 설정:
echo   - 감시 대상: .\Dev.Report\Q_*.md
echo   - 체크 간격: 5분 (300초)  
echo   - 로그 파일: qa_monitor.log
echo.

echo ╔══════════════════════════════════════════════════╗
echo ║                  시작 옵션                      ║
echo ║  1. 기본 모니터링 (5분 간격)                    ║
echo ║  2. 빠른 모니터링 (1분 간격)                    ║  
echo ║  3. 테스트 모드 (30초 간격)                     ║
echo ║  4. 종료                                       ║
echo ╚══════════════════════════════════════════════════╝
echo.

set /p choice="선택하세요 (1-4): "

if "%choice%"=="1" (
    echo [시작] 기본 모니터링 모드 (5분 간격)
    python qa_enhanced_analyzer.py --interval 300
) else if "%choice%"=="2" (
    echo [시작] 빠른 모니터링 모드 (1분 간격)
    python qa_enhanced_analyzer.py --interval 60
) else if "%choice%"=="3" (
    echo [시작] 테스트 모드 (30초 간격)
    python qa_enhanced_analyzer.py --interval 30
) else if "%choice%"=="4" (
    echo [종료] 프로그램을 종료합니다.
    goto :end
) else (
    echo [오류] 잘못된 선택입니다.
    pause
    goto :end
)

:end
echo.
echo ╔══════════════════════════════════════════════════╗
echo ║            Q&A 모니터링이 종료되었습니다          ║
echo ╚══════════════════════════════════════════════════╝
echo.
pause