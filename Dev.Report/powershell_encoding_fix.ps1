# PowerShell 한글 파일명 문제 해결 스크립트
# 이 스크립트를 실행하면 현재 세션에서 한글 파일명 문제가 해결됩니다.

Write-Host "PowerShell 한글 파일명 문제 해결 중..." -ForegroundColor Yellow

# 1. 기본 인코딩 설정
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$PSDefaultParameterValues['Set-Content:Encoding'] = 'utf8'
$PSDefaultParameterValues['Add-Content:Encoding'] = 'utf8'

# 2. 콘솔 출력 인코딩 설정
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 3. 현재 인코딩 상태 확인
Write-Host "현재 인코딩 설정:" -ForegroundColor Green
Write-Host "  - Out-File 기본 인코딩: $($PSDefaultParameterValues['Out-File:Encoding'])"
Write-Host "  - Set-Content 기본 인코딩: $($PSDefaultParameterValues['Set-Content:Encoding'])"
Write-Host "  - Add-Content 기본 인코딩: $($PSDefaultParameterValues['Add-Content:Encoding'])"
Write-Host "  - 콘솔 출력 인코딩: $([Console]::OutputEncoding.EncodingName)"

# 4. 테스트 파일 생성
$testContent = @"
# 한글 파일명 테스트
생성 일시: $(Get-Date)
테스트 내용: 한글 파일명이 정상적으로 생성되는지 확인
"@

$testContent | Out-File -FilePath "한글파일명_테스트.md" -Encoding UTF8

if (Test-Path "한글파일명_테스트.md") {
    Write-Host "✅ 한글 파일명 테스트 성공!" -ForegroundColor Green
    Remove-Item "한글파일명_테스트.md" -Force
} else {
    Write-Host "❌ 한글 파일명 테스트 실패!" -ForegroundColor Red
}

Write-Host "PowerShell 한글 파일명 문제 해결 완료!" -ForegroundColor Green
