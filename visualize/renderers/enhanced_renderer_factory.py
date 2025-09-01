# visualize/renderers/enhanced_renderer_factory.py
from typing import Dict, Any, List, Optional, Union
import json
import yaml
from pathlib import Path
import logging

from .layout_algorithms import ForceDirectedLayout, HierarchicalLayout, GridLayout, CollisionDetector
from ..templates.render import render_html

logger = logging.getLogger(__name__)

class EnhancedVisualizationFactory:
    """향상된 시각화 렌더러 팩토리"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.layout_algorithms = {
            'force_directed': ForceDirectedLayout,
            'hierarchical': HierarchicalLayout,
            'grid': GridLayout
        }
        self.collision_detector = CollisionDetector()
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """설정 파일 로드"""
        default_config = self._get_default_config()
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                        user_config = yaml.safe_load(f)
                    else:
                        user_config = json.load(f)
                
                # 설정 병합
                if user_config:
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"설정 파일 로드 실패: {e}, 기본 설정 사용")
        
        return default_config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """기본 설정 반환"""
        return {
            'visualization': {
                'erd': {
                    'layout': {
                        'type': 'force_directed',
                        'canvas': {
                            'width': 1400,
                            'height': 1000,
                            'padding': 100,
                            'auto_resize': True
                        },
                        'force_directed': {
                            'iterations': 500,
                            'node_repulsion': 25000,
                            'edge_attraction': 0.1,
                            'damping': 0.9,
                            'min_distance': 150,
                            'center_gravity': 0.01
                        },
                        'hierarchical': {
                            'level_height': 220,
                            'node_spacing': 160,
                            'center_alignment': True
                        },
                        'grid': {
                            'grid_spacing': 200,
                            'aspect_ratio': 1.33
                        }
                    },
                    'appearance': {
                        'nodes': {
                            'min_width': 140,
                            'min_height': 60,
                            'max_width': 320,
                            'max_height': 400,
                            'border_radius': 12,
                            'shadow': True,
                            'colors': {
                                'primary_table': '#E8F4FD',
                                'reference_table': '#FFF8E1',
                                'junction_table': '#F3E5F5',
                                'lookup_table': '#E8F5E8',
                                'border': '#1565C0'
                            }
                        },
                        'text': {
                            'font_family': 'Segoe UI, Arial, sans-serif',
                            'title_size': 16,
                            'column_size': 13,
                            'type_size': 11,
                            'color': '#212121'
                        },
                        'links': {
                            'color': '#616161',
                            'width': 2,
                            'arrow_size': 8
                        }
                    },
                    'interaction': {
                        'zoom': {
                            'min_scale': 0.1,
                            'max_scale': 4.0,
                            'wheel_sensitivity': 1.2
                        },
                        'drag': {
                            'enabled': True,
                            'constrain_to_canvas': False
                        }
                    },
                    'collision_detection': {
                        'enabled': True,
                        'padding': 20,
                        'max_iterations': 100
                    }
                }
            }
        }
    
    def create_enhanced_erd(self, data: Dict[str, Any], template_name: str = 'erd_view_enhanced.html') -> str:
        """향상된 ERD 생성"""
        config = self.config.get('visualization', {}).get('erd', {})
        
        # 레이아웃 계산
        layout_config = config.get('layout', {})
        layout_type = layout_config.get('type', 'force_directed')
        
        if layout_type in self.layout_algorithms:
            # 레이아웃 알고리즘 인스턴스 생성
            layout_class = self.layout_algorithms[layout_type]
            layout_algorithm = layout_class(layout_config.get(layout_type, {}))
            
            # 노드 위치 계산
            nodes = data.get('nodes', [])
            edges = data.get('edges', [])
            
            if nodes:
                positions = layout_algorithm.calculate_layout(nodes, edges)
                
                # 겹침 방지
                if config.get('collision_detection', {}).get('enabled', True):
                    collision_config = config.get('collision_detection', {})
                    detector = CollisionDetector(collision_config.get('padding', 20))
                    positions = detector.resolve_collisions(positions)
                
                # 노드 데이터에 위치 정보 추가
                for node in nodes:
                    if node['id'] in positions:
                        pos = positions[node['id']]
                        node['position'] = {
                            'x': pos.x,
                            'y': pos.y
                        }
                        node['size'] = {
                            'width': pos.width,
                            'height': pos.height
                        }
        
        # 메타데이터 추가
        enhanced_data = data.copy()
        enhanced_data['config'] = config
        enhanced_data['layout_type'] = layout_type
        
        # HTML 렌더링
        try:
            return render_html(template_name, enhanced_data)
        except FileNotFoundError:
            logger.warning(f"템플릿 {template_name}를 찾을 수 없음, 기본 템플릿 사용")
            return render_html('erd_view.html', enhanced_data)
    
    def create_hotspot_map(self, data: Dict[str, Any], metrics: Dict[str, Any]) -> str:
        """코드 복잡도 핫스팟 맵 생성"""
        # 메트릭 정보를 노드에 추가
        nodes = data.get('nodes', [])
        
        for node in nodes:
            node_id = node['id']
            if node_id in metrics:
                metric_info = metrics[node_id]
                
                # 복잡도에 따른 색상 및 크기 조정
                complexity = metric_info.get('complexity', 0)
                loc = metric_info.get('loc', 0)
                change_frequency = metric_info.get('change_frequency', 0)
                
                # 핫스팟 점수 계산
                hotspot_score = (complexity * 0.4 + loc * 0.3 + change_frequency * 0.3)
                
                # 노드 스타일 정보 추가
                node['hotspot'] = {
                    'score': hotspot_score,
                    'complexity': complexity,
                    'loc': loc,
                    'change_frequency': change_frequency,
                    'heat_level': self._calculate_heat_level(hotspot_score)
                }
        
        # 핫스팟 전용 템플릿 사용
        return self._render_with_template('hotspot_view.html', data)
    
    def create_vulnerability_map(self, data: Dict[str, Any], vulnerabilities: List[Dict[str, Any]]) -> str:
        """보안 취약점 맵 생성"""
        # 취약점 정보를 노드에 매핑
        nodes = data.get('nodes', [])
        vuln_map = {}
        
        for vuln in vulnerabilities:
            file_path = vuln.get('file_path', '')
            severity = vuln.get('severity', 'low')
            vuln_type = vuln.get('type', 'unknown')
            
            if file_path not in vuln_map:
                vuln_map[file_path] = []
            vuln_map[file_path].append({
                'severity': severity,
                'type': vuln_type,
                'description': vuln.get('description', ''),
                'line_number': vuln.get('line_number', 0)
            })
        
        # 노드에 취약점 정보 추가
        for node in nodes:
            # 파일 경로나 노드 ID를 기반으로 매핑
            node_path = node.get('meta', {}).get('file_path', node['id'])
            
            if node_path in vuln_map:
                node_vulns = vuln_map[node_path]
                
                # 심각도별 카운트
                severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
                for vuln in node_vulns:
                    severity = vuln['severity'].lower()
                    if severity in severity_counts:
                        severity_counts[severity] += 1
                
                node['vulnerability'] = {
                    'total_count': len(node_vulns),
                    'severity_counts': severity_counts,
                    'vulnerabilities': node_vulns,
                    'max_severity': self._get_max_severity(node_vulns)
                }
        
        # 취약점 전용 템플릿 사용
        return self._render_with_template('vulnerability_view.html', data)
    
    def create_confidence_overlay(self, data: Dict[str, Any]) -> str:
        """LLM 신뢰도 오버레이 생성"""
        # 엣지와 노드에 신뢰도 시각화 정보 추가
        nodes = data.get('nodes', [])
        edges = data.get('edges', [])
        
        # 신뢰도 구간별 스타일 정보 추가
        for edge in edges:
            confidence = edge.get('confidence', 0.5)
            edge['confidence_level'] = self._calculate_confidence_level(confidence)
        
        for node in nodes:
            # 연결된 엣지들의 평균 신뢰도 계산
            connected_edges = [e for e in edges if e['source'] == node['id'] or e['target'] == node['id']]
            if connected_edges:
                avg_confidence = sum(e.get('confidence', 0.5) for e in connected_edges) / len(connected_edges)
                node['avg_confidence'] = avg_confidence
                node['confidence_level'] = self._calculate_confidence_level(avg_confidence)
        
        # 신뢰도 전용 템플릿 사용
        return self._render_with_template('confidence_view.html', data)
    
    def create_saved_view(self, view_name: str, data: Dict[str, Any], settings: Dict[str, Any]) -> str:
        """저장된 뷰 생성"""
        # 뷰 설정을 데이터에 추가
        enhanced_data = data.copy()
        enhanced_data['saved_view'] = {
            'name': view_name,
            'settings': settings,
            'created_at': str(pd.Timestamp.now()) if 'pd' in globals() else 'unknown'
        }
        
        # 저장된 뷰 전용 템플릿 사용
        return self._render_with_template('saved_view.html', enhanced_data)
    
    def _calculate_heat_level(self, score: float) -> str:
        """핫스팟 점수에 따른 열 레벨 계산"""
        if score >= 0.8:
            return 'critical'
        elif score >= 0.6:
            return 'high'
        elif score >= 0.4:
            return 'medium'
        else:
            return 'low'
    
    def _get_max_severity(self, vulnerabilities: List[Dict[str, Any]]) -> str:
        """취약점 목록에서 최고 심각도 반환"""
        severity_order = ['critical', 'high', 'medium', 'low']
        
        for severity in severity_order:
            if any(vuln['severity'].lower() == severity for vuln in vulnerabilities):
                return severity
        
        return 'low'
    
    def _calculate_confidence_level(self, confidence: float) -> str:
        """신뢰도에 따른 레벨 계산"""
        if confidence >= 0.9:
            return 'very_high'
        elif confidence >= 0.7:
            return 'high'
        elif confidence >= 0.5:
            return 'medium'
        elif confidence >= 0.3:
            return 'low'
        else:
            return 'very_low'
    
    def _render_with_template(self, template_name: str, data: Dict[str, Any]) -> str:
        """템플릿으로 렌더링"""
        try:
            return render_html(template_name, data)
        except FileNotFoundError:
            logger.warning(f"템플릿 {template_name}를 찾을 수 없음, 기본 ERD 템플릿 사용")
            return render_html('erd_view_enhanced.html', data)
    
    def export_view_settings(self, view_name: str, settings: Dict[str, Any], output_path: str):
        """뷰 설정을 파일로 내보내기"""
        view_data = {
            'name': view_name,
            'settings': settings,
            'created_at': str(pd.Timestamp.now()) if 'pd' in globals() else 'unknown',
            'version': '1.0'
        }
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            if output_file.suffix.lower() == '.yaml':
                yaml.safe_dump(view_data, f, ensure_ascii=False, indent=2)
            else:
                json.dump(view_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"뷰 설정 저장 완료: {output_file}")
    
    def load_view_settings(self, settings_path: str) -> Dict[str, Any]:
        """저장된 뷰 설정 로드"""
        settings_file = Path(settings_path)
        
        if not settings_file.exists():
            raise FileNotFoundError(f"뷰 설정 파일을 찾을 수 없습니다: {settings_path}")
        
        with open(settings_file, 'r', encoding='utf-8') as f:
            if settings_file.suffix.lower() in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            else:
                return json.load(f)