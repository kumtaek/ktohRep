# JavaScript 라이브러리 다운로드 스크립트
# SourceAnalyzer 프로젝트용

Write-Host "🚀 JavaScript 라이브러리 다운로드 시작..." -ForegroundColor Green

# 디렉토리 생성
$jsDir = "visualize/static/js"
if (!(Test-Path $jsDir)) {
    New-Item -ItemType Directory -Path $jsDir -Force
    Write-Host "📁 디렉토리 생성: $jsDir" -ForegroundColor Yellow
}

# 다운로드할 라이브러리 목록
$libraries = @(
    @{
        Name = "jQuery"
        Url = "https://code.jquery.com/jquery-3.6.0.min.js"
        FileName = "jquery-3.6.0.min.js"
    },
    @{
        Name = "Cytoscape.js"
        Url = "https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.28.1/cytoscape.min.js"
        FileName = "cytoscape.min.js"
    },
    @{
        Name = "cytoscape-fcose"
        Url = "https://unpkg.com/cytoscape-fcose@2.1.0/cytoscape-fcose.js"
        FileName = "cytoscape-fcose.js"
    },
    @{
        Name = "cytoscape-qtip"
        Url = "https://cdnjs.cloudflare.com/ajax/libs/cytoscape-qtip/2.2.0/cytoscape-qtip.min.js"
        FileName = "cytoscape-qtip.js"
    },
    @{
        Name = "jquery.qtip"
        Url = "https://cdnjs.cloudflare.com/ajax/libs/qtip2/3.0.3/jquery.qtip.min.js"
        FileName = "jquery.qtip.min.js"
    }
)

# 각 라이브러리 다운로드
foreach ($lib in $libraries) {
    $filePath = Join-Path $jsDir $lib.FileName
    
    Write-Host "📥 $($lib.Name) 다운로드 중..." -ForegroundColor Cyan
    
    try {
        Invoke-WebRequest -Uri $lib.Url -OutFile $filePath -UseBasicParsing
        Write-Host "✅ $($lib.Name) 다운로드 완료: $filePath" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ $($lib.Name) 다운로드 실패: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n🎯 다운로드 완료!" -ForegroundColor Green
Write-Host "📁 다운로드된 파일 위치: $jsDir" -ForegroundColor Yellow

# 파일 목록 확인
Write-Host "`n📋 다운로드된 파일 목록:" -ForegroundColor Cyan
Get-ChildItem $jsDir -Name | ForEach-Object { Write-Host "  - $_" -ForegroundColor White }

Write-Host "`n✨ 이제 ERD를 생성할 수 있습니다!" -ForegroundColor Green
Write-Host "💡 명령어: python -m visualize --diagram-type erd --project-name sampleSrc" -ForegroundColor Yellow