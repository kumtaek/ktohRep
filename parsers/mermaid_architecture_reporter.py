"""
Mermaid 다이어그램 기반 HTML 아키텍처 리포트 생성기
"""
import sqlite3
from typing import Dict, List, Tuple, Optional
from collections import defaultdict, Counter
from datetime import datetime
import os

class MermaidArchitectureReporter:
    """Mermaid 다이어그램 기반 HTML 리포트 생성"""
    
    def __init__(self, metadata_engine):
        self.metadata_engine = metadata_engine
        self.db_path = metadata_engine.db_path
    
    def generate_html_report(self, project_id: int, output_path: str = None) -> str:
        """완전한 HTML 리포트 생성"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 데이터 수집
                components = self._get_components_by_layer(cursor, project_id)
                relationships = self._get_relationships_by_type(cursor, project_id)
                stats = self._get_component_stats(cursor, project_id)
                tables = self._get_table_info(cursor, project_id)
                
                # HTML 생성
                html_content = self._generate_html_content(components, relationships, stats, tables)
                
                # 파일 저장
                if not output_path:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_path = f"./project/sampleSrc/report/architecture_mermaid_{timestamp}.html"
                
                # 디렉토리 생성
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                return output_path
                
        except Exception as e:
            return f"HTML 리포트 생성 실패: {e}"
    
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
    
    def _generate_html_content(self, components: Dict, relationships: Dict, stats: Dict, tables: List) -> str:
        """HTML 콘텐츠 생성"""
        # Mermaid 다이어그램들 생성
        architecture_diagram = self._generate_architecture_mermaid(components, relationships)
        erd_diagram = self._generate_erd_mermaid(tables, relationships)
        relationship_diagram = self._generate_relationship_mermaid(relationships)
        
        # 통계 테이블 생성
        stats_table = self._generate_stats_table(stats)
        
        # HTML 템플릿
        html_template = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SourceAnalyzer 아키텍처 분석 리포트</title>
    <script src="../static/mermaid.min.js"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 3px solid #007acc;
        }}
        .header h1 {{
            color: #007acc;
            margin: 0;
            font-size: 2.5em;
        }}
        .header .subtitle {{
            color: #666;
            font-size: 1.1em;
            margin-top: 10px;
        }}
        .section {{
            margin: 40px 0;
            padding: 20px;
            border-left: 4px solid #007acc;
            background-color: #f8f9fa;
        }}
        .section h2 {{
            color: #007acc;
            margin-top: 0;
            font-size: 1.8em;
        }}
        .diagram-container {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .stats-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
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
        .mermaid {{
            text-align: center;
        }}
        .timestamp {{
            text-align: center;
            color: #666;
            font-size: 0.9em;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }}
        .toc {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .toc ul {{
            list-style-type: none;
            padding-left: 0;
        }}
        .toc li {{
            margin: 8px 0;
        }}
        .toc a {{
            color: #007acc;
            text-decoration: none;
            font-weight: 500;
        }}
        .toc a:hover {{
            text-decoration: underline;
        }}
    </style>
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true
            }}
        }});
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏗️ SourceAnalyzer</h1>
            <div class="subtitle">시스템 아키텍처 분석 리포트</div>
            <div class="subtitle">생성일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}</div>
        </div>

        <div class="toc">
            <h3>📑 목차</h3>
            <ul>
                <li><a href="#architecture">1. 시스템 아키텍처 구조</a></li>
                <li><a href="#erd">2. ERD (Entity Relationship Diagram)</a></li>
                <li><a href="#relationships">3. 컴포넌트 관계 분석</a></li>
                <li><a href="#statistics">4. 구성 요소 통계</a></li>
            </ul>
        </div>

        <div class="section" id="architecture">
            <h2>🏗️ 시스템 아키텍처 구조</h2>
            <p>시스템의 전체적인 계층 구조와 컴포넌트 배치를 보여줍니다.</p>
            <div class="diagram-container">
                <div class="mermaid">
{architecture_diagram}
                </div>
            </div>
        </div>

        <div class="section" id="erd">
            <h2>🗄️ ERD (Entity Relationship Diagram)</h2>
            <p>데이터베이스 테이블 간의 관계를 시각적으로 표현합니다.</p>
            <div class="diagram-container">
                <div class="mermaid">
{erd_diagram}
                </div>
            </div>
        </div>

        <div class="section" id="relationships">
            <h2>🔗 컴포넌트 관계 분석</h2>
            <p>시스템 내 컴포넌트들 간의 의존성 및 호출 관계를 분석합니다.</p>
            <div class="diagram-container">
                <div class="mermaid">
{relationship_diagram}
                </div>
            </div>
        </div>

        <div class="section" id="statistics">
            <h2>📊 구성 요소 통계</h2>
            <p>시스템을 구성하는 각 요소들의 수량 및 분포를 보여줍니다.</p>
            {stats_table}
        </div>

        <div class="timestamp">
            Generated by SourceAnalyzer | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
        """
        
        return html_template
    
    def _generate_architecture_mermaid(self, components: Dict, relationships: Dict) -> str:
        """아키텍처 구조 Mermaid 다이어그램 생성"""
        lines = ["graph TB"]
        
        # 계층별 노드 정의
        layer_order = ['controller', 'service', 'mapper', 'model']
        layer_styles = {
            'controller': 'fill:#e1f5fe,stroke:#01579b,stroke-width:2px',
            'service': 'fill:#f3e5f5,stroke:#4a148c,stroke-width:2px',
            'mapper': 'fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px',
            'model': 'fill:#fff3e0,stroke:#e65100,stroke-width:2px'
        }
        
        node_counter = 0
        node_mapping = {}
        
        for layer in layer_order:
            if layer not in components:
                continue
                
            layer_components = components[layer]
            if not layer_components:
                continue
            
            # 서브그래프로 계층 표현
            layer_name = {
                'controller': 'Controller Layer',
                'service': 'Service Layer',
                'mapper': 'Data Access Layer', 
                'model': 'Model Layer'
            }.get(layer, layer.title())
            
            lines.append(f"    subgraph {layer}[{layer_name}]")
            
            for comp in layer_components[:8]:  # 최대 8개만 표시
                node_id = f"{layer}{node_counter}"
                node_counter += 1
                node_mapping[comp['name']] = node_id
                
                # 컴포넌트 타입에 따라 모양 변경
                if comp.get('type') == 'interface':
                    lines.append(f"        {node_id}([{comp['name']}])")
                else:
                    lines.append(f"        {node_id}[{comp['name']}]")
            
            lines.append("    end")
            lines.append("")
        
        # 의존성 관계 추가 (주요 관계만)
        if 'dependency' in relationships:
            lines.append("    %% Dependencies")
            deps = relationships['dependency'][:10]  # 상위 10개만
            for dep in deps:
                source = dep['source']
                target = dep['target']
                
                if source in node_mapping and target in node_mapping:
                    lines.append(f"    {node_mapping[source]} --> {node_mapping[target]}")
        
        # 스타일 적용
        lines.append("")
        lines.append("    %% Styling")
        for layer, style in layer_styles.items():
            lines.append(f"    classDef {layer}Class {style}")
        
        return "\n".join(lines)
    
    def _generate_erd_mermaid(self, tables: List, relationships: Dict) -> str:
        """ERD Mermaid 다이어그램 생성"""
        lines = ["erDiagram"]
        
        # 실제 테이블만 표시
        real_tables = [t for t in tables if t[1] == 'table']
        
        # 테이블 정의
        for table_name, _ in real_tables:
            table_upper = table_name.upper()
            
            # 테이블별 컬럼 정의 (예시)
            if table_name.lower() == 'users':
                lines.extend([
                    f"    {table_upper} {{",
                    "        bigint id PK",
                    "        varchar username",
                    "        varchar email",
                    "        varchar password",
                    "        varchar name",
                    "        varchar status",
                    "        timestamp created_date",
                    "    }"
                ])
            elif table_name.lower() == 'products':
                lines.extend([
                    f"    {table_upper} {{",
                    "        bigint id PK",
                    "        varchar product_name",
                    "        decimal price",
                    "        varchar category_id FK",
                    "        varchar brand_id FK",
                    "        varchar status",
                    "        timestamp created_date",
                    "    }"
                ])
            elif table_name.lower() == 'categories':
                lines.extend([
                    f"    {table_upper} {{",
                    "        varchar category_id PK",
                    "        varchar category_name",
                    "        varchar description",
                    "        varchar status",
                    "    }"
                ])
            elif table_name.lower() == 'brands':
                lines.extend([
                    f"    {table_upper} {{",
                    "        varchar brand_id PK",
                    "        varchar brand_name",
                    "        varchar description",
                    "        varchar status",
                    "    }"
                ])
            else:
                lines.extend([
                    f"    {table_upper} {{",
                    "        bigint id PK",
                    "        varchar name",
                    "        timestamp created_date",
                    "    }"
                ])
        
        # 관계 정의
        if 'join' in relationships:
            joins = relationships['join'][:10]  # 상위 10개만
            added_relationships = set()
            
            for join in joins:
                source = join['source'].upper()
                target = join['target'].upper()
                
                # 중복 관계 제거
                rel_key = f"{source}-{target}"
                if rel_key not in added_relationships and source != target:
                    # 테이블 이름이 실제 테이블인지 확인
                    source_exists = any(t[0].upper() == source for t in real_tables)
                    target_exists = any(t[0].upper() == target for t in real_tables)
                    
                    if source_exists and target_exists:
                        lines.append(f"    {source} ||--o{{ {target} : joins")
                        added_relationships.add(rel_key)
        
        return "\n".join(lines)
    
    def _generate_relationship_mermaid(self, relationships: Dict) -> str:
        """관계 분석 Mermaid 다이어그램 생성"""
        lines = ["graph LR"]
        
        # 주요 관계 타입들만 표시
        important_types = ['dependency', 'implements', 'calls']
        colors = {
            'dependency': '#ff6b6b',
            'implements': '#4ecdc4', 
            'calls': '#45b7d1'
        }
        
        node_counter = 0
        node_mapping = {}
        
        for rel_type in important_types:
            if rel_type not in relationships:
                continue
                
            rels = relationships[rel_type][:5]  # 각 타입별 5개만
            
            for rel in rels:
                source = rel['source']
                target = rel['target']
                
                # 노드 ID 생성
                if source not in node_mapping:
                    node_mapping[source] = f"n{node_counter}"
                    node_counter += 1
                
                if target not in node_mapping:
                    node_mapping[target] = f"n{node_counter}"
                    node_counter += 1
                
                source_id = node_mapping[source]
                target_id = node_mapping[target]
                
                # 관계 표시
                if rel_type == 'dependency':
                    lines.append(f"    {source_id}[{source}] -->|depends on| {target_id}[{target}]")
                elif rel_type == 'implements':
                    lines.append(f"    {source_id}[{source}] -.->|implements| {target_id}[{target}]")
                elif rel_type == 'calls':
                    lines.append(f"    {source_id}[{source}] ==>|calls| {target_id}[{target}]")
        
        # 스타일 적용
        lines.append("")
        lines.append("    %% Styling")
        for rel_type, color in colors.items():
            lines.append(f"    linkStyle * stroke:{color},stroke-width:2px")
        
        return "\n".join(lines)
    
    def _generate_stats_table(self, stats: Dict) -> str:
        """통계 테이블 HTML 생성"""
        html_lines = ['<table class="stats-table">']
        html_lines.append('<thead>')
        html_lines.append('<tr><th>컴포넌트 타입</th><th>수량</th><th>설명</th></tr>')
        html_lines.append('</thead>')
        html_lines.append('<tbody>')
        
        # 주요 타입들만 표시
        display_types = {
            'class': ('클래스', 'Java 클래스 파일'),
            'interface': ('인터페이스', 'Java 인터페이스 정의'),
            'table': ('테이블', '데이터베이스 테이블'),
            'table_dummy': ('참조 테이블', 'MyBatis에서 참조된 테이블')
        }
        
        for comp_type, (display_name, description) in display_types.items():
            count = stats.get(comp_type, 0)
            if count > 0:
                html_lines.append(f'<tr><td>{display_name}</td><td>{count}개</td><td>{description}</td></tr>')
        
        # 총계
        total = sum(v for k, v in stats.items() if k in display_types)
        html_lines.append(f'<tr style="font-weight:bold;background-color:#e3f2fd;"><td>전체</td><td>{total}개</td><td>총 컴포넌트 수</td></tr>')
        
        html_lines.append('</tbody>')
        html_lines.append('</table>')
        
        return '\n'.join(html_lines)