@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
REM 빠른 데모용 스크립트 - sampleSrc 프로젝트로 전체 기능 시연
REM 사용법: run_quick_demo.bat

echo ========================================
echo 🚀 SourceAnalyzer 향상된 시각화 데모
echo ========================================
echo 프로젝트: sampleSrc (테스트 케이스)
echo 시작시간: %date% %time%
echo ========================================

REM 1. 환경 확인
echo.
echo [환경 확인] 필수 파일들 확인 중...
if not exist "testcase\sampleSrc" (
    echo ❌ testcase\sampleSrc 디렉토리가 없습니다.
    echo    샘플 소스 코드가 필요합니다.
    goto :error
)

if not exist "venvSrcAnalyzer\Scripts\python.exe" (
    echo ❌ Python 가상환경이 설정되지 않았습니다.
    echo    setup_venv.bat을 먼저 실행해주세요.
    goto :error
)

if not exist "config\config.yaml" (
    echo ❌ config.yaml 파일이 없습니다.
    goto :error
)

echo ✅ 환경 확인 완료

REM 2. 기본 분석 (빠른 버전)
echo.
echo [1/4] 기본 소스 분석...
call run_analyzer.bat --project-name sampleSrc
if !errorlevel! neq 0 (
    echo ERROR: 분석 실패
    goto :error
)
echo ✅ 기본 분석 완료

REM 3. 관계성 계산 (필수)
echo.
echo [2/4] 관계성 계산...
call venvSrcAnalyzer\Scripts\python.exe phase1\scripts\calculate_relatedness.py sampleSrc
if !errorlevel! neq 0 (
    echo WARNING: 관계성 계산 실패, 계속 진행
)
echo ✅ 관계성 계산 완료

REM 4. 향상된 시각화 생성
echo.
echo [3/4] 향상된 시각화 생성...
call run_enhanced_visualize_only.bat sampleSrc
if !errorlevel! neq 0 (
    echo ERROR: 시각화 생성 실패
    goto :error
)

REM 5. 결과 파일 확인 및 자동 열기
echo.
echo [4/4] 결과 확인 및 브라우저 열기...

set OUTPUT_DIR=output\sampleSrc\visualize
if exist "%OUTPUT_DIR%\erd_enhanced.html" (
    echo ✅ 향상된 ERD 생성됨: %OUTPUT_DIR%\erd_enhanced.html
    
    REM 브라우저에서 자동으로 열기
    echo.
    echo 🌐 브라우저에서 향상된 ERD 열기 중...
    start "" "%OUTPUT_DIR%\erd_enhanced.html"
    
    REM 3초 후 기본 ERD도 열기
    timeout /t 3 /nobreak >nul
    if exist "%OUTPUT_DIR%\erd.html" (
        echo 🌐 비교용 기본 ERD도 열기...
        start "" "%OUTPUT_DIR%\erd.html"
    )
) else (
    echo ❌ 향상된 ERD 파일이 생성되지 않았습니다.
)

echo.
echo ========================================
echo 🎉 데모 완료!
echo ========================================
echo 완료시간: %date% %time%
echo.
echo 📊 생성된 파일들:
if exist "%OUTPUT_DIR%" (
    dir /b "%OUTPUT_DIR%\*.html"
) else (
    echo 출력 디렉토리를 찾을 수 없습니다.
)
echo.
echo 🌟 새로운 기능 체험하기:
echo    1. 테이블에 마우스 오버 → 컬럼 상세정보 툴팁
echo    2. 우상단 레이아웃 버튼 → Force/Dagre 전환
echo    3. 검색창에 테이블명 입력 → 필터링
echo    4. 마우스 휠 → 줌 인/아웃
echo    5. 드래그 → 화면 이동
echo.
echo 📝 비교해보세요:
echo    • erd_enhanced.html (새로운 고도화 버전)
echo    • erd.html (기존 버전)
echo.
echo 차이점을 직접 확인해보시고 피드백 주세요! 🚀
goto :end

:error
echo.
echo ❌ 데모 실행 실패
echo 다음을 확인해주세요:
echo    1. testcase\sampleSrc 디렉토리 존재 여부
echo    2. venvSrcAnalyzer 가상환경 설정 상태
echo    3. config\config.yaml 파일 존재 여부
echo.
echo 💡 해결 방법:
echo    1. setup_venv.bat 실행
echo    2. config.yaml 설정 확인
echo    3. 샘플 소스코드 준비
exit /b 1

:end
echo.
echo 🎊 데모를 즐겨보세요!
echo Press any key to exit...
pause >nul