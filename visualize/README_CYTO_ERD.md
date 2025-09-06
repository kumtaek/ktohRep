# Cytoscape.js ERD 사용법

## 개요

Cytoscape.js를 사용한 향상된 ERD(Entity Relationship Diagram) 시각화 도구입니다. 기존 ERD 빌더와 연동하여 인터랙티브한 데이터베이스 관계 다이어그램을 생성합니다.

## 주요 기능

### 🎨 시각화 기능
- **인터랙티브 노드**: 테이블을 클릭하여 선택, 하이라이트
- **동적 레이아웃**: fcose, dagre 레이아웃 전환
- **반응형 디자인**: 모바일/데스크톱 환경 지원
- **고품질 렌더링**: 벡터 기반 그래프 렌더링

### 🔍 탐색 기능
- **테이블 검색**: 이름, 스키마별 빠른 검색
- **스키마 필터링**: 특정 스키마만 표시
- **관계 하이라이트**: 선택된 테이블의 관련 요소 강조
- **사이드바 패널**: 테이블 목록 및 통계 정보

### 📊 정보 표시
- **상세 툴팁**: 컬럼 정보, 데이터 타입, 제약조건
- **관계 정보**: 조인 조건, 빈도, 신뢰도
- **통계 대시보드**: 테이블 수, 컬럼 수, 관계 수
- **범례**: 관계 유형별 색상 구분

## 사용법

### 1. CLI를 통한 생성

```bash
# 기본 ERD와 함께 Cytoscape.js ERD 생성
python -m visualize erd sampleSrc --cytoscape

# 특정 테이블만 포함하여 생성
python -m visualize erd sampleSrc --tables "USERS,ORDERS" --cytoscape

# 특정 스키마만 포함하여 생성
python -m visualize erd sampleSrc --owners "HR,ADMIN" --cytoscape
```

### 2. Python 코드를 통한 직접 생성

```python
from visualize.renderers.cytoscape_erd_renderer import create_cytoscape_erd

# ERD 데이터 생성 (기존 빌더 사용)
erd_data = build_erd_json(config, project_id, project_name)

# Cytoscape.js ERD 생성
output_path = create_cytoscape_erd(erd_data, project_name, output_dir)
```

### 3. 테스트 실행

```bash
# 테스트 스크립트 실행
python test_cytoscape_erd.py
```

## 파일 구조

```
visualize/
├── templates/
│   └── erd_cytoscape.html      # Cytoscape.js HTML 템플릿
├── renderers/
│   └── cytoscape_erd_renderer.py  # ERD 렌더러
└── cli.py                      # CLI 명령어 (--cytoscape 옵션 추가)
```

## 생성되는 파일

- **파일명**: `erd_cytoscape_YYYYMMDD_HHMMSS.html`
- **위치**: `./project/{프로젝트명}/report/`
- **형식**: 독립 실행 가능한 HTML 파일

## 기술 스택

### Frontend
- **Cytoscape.js 3.28.1**: 그래프 시각화 엔진
- **cytoscape-dagre**: 계층적 레이아웃
- **cytoscape-fcose**: 강제 기반 레이아웃
- **jQuery 3.6.0**: DOM 조작 및 이벤트 처리

### Features
- **반응형 CSS**: 모바일 친화적 디자인
- **CSS Grid/Flexbox**: 현대적 레이아웃 시스템
- **CSS Variables**: 테마 및 색상 관리
- **CSS Animations**: 부드러운 전환 효과

## 레이아웃 옵션

### fcose (Force-Controlled Spacing)
- **장점**: 자연스러운 노드 배치, 자동 겹침 방지
- **설정**: 고품질 모드, 2500회 반복
- **적용**: 대규모 그래프, 복잡한 관계

### dagre (Directed Acyclic Graph)
- **장점**: 계층적 구조, 명확한 방향성
- **설정**: Top-to-Bottom 방향, 최장 경로 기반
- **적용**: 의존성 관계, 순서가 중요한 구조

## 관계 유형별 스타일

| 관계 유형 | 색상 | 화살표 | 설명 |
|-----------|------|--------|------|
| `foreign_key` | 🔴 빨강 | ▶️ | 외래키 관계 |
| `fk_inferred` | 🟠 주황 | ▶️ | 추론된 FK 관계 |
| `pk_to_pk` | 🔵 파랑 | ▶️ | PK-PK 관계 |
| `relationship` | ⚫ 회색 | ❌ | 일반 관계 |

