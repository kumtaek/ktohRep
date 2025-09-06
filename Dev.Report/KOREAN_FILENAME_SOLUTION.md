# 한글 파일명 문제 해결 가이드

## 문제 원인
- **PowerShell 기본 인코딩**: CP949 (한국어)
- **write 도구 인코딩**: UTF-8
- **결과**: 인코딩 불일치로 한글 파일명 생성 실패

## 근본적 해결책

### 1. PowerShell 프로필 설정 (영구 해결)
```powershell
# PowerShell 프로필 파일 위치
$PROFILE

# 프로필 파일 생성 및 설정
New-Item -ItemType File -Path $PROFILE -Force
@"
# UTF-8 인코딩을 기본값으로 설정
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$PSDefaultParameterValues['Set-Content:Encoding'] = 'utf8'
$PSDefaultParameterValues['Add-Content:Encoding'] = 'utf8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
"@ | Out-File -FilePath $PROFILE -Encoding UTF8
```

### 2. 현재 세션 즉시 적용
```powershell
# 현재 세션에 즉시 적용
$PSDefaultParameterValues['Out-File:Encoding'] = 'utf8'
$PSDefaultParameterValues['Set-Content:Encoding'] = 'utf8'
$PSDefaultParameterValues['Add-Content:Encoding'] = 'utf8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

### 3. 자동 설정 스크립트 실행
```bash
# 배치 파일로 자동 설정
setup_korean_filename_support.bat

# 또는 PowerShell 스크립트로 설정
powershell -ExecutionPolicy Bypass -File powershell_encoding_fix.ps1
```

## 사용법

### 한글 파일명으로 파일 생성
```powershell
# 방법 1: Out-File 사용 (권장)
"내용" | Out-File -FilePath "한글파일명.md" -Encoding UTF8

# 방법 2: Set-Content 사용
Set-Content -Path "한글파일명.md" -Value "내용" -Encoding UTF8

# 방법 3: Here-String 사용
@"
여러 줄 내용
한글 파일명으로 저장
"@ | Out-File -FilePath "한글파일명.md" -Encoding UTF8
```

### 테스트 방법
```powershell
# 테스트 파일 생성
"테스트 내용" | Out-File -FilePath "한글테스트.md" -Encoding UTF8

# 파일 존재 확인
Test-Path "한글테스트.md"

# 파일 내용 확인
Get-Content "한글테스트.md"

# 테스트 파일 삭제
Remove-Item "한글테스트.md" -Force
```

## 문제 해결 체크리스트

### ✅ 설정 확인
- [ ] PowerShell 프로필 파일 존재
- [ ] UTF-8 인코딩 기본값 설정
- [ ] 콘솔 출력 인코딩 설정
- [ ] 현재 세션 인코딩 적용

### ✅ 테스트 확인
- [ ] 한글 파일명 생성 테스트
- [ ] 파일 내용 정상 저장 테스트
- [ ] 파일 읽기 정상 테스트

### ✅ 프로젝트 적용
- [ ] 모든 한글 파일명 정상 생성
- [ ] 검증 스크립트 정상 실행
- [ ] 리포트 파일 정상 생성

## 주의사항

1. **PowerShell 재시작**: 프로필 설정 후 PowerShell 재시작 필요
2. **인코딩 일관성**: 모든 파일 생성 시 UTF-8 인코딩 사용
3. **백업**: 기존 파일 백업 후 설정 적용
4. **테스트**: 설정 후 반드시 테스트 수행

## 추가 정보

- **시스템 인코딩**: CP949 (한국어)
- **PowerShell 기본**: CP949
- **권장 인코딩**: UTF-8
- **호환성**: 모든 한글 윈도우즈 버전 지원

## 문제 발생 시

1. **프로필 재설정**: `setup_korean_filename_support.bat` 실행
2. **수동 설정**: 위의 PowerShell 명령어 수동 실행
3. **영문 파일명**: 임시로 영문 파일명 사용
4. **인코딩 명시**: 모든 파일 생성 시 `-Encoding UTF8` 옵션 사용
