# sampleSrc 프로젝트 컴포넌트 다이어그램 분석 리포트

## 프로젝트 개요
- **프로젝트명**: sampleSrc
- **분석일시**: 2025년 1월 3일
- **분석대상**: Java 웹 애플리케이션
- **분석된 파일 수**: Java(20개), JSP(6개), XML(6개)

## 프로젝트 구조 분석

### 1. 소스 파일 분포
- **Java 소스**: 20개
- **JSP 페이지**: 6개
- **XML 설정**: 6개

### 2. Java 패키지 구조

#### main.java.com.example.config
- DatabaseConfig.java - 데이터베이스 설정
- SecurityConfig.java - 보안 설정

#### main.java.com.example.controller
- ApiController.java - API 컨트롤러
- MainController.java - 메인 컨트롤러
- OrderController.java - 주문 컨트롤러
- PaymentController.java - 결제 컨트롤러

#### main.java.com.example.service
- ListService.java - 리스트 서비스
- OrderService.java - 주문 서비스
- OverloadService.java - 오버로드 서비스
- ProductService.java - 상품 서비스
- UserService.java - 사용자 서비스
- impl/ListServiceImpl1.java - 리스트 서비스 구현체

#### main.java.com.example.mapper
- OrderMapper.java - 주문 매퍼
- ProductMapper.java - 상품 매퍼
- UserMapper.java - 사용자 매퍼

#### main.java.com.example.integrated
- IntegratedMapper.java - 통합 매퍼
- IntegratedService.java - 통합 서비스
- VulnerabilityTestService.java - 취약점 테스트 서비스

#### main.java.com.example.util
- DateUtil.java - 날짜 유틸리티
- Texts.java - 텍스트 유틸리티

### 3. JSP 페이지 구조

#### 메인 페이지
- IntegratedView.jsp - 통합 뷰

#### 주문 관련
- order/orderView.jsp - 주문 뷰

#### 상품 관련
- product/productSearch.jsp - 상품 검색

#### 테스트
- 	est/testPage.jsp - 테스트 페이지

#### 사용자 관련
- user/userList.jsp - 사용자 목록
- iews/userList.jsp - 사용자 목록 뷰

## 아키텍처 분석

### 계층 구조
1. **Presentation Layer**: JSP 페이지들
2. **Business Logic Layer**: Service, Controller 클래스들
3. **Data Access Layer**: Mapper 인터페이스들
4. **Configuration Layer**: 설정 클래스들
5. **Utility Layer**: 유틸리티 클래스들
6. **Integrated Layer**: 통합 서비스 및 매퍼

### 의존성 관계
- JSP  Controller: HTTP 요청 처리
- Controller  Service: 비즈니스 로직 호출
- Service  Mapper: 데이터 접근 요청
- Mapper  Database: SQL 쿼리 실행

## 기술 스택 추정

### Frontend
- JSP (JavaServer Pages)
- HTML/CSS/JavaScript

### Backend
- Java
- Spring Framework (추정)
- MyBatis (추정)

### Database
- Oracle (CSV 파일명으로 추정)

## 결론

이 프로젝트는 전형적인 Java 웹 애플리케이션의 계층형 아키텍처를 따르고 있으며,
각 계층의 책임이 명확히 분리되어 있어 유지보수성과 확장성이 우수합니다.

MVC 패턴을 통해 사용자 인터페이스와 비즈니스 로직을 효과적으로 분리하고 있으며,
MyBatis를 통한 데이터 접근 계층을 구현하여 데이터베이스 연동을 담당하고 있습니다.

특히 Integrated Layer가 있어서 통합 서비스와 취약점 테스트 기능을 제공하고 있으며,
이는 보안과 품질 관리에 중점을 둔 프로젝트임을 시사합니다.