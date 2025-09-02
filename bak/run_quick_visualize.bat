@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

set PROJECT_NAME=%1
if "%PROJECT_NAME%"=="" set PROJECT_NAME=sampleSrc

echo ========================================
echo  빠른 시각화 생성 (ERD + 그래프만)
echo ========================================
echo 프로젝트명: %PROJECT_NAME%
echo 시작시간: %date% %time%
echo ========================================

REM 1. ERD만 생성
echo.
echo [1/2] ERD 생성 중...
call venvSrcAnalyzer\Scripts\python.exe -m visualize erd --project-name %PROJECT_NAME% --export-html "" --export-mermaid ""
if !errorlevel! neq 0 (
    echo ERROR: ERD 생성 실패
    goto :error
)
echo  ERD 생성 완료

REM 2. 의존성 그래프 생성
echo.
echo [2/2] 의존성 그래프 생성 중...
call venvSrcAnalyzer\Scripts\python.exe -m visualize graph --project-name %PROJECT_NAME% --export-html "" --export-mermaid ""
if !errorlevel! neq 0 (
    echo ERROR: 그래프 생성 실패
    goto :error
)
echo  그래프 생성 완료

REM 결과 확인
echo.
echo ========================================
echo  빠른 시각화 완료!
echo ========================================
echo 완료시간: %date% %time%

set OUTPUT_DIR=output\%PROJECT_NAME%\visualize
if exist "%OUTPUT_DIR%\erd.html" (
    echo  ERD: %OUTPUT_DIR%\erd.html
    echo  브라우저에서 ERD 열기...
    start "" "%OUTPUT_DIR%\erd.html"
) else (
    echo  ERD 파일이 생성되지 않았습니다.
)

if exist "%OUTPUT_DIR%\graph.html" (
    echo  Graph: %OUTPUT_DIR%\graph.html
    timeout /t 2 /nobreak >nul
    echo  브라우저에서 그래프 열기...
    start "" "%OUTPUT_DIR%\graph.html"
) else (
    echo  그래프 파일이 생성되지 않았습니다.
)

goto :end

:error
echo.
echo  빠른 시각화 실행 실패
echo 완료시간: %date% %time%
exit /b 1

:end
echo. 