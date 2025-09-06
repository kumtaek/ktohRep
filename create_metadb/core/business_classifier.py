"""
비즈니스 분류기

코드 컴포넌트를 비즈니스 도메인, 아키텍처 레이어, 기능 카테고리로 분류합니다.
"""

import re
import logging
from typing import Dict, List, Any
from pathlib import Path

class BusinessClassifier:
    """비즈니스 분류기"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"BusinessClassifier")
        
        # 분류 규칙 정의
        self.classification_rules = {
            'architecture_layers': {
                'controller': [r'.*Controller\.java$', r'.*Controller\.jsp$'],
                'service': [r'.*Service\.java$', r'.*ServiceImpl\.java$'],
                'repository': [r'.*Repository\.java$', r'.*Mapper\.java$', r'.*DAO\.java$'],
                'entity': [r'.*Entity\.java$', r'.*Model\.java$', r'.*VO\.java$', r'.*DTO\.java$'],
                'config': [r'.*Config\.java$', r'.*Configuration\.java$'],
                'util': [r'.*Util\.java$', r'.*Helper\.java$', r'.*Common\.java$']
            },
            'business_domains': {
                'user_management': [r'.*User.*', r'.*Member.*', r'.*Account.*'],
                'order_processing': [r'.*Order.*', r'.*Purchase.*', r'.*Payment.*'],
                'product_management': [r'.*Product.*', r'.*Item.*', r'.*Goods.*'],
                'inventory_management': [r'.*Inventory.*', r'.*Stock.*', r'.*Warehouse.*'],
                'authentication': [r'.*Auth.*', r'.*Login.*', r'.*Security.*'],
                'notification': [r'.*Notification.*', r'.*Alert.*', r'.*Message.*'],
                'reporting': [r'.*Report.*', r'.*Statistics.*', r'.*Analytics.*']
            },
            'functional_categories': {
                'crud': [r'.*Controller\.java$', r'.*Service\.java$', r'.*Mapper\.java$'],
                'search': [r'.*Search.*', r'.*Find.*', r'.*Query.*'],
                'authentication': [r'.*Auth.*', r'.*Login.*', r'.*Security.*'],
                'validation': [r'.*Validator.*', r'.*Validation.*', r'.*Check.*'],
                'conversion': [r'.*Converter.*', r'.*Transformer.*', r'.*Mapper.*'],
                'notification': [r'.*Notification.*', r'.*Email.*', r'.*SMS.*']
            }
        }
        
        # 복잡도 분석 규칙
        self.complexity_rules = {
            'beginner': {
                'max_methods': 5,
                'max_lines': 100,
                'patterns': [r'.*Entity\.java$', r'.*VO\.java$', r'.*DTO\.java$']
            },
            'intermediate': {
                'max_methods': 15,
                'max_lines': 300,
                'patterns': [r'.*Service\.java$', r'.*Controller\.java$']
            },
            'advanced': {
                'max_methods': 999,
                'max_lines': 999,
                'patterns': [r'.*Config\.java$', r'.*Util\.java$', r'.*Helper\.java$']
            }
        }
    
    def classify_components(self, chunks: List[Dict]) -> List[Dict]:
        """컴포넌트들을 비즈니스 관점에서 분류"""
        classifications = []
        
        for chunk in chunks:
            try:
                classification = self._classify_single_component(chunk)
                if classification:
                    classifications.append(classification)
            except Exception as e:
                self.logger.error(f"컴포넌트 분류 실패 {chunk.get('name', 'unknown')}: {e}")
                continue
        
        self.logger.info(f"비즈니스 분류 완료: {len(classifications)}개")
        return classifications
    
    def _classify_single_component(self, chunk: Dict) -> Dict:
        """단일 컴포넌트 분류"""
        component_name = chunk.get('name', '')
        file_path = chunk.get('file_path', '')
        component_type = chunk.get('type', '')
        
        # 아키텍처 레이어 분류
        architecture_layer = self._classify_architecture_layer(file_path, component_name)
        
        # 비즈니스 도메인 분류
        business_domain = self._classify_business_domain(component_name, file_path)
        
        # 기능 카테고리 분류
        functional_category = self._classify_functional_category(file_path, component_name)
        
        # 복잡도 분석
        complexity_level = self._analyze_complexity(chunk)
        
        # 학습 우선순위 결정
        learning_priority = self._determine_learning_priority(
            architecture_layer, business_domain, complexity_level
        )
        
        return {
            'component_type': component_type,
            'component_id': chunk.get('id', 0),
            'component_name': component_name,
            'business_domain': business_domain,
            'architecture_layer': architecture_layer,
            'functional_category': functional_category,
            'complexity_level': complexity_level,
            'learning_priority': learning_priority,
            'hash_value': chunk.get('hash_value', '')
        }
    
    def _classify_architecture_layer(self, file_path: str, component_name: str) -> str:
        """아키텍처 레이어 분류"""
        file_name = Path(file_path).name
        
        for layer, patterns in self.classification_rules['architecture_layers'].items():
            for pattern in patterns:
                if re.search(pattern, file_name, re.IGNORECASE):
                    return layer
        
        # 기본값: 파일 확장자 기반
        if file_path.endswith('.java'):
            return 'service'  # 기본값
        elif file_path.endswith('.jsp'):
            return 'view'
        elif file_path.endswith('.xml'):
            return 'config'
        else:
            return 'unknown'
    
    def _classify_business_domain(self, component_name: str, file_path: str) -> str:
        """비즈니스 도메인 분류"""
        # 컴포넌트명과 파일 경로를 모두 검사
        search_text = f"{component_name} {file_path}"
        
        for domain, patterns in self.classification_rules['business_domains'].items():
            for pattern in patterns:
                if re.search(pattern, search_text, re.IGNORECASE):
                    return domain
        
        return 'general'  # 기본값
    
    def _classify_functional_category(self, file_path: str, component_name: str) -> str:
        """기능 카테고리 분류"""
        file_name = Path(file_path).name
        search_text = f"{component_name} {file_name}"
        
        for category, patterns in self.classification_rules['functional_categories'].items():
            for pattern in patterns:
                if re.search(pattern, search_text, re.IGNORECASE):
                    return category
        
        return 'general'  # 기본값
    
    def _analyze_complexity(self, chunk: Dict) -> str:
        """복잡도 분석"""
        content = chunk.get('content', '')
        
        # 메서드 수 계산
        method_count = len(re.findall(r'public\s+\w+\s+\w+\s*\(', content))
        
        # 라인 수 계산
        line_count = len(content.split('\n'))
        
        # 복잡도 규칙 적용
        for level, rules in self.complexity_rules.items():
            if (method_count <= rules['max_methods'] and 
                line_count <= rules['max_lines']):
                return level
        
        return 'advanced'  # 기본값
    
    def _determine_learning_priority(self, architecture_layer: str, 
                                   business_domain: str, complexity_level: str) -> int:
        """학습 우선순위 결정 (1-5점)"""
        priority = 3  # 기본값
        
        # 아키텍처 레이어별 우선순위
        layer_priority = {
            'controller': 5,  # 가장 중요
            'service': 4,
            'repository': 3,
            'entity': 2,
            'config': 1,
            'util': 1
        }
        priority = layer_priority.get(architecture_layer, priority)
        
        # 비즈니스 도메인별 조정
        if business_domain in ['user_management', 'authentication']:
            priority += 1  # 핵심 도메인
        elif business_domain == 'general':
            priority -= 1  # 일반 도메인
        
        # 복잡도별 조정
        if complexity_level == 'beginner':
            priority += 1  # 초보자용
        elif complexity_level == 'advanced':
            priority -= 1  # 고급자용
        
        # 1-5 범위로 제한
        return max(1, min(5, priority))
