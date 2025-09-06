@echo off
REM 샘플소스 명세서 검증 실행 스크립트

echo ========================================
echo 샘플소스 명세서 검증 시작
echo ========================================

REM 현재 디렉토리를 phase1으로 변경
cd /d "%~dp0..\.."

REM Python 스크립트 실행
python temp/verification/specification_verification.py --project-name sampleSrc

echo ========================================
echo 검증 완료
echo ========================================

pause



