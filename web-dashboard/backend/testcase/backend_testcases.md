# Web Dashboard Backend Testcases

본 문서는 웹 대시보드 백엔드 API의 기능 검증을 위한 테스트 시나리오입니다.

## 1. API 테스트 환경 설정

### 1.1. 사전 준비
- Python 3.10+
- FastAPI 및 관련 dependencies 설치
- Phase1 분석 완료 (metadata.db 존재)
- 테스트 데이터 준비

### 1.2. 서버 실행
```bash
cd web-dashboard/backend
python app.py
```

기대 결과: 
- 서버가 정상적으로 시작됨
- OpenAPI 문서가 `/docs`에서 접근 가능

## 2. 기본 API 테스트

### 2.1. TC_API_001_HealthCheck: 헬스체크 테스트

---
name: 2.1. TC_API_001_HealthCheck: 헬스체크 테스트
kind: http_get
input: http://127.0.0.1:8000/api/health
expected:
  status_code: 200
---
### 2.2. TC_API_002_ProjectList: 프로젝트 목록 조회

---
name: 2.2. TC_API_002_ProjectList: 프로젝트 목록 조회
kind: http_get
input: http://127.0.0.1:8000/api/projects
expected:
  status_code: 200
---
### 2.3. TC_API_003_ProjectDetails: 프로젝트 상세 정보

---
name: 2.3. TC_API_003_ProjectDetails: 프로젝트 상세 정보
kind: http_get
input: http://127.0.0.1:8000/api/projects/{project_id}
expected:
  status_code: 200
---
### 3.1. TC_META_001_FileList: 파일 목록 조회

---
name: 3.1. TC_META_001_FileList: 파일 목록 조회
kind: http_get
input: http://127.0.0.1:8000/api/projects/{project_id}/files
expected:
  status_code: 200
---
### 3.2. TC_META_002_SQLUnits: SQL 단위 조회

---
name: 3.2. TC_META_002_SQLUnits: SQL 단위 조회
kind: http_get
input: http://127.0.0.1:8000/api/projects/{project_id}/sql-units
expected:
  status_code: 200
---
### 3.3. TC_META_003_Dependencies: 의존성 관계 조회

---
name: 3.3. TC_META_003_Dependencies: 의존성 관계 조회
kind: http_get
input: http://127.0.0.1:8000/api/projects/{project_id}/dependencies
expected:
  status_code: 200
---
### 4.1. TC_VIS_001_ERDData: ERD 데이터 조회

---
name: 4.1. TC_VIS_001_ERDData: ERD 데이터 조회
kind: http_get
input: http://127.0.0.1:8000/api/projects/{project_id}/erd-data
expected:
  status_code: 200
---
### 4.2. TC_VIS_002_GraphData: 그래프 데이터 조회

---
name: 4.2. TC_VIS_002_GraphData: 그래프 데이터 조회
kind: http_get
input: http://127.0.0.1:8000/api/projects/{project_id}/graph-data
expected:
  status_code: 200
---
### 4.3. TC_VIS_003_ComponentData: 컴포넌트 데이터 조회

---
name: 4.3. TC_VIS_003_ComponentData: 컴포넌트 데이터 조회
kind: http_get
input: http://127.0.0.1:8000/api/projects/{project_id}/component-data
expected:
  status_code: 200
---
### 5.1. TC_CONF_001_GroundTruthList: 그라운드 트루스 목록 조회

---
name: 5.1. TC_CONF_001_GroundTruthList: 그라운드 트루스 목록 조회
kind: http_get
input: http://127.0.0.1:8000/api/ground-truth
expected:
  status_code: 200
---
### 5.2. TC_CONF_002_GroundTruthCreate: 그라운드 트루스 생성

---
name: 5.2. TC_CONF_002_GroundTruthCreate: 그라운드 트루스 생성
kind: http_get
input: http://127.0.0.1:8000/api/ground-truth
expected:
  status_code: 200
---
### 5.3. TC_CONF_003_ValidationRun: 신뢰도 검증 실행

