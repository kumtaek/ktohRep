개발내역 03 — 서버 설정(server.debug/CORS/로그) config.yaml 이관
===========================================================

목표
----
- 웹 백엔드(Flask) 실행 파라미터와 CORS/로그 설정을 코드 하드코딩에서 `config/config.yaml`로 이관하여 환경별 운영 편의성/일관성 향상.

주요 변경점
----------
- `config/config.yaml`
  - `server.host`, `server.port`, `server.debug` 추가
  - `server.api_prefix` 추가(예: "/api")
  - `server.cors` 섹션 추가: `enabled`, `allow_origins`, `allow_methods`, `allow_headers`
  - `server.log_file`, `server.log_level` 추가(미설정 시 상위 `logging` 섹션 사용)
  - `server.static` 섹션 추가: `enabled`, `folder`, `url_path`
- `web-dashboard/backend/app.py`
  - 설정 로더가 `${VAR}` 환경변수 치환 후 YAML 파싱하도록 개선
  - `setup_logging()`이 `server.log_file`/`server.log_level`을 우선 사용하도록 개선
  - CORS를 `server.cors` 설정 기반으로 적용(자격증명/노출 헤더 포함)
  - 서버 실행 시 `server.host/port/debug` 사용
  - `server.api_prefix` 기반으로 모든 API 경로 바인딩(`/health`, `/metadata`, `/docs` 등)
  - `server.static` 활성 시, 지정 폴더를 `static_url_path`로 서빙

설정 예시
--------
server:
  host: "127.0.0.1"
  port: 8000
  debug: true
  cors:
    enabled: true
    allow_origins: ["*"]
    allow_methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allow_headers: ["*"]
  log_file: "./logs/backend.log"
  log_level: "DEBUG"

테스트
-----
- config 변경 후 `python web-dashboard/backend/app.py`로 기동 → 지정 포트/호스트로 정상 구동 확인
- CORS를 특정 오리진으로 제한 시, 브라우저 프리플라이트(OPTIONS) 응답 헤더 반영 확인
- 로그 파일 경로/레벨 변경 시 로그 파일 생성 및 레벨 필터링 동작 확인

비고
----
- 백엔드에서 사용하는 DB 매니저 초기화 로직 등은 기존 동작을 유지(별도 개선 이슈에서 다룸)
