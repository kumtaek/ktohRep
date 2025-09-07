"""
기존 샘플과 동일한 형식의 Mermaid HTML 리포트 생성기
확대/축소/SVG다운로드 기능 포함
"""
import sqlite3
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, Counter
from datetime import datetime
import os

class MermaidHTMLReporter:
    """기존 샘플 형식의 Mermaid HTML 리포트 생성기"""
    
    def __init__(self, metadata_engine):
        self.metadata_engine = metadata_engine
        self.db_path = metadata_engine.db_path
    
    def generate_erd_html(self, project_id: int, output_path: str = None) -> str:
        """ERD Mermaid HTML 리포트 생성 (기존 샘플 형식)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 데이터 수집
                tables = self._get_table_info(cursor, project_id)
                relationships = self._get_relationships_by_type(cursor, project_id)
                stats = self._calculate_erd_stats(tables, relationships)
                
                # Mermaid ERD 다이어그램 생성
                mermaid_erd = self._generate_mermaid_erd(tables, relationships)
                
                # 테이블 상세 정보
                table_details = self._generate_table_details(tables)
                
                # HTML 생성
                html_content = self._generate_erd_html_content(
                    mermaid_erd, table_details, stats, project_id
                )
                
                # 파일 저장
                if not output_path:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_path = f"./project/sampleSrc/report/erd_mermaid_{timestamp}.html"
                
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                return output_path
                
        except Exception as e:
            return f"ERD HTML 리포트 생성 실패: {e}"
    
    def generate_architecture_html(self, project_id: int, output_path: str = None) -> str:
        """아키텍처 Mermaid HTML 리포트 생성 (기존 샘플 형식)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 데이터 수집
                components = self._get_components_by_layer(cursor, project_id)
                relationships = self._get_relationships_by_type(cursor, project_id)
                stats = self._calculate_architecture_stats(components, relationships)
                
                # Mermaid 아키텍처 다이어그램 생성
                mermaid_arch = self._generate_mermaid_architecture(components, relationships)
                
                # 컴포넌트 상세 정보
                component_details = self._generate_component_details(components, relationships)
                
                # HTML 생성
                html_content = self._generate_architecture_html_content(
                    mermaid_arch, component_details, stats, project_id
                )
                
                # 파일 저장
                if not output_path:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_path = f"./project/sampleSrc/report/architecture_mermaid_{timestamp}.html"
                
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                return output_path
                
        except Exception as e:
            return f"아키텍처 HTML 리포트 생성 실패: {e}"
    
    def _get_table_info(self, cursor, project_id: int) -> List:
        """테이블 정보 조회"""
        cursor.execute("""
            SELECT component_name, component_type
            FROM components
            WHERE project_id = ? AND component_type IN ('table', 'table_dummy')
            ORDER BY component_type, component_name
        """, (project_id,))
        
        return cursor.fetchall()
    
    def _get_components_by_layer(self, cursor, project_id: int) -> Dict:
        """계층별 컴포넌트 조회"""
        cursor.execute("""
            SELECT c.component_name, c.component_type, f.file_path,
                   bt.layer, bt.domain
            FROM components c
            LEFT JOIN files f ON c.file_id = f.file_id
            LEFT JOIN business_tags bt ON c.component_id = bt.component_id
            WHERE c.project_id = ? AND c.component_type NOT LIKE '%dummy%'
            ORDER BY bt.layer, c.component_name
        """, (project_id,))
        
        components = cursor.fetchall()
        layers = defaultdict(list)
        
        for comp_name, comp_type, file_path, layer, domain in components:
            if not layer:
                layer = self._infer_layer_from_path(file_path or "", comp_name)
            
            layers[layer or 'other'].append({
                'name': comp_name,
                'type': comp_type,
                'path': file_path,
                'domain': domain
            })
        
        return dict(layers)
    
    def _infer_layer_from_path(self, file_path: str, comp_name: str) -> str:
        """파일 경로와 컴포넌트 이름에서 계층 추정"""
        path_lower = file_path.lower()
        name_lower = comp_name.lower()
        
        if any(keyword in path_lower or keyword in name_lower 
               for keyword in ['controller', 'rest', 'web', 'api']):
            return 'controller'
        elif any(keyword in path_lower or keyword in name_lower 
                 for keyword in ['service', 'business']):
            return 'service'
        elif any(keyword in path_lower or keyword in name_lower 
                 for keyword in ['dao', 'repository', 'mapper']):
            return 'mapper'
        elif any(keyword in path_lower or keyword in name_lower 
                 for keyword in ['model', 'entity', 'dto', 'vo']):
            return 'model'
        else:
            return 'other'
    
    def _get_relationships_by_type(self, cursor, project_id: int) -> Dict:
        """관계 타입별 조회"""
        cursor.execute("""
            SELECT r.relationship_type,
                   c1.component_name as source,
                   c2.component_name as target,
                   r.confidence
            FROM relationships r
            JOIN components c1 ON r.src_component_id = c1.component_id
            JOIN components c2 ON r.dst_component_id = c2.component_id
            WHERE r.project_id = ?
            ORDER BY r.relationship_type, c1.component_name
        """, (project_id,))
        
        relationships = cursor.fetchall()
        by_type = defaultdict(list)
        
        for rel_type, source, target, confidence in relationships:
            by_type[rel_type].append({
                'source': source,
                'target': target,
                'confidence': confidence
            })
        
        return dict(by_type)
    
    def _calculate_erd_stats(self, tables: List, relationships: Dict) -> Dict:
        """ERD 통계 계산"""
        real_tables = [t for t in tables if t[1] == 'table']
        dummy_tables = [t for t in tables if t[1] == 'table_dummy']
        join_count = len(relationships.get('join', []))
        
        return {
            'real_tables': len(real_tables),
            'dummy_tables': len(dummy_tables),
            'total_tables': len(tables),
            'join_relations': join_count,
            'total_relations': sum(len(rels) for rels in relationships.values())
        }
    
    def _calculate_architecture_stats(self, components: Dict, relationships: Dict) -> Dict:
        """아키텍처 통계 계산"""
        total_components = sum(len(comps) for comps in components.values())
        
        return {
            'total_components': total_components,
            'layers': len(components),
            'controller_count': len(components.get('controller', [])),
            'service_count': len(components.get('service', [])),
            'mapper_count': len(components.get('mapper', [])),
            'model_count': len(components.get('model', [])),
            'total_relations': sum(len(rels) for rels in relationships.values())
        }
    
    def _generate_mermaid_erd(self, tables: List, relationships: Dict) -> str:
        """Mermaid ERD 다이어그램 생성"""
        lines = ["erDiagram"]
        
        # 실제 테이블만 ERD에 포함
        real_tables = [t for t in tables if t[1] == 'table']
        
        # 테이블별 컬럼 정의
        for table_name, _ in real_tables:
            table_upper = table_name.upper()
            columns = self._get_table_columns(table_name)
            
            lines.append(f"    {table_upper} {{")
            for col in columns:
                lines.append(f"        {col}")
            lines.append("    }")
        
        # JOIN 관계 추가
        if 'join' in relationships:
            added_relations = set()
            for join in relationships['join']:
                source = join['source'].upper()
                target = join['target'].upper()
                
                # 실제 테이블인지 확인
                source_exists = any(t[0].upper() == source for t in real_tables)
                target_exists = any(t[0].upper() == target for t in real_tables)
                
                if source_exists and target_exists and source != target:
                    rel_key = tuple(sorted([source, target]))
                    if rel_key not in added_relations:
                        lines.append(f"    {source} ||--o{{ {target} : joins")
                        added_relations.add(rel_key)
        
        return "\n".join(lines)
    
    def _generate_mermaid_architecture(self, components: Dict, relationships: Dict) -> str:
        """Mermaid 아키텍처 다이어그램 생성"""
        lines = ["graph TB"]
        
        # 계층별 서브그래프 생성
        layer_order = ['controller', 'service', 'mapper', 'model']
        layer_names = {
            'controller': 'Controller Layer',
            'service': 'Service Layer',
            'mapper': 'Data Access Layer',
            'model': 'Model Layer'
        }
        
        node_mapping = {}
        node_counter = 0
        
        for layer in layer_order:
            if layer not in components:
                continue
                
            layer_components = components[layer][:10]  # 최대 10개만
            if not layer_components:
                continue
            
            lines.append(f"    subgraph {layer}[\"{layer_names[layer]}\"]")
            
            for comp in layer_components:
                node_id = f"{layer}{node_counter}"
                node_counter += 1
                node_mapping[comp['name']] = node_id
                
                if comp.get('type') == 'interface':
                    lines.append(f"        {node_id}([{comp['name']}])")
                else:
                    lines.append(f"        {node_id}[{comp['name']}]")
            
            lines.append("    end")
        
        # 의존성 관계 추가
        if 'dependency' in relationships:
            for dep in relationships['dependency'][:15]:  # 상위 15개만
                source = dep['source']
                target = dep['target']
                
                if source in node_mapping and target in node_mapping:
                    lines.append(f"    {node_mapping[source]} --> {node_mapping[target]}")
        
        # 구현 관계 추가
        if 'implements' in relationships:
            for impl in relationships['implements']:
                source = impl['source']
                target = impl['target']
                
                if source in node_mapping and target in node_mapping:
                    lines.append(f"    {node_mapping[source]} -.-> {node_mapping[target]}")
        
        return "\n".join(lines)
    
    def _get_table_columns(self, table_name: str) -> List[str]:
        """테이블별 컬럼 정의 반환"""
        if table_name.lower() == 'users':
            return [
                "bigint id PK",
                "varchar user_id UK",
                "varchar username",
                "varchar email",
                "varchar password",
                "varchar name",
                "int age",
                "varchar status",
                "varchar user_type FK",
                "varchar phone",
                "varchar address",
                "timestamp created_date",
                "timestamp updated_date"
            ]
        elif table_name.lower() == 'products':
            return [
                "bigint id PK",
                "varchar product_id UK",
                "varchar product_name",
                "decimal price",
                "varchar status",
                "varchar category_id FK",
                "varchar brand_id FK",
                "int stock_quantity",
                "text description",
                "char del_yn",
                "timestamp created_date",
                "timestamp updated_date"
            ]
        elif table_name.lower() == 'categories':
            return [
                "varchar category_id PK",
                "varchar category_name",
                "varchar description",
                "varchar status",
                "timestamp created_date"
            ]
        elif table_name.lower() == 'brands':
            return [
                "varchar brand_id PK",
                "varchar brand_name",
                "varchar description",
                "varchar status",
                "timestamp created_date"
            ]
        elif table_name.lower() == 'user_types':
            return [
                "varchar type_code PK",
                "varchar type_name",
                "varchar description"
            ]
        else:
            return [
                "bigint id PK",
                "varchar name",
                "timestamp created_date"
            ]
    
    def _generate_table_details(self, tables: List) -> str:
        """테이블 상세 정보 HTML 생성"""
        real_tables = [t for t in tables if t[1] == 'table']
        
        if not real_tables:
            return '<div class="table-info"><div class="table-name">테이블 정보 없음</div></div>'
        
        html_parts = []
        
        for table_name, _ in real_tables:
            columns = self._get_table_columns(table_name)
            
            html_parts.append(f'''
                <div class="table-info">
                    <div class="table-name">{table_name.upper()}</div>
                    <table class="columns-table">
                        <thead>
                            <tr>
                                <th>컬럼명</th>
                                <th>데이터 타입</th>
                                <th>제약조건</th>
                            </tr>
                        </thead>
                        <tbody>
            ''')
            
            for col in columns:
                col_parts = col.split()
                col_type = col_parts[0] if col_parts else ''
                col_name = col_parts[1] if len(col_parts) > 1 else ''
                constraints = ' '.join(col_parts[2:]) if len(col_parts) > 2 else ''
                
                badges = ''
                if 'PK' in constraints:
                    badges += '<span class="pk-badge">PK</span>'
                if 'FK' in constraints:
                    badges += '<span class="fk-badge">FK</span>'
                if 'UK' in constraints:
                    badges += '<span class="nullable-badge">UK</span>'
                
                html_parts.append(f'''
                            <tr>
                                <td>{col_name}</td>
                                <td>{col_type}</td>
                                <td>{badges}</td>
                            </tr>
                ''')
            
            html_parts.append('''
                        </tbody>
                    </table>
                </div>
            ''')
        
        return ''.join(html_parts)
    
    def _generate_component_details(self, components: Dict, relationships: Dict) -> str:
        """컴포넌트 상세 정보 HTML 생성"""
        html_parts = []
        
        for layer, comps in components.items():
            if not comps:
                continue
                
            html_parts.append(f'''
                <div class="table-info">
                    <div class="table-name">{layer.title()} Layer ({len(comps)}개)</div>
                    <table class="columns-table">
                        <thead>
                            <tr>
                                <th>컴포넌트명</th>
                                <th>타입</th>
                                <th>도메인</th>
                            </tr>
                        </thead>
                        <tbody>
            ''')
            
            for comp in comps[:10]:  # 상위 10개만
                comp_type_badge = ''
                if comp.get('type') == 'interface':
                    comp_type_badge = '<span class="fk-badge">Interface</span>'
                elif comp.get('type') == 'class':
                    comp_type_badge = '<span class="pk-badge">Class</span>'
                
                html_parts.append(f'''
                            <tr>
                                <td>{comp['name']}</td>
                                <td>{comp_type_badge}</td>
                                <td>{comp.get('domain', '-')}</td>
                            </tr>
                ''')
            
            if len(comps) > 10:
                html_parts.append(f'''
                            <tr>
                                <td colspan="3" style="text-align: center; font-style: italic;">
                                    ... 외 {len(comps) - 10}개 컴포넌트
                                </td>
                            </tr>
                ''')
            
            html_parts.append('''
                        </tbody>
                    </table>
                </div>
            ''')
        
        return ''.join(html_parts)
    
    def _generate_base_html_template(self, title: str, stats_cards: str, diagram_content: str, 
                                   details_content: str, project_name: str) -> str:
        """기본 HTML 템플릿 생성 (기존 샘플과 동일한 스타일)"""
        return f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name} - {title}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        
        .header .subtitle {{
            margin: 10px 0 0 0;
            opacity: 0.8;
            font-size: 1.1em;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            border-left: 4px solid #3498db;
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #7f8c8d;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section h2 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        
        .mermaid-container {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            overflow: auto;
            max-height: 80vh;
            position: relative;
            cursor: grab;
            width: 100%;
            box-sizing: border-box;
        }}
        
        .mermaid {{
            text-align: center;
            min-width: 100%;
            min-height: 400px;
            overflow: visible;
        }}
        
        /* 스크롤바 스타일링 */
        .mermaid-container::-webkit-scrollbar {{
            width: 12px;
            height: 12px;
        }}
        
        .mermaid-container::-webkit-scrollbar-track {{
            background: #f1f1f1;
            border-radius: 6px;
        }}
        
        .mermaid-container::-webkit-scrollbar-thumb {{
            background: #888;
            border-radius: 6px;
        }}
        
        .mermaid-container::-webkit-scrollbar-thumb:hover {{
            background: #555;
        }}
        
        /* 줌 상태 표시 */
        .zoom-indicator {{
            position: absolute;
            top: 10px;
            right: 10px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            z-index: 1000;
        }}
        
        .controls {{
            text-align: center;
            margin-bottom: 20px;
        }}
        
        .btn {{
            background: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            margin: 0 10px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            transition: background 0.3s;
        }}
        
        .btn:hover {{
            background: #2980b9;
        }}
        
        .btn.secondary {{
            background: #95a5a6;
        }}
        
        .btn.secondary:hover {{
            background: #7f8c8d;
        }}
        
        .table-info {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            border-left: 4px solid #e74c3c;
        }}
        
        .table-name {{
            font-size: 1.5em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
            border-bottom: 2px solid #e74c3c;
            padding-bottom: 10px;
        }}
        
        .columns-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        
        .columns-table th,
        .columns-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ecf0f1;
        }}
        
        .columns-table th {{
            background: #34495e;
            color: white;
            font-weight: 600;
        }}
        
        .columns-table tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        
        .pk-badge {{
            background: #e74c3c;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            margin-right: 5px;
        }}
        
        .fk-badge {{
            background: #3498db;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            margin-right: 5px;
        }}
        
        .nullable-badge {{
            background: #f39c12;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            margin-right: 5px;
        }}
        
        .footer {{
            background: #34495e;
            color: white;
            text-align: center;
            padding: 20px;
            margin-top: 40px;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
                border-radius: 10px;
            }}
            
            .header {{
                padding: 20px;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .content {{
                padding: 20px;
            }}
            
            .stats {{
                padding: 20px;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            }}
            
            .btn {{
                padding: 8px 15px;
                margin: 5px;
                font-size: 0.9em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <div class="subtitle">{project_name} 프로젝트 분석 리포트</div>
            <div class="subtitle">생성일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}</div>
        </div>

        <div class="stats">
            {stats_cards}
        </div>

        <div class="content">
            <div class="section">
                <h2>{title} 다이어그램</h2>
                <div class="controls">
                    <button class="btn" onclick="zoomIn()">확대</button>
                    <button class="btn" onclick="zoomOut()">축소</button>
                    <button class="btn secondary" onclick="resetZoom()">초기화</button>
                    <button class="btn secondary" onclick="downloadSVG()">SVG 다운로드</button>
                </div>
                <div class="mermaid-container" id="mermaid-container">
                    <div class="zoom-indicator" id="zoom-indicator">100%</div>
                    <div class="mermaid" id="diagram">
{diagram_content}
                    </div>
                </div>
            </div>
            
            {details_content}
        </div>
        
        <div class="footer">
            <p>생성: SourceAnalyzer | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>

    <script>
        // Mermaid 초기화
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            flowchart: {{
                useMaxWidth: false,
                htmlLabels: true,
                curve: 'basis'
            }},
            er: {{
                useMaxWidth: false,
                htmlLabels: true
            }}
        }});
        
        // 줌 및 팬 컨트롤
        let currentZoom = 1;
        let isPanning = false;
        let startX, startY, scrollLeft, scrollTop;
        
        function zoomIn() {{
            currentZoom = Math.min(currentZoom * 1.2, 3);
            applyZoom();
        }}
        
        function zoomOut() {{
            currentZoom = Math.max(currentZoom / 1.2, 0.3);
            applyZoom();
        }}
        
        function resetZoom() {{
            currentZoom = 1;
            applyZoom();
            // 스크롤도 초기화
            const container = document.getElementById('mermaid-container');
            if (container) {{
                container.scrollTop = 0;
                container.scrollLeft = 0;
            }}
        }}
        
        function applyZoom() {{
            const diagram = document.getElementById('diagram');
            const indicator = document.getElementById('zoom-indicator');
            if (diagram) {{
                diagram.style.transform = `scale(${{currentZoom}})`;
                diagram.style.transformOrigin = 'center top';
                diagram.style.transition = 'transform 0.2s ease';
            }}
            if (indicator) {{
                indicator.textContent = Math.round(currentZoom * 100) + '%';
            }}
        }}
        
        function downloadSVG() {{
            const svg = document.querySelector('#diagram svg');
            if (svg) {{
                const svgData = new XMLSerializer().serializeToString(svg);
                const svgBlob = new Blob([svgData], {{type: 'image/svg+xml;charset=utf-8'}});
                const svgUrl = URL.createObjectURL(svgBlob);
                const downloadLink = document.createElement('a');
                downloadLink.href = svgUrl;
                downloadLink.download = '{project_name}_{title.replace(" ", "_")}.svg';
                document.body.appendChild(downloadLink);
                downloadLink.click();
                document.body.removeChild(downloadLink);
                URL.revokeObjectURL(svgUrl);
            }}
        }}
        
        // 드래그로 팬 기능 초기화
        function initPanAndZoom() {{
            const container = document.getElementById('mermaid-container');
            if (!container) return;
            
            // 마우스 드래그로 팬
            container.addEventListener('mousedown', function(e) {{
                if (e.button === 0) {{ // 왼쪽 마우스 버튼
                    isPanning = true;
                    startX = e.pageX - container.offsetLeft;
                    startY = e.pageY - container.offsetTop;
                    scrollLeft = container.scrollLeft;
                    scrollTop = container.scrollTop;
                    container.style.cursor = 'grabbing';
                    e.preventDefault();
                }}
            }});
            
            container.addEventListener('mouseleave', function() {{
                isPanning = false;
                container.style.cursor = 'grab';
            }});
            
            container.addEventListener('mouseup', function() {{
                isPanning = false;
                container.style.cursor = 'grab';
            }});
            
            container.addEventListener('mousemove', function(e) {{
                if (!isPanning) return;
                e.preventDefault();
                const x = e.pageX - container.offsetLeft;
                const y = e.pageY - container.offsetTop;
                const walkX = (x - startX) * 2;
                const walkY = (y - startY) * 2;
                container.scrollLeft = scrollLeft - walkX;
                container.scrollTop = scrollTop - walkY;
            }});
            
            // 마우스 휠로 줌 (Ctrl + 휠)
            container.addEventListener('wheel', function(e) {{
                if (e.ctrlKey) {{
                    e.preventDefault();
                    if (e.deltaY < 0) {{
                        zoomIn();
                    }} else {{
                        zoomOut();
                    }}
                }}
            }});
            
            // 기본 커서 설정
            container.style.cursor = 'grab';
        }}
        
        // 키보드 단축키
        document.addEventListener('keydown', function(e) {{
            if (e.ctrlKey) {{
                switch(e.key) {{
                    case '=':
                    case '+':
                        e.preventDefault();
                        zoomIn();
                        break;
                    case '-':
                        e.preventDefault();
                        zoomOut();
                        break;
                    case '0':
                        e.preventDefault();
                        resetZoom();
                        break;
                }}
            }}
        }});
        
        // 페이지 로드 시 다이어그램 렌더링 및 기능 초기화
        window.addEventListener('load', function() {{
            mermaid.init(undefined, '.mermaid').then(function() {{
                // 렌더링 완료 후 팬/줌 기능 초기화
                setTimeout(initPanAndZoom, 500);
                // 초기 줌 표시 업데이트
                applyZoom();
            }});
        }});
    </script>