---
name: 5.3. TC_CONF_003_ValidationRun: 신뢰도 검증 실행
kind: http_get
input: http://127.0.0.1:8000/api/projects/{project_id}/validate-confidence
expected:
  status_code: 200
---
### 5.4. TC_CONF_004_ValidationResults: 검증 결과 조회

---
name: 5.4. TC_CONF_004_ValidationResults: 검증 결과 조회
kind: http_get
input: http://127.0.0.1:8000/api/projects/{project_id}/validation-results
expected:
  status_code: 200
---
### 6.1. TC_WS_001_Connection: WebSocket 연결
- **목적**: WebSocket 연결이 정상적으로 설정되는지 확인
- **엔드포인트**: `WS /ws/{client_id}`
- **기대 결과**: 연결 성공 및 초기 메시지 수신

### 6.2. TC_WS_002_RealTimeUpdates: 실시간 업데이트
- **목적**: 분석 진행 상황이 실시간으로 전달되는지 확인
- **전제 조건**: WebSocket 연결 설정
- **기대 결과**: 분석 진행률 및 상태 업데이트 실시간 수신

## 7. 에러 처리 테스트

### 7.1. TC_ERR_001_InvalidProject: 존재하지 않는 프로젝트

---
name: 7.1. TC_ERR_001_InvalidProject: 존재하지 않는 프로젝트
kind: http_get
input: http://127.0.0.1:8000/api/projects/999999
expected:
  status_code: 404
---
### 7.2. TC_ERR_002_InvalidParameters: 잘못된 매개변수

---
name: 7.2. TC_ERR_002_InvalidParameters: 잘못된 매개변수
kind: http_get
input: http://127.0.0.1:8000/api/projects/{project_id}/graph-data?min_confidence=invalid
expected:
  status_code: 422
---
### 7.3. TC_ERR_003_DatabaseError: 데이터베이스 에러 처리
- **목적**: 데이터베이스 연결 실패 시 적절한 에러 반환
- **전제 조건**: 데이터베이스 파일 삭제 또는 권한 제거
- **기대 응답**: `500 Internal Server Error` 에러

## 8. 성능 테스트

### 8.1. TC_PERF_001_ResponseTime: 응답 시간 측정
- **목적**: 각 API 엔드포인트의 응답 시간이 허용 범위 내인지 확인
- **기준**: 대부분의 API는 1초 이내, 복잡한 쿼리는 5초 이내
- **측정 방법**: 부하 테스트 도구 사용

### 8.2. TC_PERF_002_ConcurrentUsers: 동시 사용자 테스트
- **목적**: 다수의 동시 사용자 요청을 정상적으로 처리하는지 확인
- **테스트 시나리오**: 10-50명의 동시 사용자 시뮬레이션
- **기대 결과**: 응답 시간 증가 없이 모든 요청 정상 처리

## 9. 보안 테스트

### 9.1. TC_SEC_001_CORS: CORS 설정 확인
- **목적**: CORS 정책이 적절히 설정되어 있는지 확인
- **테스트 방법**: 다양한 Origin에서 API 요청
- **기대 결과**: 허용된 Origin만 접근 가능

### 9.2. TC_SEC_002_InputValidation: 입력 검증
- **목적**: 입력 데이터 검증이 적절히 수행되는지 확인
- **테스트 방법**: SQL Injection, XSS 공격 시도
- **기대 결과**: 악성 입력 차단 및 적절한 에러 반환

## 10. 자동화 테스트

### 10.1. 테스트 스크립트 작성
- pytest를 사용한 자동화 테스트 스크립트 작성
- CI/CD 파이프라인에서 자동 실행

### 10.2. 테스트 데이터 관리
- 테스트용 샘플 데이터베이스 생성
- 테스트 후 데이터 정리 자동화

### 10.3. 커버리지 측정
- 코드 커버리지 80% 이상 달성 목표
- 누락된 테스트 케이스 식별 및 추가
