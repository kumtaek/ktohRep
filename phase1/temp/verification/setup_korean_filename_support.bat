@echo off
REM 한글 파일명 지원 설정 배치 파일

echo ========================================
echo 한글 파일명 지원 설정 시작
echo ========================================

REM 1. PowerShell 프로필 디렉토리 생성
if not exist "%USERPROFILE%\Documents\WindowsPowerShell" (
    mkdir "%USERPROFILE%\Documents\WindowsPowerShell"
)

REM 2. PowerShell 프로필 파일 생성
echo # PowerShell 프로필 설정 - 한글 파일명 문제 해결 > "%USERPROFILE%\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"
echo # UTF-8 인코딩을 기본값으로 설정 >> "%USERPROFILE%\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"
echo. >> "%USERPROFILE%\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"
echo # Out-File 기본 인코딩을 UTF-8로 설정 >> "%USERPROFILE%\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"
echo $PSDefaultParameterValues['Out-File:Encoding'] = 'utf8' >> "%USERPROFILE%\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"
echo. >> "%USERPROFILE%\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"
echo # Set-Content 기본 인코딩을 UTF-8로 설정 >> "%USERPROFILE%\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"
echo $PSDefaultParameterValues['Set-Content:Encoding'] = 'utf8' >> "%USERPROFILE%\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"
echo. >> "%USERPROFILE%\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"
echo # Add-Content 기본 인코딩을 UTF-8로 설정 >> "%USERPROFILE%\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"
echo $PSDefaultParameterValues['Add-Content:Encoding'] = 'utf8' >> "%USERPROFILE%\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"
echo. >> "%USERPROFILE%\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"
echo # 콘솔 출력 인코딩을 UTF-8로 설정 >> "%USERPROFILE%\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"
echo [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 >> "%USERPROFILE%\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"
echo. >> "%USERPROFILE%\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"
echo Write-Host "PowerShell UTF-8 인코딩 설정이 완료되었습니다." -ForegroundColor Green >> "%USERPROFILE%\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"

REM 3. 현재 세션에 즉시 적용
powershell -Command "& { $PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'; $PSDefaultParameterValues['Set-Content:Encoding'] = 'utf8'; $PSDefaultParameterValues['Add-Content:Encoding'] = 'utf8'; [Console]::OutputEncoding = [System.Text.Encoding]::UTF8; Write-Host '현재 세션에 UTF-8 인코딩 설정이 적용되었습니다.' -ForegroundColor Green }"

echo ========================================
echo 한글 파일명 지원 설정 완료
echo ========================================
echo.
echo 다음 PowerShell 세션부터는 한글 파일명이 정상적으로 작동합니다.
echo 현재 세션에도 설정이 적용되었습니다.
echo.
echo 테스트: powershell -Command "& { '테스트 내용' | Out-File -FilePath '한글테스트.md' }"
echo.

pause