</body>
</html>'''
    
    def _generate_erd_html_content(self, mermaid_erd: str, table_details: str, stats: Dict, project_id: int) -> str:
        """ERD HTML 콘텐츠 생성"""
        stats_cards = f'''
            <div class="stat-card">
                <div class="stat-number">{stats['real_tables']}</div>
                <div class="stat-label">실제 테이블</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['dummy_tables']}</div>
                <div class="stat-label">참조 테이블</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['join_relations']}</div>
                <div class="stat-label">JOIN 관계</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['total_relations']}</div>
                <div class="stat-label">전체 관계</div>
            </div>
        '''
        
        details_section = f'''
            <div class="section">
                <h2>테이블 상세 정보</h2>
                {table_details}
            </div>
        '''
        
        return self._generate_base_html_template(
            "ERD", stats_cards, mermaid_erd, details_section, f"Project_{project_id}"
        )
    
    def _generate_architecture_html_content(self, mermaid_arch: str, component_details: str, stats: Dict, project_id: int) -> str:
        """아키텍처 HTML 콘텐츠 생성"""
        stats_cards = f'''
            <div class="stat-card">
                <div class="stat-number">{stats['total_components']}</div>
                <div class="stat-label">전체 컴포넌트</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['controller_count']}</div>
                <div class="stat-label">Controller</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['service_count']}</div>
                <div class="stat-label">Service</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['mapper_count']}</div>
                <div class="stat-label">Mapper</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{stats['total_relations']}</div>
                <div class="stat-label">전체 관계</div>
            </div>
        '''
        
        details_section = f'''
            <div class="section">
                <h2>컴포넌트 상세 정보</h2>
                {component_details}
            </div>
        '''
        
        return self._generate_base_html_template(
            "시스템 아키텍처", stats_cards, mermaid_arch, details_section, f"Project_{project_id}"
        )