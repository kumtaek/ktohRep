@echo off
REM =====================================================
REM 소스 분석 결과 시각화 생성 스크립트
REM ERD, 클래스 다이어그램, 의존성 그래프 등을 생성
REM 사용법: run_visualize.bat <project_name> <diagram_type>
REM =====================================================

REM UTF-8 인코딩 설정
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo  SourceAnalyzer 시각화 도구 실행
echo ========================================
echo 프로젝트: %*
echo 시작시간: %date% %time%
echo ========================================
echo.

REM Python 가상환경 활성화
echo [1/3] 가상환경 활성화 중...
call "%~dp0venvSrcAnalyzer\Scripts\activate.bat"
echo  가상환경 활성화 완료
echo.

REM 프로젝트 루트를 Python 경로에 추가하여 import 오류 방지
echo [2/3] 환경 설정 중...
set PYTHONPATH=%~dp0
echo  환경 설정 완료
echo.

REM 시각화 모듈 실행, 모든 인자를 전달
echo [3/3] 시각화 생성 시작...
echo  LLM 처리로 인해 시간이 오래 걸릴 수 있습니다. 잠시만 기다려주세요...
echo  진행 중... (Ctrl+C로 중단 가능)
echo.

REM 사용법: run_visualize.bat <diagram_type> <project_name> [options]
REM =====================================================

REM UTF-8 인코딩 설정
chcp 65001 >nul
setlocal enabledelayedexpansion

echo =========================================
echo  SourceAnalyzer 시각화 도구 실행
echo =========================================
echo 프로젝트: %1
echo 시작시간: %date% %time%
echo =========================================
echo.

REM Python 가상환경 활성화
echo [1/3] 가상환경 활성화 중...
call "%~dp0venvSrcAnalyzer\Scripts\activate.bat"
echo  가상환경 활성화 완료
echo.

REM 프로젝트 루트를 Python 경로에 추가하여 import 오류 방지
echo [2/3] 환경 설정 중...
set PYTHONPATH=%~dp0
echo  환경 설정 완료
echo.

REM 시각화 모듈 실행, 모든 인자를 전달
echo [3/3] 시각화 생성 시작...
echo  LLM 처리로 인해 시간이 오래 걸릴 수 있습니다. 잠시만 기다려주세요...
echo  진행 중... (Ctrl+C로 중단 가능)
echo.

python -m visualize.cli %1 --project-name %2 %*

if !errorlevel! equ 0 (
    echo.
    echo  시각화 생성 완료!
    echo 완료시간: %date% %time%
) else (
    echo.
    echo  시각화 생성 실패 (오류코드: !errorlevel!)
)

endlocal