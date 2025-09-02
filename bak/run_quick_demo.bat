@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
REM 빠른 데모용 스크립트 - sampleSrc 프로젝트로 전체 기능 시연
REM 사용법: run_quick_demo.bat

echo ========================================
echo  SourceAnalyzer 향상된 시각화 데모
echo ========================================
echo 프로젝트: sampleSrc (테스트 케이스)
echo 시작시간: %date% %time%
echo ========================================

REM 1. 환경 확인
echo.
echo [환경 확인] 필수 파일들 확인 중...
if not exist "testcase\sampleSrc" (
    echo  testcase\sampleSrc 디렉토리가 없습니다.
    echo    샘플 소스 코드가 필요합니다.
    goto :error
)

if not exist "venvSrcAnalyzer\Scripts\python.exe" (
    echo  Python 가상환경이 설정되지 않았습니다.
    echo    setup_venv.bat을 먼저 실행해주세요.
    goto :error
)

if not exist "config\config.yaml" (
    echo  config.yaml 파일이 없습니다.
    goto :error
)

echo  환경 확인 완료

REM 2. 기본 분석 (빠른 버전)
echo.
echo [1/4] 기본 소스 분석...
rem call run_analyzer.bat --project-name sampleSrc
call run_complete_analysis.bat --project-name sampleSrc

if !errorlevel! neq 0 (
    echo ERROR: 분석 실패
    goto :error
)
echo  기본 분석 완료

rem     REM 3. 관계성 계산 (필수)
rem     echo.
rem     echo [2/4] 관계성 계산...
rem     call venvSrcAnalyzer\Scripts\python.exe phase1\scripts\calculate_relatedness.py sampleSrc
rem     if !errorlevel! neq 0 (
rem         echo WARNING: 관계성 계산 실패, 계속 진행
rem     )
rem     echo  관계성 계산 완료

REM 4. 향상된 시각화 생성
echo.
echo [3/4] 향상된 시각화 생성...
call run_enhanced_visualize_only.bat sampleSrc
if !errorlevel! neq 0 (
    echo ERROR: 시각화 생성 실패
    goto :error
)

REM 5. 결과 파일 확인 및 자동 열기
rem echo.
rem echo [4/4] run_summarize.bat
rem call run_summarize.bat sampleSrc
call ./venvSrcAnalyzer\Scripts\python.exe phase1\tools\llm_analyzer.py source-spec --project-name sampleSrc --output

set OUTPUT_DIR=output\sampleSrc\visualize
 
echo.
echo ========================================
echo  데모 완료!
echo ========================================
echo Complete Time: %date% %time%
echo.
echo Generated Files:
if exist "%OUTPUT_DIR%" (
    dir /b "%OUTPUT_DIR%\*.html"
) else (
    echo Output directory not found.
)
echo.
echo Try New Features:
echo    1. Mouse over table = Column detail tooltip
echo    2. Top-right layout button = Force/Dagre switch
echo    3. Search box with table name = Filtering
echo    4. Mouse wheel = Zoom in/out
echo    5. Drag = Move screen
echo.
echo Compare:
echo    - erd_enhanced.html (new enhanced version)
echo    - erd.html (original version)
echo.
echo Please check the differences and provide feedback! 
goto :end

:error
echo.
echo 데모 실행 실패
echo 다음을 확인해주세요:
echo    1. testcase\sampleSrc 디렉토리 존재 여부
echo    2. venvSrcAnalyzer 가상환경 설정 상태
echo    3. config\config.yaml 파일 존재 여부
echo.
echo Solution:
echo    1. Run setup_venv.bat
echo    2. Check config.yaml settings
echo    3. Prepare sample source code
exit /b 1

:end
