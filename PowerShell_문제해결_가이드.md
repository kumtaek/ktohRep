# PowerShell 여러 줄 문자열 처리 문제 해결책

## 현재 발생한 문제
PowerShell에서 긴 Python 명령어를 실행할 때 다음과 같은 오류가 발생:
- ScriptBlock은 Command 매개 변수의 값으로만 지정되어야 합니다
- 한글 문자가 cmdlet으로 인식되는 오류
- 긴 명령어 처리 시 문법 오류

## 즉시 해결 방법

### 1. Python 스크립트 파일로 분리 (가장 확실한 방법)
```powershell
# 1단계: Python 스크립트 파일 생성
echo 'import os' > create_file.py
echo 'from datetime import datetime' >> create_file.py
echo 'content = """# 제목' >> create_file.py
echo '내용' >> create_file.py
echo '"""' >> create_file.py
echo 'with open("output.md", "w", encoding="utf-8") as f:' >> create_file.py
echo '    f.write(content)' >> create_file.py
echo 'print("File created successfully.")' >> create_file.py

# 2단계: Python 스크립트 실행
python create_file.py
```

### 2. 단계별 Add-Content 사용
```powershell
# 파일 생성
New-Item -Path "output.md" -ItemType File -Force

# 내용 추가
Add-Content -Path "output.md" -Value "# 제목" -Encoding UTF8
Add-Content -Path "output.md" -Value "" -Encoding UTF8
Add-Content -Path "output.md" -Value "내용" -Encoding UTF8
Add-Content -Path "output.md" -Value "" -Encoding UTF8
Add-Content -Path "output.md" -Value "## 부제목" -Encoding UTF8
```

### 3. Here-String 사용
```powershell
$content = @"
# 제목

내용

## 부제목
- 항목 1
- 항목 2
"@

Set-Content -Path "output.md" -Value $content -Encoding UTF8
```

### 4. 임시 스크립트 파일 사용
```powershell
# 임시 스크립트 생성
$scriptContent = @"
import os
from datetime import datetime

content = '''# 제목

내용

## 부제목
- 항목 1
- 항목 2
'''

with open('output.md', 'w', encoding='utf-8') as f:
    f.write(content)

print('File created successfully.')
"@

# 임시 파일에 저장
$scriptContent | Out-File -FilePath "temp_script.py" -Encoding UTF8

# 실행
python temp_script.py

# 정리
Remove-Item "temp_script.py"
```

### 5. 배치 파일로 우회
```batch
@echo off
echo # 제목 > output.md
echo. >> output.md
echo 내용 >> output.md
echo. >> output.md
echo ## 부제목 >> output.md
echo - 항목 1 >> output.md
echo - 항목 2 >> output.md
```

## 현재 상황에 대한 즉시 해결책

### 방법 1: 간단한 Python 스크립트 생성
```powershell
# 1. 스크립트 파일 생성
echo 'import os' > create_md.py
echo 'from datetime import datetime' >> create_md.py
echo 'content = """# PowerShell 문제 해결책' >> create_md.py
echo '' >> create_md.py
echo '이 파일은 PowerShell 문제를 해결하기 위해 생성되었습니다.' >> create_md.py
echo '"""' >> create_md.py
echo 'with open("PowerShell_해결책.md", "w", encoding="utf-8") as f:' >> create_md.py
echo '    f.write(content)' >> create_md.py
echo 'print("File created successfully.")' >> create_md.py

# 2. 실행
python create_md.py

# 3. 정리
Remove-Item create_md.py
```

### 방법 2: 직접 파일 생성
```powershell
# 파일 생성
New-Item -Path "PowerShell_해결책.md" -ItemType File -Force

# 내용 추가
Add-Content -Path "PowerShell_해결책.md" -Value "# PowerShell 문제 해결책" -Encoding UTF8
Add-Content -Path "PowerShell_해결책.md" -Value "" -Encoding UTF8
Add-Content -Path "PowerShell_해결책.md" -Value "이 파일은 PowerShell 문제를 해결하기 위해 생성되었습니다." -Encoding UTF8
```

## 근본적인 해결책

### 1. PowerShell 7+ 사용
- PowerShell 7+에서는 문자열 처리 개선
- 더 나은 한글 지원

### 2. VS Code 또는 PowerShell ISE 사용
- 복사-붙여넣기로 긴 내용 처리
- 스크립트 파일로 분리하여 실행

### 3. Python 가상환경 활용
- 복잡한 파일 생성 작업은 Python으로 처리
- PowerShell은 단순한 명령어만 사용

## 주의사항

1. **인코딩**: 항상 UTF-8 사용
2. **경로**: 상대경로와 절대경로 구분
3. **권한**: 파일 쓰기 권한 확인
4. **문자열**: 특수문자 이스케이프 처리

## 결론

PowerShell에서 긴 명령어나 복잡한 문자열 처리 시에는:
1. Python 스크립트 파일로 분리
2. 단계별 Add-Content 사용
3. Here-String 활용
4. 임시 스크립트 파일 사용

이 중에서 **Python 스크립트 파일로 분리**하는 것이 가장 안전하고 확실한 방법입니다.

---

**생성일시**: 2025년 1월 3일
**작성자**: AI Assistant
**목적**: PowerShell 문제 해결 가이드

