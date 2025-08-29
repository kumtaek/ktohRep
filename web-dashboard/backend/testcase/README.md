# Backend API 테스트 케이스

## 환경 변수
- `HOST`, `PORT`: 서버 바인딩 (기본 `0.0.0.0:8000`)
- `RELOAD`: 코드 변경 감지(`true`/`false`)
- `ALLOWED_ORIGINS`: CORS 허용 Origin(콤마 구분)

## 구동
```
python web-dashboard/backend/app.py
# 또는
HOST=0.0.0.0 PORT=8000 ALLOWED_ORIGINS=http://127.0.0.1:3000 uvicorn web-dashboard.backend.app:app
```

## 점검 항목
- `/api/health` 헬스체크 응답
- `/api/projects` 프로젝트 목록 및 필드 형태
- `/api/export/classes.csv?project_id=1` 등 내보내기 엔드포인트
- `/api/docs/owasp/A03` 및 `/api/docs/cwe/CWE-89` 로컬 문서 제공
- `/docs/owasp/A03.md` 정적 파일 서빙
