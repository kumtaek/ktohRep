"""
분리된 HTML 리포트 생성기 (ERD 전용 / 아키텍처 전용)
"""
import sqlite3
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, Counter
from datetime import datetime
import os

class SeparateHTMLReporter:
    """분리된 HTML 리포트 생성기"""
    
    def __init__(self, metadata_engine):
        self.metadata_engine = metadata_engine
        self.db_path = metadata_engine.db_path
    
    def generate_erd_html(self, project_id: int, output_path: str = None) -> str:
        """ERD 전용 HTML 리포트 생성"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 테이블 정보 수집
                tables = self._get_table_info(cursor, project_id)
                relationships = self._get_relationships_by_type(cursor, project_id)
                
                # HTML 생성
                html_content = self._generate_erd_html_content(tables, relationships)
                
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
        """아키텍처 전용 HTML 리포트 생성"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 아키텍처 정보 수집
                components = self._get_components_by_layer(cursor, project_id)
                relationships = self._get_relationships_by_type(cursor, project_id)
                stats = self._get_component_stats(cursor, project_id)
                
                # HTML 생성
                html_content = self._generate_architecture_html_content(components, relationships, stats)
                
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
    
    def _get_component_stats(self, cursor, project_id: int) -> Dict:
        """컴포넌트 통계 조회"""
        cursor.execute("""
            SELECT component_type, COUNT(*) 
            FROM components 
            WHERE project_id = ? 
            GROUP BY component_type
        """, (project_id,))
        
        return dict(cursor.fetchall())
    
    def _get_table_info(self, cursor, project_id: int) -> List:
        """테이블 정보 조회"""
        cursor.execute("""
            SELECT component_name, component_type
            FROM components
            WHERE project_id = ? AND component_type IN ('table', 'table_dummy')
            ORDER BY component_type, component_name
        """, (project_id,))
        
        return cursor.fetchall()
    
    def _generate_erd_html_content(self, tables: List, relationships: Dict) -> str:
        """ERD 전용 HTML 콘텐츠 생성"""
        # ERD 다이어그램 생성 (SVG 직접 생성)
        erd_svg = self._generate_erd_svg(tables, relationships)
        
        # 테이블 상세 정보
        table_details = self._generate_table_details_html(tables, relationships)
        
        html_template = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ERD 분석 리포트 - SourceAnalyzer</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 15px;
            background-color: #f5f5f5;
            line-height: 1.6;
        }}
        .container {{
            max-width: 95%;
            margin: 0 auto;
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 3px solid #007acc;
        }}
        .header h1 {{
            color: #007acc;
            margin: 0;
            font-size: 2.2em;
        }}
        .header .subtitle {{
            color: #666;
            font-size: 1.1em;
            margin-top: 10px;
        }}
        .diagram-section {{
            margin: 30px 0;
            padding: 20px;
            border-left: 4px solid #007acc;
            background-color: #f8f9fa;
        }}
        .diagram-section h2 {{
            color: #007acc;
            margin-top: 0;
            font-size: 1.6em;
        }}
        .diagram-container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            overflow-x: auto;
        }}
        .table-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .table-card {{
            background: white;
            border: 2px solid #007acc;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .table-header {{
            background: #007acc;
            color: white;
            padding: 15px;
            font-weight: bold;
            text-align: center;
        }}
        .table-body {{
            padding: 15px;
        }}
        .column {{
            margin: 8px 0;
            padding: 5px;
            background: #f8f9fa;
            border-radius: 4px;
            font-size: 0.9em;
        }}
        .pk {{ background: #fff3cd; border-left: 4px solid #ffc107; }}
        .fk {{ background: #d1ecf1; border-left: 4px solid #17a2b8; }}
        .timestamp {{
            text-align: center;
            color: #666;
            font-size: 0.9em;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
        .relationships-section {{
            margin: 30px 0;
        }}
        .relationship-list {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .relationship-item {{
            margin: 10px 0;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 4px;
            border-left: 4px solid #28a745;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 ERD 분석 리포트</h1>
            <div class="subtitle">Entity Relationship Diagram</div>
            <div class="subtitle">생성일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}</div>
        </div>

        <div class="diagram-section">
            <h2>🗂️ 데이터베이스 구조 다이어그램</h2>
            <div class="diagram-container">
                {erd_svg}
            </div>
        </div>

        {table_details}

        <div class="timestamp">
            Generated by SourceAnalyzer ERD Reporter | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
        """
        
        return html_template
    
    def _generate_architecture_html_content(self, components: Dict, relationships: Dict, stats: Dict) -> str:
        """아키텍처 전용 HTML 콘텐츠 생성"""
        # 아키텍처 다이어그램 생성 (SVG 직접 생성)
        arch_svg = self._generate_architecture_svg(components, relationships)
        
        # 관계 분석
        relationship_analysis = self._generate_relationship_analysis_html(relationships)
        
        # 통계 테이블
        stats_table = self._generate_stats_table_html(stats)
        
        html_template = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>시스템 아키텍처 분석 리포트 - SourceAnalyzer</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 15px;
            background-color: #f5f5f5;
            line-height: 1.6;
        }}
        .container {{
            max-width: 95%;
            margin: 0 auto;
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 3px solid #007acc;
        }}
        .header h1 {{
            color: #007acc;
            margin: 0;
            font-size: 2.2em;
        }}
        .header .subtitle {{
            color: #666;
            font-size: 1.1em;
            margin-top: 10px;
        }}
        .section {{
            margin: 30px 0;
            padding: 20px;
            border-left: 4px solid #007acc;
            background-color: #f8f9fa;
        }}
        .section h2 {{
            color: #007acc;
            margin-top: 0;
            font-size: 1.6em;
        }}
        .diagram-container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            overflow-x: auto;
        }}
        .stats-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .stats-table th, .stats-table td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        .stats-table th {{
            background-color: #007acc;
            color: white;
            font-weight: bold;
        }}
        .stats-table tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        .relationship-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .relationship-card {{
            background: white;
            border: 2px solid #28a745;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .relationship-header {{
            background: #28a745;
            color: white;
            padding: 15px;
            font-weight: bold;
            text-align: center;
        }}
        .relationship-body {{
            padding: 15px;
            max-height: 300px;
            overflow-y: auto;
        }}
        .relationship-item {{
            margin: 5px 0;
            padding: 8px;
            background: #f8f9fa;
            border-radius: 4px;
            font-size: 0.9em;
        }}
        .timestamp {{
            text-align: center;
            color: #666;
            font-size: 0.9em;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏗️ 시스템 아키텍처 분석</h1>
            <div class="subtitle">System Architecture Analysis Report</div>
            <div class="subtitle">생성일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}</div>
        </div>

        <div class="section">
            <h2>🏗️ 아키텍처 구조 다이어그램</h2>
            <div class="diagram-container">
                {arch_svg}
            </div>
        </div>

        <div class="section">
            <h2>🔗 컴포넌트 관계 분석</h2>
            {relationship_analysis}
        </div>

        <div class="section">
            <h2>📊 구성 요소 통계</h2>
            {stats_table}
        </div>

        <div class="timestamp">
            Generated by SourceAnalyzer Architecture Reporter | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
        """
        
        return html_template
    
    def _generate_erd_svg(self, tables: List, relationships: Dict) -> str:
        """ERD SVG 생성"""
        real_tables = [t for t in tables if t[1] == 'table']
        
        if not real_tables:
            return '<div style="text-align: center; padding: 50px; color: #666;">표시할 테이블이 없습니다.</div>'
        
        # SVG 시작
        svg_width = max(800, len(real_tables) * 200)
        svg_height = 400
        
        svg_content = f'<svg width="100%" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}">'
        
        # 테이블들을 가로로 배치
        table_width = 180
        table_height = 120
        spacing = 50
        
        for i, (table_name, _) in enumerate(real_tables[:5]):  # 최대 5개만
            x = 50 + i * (table_width + spacing)
            y = 50
            
            # 테이블 박스
            svg_content += f'''
                <rect x="{x}" y="{y}" width="{table_width}" height="{table_height}" 
                      fill="#fff3e0" stroke="#e65100" stroke-width="2" rx="5"/>
                <rect x="{x}" y="{y}" width="{table_width}" height="25" fill="#e65100"/>
                <text x="{x + table_width//2}" y="{y + 17}" text-anchor="middle" 
                      fill="white" font-weight="bold" font-size="12">{table_name.upper()}</text>
            '''
            
            # 컬럼 정보 (예시)
            columns = self._get_sample_columns(table_name)
            for j, col in enumerate(columns[:4]):  # 최대 4개 컬럼만
                col_y = y + 35 + j * 15
                svg_content += f'''
                    <text x="{x + 10}" y="{col_y}" fill="#333" font-size="10">{col}</text>
                '''
        
        # 관계선 그리기 (간단한 예시)
        if len(real_tables) > 1 and 'join' in relationships:
            # 첫 번째와 두 번째 테이블 연결
            svg_content += f'''
                <defs>
                    <marker id="arrowhead" markerWidth="10" markerHeight="7" 
                            refX="10" refY="3.5" orient="auto">
                        <polygon points="0 0, 10 3.5, 0 7" fill="#666"/>
                    </marker>
                </defs>
                <line x1="{50 + table_width}" y1="{50 + table_height//2}" 
                      x2="{50 + table_width + spacing}" y2="{50 + table_height//2}" 
                      stroke="#666" stroke-width="2" marker-end="url(#arrowhead)"/>
                <text x="{50 + table_width + spacing//2}" y="{50 + table_height//2 - 5}" 
                      text-anchor="middle" fill="#666" font-size="10">1:N</text>
            '''
        
        svg_content += '</svg>'
        return svg_content
    
    def _generate_architecture_svg(self, components: Dict, relationships: Dict) -> str:
        """아키텍처 SVG 생성"""
        if not components:
            return '<div style="text-align: center; padding: 50px; color: #666;">표시할 컴포넌트가 없습니다.</div>'
        
        # SVG 시작
        svg_width = 1000
        svg_height = 500
        
        svg_content = f'<svg width="100%" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}">'
        
        # 계층별 배치
        layer_order = ['controller', 'service', 'mapper', 'model']
        layer_colors = {
            'controller': {'fill': '#e1f5fe', 'stroke': '#01579b'},
            'service': {'fill': '#f3e5f5', 'stroke': '#4a148c'},
            'mapper': {'fill': '#e8f5e8', 'stroke': '#1b5e20'},
            'model': {'fill': '#fff3e0', 'stroke': '#e65100'}
        }
        
        y_start = 50
        layer_height = 80
        layer_spacing = 20
        
        for i, layer in enumerate(layer_order):
            if layer not in components:
                continue
                
            y = y_start + i * (layer_height + layer_spacing)
            layer_components = components[layer][:8]  # 최대 8개만
            
            # 계층 배경
            svg_content += f'''
                <rect x="50" y="{y}" width="900" height="{layer_height}" 
                      fill="{layer_colors[layer]['fill']}" stroke="{layer_colors[layer]['stroke']}" 
                      stroke-width="2" rx="10"/>
                <text x="500" y="{y + 20}" text-anchor="middle" 
                      fill="{layer_colors[layer]['stroke']}" font-weight="bold" font-size="14">
                      {layer.title()} Layer</text>
            '''
            
            # 컴포넌트들
            comp_width = 100
            comp_spacing = 10
            start_x = 80
            
            for j, comp in enumerate(layer_components):
                comp_x = start_x + j * (comp_width + comp_spacing)
                comp_y = y + 35
                
                svg_content += f'''
                    <rect x="{comp_x}" y="{comp_y}" width="{comp_width}" height="25" 
                          fill="white" stroke="{layer_colors[layer]['stroke']}" rx="3"/>
                    <text x="{comp_x + comp_width//2}" y="{comp_y + 16}" text-anchor="middle" 
                          fill="#333" font-size="9">{comp['name'][:12]}</text>
                '''
        
        # 화살표 추가 (계층간 관계)
        for i in range(len(layer_order) - 1):
            if layer_order[i] in components and layer_order[i+1] in components:
                y1 = y_start + i * (layer_height + layer_spacing) + layer_height
                y2 = y_start + (i+1) * (layer_height + layer_spacing)
                
                svg_content += f'''
                    <defs>
                        <marker id="layer-arrow" markerWidth="10" markerHeight="7" 
                                refX="10" refY="3.5" orient="auto">
                            <polygon points="0 0, 10 3.5, 0 7" fill="#333"/>
                        </marker>
                    </defs>
                    <line x1="500" y1="{y1}" x2="500" y2="{y2}" 
                          stroke="#333" stroke-width="2" marker-end="url(#layer-arrow)"/>
                '''
        
        svg_content += '</svg>'
        return svg_content
    
    def _get_sample_columns(self, table_name: str) -> List[str]:
        """테이블별 샘플 컬럼 반환"""
        if table_name.lower() == 'users':
            return ['🔑 id (PK)', 'username', 'email', 'status']
        elif table_name.lower() == 'products':
            return ['🔑 id (PK)', 'name', 'price', 'category_id (FK)']
        elif table_name.lower() == 'categories':
            return ['🔑 category_id (PK)', 'name', 'description']
        else:
            return ['🔑 id (PK)', 'name', 'created_date']
    
    def _generate_table_details_html(self, tables: List, relationships: Dict) -> str:
        """테이블 상세 정보 HTML 생성"""
        real_tables = [t for t in tables if t[1] == 'table']
        
        if not real_tables:
            return '<div class="diagram-section"><h2>📋 테이블 상세 정보</h2><p>표시할 테이블이 없습니다.</p></div>'
        
        html_content = '<div class="diagram-section"><h2>📋 테이블 상세 정보</h2><div class="table-details">'
        
        for table_name, _ in real_tables:
            columns = self._get_sample_columns(table_name)
            
            html_content += f'''
                <div class="table-card">
                    <div class="table-header">{table_name.upper()}</div>
                    <div class="table-body">
            '''
            
            for col in columns:
                css_class = 'pk' if 'PK' in col else 'fk' if 'FK' in col else ''
                html_content += f'<div class="column {css_class}">{col}</div>'
            
            html_content += '</div></div>'
        
        # 관계 정보 추가
        if 'join' in relationships:
            html_content += '</div><div class="relationships-section"><h3>🔗 테이블 관계</h3><div class="relationship-list">'
            
            joins = relationships['join'][:10]  # 상위 10개만
            for join in joins:
                html_content += f'''
                    <div class="relationship-item">
                        {join['source']} ➜ {join['target']}
                        {f" (신뢰도: {join['confidence']})" if join['confidence'] < 1.0 else ""}
                    </div>
                '''
            
            html_content += '</div></div>'
        else:
            html_content += '</div>'
        
        html_content += '</div>'
        return html_content
    
    def _generate_relationship_analysis_html(self, relationships: Dict) -> str:
        """관계 분석 HTML 생성"""
        important_types = ['dependency', 'implements', 'calls', 'extends']
        
        html_content = '<div class="relationship-grid">'
        
        for rel_type in important_types:
            if rel_type not in relationships:
                continue
                
            rels = relationships[rel_type][:10]  # 최대 10개
            if not rels:
                continue
            
            type_names = {
                'dependency': '의존성 관계',
                'implements': '구현 관계',
                'calls': '호출 관계',
                'extends': '상속 관계'
            }
            
            html_content += f'''
                <div class="relationship-card">
                    <div class="relationship-header">{type_names.get(rel_type, rel_type)} ({len(rels)}개)</div>
                    <div class="relationship-body">
            '''
            
            for rel in rels:
                html_content += f'''
                    <div class="relationship-item">
                        {rel['source']} ➜ {rel['target']}
                    </div>
                '''
            
            html_content += '</div></div>'
        
        html_content += '</div>'
        return html_content
    
    def _generate_stats_table_html(self, stats: Dict) -> str:
        """통계 테이블 HTML 생성"""
        html_content = '<table class="stats-table"><thead><tr><th>컴포넌트 타입</th><th>수량</th><th>설명</th></tr></thead><tbody>'
        
        display_types = {
            'class': ('클래스', 'Java 클래스 파일'),
            'interface': ('인터페이스', 'Java 인터페이스 정의'),
            'table': ('테이블', '데이터베이스 테이블'),
            'table_dummy': ('참조 테이블', 'MyBatis에서 참조된 테이블')
        }
        
        for comp_type, (display_name, description) in display_types.items():
            count = stats.get(comp_type, 0)
            if count > 0:
                html_content += f'<tr><td>{display_name}</td><td>{count}개</td><td>{description}</td></tr>'
        
        total = sum(v for k, v in stats.items() if k in display_types)
        html_content += f'<tr style="font-weight:bold;background-color:#e3f2fd;"><td>전체</td><td>{total}개</td><td>총 컴포넌트 수</td></tr>'
        
        html_content += '</tbody></table>'
        return html_content