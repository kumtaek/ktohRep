@echo off
chcp 65001 >nul
REM 향상된 시각화만 생성하는 스크립트 (분석은 이미 완료된 상태)
REM 사용법: run_enhanced_visualize_only.bat [프로젝트명]

setlocal enabledelayedexpansion

set PROJECT_NAME=%1
if "%PROJECT_NAME%"=="" set PROJECT_NAME=sampleSrc

echo ========================================
echo 향상된 시각화 생성 (분석 데이터 기반)
echo ========================================
echo 프로젝트명: %PROJECT_NAME%
echo 시작시간: %date% %time%
echo ========================================

REM 1. 기본 시각화 생성
echo.
echo [1/3] 기본 시각화 생성 중...
echo ⏳ 여러 시각화 타입을 순차적으로 생성합니다. 시간이 오래 걸릴 수 있습니다...
echo.
echo 📊 의존성 그래프 생성 중...
call venvSrcAnalyzer\Scripts\python.exe -m visualize graph --project-name %PROJECT_NAME% --export-html "" --export-mermaid ""
echo.
echo 🗃️ ERD 생성 중...
call venvSrcAnalyzer\Scripts\python.exe -m visualize erd --project-name %PROJECT_NAME% --export-html "" --export-mermaid ""
echo.
echo 🧩 컴포넌트 다이어그램 생성 중...
call venvSrcAnalyzer\Scripts\python.exe -m visualize component --project-name %PROJECT_NAME% --export-html "" --export-mermaid ""
echo.
echo ☕ 클래스 다이어그램 생성 중...
call venvSrcAnalyzer\Scripts\python.exe -m visualize class --project-name %PROJECT_NAME% --export-html "" --export-mermaid ""
echo.
echo 🔗 연관성 분석 중... (LLM 처리로 가장 오래 걸립니다)
call venvSrcAnalyzer\Scripts\python.exe -m visualize relatedness --project-name %PROJECT_NAME% --export-html "" --export-mermaid ""
if !errorlevel! neq 0 (
    echo ERROR: 기본 시각화 생성 실패
    goto :error
)
echo ✅ 기본 시각화 완료

REM 2. 향상된 ERD 생성
echo.
echo [2/3] 향상된 ERD 생성 중...
call venvSrcAnalyzer\Scripts\python.exe generate_enhanced_erd.py %PROJECT_NAME%

REM 3. 시퀀스 다이어그램 생성
echo.
echo [3/3] 시퀀스 다이어그램 생성 중...
call venvSrcAnalyzer\Scripts\python.exe -m visualize sequence --project-name %PROJECT_NAME% --depth 2 --max-nodes 50
if !errorlevel! neq 0 (
    echo WARNING: 시퀀스 다이어그램 생성 실패
)
echo ✅ 시퀀스 다이어그램 완료

REM 완료 보고
echo.
echo ========================================
echo 🎉 향상된 시각화 생성 완료!
echo ========================================
echo 완료시간: %date% %time%
echo.
echo 📁 생성된 파일 위치:
dir /b output\%PROJECT_NAME%\visualize\*.html 2>nul
echo.
echo 🌟 새로운 기능들:
echo    • erd_enhanced.html: 컬럼 상세 툴팁
echo    • 겹침 방지 레이아웃
echo    • 3가지 레이아웃 알고리즘 (Force/Hierarchical/Grid)
echo    • 향상된 상호작용 (줌, 팬, 검색)
echo.
echo 💡 사용법:
echo    1. erd_enhanced.html을 브라우저에서 열기
echo    2. 테이블에 마우스 오버하여 상세정보 확인
echo    3. 레이아웃 버튼으로 최적 배치 선택
echo    4. 검색창에서 테이블명 검색
goto :end

:error
echo.
echo ❌ 오류 발생
echo 기존 분석 데이터가 있는지 확인해주세요.
echo 없다면 run_complete_analysis.bat을 먼저 실행해주세요.
exit /b 1

:end
echo.
echo Press any key to exit...
pause >nul