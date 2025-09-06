"""
신규입사자 온보딩을 위한 지능적 청킹 시스템
비즈니스 맥락과 이해하기 쉬운 단위로 코드를 청킹
"""

import re
import logging
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from pathlib import Path

from phase1.llm.intelligent_chunker import IntelligentChunker, CodeChunk

logger = logging.getLogger(__name__)

@dataclass
class OnboardingChunk:
    """신규입사자를 위한 확장된 청크 정보"""
    chunk_type: str
    name: str
    content: str
    start_line: int
    end_line: int
    context: str
    metadata: Dict
    
    # 신규입사자를 위한 추가 필드
    business_purpose: str  # 비즈니스 목적
    complexity_level: str  # 복잡도 (beginner/intermediate/advanced)
    learning_priority: int  # 학습 우선순위 (1-5)
    related_concepts: List[str]  # 관련 개념들
    explanation: str  # 초보자를 위한 설명

class OnboardingChunker(IntelligentChunker):
    """신규입사자 온보딩을 위한 청킹 시스템"""
    
    def __init__(self):
        super().__init__()
        
        # 학습 우선순위 정의
        self.learning_priorities = {
            'controller_entry': 5,  # 가장 높음 - 진입점
            'main_service': 4,      # 주요 비즈니스 로직
            'data_model': 4,        # 데이터 구조
            'repository': 3,        # 데이터 접근
            'utility': 2,           # 유틸리티
            'config': 1             # 설정 (가장 낮음)
        }
        
        # 복잡도 분석 기준
        self.complexity_indicators = {
            'beginner': {
                'max_lines': 30,
                'max_methods': 5,
                'has_loops': False,
                'has_exceptions': False,
                'has_generics': False
            },
            'intermediate': {
                'max_lines': 100,
                'max_methods': 15,
                'has_loops': True,
                'has_exceptions': True,
                'has_generics': True
            }
        }
        
        # 비즈니스 맥락 설명 템플릿
        self.explanation_templates = {
            'controller': "사용자 요청을 받아서 처리하고 응답을 반환하는 웹 컨트롤러입니다.",
            'service': "핵심 비즈니스 로직을 처리하는 서비스 클래스입니다.",
            'repository': "데이터베이스와 상호작용하여 데이터를 저장/조회하는 클래스입니다.",
            'model': "데이터의 구조를 정의하는 모델 클래스입니다.",
            'config': "시스템 설정을 관리하는 설정 클래스입니다.",
            'util': "공통으로 사용되는 유틸리티 기능을 제공하는 클래스입니다."
        }

    def create_onboarding_chunks(self, file_path: str, content: str) -> List[OnboardingChunk]:
        """신규입사자를 위한 청크 생성"""
        
        # 기본 청크 생성
        basic_chunks = self.chunk_file(file_path, content)
        
        # 온보딩용 청크로 변환
        onboarding_chunks = []
        for chunk in basic_chunks:
            onboarding_chunk = self._enhance_chunk_for_onboarding(chunk, file_path, content)
            onboarding_chunks.append(onboarding_chunk)
        
        # 학습 우선순위로 정렬
        onboarding_chunks.sort(key=lambda x: x.learning_priority, reverse=True)
        
        return onboarding_chunks

    def _enhance_chunk_for_onboarding(self, chunk: CodeChunk, file_path: str, full_content: str) -> OnboardingChunk:
        """기본 청크를 온보딩용으로 확장"""
        
        # 비즈니스 목적 분석
        business_purpose = self._analyze_business_purpose(chunk, full_content)
        
        # 복잡도 분석
        complexity_level = self._analyze_complexity(chunk)
        
        # 학습 우선순위 계산
        learning_priority = self._calculate_learning_priority(chunk, file_path)
        
        # 관련 개념 추출
        related_concepts = self._extract_related_concepts(chunk, full_content)
        
        # 초보자용 설명 생성
        explanation = self._generate_explanation(chunk, business_purpose)
        
        return OnboardingChunk(
            chunk_type=chunk.chunk_type,
            name=chunk.name,
            content=chunk.content,
            start_line=chunk.start_line,
            end_line=chunk.end_line,
            context=chunk.context,
            metadata=chunk.metadata,
            business_purpose=business_purpose,
            complexity_level=complexity_level,
            learning_priority=learning_priority,
            related_concepts=related_concepts,
            explanation=explanation
        )

    def _analyze_business_purpose(self, chunk: CodeChunk, content: str) -> str:
        """청크의 비즈니스 목적 분석"""
        
        chunk_lower = chunk.name.lower()
        content_lower = content.lower()
        
        # 컨트롤러 패턴
        if any(pattern in content for pattern in ['@Controller', '@RestController', '@RequestMapping']):
            if 'user' in chunk_lower:
                return "사용자 관리 웹 API를 제공합니다"
            elif 'order' in chunk_lower:
                return "주문 처리 웹 API를 제공합니다"
            elif 'product' in chunk_lower:
                return "상품 관리 웹 API를 제공합니다"
            else:
                return "웹 요청을 처리하고 응답을 반환합니다"
        
        # 서비스 패턴
        elif any(pattern in content for pattern in ['@Service', '@Component']):
            if 'user' in chunk_lower:
                return "사용자 관련 비즈니스 로직을 처리합니다"
            elif 'order' in chunk_lower:
                return "주문 처리 비즈니스 로직을 담당합니다"
            elif 'product' in chunk_lower:
                return "상품 관리 비즈니스 로직을 수행합니다"
            else:
                return "핵심 비즈니스 로직을 처리합니다"
        
        # 매퍼/리포지토리 패턴
        elif any(pattern in content for pattern in ['@Repository', '@Mapper']) or 'mapper' in chunk_lower:
            return "데이터베이스 접근 및 데이터 조작을 담당합니다"
        
        # 모델/엔티티 패턴
        elif chunk.chunk_type in ['class'] and ('model' in chunk_lower or 'entity' in chunk_lower):
            return "데이터 구조와 비즈니스 객체를 정의합니다"
        
        # 메서드별 분석
        elif chunk.chunk_type == 'method':
            return self._analyze_method_purpose(chunk.name)
        
        else:
            return "시스템 기능을 지원합니다"

    def _analyze_method_purpose(self, method_name: str) -> str:
        """메서드의 목적 분석"""
        method_lower = method_name.lower()
        
        # CRUD 패턴
        if any(word in method_lower for word in ['create', 'insert', 'add', 'register', 'save']):
            return "새로운 데이터를 생성하거나 저장합니다"
        elif any(word in method_lower for word in ['get', 'find', 'select', 'search', 'list']):
            return "데이터를 조회하거나 검색합니다"
        elif any(word in method_lower for word in ['update', 'modify', 'edit', 'change']):
            return "기존 데이터를 수정하거나 업데이트합니다"
        elif any(word in method_lower for word in ['delete', 'remove', 'drop']):
            return "데이터를 삭제하거나 제거합니다"
        
        # 비즈니스 액션
        elif any(word in method_lower for word in ['login', 'authenticate', 'auth']):
            return "사용자 인증을 처리합니다"
        elif any(word in method_lower for word in ['validate', 'verify', 'check']):
            return "데이터 유효성을 검증합니다"
        elif any(word in method_lower for word in ['send', 'notify', 'email']):
            return "알림이나 메시지를 전송합니다"
        elif any(word in method_lower for word in ['calculate', 'compute', 'process']):
            return "계산이나 데이터 처리를 수행합니다"
        
        else:
            return "특정 기능을 수행합니다"

    def _analyze_complexity(self, chunk: CodeChunk) -> str:
        """청크의 복잡도 분석"""
        content = chunk.content
        lines = content.split('\n')
        line_count = len(lines)
        
        # 메서드 개수 계산
        method_count = len(re.findall(r'public\s+\w+\s+\w+\s*\(', content))
        
        # 복잡도 지표 확인
        has_loops = bool(re.search(r'\b(for|while|do)\b', content))
        has_exceptions = bool(re.search(r'\b(try|catch|throw)\b', content))
        has_generics = bool(re.search(r'<\w+>', content))
        has_annotations = bool(re.search(r'@\w+', content))
        has_conditionals = len(re.findall(r'\b(if|else|switch)\b', content))
        
        # 복잡도 점수 계산
        complexity_score = 0
        
        if line_count > 100:
            complexity_score += 3
        elif line_count > 50:
            complexity_score += 2
        elif line_count > 20:
            complexity_score += 1
        
        if method_count > 10:
            complexity_score += 2
        elif method_count > 5:
            complexity_score += 1
        
        if has_loops:
            complexity_score += 1
        if has_exceptions:
            complexity_score += 1
        if has_generics:
            complexity_score += 1
        if has_conditionals > 5:
            complexity_score += 1
        
        # 복잡도 레벨 결정
        if complexity_score <= 2:
            return 'beginner'
        elif complexity_score <= 5:
            return 'intermediate'
        else:
            return 'advanced'

    def _calculate_learning_priority(self, chunk: CodeChunk, file_path: str) -> int:
        """학습 우선순위 계산"""
        
        chunk_lower = chunk.name.lower()
        file_name = Path(file_path).name.lower()
        
        # 파일 타입별 기본 우선순위
        if 'controller' in file_name:
            base_priority = self.learning_priorities['controller_entry']
        elif 'service' in file_name:
            base_priority = self.learning_priorities['main_service']
        elif 'mapper' in file_name or 'repository' in file_name:
            base_priority = self.learning_priorities['repository']
        elif 'model' in file_name or 'entity' in file_name:
            base_priority = self.learning_priorities['data_model']
        elif 'config' in file_name:
            base_priority = self.learning_priorities['config']
        else:
            base_priority = self.learning_priorities['utility']
        
        # 메서드 타입별 가중치
        if chunk.chunk_type == 'method':
            if any(word in chunk_lower for word in ['main', 'process', 'handle']):
                base_priority += 1  # 주요 메서드
            elif any(word in chunk_lower for word in ['get', 'find', 'list']):
                base_priority += 0  # 조회 메서드 (평균)
            elif chunk_lower.startswith('_') or 'helper' in chunk_lower:
                base_priority -= 1  # 헬퍼 메서드
        
        return max(1, min(5, base_priority))  # 1-5 범위로 제한

    def _extract_related_concepts(self, chunk: CodeChunk, content: str) -> List[str]:
        """관련 개념 추출"""
        concepts = []
        
        # 기술적 개념
        if '@Autowired' in content or '@Inject' in content:
            concepts.append('의존성 주입(Dependency Injection)')
        if '@Transactional' in content:
            concepts.append('트랜잭션 관리')
        if re.search(r'@RequestMapping|@GetMapping|@PostMapping', content):
            concepts.append('REST API')
        if 'List<' in content or 'Map<' in content:
            concepts.append('컬렉션 프레임워크')
        if 'try' in content and 'catch' in content:
            concepts.append('예외 처리')
        
        # 비즈니스 개념
        chunk_lower = chunk.name.lower()
        if 'user' in chunk_lower:
            concepts.append('사용자 관리')
        if 'order' in chunk_lower:
            concepts.append('주문 처리')
        if 'product' in chunk_lower:
            concepts.append('상품 관리')
        if 'payment' in chunk_lower:
            concepts.append('결제 시스템')
        
        # 아키텍처 개념
        if chunk.chunk_type == 'class':
            if 'Controller' in chunk.name:
                concepts.append('MVC 패턴 - Controller')
            elif 'Service' in chunk.name:
                concepts.append('MVC 패턴 - Service Layer')
            elif 'Mapper' in chunk.name or 'Repository' in chunk.name:
                concepts.append('데이터 액세스 객체(DAO)')
        
        return concepts

    def _generate_explanation(self, chunk: CodeChunk, business_purpose: str) -> str:
        """초보자를 위한 설명 생성"""
        
        explanation_parts = []
        
        # 기본 설명
        if chunk.chunk_type == 'class':
            explanation_parts.append(f"이 클래스는 {business_purpose}.")
            
            # 클래스 타입별 설명 추가
            chunk_lower = chunk.name.lower()
            if 'controller' in chunk_lower:
                explanation_parts.append("웹 브라우저나 모바일 앱에서 오는 요청을 받아서 처리합니다.")
            elif 'service' in chunk_lower:
                explanation_parts.append("실제 업무 규칙과 로직이 구현되어 있는 핵심 부분입니다.")
            elif 'mapper' in chunk_lower:
                explanation_parts.append("데이터베이스와 자바 객체 사이의 데이터 변환을 담당합니다.")
                
        elif chunk.chunk_type == 'method':
            explanation_parts.append(f"이 메서드는 {business_purpose}.")
            
            # 메서드 복잡도에 따른 추가 설명
            if len(chunk.content.split('\n')) > 30:
                explanation_parts.append("코드가 다소 길어서 천천히 읽어보시기 바랍니다.")
                
        elif chunk.chunk_type == 'query':
            explanation_parts.append("이 SQL 쿼리는 데이터베이스에서 데이터를 조작하는 명령어입니다.")
            
        # 학습 팁 추가
        if chunk.chunk_type in ['class', 'method']:
            if any(word in chunk.content for word in ['@Autowired', '@Inject']):
                explanation_parts.append("다른 클래스에 의존하고 있으니 연관된 클래스들도 함께 보시면 이해하기 쉽습니다.")
        
        return ' '.join(explanation_parts)

    def generate_learning_sequence(self, chunks: List[OnboardingChunk]) -> List[List[OnboardingChunk]]:
        """학습 순서 생성 - 단계별로 그룹화"""
        
        # 단계별 그룹화
        phases = {
            'phase1_overview': [],      # 1단계: 전체 개요
            'phase2_controllers': [],   # 2단계: 진입점 (Controllers)
            'phase3_services': [],      # 3단계: 비즈니스 로직
            'phase4_data': [],          # 4단계: 데이터 처리
            'phase5_details': []        # 5단계: 세부 구현
        }
        
        for chunk in chunks:
            chunk_lower = chunk.name.lower()
            
            if chunk.complexity_level == 'beginner' and chunk.learning_priority >= 4:
                phases['phase1_overview'].append(chunk)
            elif 'controller' in chunk_lower:
                phases['phase2_controllers'].append(chunk)
            elif 'service' in chunk_lower:
                phases['phase3_services'].append(chunk)
            elif any(word in chunk_lower for word in ['mapper', 'repository', 'model']):
                phases['phase4_data'].append(chunk)
            else:
                phases['phase5_details'].append(chunk)
        
        return [group for group in phases.values() if group]