## 사용자 인터페이스

### 헤더 영역
- 프로젝트 정보 및 통계 표시
- 테이블 수, 관계 수 실시간 업데이트

### 툴바
- 레이아웃 전환 (fcose ↔ dagre)
- 검색 기능
- 전체보기, PNG 내보내기
- 사이드바 토글

### 사이드바
- **테이블 목록**: 클릭 가능한 테이블 목록
- **필터링**: 스키마별 필터링
- **통계**: 상세 통계 정보

### 메인 캔버스
- Cytoscape.js 그래프 영역
- 줌, 팬, 선택 기능
- 우클릭 컨텍스트 메뉴

## 상호작용

### 마우스 조작
- **클릭**: 노드 선택
- **더블클릭**: 노드 편집 (향후 기능)
- **드래그**: 노드 이동
- **휠**: 줌 인/아웃
- **우클릭**: 컨텍스트 메뉴

### 키보드 단축키
- **Ctrl+A**: 전체 선택
- **Delete**: 선택된 요소 삭제 (향후 기능)
- **Escape**: 선택 해제

## 성능 최적화

### 렌더링 최적화
- **노드 제한**: 기본 최대 1000개 노드
- **레이아웃 캐싱**: 레이아웃 결과 재사용
- **점진적 로딩**: 대용량 데이터 점진적 표시

### 메모리 관리
- **이벤트 정리**: 불필요한 이벤트 리스너 제거
- **DOM 정리**: 툴팁 및 모달 자동 정리
- **가비지 컬렉션**: 메모리 누수 방지

## 오프라인 지원

### CDN 의존성
- **Cytoscape.js**: CDN에서 로드
- **jQuery**: CDN에서 로드
- **레이아웃 확장**: CDN에서 로드

### 오프라인 대응
- **로컬 파일**: 모든 라이브러리를 로컬에 다운로드
- **번들링**: Webpack 등으로 번들링 가능
- **PWA**: Progressive Web App으로 변환 가능

## 확장 가능성

### 플러그인 시스템
- **커스텀 레이아웃**: 새로운 레이아웃 알고리즘 추가
- **커스텀 스타일**: 노드/엣지 스타일 커스터마이징
- **커스텀 툴**: 추가 분석 도구 통합

### 데이터 소스
- **실시간 데이터**: WebSocket을 통한 실시간 업데이트
- **외부 API**: REST API 연동
- **데이터베이스**: 직접 데이터베이스 연결

## 문제 해결

### 일반적인 문제

#### 1. 그래프가 표시되지 않음
```bash
# 브라우저 콘솔 확인
# JavaScript 오류 메시지 확인
# 네트워크 탭에서 CDN 로딩 상태 확인
```

#### 2. 레이아웃이 이상함
```bash
# 레이아웃 전환 시도
# 브라우저 새로고침
# 노드 수가 너무 많은 경우 제한 설정
```

#### 3. 성능 문제
```bash
# 노드 수 제한 (--max-nodes 옵션)
# 레이아웃 품질 조정 (quality: 'draft')
# 애니메이션 비활성화
```

### 디버깅 모드
```bash
# 상세 로그 활성화
python -m visualize erd sampleSrc --cytoscape --verbose 2

# 로그 파일 저장
python -m visualize erd sampleSrc --cytoscape --log-file debug.log
```

## 라이선스

- **Cytoscape.js**: MIT License
- **cytoscape-dagre**: MIT License  
- **cytoscape-fcose**: MIT License
- **jQuery**: MIT License

모든 라이브러리는 기업 내 무료 사용이 가능합니다.

## 지원 및 문의

- **이슈 리포트**: GitHub Issues
- **기능 요청**: Feature Request 라벨
- **버그 리포트**: Bug 라벨
- **문서 개선**: Documentation 라벨

## 변경 이력

### v1.0.0 (2024-12-19)
- 초기 Cytoscape.js ERD 구현
- fcose, dagre 레이아웃 지원
- 인터랙티브 툴팁 및 사이드바
- 반응형 디자인 및 모바일 지원
- CLI 통합 (--cytoscape 옵션)
