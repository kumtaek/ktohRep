"""
시스템 아키텍처 분석기
메타데이터에서 아키텍처 패턴과 구조 정보를 분석하여 추출
"""
import sqlite3
import re
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, Counter
from pathlib import Path

class ArchitectureAnalyzer:
    """시스템 아키텍처 분석 및 리포트 생성"""
    
    def __init__(self, metadata_engine):
        self.metadata_engine = metadata_engine
        self.db_path = metadata_engine.db_path
        
    def analyze_project_architecture(self, project_id: int) -> Dict:
        """프로젝트의 전체 아키텍처를 분석"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 기본 통계 수집
                stats = self._collect_basic_stats(cursor, project_id)
                
                # 관계 상세 정보 분석
                relationships = self._analyze_relationships(cursor, project_id)
                
                # 계층 구조 분석
                layer_analysis = self._analyze_layers(cursor, project_id)
                
                # 아키텍처 패턴 분석
                patterns = self._analyze_architecture_patterns(cursor, project_id, relationships, layer_analysis)
                
                # 핵심 컴포넌트 식별
                core_components = self._identify_core_components(cursor, project_id, relationships)
                
                return {
                    'success': True,
                    'project_id': project_id,
                    'stats': stats,
                    'relationships': relationships,
                    'layers': layer_analysis,
                    'patterns': patterns,
                    'core_components': core_components
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _collect_basic_stats(self, cursor, project_id: int) -> Dict:
        """기본 통계 정보 수집"""
        stats = {}
        
        # 컴포넌트 통계
        cursor.execute("""
            SELECT component_type, COUNT(*) 
            FROM components 
            WHERE project_id = ? 
            GROUP BY component_type
        """, (project_id,))
        
        component_stats = dict(cursor.fetchall())
        stats['components'] = component_stats
        stats['total_components'] = sum(component_stats.values())
        
        # 관계 통계
        cursor.execute("""
            SELECT relationship_type, COUNT(*) 
            FROM relationships 
            WHERE project_id = ? 
            GROUP BY relationship_type
        """, (project_id,))
        
        relationship_stats = dict(cursor.fetchall())
        stats['relationships'] = relationship_stats
        stats['total_relationships'] = sum(relationship_stats.values())
        
        # 파일 통계
        cursor.execute("""
            SELECT file_type, COUNT(*) 
            FROM files f
            JOIN components c ON f.file_id = c.file_id
            WHERE c.project_id = ? AND f.file_type != 'virtual'
            GROUP BY file_type
        """, (project_id,))
        
        file_stats = dict(cursor.fetchall())
        stats['files'] = file_stats
        
        return stats
    
    def _analyze_relationships(self, cursor, project_id: int) -> Dict:
        """관계 상세 분석"""
        relationships = {}
        
        # 각 관계 타입별 상세 정보
        cursor.execute("""
            SELECT r.relationship_type,
                   c1.component_name as source,
                   c1.component_type as source_type,
                   c2.component_name as target,  
                   c2.component_type as target_type,
                   r.confidence,
                   f1.file_path as source_file,
                   f2.file_path as target_file
            FROM relationships r
            JOIN components c1 ON r.src_component_id = c1.component_id
            JOIN components c2 ON r.dst_component_id = c2.component_id
            JOIN files f1 ON c1.file_id = f1.file_id
            JOIN files f2 ON c2.file_id = f2.file_id
            WHERE r.project_id = ?
            ORDER BY r.relationship_type, c1.component_name
        """, (project_id,))
        
        all_relationships = cursor.fetchall()
        
        # 관계 타입별 그룹화
        grouped = defaultdict(list)
        for rel in all_relationships:
            rel_type = rel[0]
            grouped[rel_type].append({
                'source': rel[1],
                'source_type': rel[2], 
                'target': rel[3],
                'target_type': rel[4],
                'confidence': rel[5],
                'source_file': rel[6],
                'target_file': rel[7]
            })
        
        relationships['details'] = dict(grouped)
        relationships['summary'] = {rel_type: len(rels) for rel_type, rels in grouped.items()}
        
        return relationships
    
    def _analyze_layers(self, cursor, project_id: int) -> Dict:
        """계층 구조 분석"""
        layers = {}
        
        # 비즈니스 태그를 통한 계층 분석
        cursor.execute("""
            SELECT bt.layer, COUNT(*) as count,
                   GROUP_CONCAT(DISTINCT c.component_name) as components
            FROM business_tags bt
            JOIN components c ON bt.component_id = c.component_id
            WHERE bt.project_id = ? AND bt.layer IS NOT NULL
            GROUP BY bt.layer
            ORDER BY count DESC
        """, (project_id,))
        
        layer_data = cursor.fetchall()
        if layer_data:
            layers['business_layers'] = {
                layer: {
                    'count': count,
                    'components': components.split(',') if components else []
                }
                for layer, count, components in layer_data
            }
        else:
            layers['business_layers'] = {}
        
        # 파일 경로 기반 계층 추정
        cursor.execute("""
            SELECT DISTINCT f.file_path, c.component_name, c.component_type
            FROM files f
            JOIN components c ON f.file_id = c.file_id
            WHERE c.project_id = ? AND f.file_type != 'virtual'
            ORDER BY f.file_path
        """, (project_id,))
        
        file_components = cursor.fetchall()
        path_layers = self._infer_layers_from_paths(file_components)
        layers['path_based_layers'] = path_layers
        
        return layers
    
    def _infer_layers_from_paths(self, file_components: List[Tuple]) -> Dict:
        """파일 경로에서 계층 구조 추정"""
        layer_patterns = {
            'controller': ['controller', 'web', 'rest', 'api'],
            'service': ['service', 'business', 'logic'],
            'dao': ['dao', 'repository', 'persistence', 'data'],
            'model': ['model', 'entity', 'dto', 'vo', 'domain'],
            'util': ['util', 'helper', 'common'],
            'config': ['config', 'configuration', 'setting']
        }
        
        layers = defaultdict(list)
        
        for file_path, component_name, component_type in file_components:
            file_path_lower = file_path.lower()
            
            # 파일 경로에서 계층 패턴 매칭
            for layer, patterns in layer_patterns.items():
                if any(pattern in file_path_lower for pattern in patterns):
                    layers[layer].append({
                        'component': component_name,
                        'type': component_type,
                        'file': file_path
                    })
                    break
            else:
                # 매칭되지 않는 경우 기타로 분류
                layers['other'].append({
                    'component': component_name,
                    'type': component_type, 
                    'file': file_path
                })
        
        return dict(layers)
    
    def _analyze_architecture_patterns(self, cursor, project_id: int, 
                                     relationships: Dict, layers: Dict) -> List[str]:
        """아키텍처 패턴 분석"""
        patterns = []
        
        # 계층형 아키텍처 패턴 감지
        if self._detect_layered_pattern(layers):
            patterns.append("계층형 아키텍처 (Layered Architecture)")
        
        # MVC 패턴 감지
        if self._detect_mvc_pattern(layers):
            patterns.append("MVC 패턴 (Model-View-Controller)")
        
        # Repository 패턴 감지
        if self._detect_repository_pattern(relationships):
            patterns.append("Repository 패턴")
        
        # Service 패턴 감지  
        if self._detect_service_pattern(layers):
            patterns.append("Service 계층 패턴")
        
        # 의존성 주입 패턴 감지
        if self._detect_dependency_injection(relationships):
            patterns.append("의존성 주입 패턴")
        
        return patterns
    
    def _detect_layered_pattern(self, layers: Dict) -> bool:
        """계층형 아키텍처 패턴 감지"""
        path_layers = layers.get('path_based_layers', {})
        business_layers = layers.get('business_layers', {})
        
        # 주요 계층이 존재하는지 확인
        common_layers = {'controller', 'service', 'dao', 'model'}
        found_layers = set(path_layers.keys()) | set(business_layers.keys())
        
        return len(common_layers & found_layers) >= 2
    
    def _detect_mvc_pattern(self, layers: Dict) -> bool:
        """MVC 패턴 감지"""
        path_layers = layers.get('path_based_layers', {})
        
        has_controller = 'controller' in path_layers
        has_model = 'model' in path_layers
        
        return has_controller and has_model
    
    def _detect_repository_pattern(self, relationships: Dict) -> bool:
        """Repository 패턴 감지"""
        details = relationships.get('details', {})
        
        # DAO나 Repository 관련 컴포넌트가 있는지 확인
        for rel_type, rels in details.items():
            for rel in rels:
                if any(keyword in rel['source'].lower() or keyword in rel['target'].lower()
                       for keyword in ['dao', 'repository']):
                    return True
        return False
    
    def _detect_service_pattern(self, layers: Dict) -> bool:
        """Service 계층 패턴 감지"""
        path_layers = layers.get('path_based_layers', {})
        return 'service' in path_layers and len(path_layers['service']) > 0
    
    def _detect_dependency_injection(self, relationships: Dict) -> bool:
        """의존성 주입 패턴 감지"""
        details = relationships.get('details', {})
        
        # implements나 dependency 관계가 있는지 확인
        return 'implements' in details or 'dependency' in details
    
    def _identify_core_components(self, cursor, project_id: int, relationships: Dict) -> Dict:
        """핵심 컴포넌트 식별"""
        core_components = {}
        
        # 가장 많이 참조되는 컴포넌트들 (허브 컴포넌트)
        cursor.execute("""
            SELECT c.component_name, c.component_type, COUNT(*) as reference_count
            FROM relationships r
            JOIN components c ON r.dst_component_id = c.component_id
            WHERE r.project_id = ?
            GROUP BY c.component_id
            HAVING COUNT(*) >= 3
            ORDER BY COUNT(*) DESC
            LIMIT 10
        """, (project_id,))
        
        hubs = cursor.fetchall()
        core_components['hub_components'] = [
            {'name': name, 'type': comp_type, 'references': count}
            for name, comp_type, count in hubs
        ]
        
        # 가장 많이 다른 컴포넌트를 참조하는 컴포넌트들 (팬아웃 컴포넌트)
        cursor.execute("""
            SELECT c.component_name, c.component_type, COUNT(*) as dependency_count
            FROM relationships r
            JOIN components c ON r.src_component_id = c.component_id
            WHERE r.project_id = ?
            GROUP BY c.component_id
            HAVING COUNT(*) >= 3
            ORDER BY COUNT(*) DESC
            LIMIT 10
        """, (project_id,))
        
        fanouts = cursor.fetchall()
        core_components['fanout_components'] = [
            {'name': name, 'type': comp_type, 'dependencies': count}
            for name, comp_type, count in fanouts
        ]
        
        return core_components
    
    def generate_architecture_report(self, analysis_result: Dict) -> str:
        """아키텍처 분석 결과를 텍스트 리포트로 생성"""
        if not analysis_result['success']:
            return f"분석 실패: {analysis_result['error']}"
        
        report_lines = []
        report_lines.append("시스템 아키텍처 분석 리포트")
        report_lines.append("=" * 50)
        
        # 기본 통계
        stats = analysis_result['stats']
        report_lines.append(f"\n[통계] 구성 요소 통계")
        report_lines.append(f"  - 총 컴포넌트: {stats['total_components']}개")
        for comp_type, count in stats['components'].items():
            report_lines.append(f"    - {comp_type}: {count}개")
        
        report_lines.append(f"\n  - 총 관계: {stats['total_relationships']}개")
        for rel_type, count in stats['relationships'].items():
            report_lines.append(f"    - {rel_type}: {count}개")
        
        # 관계 상세 정보
        relationships = analysis_result['relationships']
        report_lines.append(f"\n[관계] 관계 상세 정보")
        
        for rel_type, rels in relationships['details'].items():
            report_lines.append(f"\n{rel_type.title()} 관계 ({len(rels)}개)")
            for rel in rels[:10]:  # 상위 10개만 표시
                confidence_str = f"(신뢰도: {rel['confidence']})" if rel['confidence'] < 1.0 else ""
                report_lines.append(f"  - {rel['source']} -> {rel['target']} {confidence_str}")
            if len(rels) > 10:
                report_lines.append(f"  ... 외 {len(rels) - 10}개")
        
        # 계층 구조
        layers = analysis_result['layers']
        if layers['path_based_layers']:
            report_lines.append(f"\n[계층] 계층 구조")
            for layer_name, components in layers['path_based_layers'].items():
                if components:  # 빈 계층은 제외
                    report_lines.append(f"  {layer_name.title()} 계층 ({len(components)}개)")
                    for comp in components[:5]:  # 상위 5개만 표시
                        report_lines.append(f"    - {comp['component']} ({comp['type']})")
                    if len(components) > 5:
                        report_lines.append(f"    ... 외 {len(components) - 5}개")
        
        # 아키텍처 패턴
        patterns = analysis_result['patterns']
        if patterns:
            report_lines.append(f"\n[패턴] 아키텍처 패턴 분석")
            for pattern in patterns:
                report_lines.append(f"  * {pattern}")
        
        # 핵심 컴포넌트
        core = analysis_result['core_components']
        if core['hub_components']:
            report_lines.append(f"\n[핵심] 핵심 컴포넌트 (허브)")
            for comp in core['hub_components'][:5]:
                report_lines.append(f"  - {comp['name']} : {comp['references']}개 참조")
        
        if core['fanout_components']:
            report_lines.append(f"\n[의존성] 의존성 중심 컴포넌트")
            for comp in core['fanout_components'][:5]:
                report_lines.append(f"  - {comp['name']} : {comp['dependencies']}개 의존")
        
        return "\n".join(report_lines)