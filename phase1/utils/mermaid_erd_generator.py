#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mermaid 기반 ERD 생성기
데이터베이스 스키마 정보를 기반으로 Mermaid ERD를 생성합니다.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional


class MermaidErdGenerator:
    """Mermaid 기반 ERD 생성기"""
    
    def __init__(self, db_path: str, project_name: str):
        self.db_path = db_path
        self.project_name = project_name
        self.connection = None
    
    def connect_database(self) -> bool:
        """데이터베이스에 연결합니다."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            return True
        except Exception as e:
            print(f"데이터베이스 연결 실패: {e}")
            return False
    
    def close_database(self):
        """데이터베이스 연결을 종료합니다."""
        if self.connection:
            self.connection.close()
    
    def analyze_database_schema(self) -> Dict[str, Any]:
        """데이터베이스 스키마를 분석합니다."""
        if not self.connection:
            return {}
        
        try:
            # 테이블 정보 조회
            tables_query = """
            SELECT table_id, owner, table_name, status, table_comment
            FROM db_tables
            ORDER BY table_name
            """
            
            tables = self.connection.execute(tables_query).fetchall()
            
            # 컬럼 정보 조회
            columns_query = """
            SELECT c.table_id, c.column_name, c.data_type, c.nullable, 
                   c.column_comment, t.table_name
            FROM db_columns c
            JOIN db_tables t ON c.table_id = t.table_id
            ORDER BY c.table_id, c.column_name
            """
            
            columns = self.connection.execute(columns_query).fetchall()
            
            # 기본키 정보 조회
            primary_keys_query = """
            SELECT pk.table_id, pk.column_name, t.table_name
            FROM db_pk pk
            JOIN db_tables t ON pk.table_id = t.table_id
            ORDER BY pk.table_id, pk.pk_pos
            """
            
            primary_keys = self.connection.execute(primary_keys_query).fetchall()
            
            # 외래키 정보 조회 (컬럼명 패턴으로 추정)
            foreign_keys = []
            for col in columns:
                if col['column_name'].endswith('_ID') and col['column_name'] != 'ID':
                    # 외래키로 추정되는 컬럼들
                    foreign_keys.append({
                        'table_id': col['table_id'],
                        'column_name': col['column_name'],
                        'table_name': col['table_name'],
                        'referenced_table': col['column_name'].replace('_ID', 'S'),  # 추정
                        'referenced_column': 'ID'
                    })
            
            # 스키마 구조 구성
            schema = self._build_db_schema_structure(tables, columns, primary_keys, foreign_keys)
            
            return schema
            
        except Exception as e:
            print(f"스키마 분석 실패: {e}")
            return {}
    
    def _build_db_schema_structure(self, tables: List, columns: List, 
                                  primary_keys: List, foreign_keys: List) -> Dict[str, Any]:
        """데이터베이스 스키마 구조를 구성합니다."""
        schema = {
            'project_name': self.project_name,
            'analysis_time': datetime.now().isoformat(),
            'tables': {},
            'relationships': [],
            'statistics': {}
        }
        
        # 테이블 정보 구성
        for table in tables:
            table_id = table['table_id']
            table_name = table['table_name']
            table_comment = table['table_comment'] or ''
            
            schema['tables'][table_name] = {
                'name': table_name,
                'comment': table_comment,
                'columns': [],
                'primary_keys': [],
                'foreign_keys': [],
                'indexes': [],
                'column_count': 0,
                'row_count': 0
            }
        
        # 컬럼 정보 구성
        for column in columns:
            table_name = column['table_name']
            if table_name in schema['tables']:
                column_info = {
                    'name': column['column_name'],
                    'type': column['data_type'] or 'UNKNOWN',
                    'nullable': column['nullable'] == 'Y',
                    'default': None,
                    'comment': column['column_comment'] or '',
                    'is_primary_key': False,
                    'is_foreign_key': False
                }
                
                schema['tables'][table_name]['columns'].append(column_info)
                schema['tables'][table_name]['column_count'] += 1
        
        # 기본키 정보 구성
        for pk in primary_keys:
            table_name = pk['table_name']
            column_name = pk['column_name']
            
            if table_name in schema['tables']:
                # 해당 컬럼을 기본키로 표시
                for col in schema['tables'][table_name]['columns']:
                    if col['name'] == column_name:
                        col['is_primary_key'] = True
                        schema['tables'][table_name]['primary_keys'].append(column_name)
                        break
        
        # 외래키 관계 구성
        for fk in foreign_keys:
            table_name = fk['table_name']
            column_name = fk['column_name']
            referenced_table = fk['referenced_table']
            
            if table_name in schema['tables'] and referenced_table in schema['tables']:
                # 해당 컬럼을 외래키로 표시
                for col in schema['tables'][table_name]['columns']:
                    if col['name'] == column_name:
                        col['is_foreign_key'] = True
                        break
                
                relationship = {
                    'source_table': table_name,
                    'source_column': column_name,
                    'target_table': referenced_table,
                    'target_column': 'ID',
                    'constraint_name': f"FK_{table_name}_{column_name}"
                }
                
                schema['relationships'].append(relationship)
                schema['tables'][table_name]['foreign_keys'].append(relationship)
        
        # 통계 계산
        schema['statistics'] = {
            'total_tables': len(schema['tables']),
            'total_columns': sum(t['column_count'] for t in schema['tables'].values()),
            'total_relationships': len(schema['relationships']),
            'tables_with_pk': len([t for t in schema['tables'].values() if t['primary_keys']]),
            'tables_with_fk': len([t for t in schema['tables'].values() if t['foreign_keys']])
        }
        
        return schema
    
    def generate_mermaid_erd(self, output_path: Optional[str] = None) -> str:
        """Mermaid ERD를 생성합니다."""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"erd_mermaid_{timestamp}.html"
        
        schema = self.analyze_database_schema()
        
        # HTML 내용 생성
        html_content = self._create_html_content(schema)
        
        # 파일 저장
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"Mermaid ERD가 생성되었습니다: {output_path}")
        except Exception as e:
            print(f"파일 저장 실패: {e}")
        
        return output_path
    
    def _create_html_content(self, schema: Dict[str, Any]) -> str:
        """HTML 내용을 생성합니다."""
        mermaid_code = self._generate_mermaid_erd(schema)
        
        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.project_name} - Mermaid ERD</title>
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
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            border: 1px solid #e9ecef;
            position: relative;
            overflow: auto;
            max-height: 80vh;
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
            .stats {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .content {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏗️ {self.project_name} ERD</h1>
            <p class="subtitle">Mermaid 기반 데이터베이스 스키마 다이어그램</p>
            <p class="subtitle">생성 시간: {schema['analysis_time']}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{schema['statistics']['total_tables']}</div>
                <div class="stat-label">테이블</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{schema['statistics']['total_columns']}</div>
                <div class="stat-label">컬럼</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{schema['statistics']['total_relationships']}</div>
                <div class="stat-label">관계</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{schema['statistics']['tables_with_pk']}</div>
                <div class="stat-label">PK 테이블</div>
            </div>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>📊 ERD 다이어그램</h2>
                <div class="controls">
                    <button class="btn" onclick="zoomIn()">🔍 확대</button>
                    <button class="btn" onclick="zoomOut()">🔍 축소</button>
                    <button class="btn secondary" onclick="resetZoom()">🔄 초기화</button>
                    <button class="btn secondary" onclick="downloadSVG()">💾 SVG 다운로드</button>
                </div>
                <div class="mermaid-container" id="mermaid-container">
                    <div class="zoom-indicator" id="zoom-indicator">100%</div>
                    <div class="mermaid" id="erd-diagram">
{mermaid_code}
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>📋 테이블 상세 정보</h2>
                {self._generate_table_details(schema)}
            </div>
            
            <div class="section">
                <h2>🔗 관계 정보</h2>
                {self._generate_relationship_details(schema)}
            </div>
        </div>
        
        <div class="footer">
            <p>이 ERD는 SourceAnalyzer Phase1 시스템에 의해 자동 생성되었습니다.</p>
            <p>생성 시간: {schema['analysis_time']}</p>
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
            const diagram = document.getElementById('erd-diagram');
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
            const svg = document.querySelector('#erd-diagram svg');
            if (svg) {{
                const svgData = new XMLSerializer().serializeToString(svg);
                const svgBlob = new Blob([svgData], {{type: 'image/svg+xml;charset=utf-8'}});
                const svgUrl = URL.createObjectURL(svgBlob);
                const downloadLink = document.createElement('a');
                downloadLink.href = svgUrl;
                downloadLink.download = '{self.project_name}_ERD.svg';
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
</html>"""
        
        return html_content
    
    def _generate_mermaid_erd(self, schema: Dict[str, Any]) -> str:
        """완전히 수정된 Mermaid ERD 다이어그램을 생성합니다."""
        mermaid_lines = []
        mermaid_lines.append("erDiagram")
        
        # 테이블명 정규화 매핑 (점 제거 및 안전한 이름으로 변환)
        table_name_map = {}
        for table_name in schema['tables'].keys():
            safe_name = self._sanitize_table_name(table_name)
            table_name_map[table_name] = safe_name
        
        # 테이블 정의 (엔티티) - 개선된 버전
        for original_table_name, table_info in schema['tables'].items():
            safe_table_name = table_name_map[original_table_name]
            mermaid_lines.append(f"    {safe_table_name} {{")
            
            # 컬럼 정보 추가 (중복 완전 제거)
            seen_columns = set()
            sorted_columns = sorted(table_info['columns'], key=lambda x: (not x['is_primary_key'], x['name']))
            
            for column in sorted_columns:
                column_name = column['name']
                if column_name not in seen_columns:
                    seen_columns.add(column_name)
                    
                    # 데이터 타입 정규화 (UNKNOWN 제거)
                    data_type = self._normalize_data_type(column['type'])
                    
                    # 제약조건 생성
                    constraints = []
                    if column['is_primary_key']:
                        constraints.append("PK")
                    if column['is_foreign_key']:
                        constraints.append("FK")
                    if not column['nullable']:
                        constraints.append("NOT NULL")
                    
                    # Mermaid 문법: datatype columnName "constraints"
                    if constraints:
                        constraint_str = ", ".join(constraints)
                        mermaid_lines.append(f"        {data_type} {column_name} \"{constraint_str}\"")
                    else:
                        mermaid_lines.append(f"        {data_type} {column_name}")
            
            mermaid_lines.append("    }")
            mermaid_lines.append("")
        
        # 관계 정의 (스마트한 관계 필터링)
        seen_relationships = set()
        valid_relationships = []
        
        for relationship in schema['relationships']:
            source_table = table_name_map.get(relationship['source_table'])
            target_table = table_name_map.get(relationship['target_table'])
            source_column = relationship['source_column']
            
            # 자기 참조 관계 제외 (같은 테이블끼리)
            if source_table == target_table:
                continue
            
            # 관계 유효성 검증
            if (source_table and target_table and 
                source_table in table_name_map.values() and 
                target_table in table_name_map.values()):
                
                # 실제 존재하는 컬럼인지 확인
                source_columns = [c['name'] for c in schema['tables'][relationship['source_table']]['columns']]
                target_columns = [c['name'] for c in schema['tables'][relationship['target_table']]['columns']]
                
                # 타겟 컬럼 결정 (스마트한 매칭)
                target_column = None
                
                # 1. 정확한 매칭 (예: USER_ID -> USER_ID)
                if source_column in target_columns:
                    target_column = source_column
                # 2. ID 컬럼이 있다면 사용
                elif 'ID' in target_columns:
                    target_column = 'ID'
                # 3. 기본키 찾기
                else:
                    target_pks = [c['name'] for c in schema['tables'][relationship['target_table']]['columns'] if c['is_primary_key']]
                    if target_pks:
                        target_column = target_pks[0]
                
                # 유효한 관계만 추가
                if (target_column and source_column in source_columns and 
                    target_column in target_columns):
                    
                    # 중복 관계 제거 (양방향 고려)
                    rel_key1 = f"{source_table}_{target_table}_{source_column}_{target_column}"
                    rel_key2 = f"{target_table}_{source_table}_{target_column}_{source_column}"
                    
                    if rel_key1 not in seen_relationships and rel_key2 not in seen_relationships:
                        seen_relationships.add(rel_key1)
                        valid_relationships.append({
                            'source': source_table,
                            'target': target_table,
                            'source_col': source_column,
                            'target_col': target_column
                        })
        
        # 관계를 알파벳 순으로 정렬하여 일관성 있게 출력
        valid_relationships.sort(key=lambda x: (x['target'], x['source']))
        
        # 관계 출력 (정확한 Mermaid 문법)
        for rel in valid_relationships:
            # 관계 라벨 간소화 (더 읽기 쉽게)
            if rel['source_col'] == rel['target_col']:
                label = rel['source_col']
            else:
                label = f"{rel['source_col']} -> {rel['target_col']}"
            
            mermaid_lines.append(f"    {rel['target']} ||--o{{ {rel['source']} : \"{label}\"")
        
        mermaid_lines.append("")
        return "\n".join(mermaid_lines)
    
    def _sanitize_table_name(self, table_name: str) -> str:
        """테이블명을 Mermaid 호환 형식으로 변환합니다."""
        # 점(.)을 언더스코어(_)로 변환
        safe_name = table_name.replace('.', '_')
        # 기타 특수문자 제거/변환
        safe_name = safe_name.replace('-', '_').replace(' ', '_').replace('(', '').replace(')', '')
        # 대문자로 통일
        return safe_name.upper()
    
    def _normalize_data_type(self, data_type: str) -> str:
        """데이터 타입을 Mermaid 호환 형식으로 정규화합니다."""
        if not data_type or data_type.upper() == 'UNKNOWN':
            return 'STRING'
        
        # 일반적인 데이터 타입 정규화
        type_mapping = {
            'VARCHAR2': 'VARCHAR',
            'NUMBER': 'DECIMAL',
            'CLOB': 'TEXT',
            'BLOB': 'BINARY',
            'TIMESTAMP': 'DATETIME',
            'CHAR': 'STRING'
        }
        
        normalized = data_type.upper()
        for old_type, new_type in type_mapping.items():
            if old_type in normalized:
                return new_type
        
        return normalized
    
    def _generate_table_details(self, schema: Dict[str, Any]) -> str:
        """테이블 상세 정보를 생성합니다."""
        html_parts = []
        
        for table_name, table_info in schema['tables'].items():
            html_parts.append(f"""
            <div class="table-info">
                <div class="table-name">📋 {table_name}</div>
                <p><strong>컬럼 수:</strong> {table_info['column_count']}개</p>
                <p><strong>설명:</strong> {table_info['comment'] or '설명 없음'}</p>
                
                <table class="columns-table">
                    <thead>
                        <tr>
                            <th>컬럼명</th>
                            <th>데이터 타입</th>
                            <th>제약조건</th>
                            <th>기본값</th>
                            <th>설명</th>
                        </tr>
                    </thead>
                    <tbody>""")
            
            for column in table_info['columns']:
                constraints = []
                if column['is_primary_key']:
                    constraints.append('<span class="pk-badge">PK</span>')
                if column['is_foreign_key']:
                    constraints.append('<span class="fk-badge">FK</span>')
                if not column['nullable']:
                    constraints.append('<span class="nullable-badge">NOT NULL</span>')
                
                constraints_html = ' '.join(constraints) if constraints else '-'
                default_value = column['default'] if column['default'] else '-'
                comment = column['comment'] if column['comment'] else '-'
                
                html_parts.append(f"""
                        <tr>
                            <td><strong>{column['name']}</strong></td>
                            <td><code>{column['type']}</code></td>
                            <td>{constraints_html}</td>
                            <td><code>{default_value}</code></td>
                            <td>{comment}</td>
                        </tr>""")
            
            html_parts.append("""
                    </tbody>
                </table>
            </div>""")
        
        return ''.join(html_parts)
    
    def _generate_relationship_details(self, schema: Dict[str, Any]) -> str:
        """관계 정보를 생성합니다."""
        if not schema['relationships']:
            return "<p>외래키 관계가 없습니다.</p>"
        
        html_parts = ['<table class="columns-table">']
        html_parts.append("""
            <thead>
                <tr>
                    <th>소스 테이블</th>
                    <th>소스 컬럼</th>
                    <th>타겟 테이블</th>
                    <th>타겟 컬럼</th>
                    <th>제약조건명</th>
                </tr>
            </thead>
            <tbody>""")
        
        for relationship in schema['relationships']:
            html_parts.append(f"""
                <tr>
                    <td><strong>{relationship['source_table']}</strong></td>
                    <td><code>{relationship['source_column']}</code></td>
                    <td><strong>{relationship['target_table']}</strong></td>
                    <td><code>{relationship['target_column']}</code></td>
                    <td>{relationship['constraint_name']}</td>
                </tr>""")
        
        html_parts.append("""
            </tbody>
        </table>""")
        
        return ''.join(html_parts)


def main():
    """메인 함수"""
    import sys
    
    if len(sys.argv) < 3:
        print("사용법: python mermaid_erd_generator.py <db_path> <project_name> [output_path]")
        sys.exit(1)
    
    db_path = sys.argv[1]
    project_name = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    generator = MermaidErdGenerator(db_path, project_name)
    
    if generator.connect_database():
        try:
            output_file = generator.generate_mermaid_erd(output_path)
            print(f"Mermaid ERD 생성이 완료되었습니다: {output_file}")
        finally:
            generator.close_database()
    else:
        print("데이터베이스 연결에 실패했습니다.")


if __name__ == "__main__":
    main()
