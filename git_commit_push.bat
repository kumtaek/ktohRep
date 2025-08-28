@echo off
setlocal

:: 첫 번째 인자를 커밋 메시지로 사용
set "commit_message=%~1"

echo 디버그: 수신된 커밋 메시지: "%commit_message%"

:: 커밋 메시지가 비어있는지 확인
if "%commit_message%"=="" (
    echo 오류: 커밋 메시지를 입력해주세요.
    echo 사용법: %~nx0 "Your commit message here"
    goto :eof
)

echo.
echo 모든 변경 사항을 스테이징합니다...
git add .
if %errorlevel% neq 0 (
    echo 오류: git add 실패.
    goto :eof
)
echo.

echo 변경 사항을 커밋합니다: "%commit_message%"
git commit -m "%commit_message%"
if %errorlevel% neq 0 (
    echo 오류: git commit 실패.
    goto :eof
)
echo.

echo 원격 저장소로 푸시합니다...
git push
if %errorlevel% neq 0 (
    echo 오류: git push 실패.
    goto :eof
)
echo.

echo Git 작업이 성공적으로 완료되었습니다.
endlocal