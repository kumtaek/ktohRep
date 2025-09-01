@echo off
REM SourceAnalyzer 완전 분석 및 시각화 생성 스크립트
REM 사용법: run_complete_analysis.bat [프로젝트명] [소스경로]

setlocal enabledelayedexpansion

REM 기본값 설정
set PROJECT_NAME=%1
set SOURCE_PATH=%2

if "%PROJECT_NAME%"=="" set PROJECT_NAME=sampleSrc
if "%SOURCE_PATH%"=="" set SOURCE_PATH=testcase\sampleSrc

echo ========================================
echo SourceAnalyzer 완전 분석 및 시각화 생성
echo ========================================
echo 프로젝트명: %PROJECT_NAME%
echo 소스경로: %SOURCE_PATH%
echo 시작시간: %date% %time%
echo ========================================

REM 1. 기본 분석 실행
echo.
echo [1/7] 기본 소스 분석 시작...
call run_analyzer.bat %PROJECT_NAME%
if !errorlevel! neq 0 (
    echo ERROR: 기본 분석 실패
    goto :error
)
echo ✅ 기본 분석 완료

REM 2. 관계성 계산
echo.
echo [2/7] 관계성 점수 계산 중...
call venvSrcAnalyzer\Scripts\python.exe phase1\scripts\calculate_relatedness.py --project-name %PROJECT_NAME%
if !errorlevel! neq 0 (
    echo ERROR: 관계성 계산 실패
    goto :error
)
echo ✅ 관계성 계산 완료

REM 3. LLM 요약 및 강화
echo.
echo [3/7] LLM 요약 및 메타데이터 강화 중...
call "venvSrcAnalyzer\Scripts\python.exe" phase1/tools/llm_analyzer.py summarize --project-name %PROJECT_NAME% --batch-size 3
if !errorlevel! neq 0 (
    echo WARNING: LLM 요약 실패 (선택사항)
)

call "venvSrcAnalyzer\Scripts\python.exe" phase1/tools/llm_analyzer.py enhance-db --project-name %PROJECT_NAME% --batch-size 3
if !errorlevel! neq 0 (
    echo WARNING: 메타데이터 강화 실패 (선택사항)
)
echo ✅ LLM 처리 완료

REM 4. 조인 분석
echo.
echo [4/7] SQL 조인 관계 분석 중...
call "venvSrcAnalyzer\Scripts\python.exe" phase1/tools/llm_analyzer.py analyze-joins --project-name %PROJECT_NAME% --batch-size 2
if !errorlevel! neq 0 (
    echo WARNING: 조인 분석 실패 (선택사항)
)
echo ✅ 조인 분석 완료

REM 5. 기본 시각화 생성 (ERD, 의존성 그래프, 컴포넌트)
echo.
echo [5/7] 기본 시각화 생성 중...
call venvSrcAnalyzer\Scripts\python.exe -m visualize all --project-name %PROJECT_NAME% --export-html "" --export-mermaid ""
if !errorlevel! neq 0 (
    echo ERROR: 기본 시각화 생성 실패
    goto :error
)
echo ✅ 기본 시각화 완료

REM 6. 향상된 ERD 생성 (새로운 기능)
echo.
echo [6/7] 향상된 ERD 생성 중...
call venvSrcAnalyzer\Scripts\python.exe -c "
from visualize.builders.erd_enhanced import build_enhanced_erd_json
from visualize.renderers.enhanced_renderer_factory import EnhancedVisualizationFactory
import yaml
import json
from pathlib import Path

# 설정 로드
config_path = Path('config/config.yaml')
config = {}
if config_path.exists():
    with open(config_path, 'r', encoding='utf-8') as f:
        raw = f.read().replace('{project_name}', '%PROJECT_NAME%')
        config = yaml.safe_load(raw) or {}

# ERD 데이터 생성
data = build_enhanced_erd_json(config, 1, '%PROJECT_NAME%')

# 향상된 렌더러로 HTML 생성
factory = EnhancedVisualizationFactory()
html = factory.create_enhanced_erd(data)

# 출력 디렉토리 생성 및 파일 저장
output_dir = Path('output/%PROJECT_NAME%/visualize')
output_dir.mkdir(parents=True, exist_ok=True)

with open(output_dir / 'erd_enhanced.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('✅ 향상된 ERD 저장 완료: ' + str(output_dir / 'erd_enhanced.html'))
"
if !errorlevel! neq 0 (
    echo WARNING: 향상된 ERD 생성 실패, 기본 ERD 사용
)

REM 7. 시퀀스 다이어그램 생성 (주요 메서드들)
echo.
echo [7/7] 시퀀스 다이어그램 생성 중...
call venvSrcAnalyzer\Scripts\python.exe -m visualize sequence --project-name %PROJECT_NAME% --depth 3
if !errorlevel! neq 0 (
    echo WARNING: 시퀀스 다이어그램 생성 실패
)
echo ✅ 시퀀스 다이어그램 완료

REM 완료 보고서 생성
echo.
echo ========================================
echo 🎉 모든 분석 및 시각화 완료!
echo ========================================
echo 완료시간: %date% %time%
echo.
echo 📁 생성된 파일들:
echo    output\%PROJECT_NAME%\visualize\
echo    ├── graph.html              (의존성 그래프)
echo    ├── erd.html               (기본 ERD)
echo    ├── erd_enhanced.html      (향상된 ERD - 새로운!)
echo    ├── components.html        (컴포넌트 다이어그램)
echo    ├── class.html            (클래스 다이어그램)
echo    ├── relatedness.html      (관계성 그래프)
echo    └── *_sequence.html       (시퀀스 다이어그램들)
echo.
echo 📊 추천 확인 순서:
echo    1. erd_enhanced.html      (컬럼 툴팁, 겹침 방지)
echo    2. graph.html            (전체 의존성 구조)
echo    3. components.html       (컴포넌트별 구조)
echo    4. relatedness.html      (관계성 분석)
echo.
echo 🚀 브라우저에서 파일들을 열어 확인해보세요!
goto :end

:error
echo.
echo ❌ 오류 발생으로 스크립트가 중단되었습니다.
echo 로그를 확인하고 문제를 해결한 후 다시 실행해주세요.
exit /b 1

:end
echo.
echo Press any key to exit...
pause >nul