"""
신규입사자 지원을 위한 강화된 엣지 생성 시스템
비즈니스 흐름과 학습에 도움이 되는 관계들을 우선적으로 추출
"""

import re
import os
import logging
from typing import Dict, List, Any, Set, Tuple, Optional
from sqlalchemy.orm import Session
from pathlib import Path

from phase1.models.database import Project, Class, File, SqlUnit, DbTable, Edge, Method
from phase1.utils.edge_generator import EdgeGenerator

logger = logging.getLogger(__name__)

class OnboardingEdgeGenerator(EdgeGenerator):
    """신규입사자를 위한 엣지 생성기"""
    
    def __init__(self, db_session: Session, source_path: str, project_id: int = 1):
        super().__init__(db_session, source_path, project_id)
        
        # 신규입사자 지원을 위한 우선순위 정의
        self.edge_priorities = {
            'business_flow': 10,      # 최우선: 비즈니스 흐름
            'calls': 9,               # 메서드/서비스 호출 관계
            'dependency': 8,          # 의존성 주입
            'data_flow': 7,           # 데이터 흐름
            'api_endpoint': 6,        # API 엔드포인트 관계
            'import': 5,              # 임포트 관계
            'implements': 4,          # 상속/구현
            'foreign_key': 3,         # DB 관계
            'uses': 2,                # 일반적 사용
            'renders': 1              # 뷰 렌더링
        }
        
        # 비즈니스 패턴 정의
        self.business_patterns = {
            'controller_to_service': {
                'source_patterns': [r'@Controller', r'@RestController'],
                'target_patterns': [r'@Service', r'@Component'],
                'call_patterns': [r'(\w+Service)\.(\w+)\(']
            },
            'service_to_repository': {
                'source_patterns': [r'@Service'],
                'target_patterns': [r'@Repository', r'@Mapper'],
                'call_patterns': [r'(\w+Mapper)\.(\w+)\(', r'(\w+Repository)\.(\w+)\(']
            },
            'api_endpoints': {
                'mapping_patterns': [
                    r'@RequestMapping\([^)]*"([^"]+)"',
                    r'@GetMapping\([^)]*"([^"]+)"',
                    r'@PostMapping\([^)]*"([^"]+)"',
                    r'@PutMapping\([^)]*"([^"]+)"',
                    r'@DeleteMapping\([^)]*"([^"]+)"'
                ]
            }
        }

    def generate_all_edges(self) -> Dict[str, Any]:
        """신규입사자 지원을 위한 모든 엣지 생성"""
        logger.info("신규입사자 지원 엣지 생성 시작")
        
        results = {
            'total_edges': 0,
            'edge_types': {},
            'business_flows': 0,
            'learning_paths': 0
        }
        
        try:
            # 1. 비즈니스 흐름 엣지 생성 (최우선)
            business_edges = self._generate_business_flow_edges()
            results['business_flows'] = len(business_edges)
            results['edge_types']['business_flow'] = len(business_edges)
            
            # 2. API 엔드포인트 엣지 생성
            api_edges = self._generate_api_endpoint_edges()
            results['edge_types']['api_endpoint'] = len(api_edges)
            
            # 3. 서비스 호출 관계 생성 (기존 강화)
            service_edges = self._generate_enhanced_service_calls()
            results['edge_types']['calls'] = len(service_edges)
            
            # 4. 데이터 흐름 엣지 생성 (기존 강화)
            data_edges = self._generate_enhanced_data_flows()
            results['edge_types']['data_flow'] = len(data_edges)
            
            # 5. 의존성 주입 엣지 생성 (기존 강화)
            dependency_edges = self._generate_enhanced_dependencies()
            results['edge_types']['dependency'] = len(dependency_edges)
            
            # 6. 학습 경로 엣지 생성
            learning_edges = self._generate_learning_path_edges()
            results['learning_paths'] = len(learning_edges)
            results['edge_types']['learning_path'] = len(learning_edges)
            
            # 7. 기존 엣지들도 생성 (import, implements 등)
            basic_edges = self._generate_basic_edges()
            
            all_edges = (business_edges + api_edges + service_edges + 
                        data_edges + dependency_edges + learning_edges + basic_edges)
            
            # DB에 저장
            self._save_edges_to_db(all_edges)
            
            results['total_edges'] = len(all_edges)
            logger.info(f"신규입사자 지원 엣지 생성 완료: {results['total_edges']}개")
            
        except Exception as e:
            logger.error(f"엣지 생성 중 오류: {e}")
            results['error'] = str(e)
        
        return results

    def _generate_business_flow_edges(self) -> List[Edge]:
        """비즈니스 흐름 엣지 생성"""
        edges = []
        
        # Controller -> Service -> Repository 흐름 추출
        controllers = self._get_controllers()
        
        for controller in controllers:
            controller_file_path = self._get_file_path(controller.file_id)
            if not controller_file_path:
                continue
                
            try:
                with open(controller_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Controller의 Service 의존성 찾기
                service_deps = self._find_service_dependencies(content)
                
                for service_var, service_class in service_deps:
                    # Controller -> Service 엣지
                    service_obj = self._find_class_by_name(service_class)
                    if service_obj:
                        edge = self._create_edge(
                            controller, service_obj, 'business_flow',
                            confidence=0.9,
                            meta=f"비즈니스 흐름: {controller.name} -> {service_class} (웹 요청 처리)"
                        )
                        edges.append(edge)
                        
                        # Service -> Repository 흐름도 추적
                        repo_edges = self._trace_service_to_repository(service_obj)
                        edges.extend(repo_edges)
                
            except Exception as e:
                logger.warning(f"Controller {controller.name} 분석 중 오류: {e}")
        
        return edges

    def _generate_api_endpoint_edges(self) -> List[Edge]:
        """API 엔드포인트 관계 엣지 생성"""
        edges = []
        
        controllers = self._get_controllers()
        
        for controller in controllers:
            controller_file_path = self._get_file_path(controller.file_id)
            if not controller_file_path:
                continue
                
            try:
                with open(controller_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # API 엔드포인트 추출
                endpoints = self._extract_api_endpoints(content)
                
                for endpoint_info in endpoints:
                    # 가상의 API 엔드포인트 노드 생성 (필요시 새 테이블 추가 가능)
                    edge = Edge(
                        project_id=self.project_id,
                        src_type='class',
                        src_id=controller.class_id,
                        dst_type='api_endpoint',
                        dst_id=0,  # 또는 별도 엔드포인트 테이블 ID
                        edge_kind='api_endpoint',
                        confidence=1.0,
                        meta=f"API: {endpoint_info['method']} {endpoint_info['path']} - {endpoint_info['description']}"
                    )
                    edges.append(edge)
                    
            except Exception as e:
                logger.warning(f"API 엔드포인트 추출 중 오류: {e}")
        
        return edges

    def _generate_enhanced_service_calls(self) -> List[Edge]:
        """강화된 서비스 호출 관계 생성"""
        edges = []
        
        # 모든 클래스에 대해 서비스 호출 관계 분석
        all_classes = self.db_session.query(Class).filter(
            Class.file_id.in_(
                self.db_session.query(File.file_id).filter(File.project_id == self.project_id)
            )
        ).all()
        
        for source_class in all_classes:
            source_file_path = self._get_file_path(source_class.file_id)
            if not source_file_path:
                continue
                
            try:
                with open(source_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 메서드 호출 패턴 찾기
                method_calls = self._find_method_calls(content)
                
                for call_info in method_calls:
                    target_class = self._find_class_by_pattern(call_info['class_pattern'])
                    if target_class and target_class.class_id != source_class.class_id:
                        
                        # 비즈니스 맥락 분석
                        business_context = self._analyze_call_context(
                            source_class.name, target_class.name, call_info['method']
                        )
                        
                        edge = self._create_edge(
                            source_class, target_class, 'calls',
                            confidence=0.8,
                            meta=f"메서드 호출: {call_info['method']} - {business_context}"
                        )
                        edges.append(edge)
                        
            except Exception as e:
                logger.warning(f"서비스 호출 분석 중 오류: {e}")
        
        return edges

    def _generate_enhanced_data_flows(self) -> List[Edge]:
        """강화된 데이터 흐름 엣지 생성"""
        edges = []
        
        # DTO 변환 패턴 찾기
        conversion_edges = self._find_data_conversions()
        edges.extend(conversion_edges)
        
        # 파라미터 전달 패턴 찾기
        parameter_edges = self._find_parameter_flows()
        edges.extend(parameter_edges)
        
        # SQL 결과 매핑 패턴 찾기
        mapping_edges = self._find_result_mappings()
        edges.extend(mapping_edges)
        
        return edges

    def _generate_enhanced_dependencies(self) -> List[Edge]:
        """강화된 의존성 주입 엣지 생성"""
        edges = []
        
        all_classes = self.db_session.query(Class).filter(
            Class.file_id.in_(
                self.db_session.query(File.file_id).filter(File.project_id == self.project_id)
            )
        ).all()
        
        for source_class in all_classes:
            source_file_path = self._get_file_path(source_class.file_id)
            if not source_file_path:
                continue
                
            try:
                with open(source_file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 의존성 주입 패턴 찾기 (@Autowired, @Inject 등)
                dependencies = self._find_dependency_injections(content)
                
                for dep_info in dependencies:
                    target_class = self._find_class_by_name(dep_info['type'])
                    if target_class:
                        
                        # 의존성 목적 분석
                        purpose = self._analyze_dependency_purpose(
                            source_class.name, target_class.name, dep_info['field']
                        )
                        
                        edge = self._create_edge(
                            source_class, target_class, 'dependency',
                            confidence=0.95,
                            meta=f"의존성 주입: {dep_info['field']} - {purpose}"
                        )
                        edges.append(edge)
                        
            except Exception as e:
                logger.warning(f"의존성 분석 중 오류: {e}")
        
        return edges

    def _generate_learning_path_edges(self) -> List[Edge]:
        """학습 경로 엣지 생성 (신규입사자를 위한 추천 순서)"""
        edges = []
        
        # 학습 경로: Entry Points -> Core Business -> Data Layer
        entry_points = self._find_entry_points()  # Controllers, Main methods
        core_services = self._find_core_services()  # Main business logic
        data_layers = self._find_data_layers()   # Repositories, Mappers
        
        # Entry Point -> Core Service 학습 경로
        for entry in entry_points:
            related_services = self._find_related_services(entry)
            for service in related_services:
                edge = Edge(
                    project_id=self.project_id,
                    src_type='class',
                    src_id=entry.class_id,
                    dst_type='class', 
                    dst_id=service.class_id,
                    edge_kind='learning_path',
                    confidence=0.8,
                    meta=f"추천 학습 순서: {entry.name} 다음에 {service.name} 학습"
                )
                edges.append(edge)
        
        return edges

    # Helper Methods
    
    def _get_controllers(self) -> List[Class]:
        """컨트롤러 클래스들 조회"""
        return self.db_session.query(Class).filter(
            Class.file_id.in_(
                self.db_session.query(File.file_id).filter(File.project_id == self.project_id)
            ),
            Class.name.like('%Controller%')
        ).all()

    def _find_service_dependencies(self, content: str) -> List[Tuple[str, str]]:
        """서비스 의존성 찾기"""
        dependencies = []
        
        # @Autowired나 @Inject로 주입된 서비스 찾기
        patterns = [
            r'@(?:Autowired|Inject)\s+(?:private\s+)?(\w+Service)\s+(\w+)',
            r'@(?:Autowired|Inject)\s+(?:private\s+)?(\w+Manager)\s+(\w+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for service_type, service_var in matches:
                dependencies.append((service_var, service_type))
        
        return dependencies

    def _extract_api_endpoints(self, content: str) -> List[Dict[str, Any]]:
        """API 엔드포인트 정보 추출"""
        endpoints = []
        
        # 매핑 어노테이션 패턴
        mapping_patterns = {
            'GET': r'@GetMapping\([^)]*"([^"]+)"[^)]*\)',
            'POST': r'@PostMapping\([^)]*"([^"]+)"[^)]*\)',
            'PUT': r'@PutMapping\([^)]*"([^"]+)"[^)]*\)',
            'DELETE': r'@DeleteMapping\([^)]*"([^"]+)"[^)]*\)',
            'REQUEST': r'@RequestMapping\([^)]*"([^"]+)"[^)]*\)'
        }
        
        for method, pattern in mapping_patterns.items():
            matches = re.findall(pattern, content)
            for path in matches:
                # 메서드명에서 설명 추론
                description = self._infer_endpoint_description(path, method)
                
                endpoints.append({
                    'method': method,
                    'path': path,
                    'description': description
                })
        
        return endpoints

    def _infer_endpoint_description(self, path: str, method: str) -> str:
        """API 엔드포인트 설명 추론"""
        path_lower = path.lower()
        
        if 'user' in path_lower:
            if method == 'GET':
                return "사용자 정보 조회"
            elif method == 'POST':
                return "사용자 등록/생성"
            elif method == 'PUT':
                return "사용자 정보 수정"
            elif method == 'DELETE':
                return "사용자 삭제"
        elif 'order' in path_lower:
            if method == 'GET':
                return "주문 정보 조회"
            elif method == 'POST':
                return "주문 생성"
        elif 'product' in path_lower:
            if method == 'GET':
                return "상품 정보 조회"
        
        return f"{method} 요청 처리"

    def _find_method_calls(self, content: str) -> List[Dict[str, Any]]:
        """메서드 호출 패턴 찾기"""
        calls = []
        
        # 일반적인 메서드 호출 패턴
        call_pattern = r'(\w+)\.(\w+)\s*\('
        matches = re.findall(call_pattern, content)
        
        for obj_var, method_name in matches:
            # 객체 타입 추론 (간단한 패턴)
            if obj_var.endswith('Service') or obj_var.endswith('Manager'):
                calls.append({
                    'class_pattern': obj_var.replace('service', 'Service').replace('manager', 'Manager'),
                    'method': method_name,
                    'variable': obj_var
                })
        
        return calls

    def _analyze_call_context(self, source_class: str, target_class: str, method: str) -> str:
        """호출 맥락 분석"""
        
        # 비즈니스 맥락 추론
        if 'Controller' in source_class and 'Service' in target_class:
            return f"웹 요청을 비즈니스 로직으로 전달"
        elif 'Service' in source_class and 'Mapper' in target_class:
            return f"비즈니스 로직에서 데이터 접근"
        elif 'Service' in source_class and 'Service' in target_class:
            return f"서비스 간 협력"
        else:
            return f"클래스 간 메서드 호출"

    def _save_edges_to_db(self, edges: List[Edge]):
        """엣지들을 데이터베이스에 저장"""
        try:
            # 기존 엣지 삭제 (중복 방지)
            self.db_session.query(Edge).filter(Edge.project_id == self.project_id).delete()
            
            # 새 엣지들 추가
            self.db_session.add_all(edges)
            self.db_session.commit()
            
            logger.info(f"{len(edges)}개 엣지가 데이터베이스에 저장되었습니다")
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"엣지 저장 중 오류: {e}")
            raise

    def _create_edge(self, source_obj, target_obj, edge_kind: str, confidence: float = 0.5, meta: str = "") -> Edge:
        """엣지 생성 헬퍼"""
        return Edge(
            project_id=self.project_id,
            src_type='class',
            src_id=source_obj.class_id,
            dst_type='class',
            dst_id=target_obj.class_id,
            edge_kind=edge_kind,
            confidence=confidence,
            meta=meta
        )