@echo off
REM ================================================================
REM Source Analyzer - 관계 정보 생성 배치 파일
REM ================================================================
REM 이 스크립트는 프로젝트의 모든 관계 정보를 포함한 시각화를 생성합니다.
REM 
REM 사용법:
REM   run_relationships.bat --project-name [프로젝트명]
REM
REM 예시:
REM   run_relationships.bat --project-name sampleSrc
REM   run_relationships.bat --project-name myProject
REM ================================================================

setlocal enabledelayedexpansion

REM 프로젝트 이름 설정 (기본값: sampleSrc)
set PROJECT_NAME=%1

:start_analysis

echo ================================================================
echo Source Analyzer - 관계 정보 생성 시작
echo 프로젝트: %PROJECT_NAME%
echo 시각: %date% %time%
echo ================================================================

REM Python 가상환경 활성화
if exist "venvSrcAnalyzer\Scripts\activate.bat" (
    echo [INFO] 가상환경 활성화 중...
    call venvSrcAnalyzer\Scripts\activate.bat
) else (
    echo [WARNING] 가상환경을 찾을 수 없습니다. 시스템 Python을 사용합니다.
)

echo.
echo [1/5] ERD 다이어그램 생성 (테이블 관계)...
python -m visualize.cli erd --project-name %PROJECT_NAME% --export-html --export-mermaid
if errorlevel 1 (
    echo [ERROR] ERD 생성 실패
    goto :error
)

echo.
echo [2/5] 의존성 그래프 생성 (코드 관계)...
python -m visualize.cli graph --project-name %PROJECT_NAME% --export-html --export-mermaid
if errorlevel 1 (
    echo [ERROR] 의존성 그래프 생성 실패
    goto :error
)

echo.
echo [3/5] 클래스 다이어그램 생성 (클래스 관계)...
python -m visualize.cli class --project-name %PROJECT_NAME% --export-html --export-mermaid
if errorlevel 1 (
    echo [ERROR] 클래스 다이어그램 생성 실패
    goto :error
)

echo.
echo [4/5] 컴포넌트 다이어그램 생성 (컴포넌트 관계)...
python -m visualize.cli component --project-name %PROJECT_NAME% --export-html --export-mermaid
if errorlevel 1 (
    echo [ERROR] 컴포넌트 다이어그램 생성 실패
    goto :error
)

echo.
echo [5/5] 연관성 그래프 생성 (전체 관계)...
python -m visualize.cli relatedness --project-name %PROJECT_NAME% --export-html --min-score 0.3
if errorlevel 1 (
    echo [ERROR] 연관성 그래프 생성 실패
    goto :error
)

echo.
echo ================================================================
echo 관계 정보 생성 완료!
echo.
echo 생성된 파일 위치: .\output\%PROJECT_NAME%\visualize\
echo   - graph.html      : 의존성 그래프 (코드 관계)
echo   - erd.html        : 엔터티 관계도 (테이블 관계)
echo   - class.html      : 클래스 다이어그램 (클래스 상속/구현 관계)
echo   - component.html  : 컴포넌트 다이어그램 (모듈 관계)
echo   - relatedness.html: 연관성 그래프 (전체 연관 관계)
echo   - *.md            : Mermaid 다이어그램
echo.
echo 웹 브라우저에서 HTML 파일을 열어 인터랙티브 시각화를 확인하세요.
echo ================================================================
goto :end

:error
echo.
echo ================================================================
echo [ERROR] 관계 정보 생성 중 오류 발생
echo 프로젝트 분석이 완료되었는지 확인하세요:
echo   .\run_analyzer.bat --project-name %PROJECT_NAME%
echo ================================================================
exit /b 1

:end
endlocal�료되었는지 확인하세요:
echo   .\run_analyzer.bat --project-name %PROJECT_NAME%
echo ================================================================
exit /b 1

:end
endlocal