# Phase1 v6.1 소스 분석기 테스트 케이스

본 문서는 Phase1 v6.1의 주요 개선사항을 검증하기 위한 테스트 케이스를 정의합니다.

## 1. v6.1 주요 개선사항 테스트

### 1.1 MyBatis `<include>` 및 `<bind>` 구문 처리 테스트

**TC_V6_001: MyBatis Include 구문 해결 테스트**
- **목적**: `<include refid="">` 구문이 올바르게 해결되는지 검증
- **테스트 데이터**: `UserMapper.xml`의 `<include refid="userBaseColumns"/>` 패턴
- **기대결과**: 
  - Include가 해결되면 confidence ≥ 0.95
  - 해결되지 않으면 `/* UNRESOLVED INCLUDE: userBaseColumns */`로 마킹
  - SQL fingerprint에 include 내용이 포함됨

**TC_V6_002: MyBatis Bind 변수 추적 테스트**  
- **목적**: `<bind>` 구문으로 선언된 변수가 추적되는지 검증
- **테스트 데이터**: `UserMapper.xml`의 `<bind name="searchPattern" value="'%' + searchKeyword + '%'"/>`
- **기대결과**:
  - Bind 변수 캐시에 변수명, 값, 파일경로, 라인번호 저장
  - SQL에서 `#{searchPattern}` 사용 시 bind 변수로 인식

### 1.2 증분 분석 삭제 파일 처리 테스트

**TC_V6_003: 삭제된 파일 메타데이터 정리 테스트**
- **목적**: 삭제된 파일의 메타데이터가 올바르게 정리되는지 검증
- **테스트 절차**:
  1. 초기 프로젝트 분석 수행
  2. 특정 파일(예: `UserService.java`) 삭제
  3. `--incremental` 플래그로 재분석
- **기대결과**:
  - 삭제된 파일의 File, Class, Method, SqlUnit 레코드 제거
  - 관련 Edge, Join, RequiredFilter 레코드 제거  
  - JSP/MyBatis 파서 캐시에서도 해당 파일 정보 제거

### 1.3 크기 기반 파일 처리 전략 테스트

**TC_V6_004: 파일 크기별 처리 전략 테스트**
- **목적**: 파일 크기에 따른 처리 전략이 올바르게 적용되는지 검증
- **테스트 데이터**:
  - 소형 파일(<50KB): 기본 Java/JSP 파일들
  - 중형 파일(50KB~10MB): 반복 섹션이 추가된 JSP 파일
  - 대형 파일(>10MB): 대량 더미 메서드가 포함된 Java 파일
- **기대결과**:
  - 소형 파일: 항상 해시 계산
  - 중형 파일: mtime 확인 후 필요시 해시 계산  
  - 대형 파일: mtime만 확인

### 1.4 Suspect 마킹 시스템 테스트

**TC_V6_005: 저신뢰도 결과 Suspect 마킹 테스트**
- **목적**: 낮은 신뢰도의 결과가 suspect로 마킹되는지 검증
- **테스트 데이터**: 
  - 리플렉션 사용 메서드 (`processWithReflection`)
  - 동적 SQL 생성 메서드 (`getDynamicUserData`)
- **기대결과**:
  - confidence < 0.3인 결과의 stmt_id에 `_SUSPECT` 접미사 추가
  - 결과는 여전히 DB에 저장됨 (필터링되지 않음)
  - confidence 값이 suspect threshold로 조정됨

### 1.5 설정 가능한 DB 스키마 매칭 테스트

**TC_V6_006: 데이터베이스 스키마 유연화 테스트**
- **목적**: `config.yaml`의 `database.default_schema` 설정이 올바르게 동작하는지 검증
- **테스트 절차**:
  1. `database.default_schema: SAMPLE` 설정
  2. SAMPLE 스키마의 테이블들을 참조하는 SQL 분석
- **기대결과**:
  - 1차: SAMPLE 스키마에서 테이블 검색
  - 2차: 못 찾으면 전역 검색으로 폴백
  - 로그에 스키마 정보 포함된 경고/디버그 메시지 출력

## 2. 샘플 소스 기반 기능 테스트

### 2.1 Java 파일 분석 테스트

**TC_V6_007: 다중 Service 클래스 분석**
- **테스트 대상**: `UserService.java`, `OrderService.java`, `ProductService.java`
- **검증 항목**:
  - 클래스/메서드 메타데이터 추출
  - @Service, @Transactional 등 어노테이션 인식
  - 메서드 간 호출 관계 추적
  - 표준화된 주석과 부실한 주석의 구분

**TC_V6_008: 복잡도 기반 신뢰도 계산**
- **테스트 대상**: `ProductService.processComplexBusiness()` 메서드
- **검증 항목**:
  - 중첩된 조건문으로 인한 복잡도 증가 감지
  - 복잡도에 따른 confidence 감점 적용
  - 이중 루프 등 성능 이슈 패턴 감지

### 2.2 JSP 파일 분석 테스트

**TC_V6_009: JSP Include 의존성 추적**  
- **테스트 대상**: `userList.jsp`, `orderView.jsp`, `productSearch.jsp`
- **검증 항목**:
  - `<%@ include file="/WEB-INF/jsp/_fragments/header.jspf" %>` 관계 추출
  - JSP 파일 간 의존성 Edge 생성
  - Include 경로 해결 정확도

