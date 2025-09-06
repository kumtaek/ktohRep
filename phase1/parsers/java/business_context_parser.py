"""
신규입사자 지원을 위한 비즈니스 맥락 인식 Java 파서
기존 기술적 파싱에 비즈니스 의미와 실행 흐름을 추가로 추출
"""

import re
import ast
import logging
from typing import Dict, List, Any, Set, Tuple, Optional
from pathlib import Path

from phase1.parsers.java.javaparser_enhanced import JavaParserEnhanced
from phase1.models.database import Class, Method, Edge, File

logger = logging.getLogger(__name__)

class BusinessContextParser(JavaParserEnhanced):
    """비즈니스 맥락을 인식하는 Java 파서"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # 비즈니스 패턴 정의
        self.business_patterns = {
            'controller_patterns': [
                r'@RequestMapping',
                r'@GetMapping',
                r'@PostMapping',
                r'@PutMapping',
                r'@DeleteMapping',
                r'@Controller',
                r'@RestController'
            ],
            'service_patterns': [
                r'@Service',
                r'@Component',
                r'@Transactional'
            ],
            'repository_patterns': [
                r'@Repository',
                r'@Mapper',
                r'extends.*Mapper'
            ],
            'entity_patterns': [
                r'@Entity',
                r'@Table',
                r'@Id'
            ]
        }
        
        # 비즈니스 도메인 키워드
        self.domain_keywords = {
            'user_domain': ['user', 'member', 'account', 'profile'],
            'order_domain': ['order', 'purchase', 'transaction', 'payment'],
            'product_domain': ['product', 'item', 'goods', 'inventory'],
            'auth_domain': ['login', 'auth', 'security', 'permission', 'role']
        }
        
        # 액션 패턴
        self.action_patterns = {
            'crud_create': ['create', 'insert', 'add', 'register', 'save'],
            'crud_read': ['get', 'find', 'select', 'search', 'list', 'view'],
            'crud_update': ['update', 'modify', 'edit', 'change'],
            'crud_delete': ['delete', 'remove', 'drop']
        }

    def parse_file(self, file_path: str, project_id: int) -> Tuple[File, List[Class], List[Method], List[Edge]]:
        """
        비즈니스 맥락을 포함하여 Java 파일을 파싱
        """
        # 기본 파싱 실행
        file_obj, classes, methods, edges = super().parse_file(file_path, project_id)
        
        # 비즈니스 맥락 정보 추가
        enhanced_classes = self._enhance_with_business_context(classes, file_path)
        enhanced_methods = self._enhance_methods_with_context(methods, file_path)
        business_edges = self._extract_business_relationships(enhanced_classes, enhanced_methods, file_path)
        
        return file_obj, enhanced_classes, enhanced_methods, edges + business_edges

    def _enhance_with_business_context(self, classes: List[Class], file_path: str) -> List[Class]:
        """클래스에 비즈니스 맥락 정보 추가"""
        enhanced_classes = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for class_obj in classes:
            # 비즈니스 계층 식별
            business_layer = self._identify_business_layer(class_obj.name, content)
            
            # 도메인 식별
            domain = self._identify_domain(class_obj.name, content)
            
            # 비즈니스 목적 추론
            purpose = self._infer_business_purpose(class_obj.name, business_layer, domain)
            
            # 메타데이터에 비즈니스 정보 추가
            business_info = {
                'business_layer': business_layer,
                'domain': domain,
                'purpose': purpose,
                'responsibilities': self._extract_responsibilities(content, class_obj.name)
            }
            
            # 기존 Class 객체 복사하고 비즈니스 정보 추가
            enhanced_class = Class(
                class_id=class_obj.class_id,
                file_id=class_obj.file_id,
                fqn=class_obj.fqn,
                name=class_obj.name,
                start_line=class_obj.start_line,
                end_line=class_obj.end_line,
                modifiers=class_obj.modifiers,
                annotations=class_obj.annotations,
                llm_summary=f"비즈니스 맥락: {business_info}"
            )
            
            enhanced_classes.append(enhanced_class)
        
        return enhanced_classes

    def _identify_business_layer(self, class_name: str, content: str) -> str:
        """비즈니스 계층 식별"""
        class_lower = class_name.lower()
        
        # 어노테이션 기반 식별
        for pattern in self.business_patterns['controller_patterns']:
            if re.search(pattern, content):
                return 'presentation'
        
        for pattern in self.business_patterns['service_patterns']:
            if re.search(pattern, content):
                return 'business'
        
        for pattern in self.business_patterns['repository_patterns']:
            if re.search(pattern, content):
                return 'data_access'
        
        for pattern in self.business_patterns['entity_patterns']:
            if re.search(pattern, content):
                return 'entity'
        
        # 이름 기반 식별
        if 'controller' in class_lower:
            return 'presentation'
        elif 'service' in class_lower or 'manager' in class_lower:
            return 'business'
        elif 'mapper' in class_lower or 'dao' in class_lower or 'repository' in class_lower:
            return 'data_access'
        elif 'model' in class_lower or 'entity' in class_lower or 'dto' in class_lower:
            return 'entity'
        else:
            return 'utility'

    def _identify_domain(self, class_name: str, content: str) -> str:
        """비즈니스 도메인 식별"""
        class_lower = class_name.lower()
        content_lower = content.lower()
        
        for domain, keywords in self.domain_keywords.items():
            for keyword in keywords:
                if keyword in class_lower or keyword in content_lower:
                    return domain.replace('_domain', '')
        
        return 'general'

    def _infer_business_purpose(self, class_name: str, layer: str, domain: str) -> str:
        """비즈니스 목적 추론"""
        purposes = {
            'presentation': f"{domain} 관련 웹 요청을 처리하고 응답을 관리",
            'business': f"{domain} 비즈니스 로직을 처리하고 규칙을 적용",  
            'data_access': f"{domain} 데이터의 저장, 조회, 수정을 담당",
            'entity': f"{domain} 도메인 객체의 데이터 구조를 정의"
        }
        
        return purposes.get(layer, "시스템 지원 기능을 제공")

    def _extract_responsibilities(self, content: str, class_name: str) -> List[str]:
        """클래스의 책임 사항 추출"""
        responsibilities = []
        
        # 메서드 이름에서 책임 추출
        method_pattern = r'public\s+\w+\s+(\w+)\s*\('
        methods = re.findall(method_pattern, content)
        
        for method in methods:
            method_lower = method.lower()
            
            for action_type, keywords in self.action_patterns.items():
                for keyword in keywords:
                    if keyword in method_lower:
                        action_desc = action_type.replace('crud_', '').replace('_', ' ')
                        responsibilities.append(f"{action_desc.title()} 기능 제공")
                        break
        
        return list(set(responsibilities))  # 중복 제거

    def _enhance_methods_with_context(self, methods: List[Method], file_path: str) -> List[Method]:
        """메서드에 비즈니스 맥락 정보 추가"""
        enhanced_methods = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for method in methods:
            # 메서드 타입 식별 (CRUD 등)
            method_type = self._identify_method_type(method.name)
            
            # 비즈니스 액션 식별
            business_action = self._identify_business_action(method.name, content)
            
            # 파라미터와 리턴 타입 분석
            data_flow = self._analyze_method_data_flow(method, content)
            
            business_info = {
                'method_type': method_type,
                'business_action': business_action,
                'data_flow': data_flow
            }
            
            enhanced_method = Method(
                method_id=method.method_id,
                class_id=method.class_id,
                name=method.name,
                start_line=method.start_line,
                end_line=method.end_line,
                modifiers=method.modifiers,
                parameters=method.parameters,
                return_type=method.return_type,
                llm_summary=f"비즈니스 정보: {business_info}"
            )
            
            enhanced_methods.append(enhanced_method)
        
        return enhanced_methods

    def _identify_method_type(self, method_name: str) -> str:
        """메서드 타입 식별"""
        method_lower = method_name.lower()
        
        for action_type, keywords in self.action_patterns.items():
            for keyword in keywords:
                if keyword in method_lower:
                    return action_type
        
        return 'business_logic'

    def _identify_business_action(self, method_name: str, content: str) -> str:
        """비즈니스 액션 식별"""
        method_lower = method_name.lower()
        
        # 일반적인 비즈니스 액션 패턴
        action_patterns = {
            'authentication': ['login', 'logout', 'authenticate', 'authorize'],
            'registration': ['register', 'signup', 'enroll'],
            'validation': ['validate', 'verify', 'check'],
            'notification': ['send', 'notify', 'alert', 'email'],
            'calculation': ['calculate', 'compute', 'process'],
            'search': ['search', 'find', 'query', 'filter'],
            'management': ['manage', 'handle', 'control']
        }
        
        for action, keywords in action_patterns.items():
            for keyword in keywords:
                if keyword in method_lower:
                    return action
        
        return 'general_operation'

    def _analyze_method_data_flow(self, method: Method, content: str) -> Dict[str, Any]:
        """메서드의 데이터 흐름 분석"""
        return {
            'input_types': self._extract_parameter_types(method.parameters or ''),
            'output_type': method.return_type or 'void',
            'data_transformations': self._identify_transformations(content, method.name)
        }

    def _extract_parameter_types(self, parameters: str) -> List[str]:
        """파라미터 타입 추출"""
        if not parameters:
            return []
        
        # 간단한 타입 추출 (더 정교한 파싱 필요)
        param_pattern = r'(\w+)\s+\w+'
        types = re.findall(param_pattern, parameters)
        return types

    def _identify_transformations(self, content: str, method_name: str) -> List[str]:
        """데이터 변환 패턴 식별"""
        transformations = []
        
        # 일반적인 변환 패턴
        transform_patterns = {
            'dto_conversion': [r'toDto\(', r'fromDto\(', r'convert\('],
            'validation': [r'validate\(', r'isValid\(', r'check\('],
            'formatting': [r'format\(', r'toString\(', r'parse\('],
            'mapping': [r'map\(', r'transform\(', r'adapt\(']
        }
        
        for transform_type, patterns in transform_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content):
                    transformations.append(transform_type)
        
        return transformations

    def _extract_business_relationships(self, classes: List[Class], methods: List[Method], file_path: str) -> List[Edge]:
        """비즈니스 관계 추출"""
        business_edges = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 서비스 호출 관계 추출
        service_calls = self._extract_service_calls(content, classes)
        business_edges.extend(service_calls)
        
        # 데이터 흐름 관계 추출  
        data_flows = self._extract_data_flows(content, classes, methods)
        business_edges.extend(data_flows)
        
        # 비즈니스 프로세스 관계 추출
        process_flows = self._extract_process_flows(content, classes)
        business_edges.extend(process_flows)
        
        return business_edges

    def _extract_service_calls(self, content: str, classes: List[Class]) -> List[Edge]:
        """서비스 호출 관계 추출"""
        edges = []
        
        # @Autowired나 @Inject로 주입된 서비스 찾기
        injection_pattern = r'@(?:Autowired|Inject)\s+(?:private\s+)?(\w+)\s+(\w+)'
        injections = re.findall(injection_pattern, content)
        
        for service_type, service_var in injections:
            if 'service' in service_type.lower() or 'manager' in service_type.lower():
                # 서비스 호출을 나타내는 엣지 생성
                edge = Edge(
                    project_id=1,  # TODO: 실제 project_id 전달 필요
                    src_type='class',
                    src_id=classes[0].class_id if classes else 0,
                    dst_type='class', 
                    dst_id=0,  # TODO: 실제 대상 클래스 ID 찾기
                    edge_kind='uses_service',
                    confidence=0.9,
                    meta=f"비즈니스 서비스 호출: {service_type}"
                )
                edges.append(edge)
        
        return edges

    def _extract_data_flows(self, content: str, classes: List[Class], methods: List[Method]) -> List[Edge]:
        """데이터 흐름 관계 추출"""
        edges = []
        
        # DTO 변환 패턴 찾기
        conversion_pattern = r'(\w+)\.to(\w+)\('
        conversions = re.findall(conversion_pattern, content)
        
        for source, target in conversions:
            edge = Edge(
                project_id=1,
                src_type='class',
                src_id=classes[0].class_id if classes else 0,
                dst_type='class',
                dst_id=0,
                edge_kind='data_transformation',
                confidence=0.8,
                meta=f"데이터 변환: {source} -> {target}"
            )
            edges.append(edge)
        
        return edges

    def _extract_process_flows(self, content: str, classes: List[Class]) -> List[Edge]:
        """비즈니스 프로세스 흐름 추출"""
        edges = []
        
        # 트랜잭션 경계 식별
        if '@Transactional' in content:
            edge = Edge(
                project_id=1,
                src_type='class',
                src_id=classes[0].class_id if classes else 0,
                dst_type='process',
                dst_id=0,
                edge_kind='transaction_boundary',
                confidence=1.0,
                meta="트랜잭션 경계를 정의하는 비즈니스 프로세스"
            )
            edges.append(edge)
        
        return edges