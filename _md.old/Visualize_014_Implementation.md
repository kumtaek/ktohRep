# Visualize 014 Implementation

## 작업 요약
- 절대 경로/localhost 정리 및 환경 변수화
  - Backend CORS `allow_origins`를 `ALLOWED_ORIGINS` 환경 변수로 제어하도록 변경.
  - 서버 실행 파라미터를 환경 변수(`HOST`, `PORT`, `RELOAD`)로 제어.
  - 정적 경로는 모두 리포지토리 상대 경로(`Path(__file__).parent...`) 사용 유지.
- OWASP Top 10/CWE 오프라인 문서화
  - `doc/` 폴더 추가: `doc/owasp/A01..A10.md`(사례/샘플 코드 포함), `doc/cwe/CWE-89.md`, `doc/cwe/CWE-79.md`, `doc/README.md`.
  - Backend에 정적 마운트(`/docs`) 및 문서 API 추가(`/api/docs/owasp/{code}`, `/api/docs/cwe/{code}`).
  - 기존 `/api/open/owasp/{code}`는 호환성을 위해 유지(온라인 리다이렉트).
- 폐쇄망 고려 점검
  - 기본 동작은 로컬 파일/DB 중심. 외부 호출은 문서 미존재 시 리다이렉트에 한정.
  - 로컬 문서/정적자원 제공으로 네트워크 단절 환경에서도 취약점 설명 조회 가능.
- 테스트케이스 보완
  - `testcase/visualize/README.md`: CLI 출력(HTML/JSON/CSV/MD) 점검 절차 추가.
  - `web-dashboard/backend/testcase/README.md`: API 점검 절차 및 환경 변수 사용법 추가.
- 설정 로더 개선
  - `visualize/data_access.py`, `phase1/src/main.py`: YAML 로딩 시 환경변수 치환(`${VAR}`) 지원.
 - 문서/가이드 현행화
   - `README.md` 요약본 재작성, `README_detailed.md` 상세 운영/오프라인 설치 가이드를 신규 작성.
 - 요구 패키지 정리
   - `requirements.txt`에 FastAPI/uvicorn 추가(백엔드 실행 시 필요).

## 변경 파일
- `web-dashboard/backend/app.py`
  - CORS/서버 파라미터 환경 변수화, `/docs` 마운트, 문서 API 추가, `__main__` 구동 옵션 환경 변수화.
- `visualize/data_access.py`
  - 설정 로드 시 `os.path.expandvars`로 환경 변수 치환 지원.
- `phase1/src/main.py`
  - 설정 로드 시 환경 변수 치환 지원.
- `doc/` 신규 추가(오프라인 문서).
- `testcase/visualize/README.md`, `web-dashboard/backend/testcase/README.md` 신규 추가.

## 사용 가이드
- Backend 구동
  - `HOST=0.0.0.0 PORT=8000 ALLOWED_ORIGINS=http://127.0.0.1:3000 python web-dashboard/backend/app.py`
- 오프라인 문서 확인
  - `http://<HOST>:<PORT>/api/docs/owasp/A03`
  - `http://<HOST>:<PORT>/api/docs/cwe/CWE-89`
- Visualize CLI 예시
  - `python -m visualize.cli graph --project-id 1 --export-mermaid ./outputs/graph.md`

## 주의/한계
- `config/config.yaml` 내 `vllm_endpoint` 등은 실제 코드 사용 부위가 없어 런타임 영향 없음. 필요 시 `${VLLM_ENDPOINT}`로 교체하여 환경 변수로 일원화 가능(현재는 보수적으로 유지).
- 프런트엔드(React) 개발 서버(3000/5173) CORS 허용은 운영 환경에서 필요한 Origin만 설정 바람.

## 차후 개선 제안
- `/api/open/owasp/{code}`도 로컬 우선 동작으로 전환(현재는 호환 목적 유지).
- 문서 자동 갱신 파이프라인(OWASP 최신 버전 반영) 구축.
- API/CLI에 `--api-base` 등 명시적 파라미터 제공하여 URL 생성 일원화.