**TC_V6_010: JSP 동적 SQL 및 취약점 탐지**
- **테스트 대상**: JSP 파일들의 동적 SQL 생성 패턴
- **검증 항목**:
  - SQL Injection 취약점 패턴 탐지
  - XSS 취약점 패턴 탐지  
  - 동적 SQL에 대한 낮은 신뢰도 적용

### 2.3 MyBatis XML 분석 테스트

**TC_V6_011: MyBatis Include 및 Bind 통합 테스트**
- **테스트 대상**: `UserMapper.xml`, `OrderMapper.xml`, `ProductMapper.xml`
- **검증 항목**:
  - `<sql id="">` 블록과 `<include refid="">` 해결
  - `<bind>` 변수 선언 및 사용 추적
  - 동적 SQL (`<if>`, `<choose>`, `<foreach>`) 처리

**TC_V6_012: 복잡한 SQL 패턴 분석**
- **테스트 대상**: `ProductMapper.xml`의 `getComplexProductAnalysis`
- **검증 항목**:
  - 10개 테이블 JOIN 조건 추출
  - 서브쿼리 내 테이블 참조 인식
  - 스토어드 함수 호출 감지
  - CTE(Common Table Expression) 처리

### 2.4 데이터베이스 스키마 연동 테스트

**TC_V6_013: 업데이트된 DB 스키마 연동**
- **테스트 대상**: `DB_SCHEMA/` 폴더의 CSV 파일들
- **검증 항목**:
  - SAMPLE 스키마 테이블들의 올바른 로딩
  - PK 정보와 JOIN 조건 매칭
  - 컬럼 타입 및 Nullable 정보 활용

## 3. 성능 및 안정성 테스트

### 3.1 증분 분석 성능 테스트

**TC_V6_014: 크기별 파일 처리 성능**
- **목적**: 파일 크기별 처리 전략의 성능 개선 확인
- **측정 항목**:
  - 소형 파일: 해시 계산 시간
  - 중형 파일: mtime vs 해시 비교 시간  
  - 대형 파일: mtime만 확인하는 시간 단축

### 3.2 메모리 사용량 테스트

**TC_V6_015: MyBatis Include/Bind 캐시 메모리**
- **목적**: 새로 추가된 캐시들의 메모리 사용량 확인
- **측정 항목**:
  - SQL fragment 캐시 크기
  - Bind 변수 캐시 크기
  - 파일 삭제 시 캐시 정리 확인

## 4. 회귀 테스트 (기존 기능 유지 확인)

### 4.1 기본 파싱 기능 회귀 테스트

**TC_V6_016: 기존 Java 파싱 호환성**
- **검증 항목**: 기존 Java 파싱 결과와 동일성
- **테스트 방법**: v5.1 결과와 v6.1 결과 비교

**TC_V6_017: 기존 SQL 파싱 호환성**  
- **검증 항목**: 기존 MyBatis SQL 파싱 결과와 동일성
- **테스트 방법**: v5.1 결과와 v6.1 결과 비교

### 4.2 신뢰도 계산 회귀 테스트

**TC_V6_018: 기존 신뢰도 공식 유지**
- **검증 항목**: suspect 마킹 제외하고 기존 신뢰도 공식 결과 동일성
- **테스트 방법**: 동일 입력에 대한 신뢰도 값 비교

## 5. 종단간(E2E) 통합 테스트

### 5.1 전체 프로젝트 분석 테스트

**TC_V6_019: PROJECT/sampleSrc 전체 분석**
- **목적**: 새로 구성된 샘플 소스 전체가 정상 분석되는지 검증
- **절차**:
  1. 전체 프로젝트 최초 분석
  2. 일부 파일 수정 후 증분 분석
  3. 일부 파일 삭제 후 증분 분석
- **기대결과**: 모든 단계에서 오류 없이 완료

### 5.2 설정 파일 기반 동작 테스트

**TC_V6_020: config.yaml 설정 적용**
- **목적**: 새로 추가된 설정 항목들이 올바르게 동작하는지 검증
- **테스트 설정**:
  - `database.default_schema: SAMPLE`
  - `processing.size_threshold_hash: 51200` (50KB)
  - `processing.size_threshold_mtime: 10485760` (10MB)
  - `processing.confidence_threshold: 0.3`

## 6. 테스트 자동화 및 지속적 검증

### 6.1 회귀 방지 자동화 테스트

**TC_V6_021: 자동화된 결과 비교**
- **목적**: 버전 업그레이드 시 기본 기능 회귀 방지
- **방법**: 
  1. 표준 테스트 프로젝트에 대한 기준 결과 저장
  2. 신규 버전 결과와 자동 비교
  3. 차이점 분석 및 리포트 생성

### 6.2 성능 기준선 테스트

**TC_V6_022: 성능 개선 측정**  
- **목적**: v6.1 개선사항들의 성능 향상 정량 측정
- **측정 항목**:
  - 증분 분석 시간 단축율
  - 메모리 사용량 최적화  
  - 분석 정확도 향상도

이러한 테스트 케이스들을 통해 Phase1 v6.1의 모든 개선사항이 올바르게 구현되었는지 체계적으로 검증할 수 있습니다.