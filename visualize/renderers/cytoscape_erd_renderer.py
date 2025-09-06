#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cytoscape.js 기반 ERD 렌더러
기존 ERD 빌더와 연동하여 Cytoscape.js HTML을 생성합니다.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from ..templates.render import render_html

logger = logging.getLogger(__name__)


class CytoscapeERDRenderer:
    """Cytoscape.js 기반 ERD 렌더러"""
    
    def __init__(self, template_dir: Path):
        self.template_dir = template_dir
        self.cytoscape_template = template_dir / "erd_cytoscape.html"
        
        if not self.cytoscape_template.exists():
            raise FileNotFoundError(f"Cytoscape ERD 템플릿을 찾을 수 없습니다: {self.cytoscape_template}")
    
    def render(self, erd_data: Dict[str, Any], project_name: str, output_dir: Path) -> Path:
        """
        ERD 데이터를 Cytoscape.js HTML로 렌더링합니다.
        
        Args:
            erd_data: ERD 빌더에서 생성된 데이터
            project_name: 프로젝트 이름
            output_dir: 출력 디렉토리 경로
            
        Returns:
            생성된 HTML 파일 경로
        """
        try:
            logger.info(f"Cytoscape.js ERD 렌더링 시작: {project_name}")
            
            # 타임스탬프 기반 파일명 생성: erd_cytoscape_yyyymmdd_hms.html
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"erd_cytoscape_{timestamp}.html"
            output_path = output_dir / output_filename
            
            # Cytoscape.js용 데이터 변환
            cytoscape_data = self._convert_to_cytoscape_format(erd_data)
            
            # HTML 템플릿 렌더링
            html_content = self._render_html_template(cytoscape_data, project_name)
            
            # 출력 파일 생성
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Cytoscape.js ERD 생성 완료: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Cytoscape.js ERD 렌더링 실패: {e}")
            raise
    
    def _convert_to_cytoscape_format(self, erd_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        ERD 데이터를 Cytoscape.js 형식으로 변환합니다.
        
        Args:
            erd_data: 원본 ERD 데이터
            
        Returns:
            Cytoscape.js 형식의 데이터
        """
        cytoscape_data = {
            'project_info': {
                'name': 'Unknown Project',
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            'nodes': [],
            'edges': [],
            'metadata': {
                'total_tables': 0,
                'total_columns': 0,
                'total_pk': 0,
                'total_fk': 0,
                'total_relationships': 0
            }
        }
        
        # 노드 변환
        if 'nodes' in erd_data:
            for node in erd_data['nodes']:
                cytoscape_node = self._convert_node(node)
                if cytoscape_node:
                    cytoscape_data['nodes'].append(cytoscape_node)
        
        # 엣지 변환
        if 'edges' in erd_data:
            for edge in erd_data['edges']:
                cytoscape_edge = self._convert_edge(edge)
                if cytoscape_edge:
                    cytoscape_data['edges'].append(cytoscape_edge)
        
        # 메타데이터 계산
        cytoscape_data['metadata'] = self._calculate_metadata(cytoscape_data)
        
        return cytoscape_data
    
    def _convert_node(self, node: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        노드를 Cytoscape.js 형식으로 변환합니다.
        
        Args:
            node: 원본 노드 데이터
            
        Returns:
            변환된 노드 데이터
        """
        try:
            if not isinstance(node, dict) or 'id' not in node:
                return None
            
            # 기본 노드 정보
            cytoscape_node = {
                'id': node['id'],
                'label': node.get('label', 'Unknown'),
                'type': node.get('type', 'table'),
                'group': node.get('group', 'DB'),
                'meta': {}
            }
            
            # 메타데이터 변환
            if 'meta' in node and isinstance(node['meta'], dict):
                meta = node['meta']
                cytoscape_node['meta'] = {
                    'owner': meta.get('owner', ''),
                    'table_name': meta.get('table_name', ''),
                    'status': meta.get('status', 'VALID'),
                    'comment': meta.get('comment', ''),
                    'columns': []
                }
                
                # 컬럼 정보 변환
                if 'columns' in meta and isinstance(meta['columns'], list):
                    for col in meta['columns']:
                        if isinstance(col, dict):
                            column_info = {
                                'name': col.get('name', ''),
                                'data_type': col.get('data_type', ''),
                                'nullable': col.get('nullable', True),
                                'is_pk': col.get('is_pk', False),
                                'comment': col.get('comment', '')
                            }
                            cytoscape_node['meta']['columns'].append(column_info)
                
                # PK 컬럼 정보
                if 'pk_columns' in meta and isinstance(meta['pk_columns'], list):
                    cytoscape_node['meta']['pk_columns'] = meta['pk_columns']
            
            return cytoscape_node
            
        except Exception as e:
            logger.warning(f"노드 변환 실패: {e}, 노드: {node}")
            return None
    
    def _convert_edge(self, edge: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        엣지를 Cytoscape.js 형식으로 변환합니다.
        
        Args:
            edge: 원본 엣지 데이터
            
        Returns:
            변환된 엣지 데이터
        """
        try:
            if not isinstance(edge, dict) or 'source' not in edge or 'target' not in edge:
                return None
            
            # 기본 엣지 정보
            cytoscape_edge = {
                'id': edge.get('id', f"edge_{edge['source']}_{edge['target']}"),
                'source': edge['source'],
                'target': edge['target'],
                'kind': edge.get('kind', 'relationship'),
                'confidence': edge.get('confidence', 0.5),
                'meta': {}
            }
            
            # 메타데이터 변환
            if 'meta' in edge and isinstance(edge['meta'], dict):
                meta = edge['meta']
                cytoscape_edge['meta'] = {
                    'left_column': meta.get('left_column', ''),
                    'right_column': meta.get('right_column', ''),
                    'frequency': meta.get('frequency', 1),
                    'arrow': meta.get('arrow', True),
                    'source': meta.get('source', 'unknown'),
                    'join_condition': meta.get('join_condition', '')
                }
            
            return cytoscape_edge
            
        except Exception as e:
            logger.warning(f"엣지 변환 실패: {e}, 엣지: {edge}")
            return None
    
    def _calculate_metadata(self, cytoscape_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cytoscape.js 데이터의 메타데이터를 계산합니다.
        
        Args:
            cytoscape_data: Cytoscape.js 형식의 데이터
            
        Returns:
            계산된 메타데이터
        """
        metadata = {
            'total_tables': len(cytoscape_data['nodes']),
            'total_columns': 0,
            'total_pk': 0,
            'total_fk': 0,
            'total_relationships': len(cytoscape_data['edges'])
        }
        
        # 컬럼 및 PK 개수 계산
        for node in cytoscape_data['nodes']:
            if 'meta' in node and 'columns' in node['meta']:
                metadata['total_columns'] += len(node['meta']['columns'])
                
                # PK 컬럼 개수 계산
                for col in node['meta']['columns']:
                    if col.get('is_pk', False):
                        metadata['total_pk'] += 1
        
        # FK 관계 개수 계산
        for edge in cytoscape_data['edges']:
            if edge.get('kind') in ['foreign_key', 'fk_inferred']:
                metadata['total_fk'] += 1
        
        return metadata
    
    def _render_html_template(self, cytoscape_data: Dict[str, Any], project_name: str) -> str:
        """
        HTML 템플릿을 렌더링합니다.
        
        Args:
            cytoscape_data: Cytoscape.js 데이터
            project_name: 프로젝트 이름
            
        Returns:
            렌더링된 HTML 내용
        """
        try:
            # Cytoscape.js 데이터를 JSON으로 직렬화
            data_json = json.dumps(cytoscape_data, ensure_ascii=False, indent=2)
            
            # HTML 템플릿 읽기
            with open(self.cytoscape_template, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # 프로젝트 정보 업데이트
            template_content = template_content.replace(
                '프로젝트: 로딩 중...',
                f'프로젝트: {project_name}'
            )
            
            # 샘플 데이터를 실제 데이터로 교체
            # 실제 구현에서는 서버 사이드 렌더링이나 AJAX를 사용해야 함
            # 여기서는 간단한 인라인 데이터 삽입 방식 사용
            sample_data_script = f"""
            // 실제 데이터는 서버에서 로드되어야 함
            const DATA = {data_json};
            
            // 데이터 로드 함수 수정
            function loadData() {{
                // Cytoscape에 데이터 적용
                applyData(DATA);
                
                // 사이드바 업데이트
                updateSidebar(DATA);
                
                // 프로젝트 정보 업데이트
                document.getElementById('project-info').textContent = '프로젝트: {project_name}';
            }}
            """
            
            # 기존 loadData 함수 교체
            template_content = template_content.replace(
                '// 데이터 로드\n        function loadData() {',
                sample_data_script + '\n        // 데이터 로드\n        function loadData() {'
            )
            
            return template_content
            
        except Exception as e:
            logger.error(f"HTML 템플릿 렌더링 실패: {e}")
            raise


def create_cytoscape_erd(erd_data: Dict[str, Any], project_name: str, output_dir: Path) -> Path:
    """
    Cytoscape.js ERD를 생성하는 편의 함수입니다.
    
    Args:
        erd_data: ERD 빌더에서 생성된 데이터
        project_name: 프로젝트 이름
        output_dir: 출력 디렉토리
        
    Returns:
        생성된 HTML 파일 경로
    """
    try:
        # 템플릿 디렉토리 경로
        template_dir = Path(__file__).parent.parent / "templates"
        
        # 렌더러 생성
        renderer = CytoscapeERDRenderer(template_dir)
        
        # ERD 렌더링 (파일명 생성은 render 메서드 내부에서 처리)
        result_path = renderer.render(erd_data, project_name, output_dir)
        
        return result_path
        
    except Exception as e:
        logger.error(f"Cytoscape.js ERD 생성 실패: {e}")
        raise


if __name__ == "__main__":
    # 테스트용 코드
    import sys
    from pathlib import Path
    
    # 로깅 설정
    logging.basicConfig(level=logging.INFO)
    
    # 테스트 데이터
    test_data = {
        'nodes': [
            {
                'id': 'table:HR.EMPLOYEES',
                'label': 'EMPLOYEES',
                'type': 'table',
                'group': 'DB',
                'meta': {
                    'owner': 'HR',
                    'table_name': 'EMPLOYEES',
                    'columns': [
                        {'name': 'EMPLOYEE_ID', 'data_type': 'NUMBER', 'is_pk': True, 'nullable': False},
                        {'name': 'FIRST_NAME', 'data_type': 'VARCHAR2', 'is_pk': False, 'nullable': False}
                    ]
                }
            }
        ],
        'edges': []
    }
    
    # 출력 디렉토리
    output_dir = Path("./output")
    
    try:
        result = create_cytoscape_erd(test_data, "TEST_PROJECT", output_dir)
        print(f"테스트 ERD 생성 완료: {result}")
    except Exception as e:
        print(f"테스트 실패: {e}")
        sys.exit(1)
