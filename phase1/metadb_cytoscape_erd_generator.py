#!/usr/bin/env python3
"""
메타디비 기반 Cytoscape ERD HTML 생성기
메타디비에서 분석한 ERD 구조를 바탕으로 Cytoscape 기반 HTML을 생성합니다.
"""

from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import logging
from metadb_erd_analyzer import ERDStructure, TableInfo, ColumnInfo

class MetaDBCytoscapeERDGenerator:
    """메타디비 기반 Cytoscape ERD HTML 생성기"""
    
    def __init__(self):
        """생성기 초기화"""
        self.logger = logging.getLogger(__name__)
        
    def generate_html(self, erd_structure: ERDStructure, output_path: str = None) -> str:
        """
        Cytoscape ERD HTML 생성
        
        Args:
            erd_structure: 분석된 ERD 구조
            output_path: 출력 파일 경로 (None이면 문자열 반환)
            
        Returns:
            생성된 HTML 내용
        """
        self.logger.info("메타디비 기반 Cytoscape ERD HTML 생성 시작")
        
        # HTML 내용 생성
        html_content = self._generate_html_content(erd_structure)
        
        # 파일로 저장
        if output_path:
            self._save_html(html_content, output_path)
            self.logger.info(f"Cytoscape ERD HTML 저장 완료: {output_path}")
        
        return html_content
    
    def _generate_html_content(self, erd_structure: ERDStructure) -> str:
        """HTML 내용 생성"""
        project_name = erd_structure.project_name
        current_time = datetime.now().strftime('%Y년 %m월 %d일 %H:%M')
        
        # Cytoscape 데이터 생성
        cytoscape_data = self._generate_cytoscape_data(erd_structure)
        
        # HTML 템플릿
        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name} - Cytoscape ERD</title>
    <!-- 오프라인 환경을 위한 로컬 Cytoscape 라이브러리 -->
    <!-- 오프라인 환경 지원 -->
    <script>
        // 오프라인 환경에서는 아래 주석을 해제하고 CDN 링크를 주석 처리하세요
        // <script src="./libs/cytoscape.min.js"></script>
        
        // 오프라인 모드 감지 및 자동 전환
        function loadCytoscape() {{
            const isOffline = !navigator.onLine || window.location.protocol === 'file:';
            
            if (isOffline) {{
                console.log('Cytoscape ERD: 오프라인 모드 감지됨');
                // 오프라인 모드에서는 로컬 파일 사용
                const script = document.createElement('script');
                script.src = './libs/cytoscape.min.js';
                script.onerror = function() {{
                    console.error('오프라인 모드: cytoscape.min.js 파일을 찾을 수 없습니다.');
                    console.log('다운로드: https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.28.1/cytoscape.min.js');
                    console.log('저장 위치: ./libs/cytoscape.min.js');
                }};
                document.head.appendChild(script);
            }} else {{
                console.log('Cytoscape ERD: 온라인 CDN 사용 중');
                // 온라인 모드에서는 CDN 사용
                const script = document.createElement('script');
                script.src = 'https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.28.1/cytoscape.min.js';
                document.head.appendChild(script);
            }}
        }}
        
        // 페이지 로드 시 Cytoscape 라이브러리 로드
        loadCytoscape();
    </script>
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
        
        .controls {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .control-btn {{
            background: #3498db;
            color: white;
            border: none;
            padding: 10px 20px;
            margin: 0 5px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }}
        
        .control-btn:hover {{
            background: #2980b9;
        }}
        
        .cytoscape-container {{
            height: 600px;
            width: 100%;
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            position: relative;
        }}
        
        .table-info {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            border: 1px solid #e9ecef;
        }}
        
        .table-info h3 {{
            color: #2c3e50;
            margin-top: 0;
        }}
        
        .column-list {{
            list-style: none;
            padding: 0;
        }}
        
        .column-list li {{
            padding: 5px 0;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .pk {{
            background: #e74c3c;
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.8em;
            margin-left: 10px;
        }}
        
        .fk {{
            background: #3498db;
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 0.8em;
            margin-left: 10px;
        }}
        
        .footer {{
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🗄️ {project_name} 데이터베이스 ERD</h1>
            <div class="subtitle">메타디비 기반 Cytoscape ERD 다이어그램</div>
            <div class="subtitle">생성일시: {current_time}</div>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{erd_structure.total_tables}</div>
                <div class="stat-label">테이블</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{erd_structure.total_columns}</div>
                <div class="stat-label">컬럼</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{erd_structure.total_relationships}</div>
                <div class="stat-label">관계</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{erd_structure.total_columns / erd_structure.total_tables:.1f}</div>
                <div class="stat-label">평균 컬럼/테이블</div>
            </div>
        </div>
        
        <div class="controls">
            <button class="control-btn" onclick="resetView()">🔍 초기화</button>
            <button class="control-btn" onclick="fitView()">📐 맞춤보기</button>
            <button class="control-btn" onclick="toggleLabels()">🏷️ 라벨 토글</button>
            <button class="control-btn" onclick="exportPNG()">📷 PNG 저장</button>
        </div>
        
        <div class="cytoscape-container" id="cy"></div>
        
        <div class="content" style="padding: 30px;">
            <div class="section">
                <h2>📊 테이블 상세 정보</h2>
                {self._generate_table_details_html(erd_structure)}
            </div>
        </div>
        
        <div class="footer">
            <p>이 문서는 메타디비를 기반으로 자동 생성되었습니다.</p>
            <p>분석 시간: {erd_structure.analysis_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
    
    <script>
        // Cytoscape 데이터
        const cyData = {cytoscape_data};
        
        // Cytoscape 초기화
        const cy = cytoscape({{
            container: document.getElementById('cy'),
            elements: cyData,
            style: [
                {{
                    selector: 'node',
                    style: {{
                        'background-color': '#3498db',
                        'label': 'data(label)',
                        'color': 'white',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'width': '120px',
                        'height': '60px',
                        'font-size': '12px',
                        'font-weight': 'bold',
                        'border-width': 2,
                        'border-color': '#2c3e50'
                    }}
                }},
                {{
                    selector: 'node[type="table"]',
                    style: {{
                        'background-color': '#27ae60',
                        'shape': 'rectangle'
                    }}
                }},
                {{
                    selector: 'edge',
                    style: {{
                        'width': 3,
                        'line-color': '#95a5a6',
                        'target-arrow-color': '#95a5a6',
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier',
                        'label': 'data(label)',
                        'font-size': '10px',
                        'color': '#7f8c8d'
                    }}
                }}
            ],
            layout: {{
                name: 'cose',
                animate: 'end',
                animationDuration: 1000,
                nodeDimensionsIncludeLabels: true,
                fit: true,
                padding: 50
            }},
            wheelSensitivity: 0.3
        }});
        
        // 컨트롤 함수들
        function resetView() {{
            cy.fit();
            cy.center();
        }}
        
        function fitView() {{
            cy.fit();
        }}
        
        function toggleLabels() {{
            const nodes = cy.nodes();
            const currentDisplay = nodes.style('label');
            nodes.style('label', currentDisplay === 'none' ? 'data(label)' : 'none');
        }}
        
        function exportPNG() {{
            const png = cy.png({{
                full: true,
                quality: 1,
                output: 'blob'
            }});
            
            const link = document.createElement('a');
            link.download = '{project_name}_ERD.png';
            link.href = URL.createObjectURL(png);
            link.click();
        }}
        
        // 이벤트 리스너
        cy.on('tap', 'node', function(evt) {{
            const node = evt.target;
            console.log('테이블 클릭:', node.data('label'));
        }});
        
        cy.on('tap', 'edge', function(evt) {{
            const edge = evt.target;
            console.log('관계 클릭:', edge.data('label'));
        }});
    </script>
</body>
</html>"""
        
        return html_content
    
    def _generate_cytoscape_data(self, erd_structure: ERDStructure) -> str:
        """Cytoscape 데이터 생성"""
        nodes = []
        edges = []
        
        # 노드(테이블) 생성
        for table in erd_structure.tables:
            nodes.append(f"""
                {{
                    data: {{
                        id: '{table.name}',
                        label: '{table.name}',
                        type: 'table',
                        columns: {len(table.columns)},
                        pk: {len(table.primary_keys)},
                        fk: {len(table.foreign_keys)}
                    }}
                }}""")
        
        # 엣지(관계) 생성
        for table in erd_structure.tables:
            # 같은 테이블로의 관계들을 그룹화
            relationships = {}
            for fk_column, ref_table, ref_column in table.foreign_keys:
                # 참조 테이블명에서 스키마 제거
                ref_table_name = ref_table.split('.')[-1] if '.' in ref_table else ref_table
                key = f"{table.name}_to_{ref_table_name}"
                
                if key not in relationships:
                    relationships[key] = []
                relationships[key].append((fk_column, ref_column))
            
            # 관계별로 엣지 생성
            for key, joins in relationships.items():
                table_name, ref_table_name = key.split('_to_')
                
                # 조인키 표기 방식 결정
                if len(joins) == 1:
                    fk_col, ref_col = joins[0]
                    if fk_col == ref_col:
                        label = fk_col  # 동일한 경우 하나만 표시
                    else:
                        label = f"{fk_col} → {ref_col}"  # 다른 경우 화살표로 표시
                else:
                    # 여러 조인키가 있는 경우
                    labels = []
                    for fk_col, ref_col in joins:
                        if fk_col == ref_col:
                            labels.append(fk_col)
                        else:
                            labels.append(f"{fk_col} → {ref_col}")
                    label = ", ".join(labels)
                
                edges.append(f"""
                    {{
                        data: {{
                            id: '{key}',
                            source: '{table_name}',
                            target: '{ref_table_name}',
                            label: '{label}'
                        }}
                    }}""")
        
        # JSON 형태로 반환
        return f"""{{
            nodes: [{','.join(nodes)}],
            edges: [{','.join(edges)}]
        }}"""
    
    def _generate_table_details_html(self, erd_structure: ERDStructure) -> str:
        """테이블 상세 정보 HTML 생성"""
        html_parts = []
        
        # 스키마별로 테이블 그룹화
        schema_groups = {}
        for table in erd_structure.tables:
            schema_name = table.owner if table.owner else 'DEFAULT'
            if schema_name not in schema_groups:
                schema_groups[schema_name] = []
            schema_groups[schema_name].append(table)
        
        # 스키마별 테이블 정보 생성
        for schema_name, tables in sorted(schema_groups.items()):
            html_parts.append(f'<h3>🎯 {schema_name} 스키마 ({len(tables)}개 테이블)</h3>')
            
            for table in tables:
                html_parts.append(f'''
                <div class="table-info">
                    <h3>📊 {table.name}</h3>
                    <p><strong>전체명:</strong> {table.full_name}</p>
                    <p><strong>설명:</strong> {table.comment}</p>
                    <p><strong>컬럼 수:</strong> {len(table.columns)}개</p>
                    <p><strong>기본키:</strong> {', '.join(table.primary_keys) if table.primary_keys else '없음'}</p>
                    <p><strong>외래키:</strong> {len(table.foreign_keys)}개</p>
                    
                    <h4>📝 컬럼 목록</h4>
                    <ul class="column-list">
                ''')
                
                for column in table.columns:
                    pk_class = "pk" if column.name in table.primary_keys else ""
                    fk_class = "fk" if any(fk[0] == column.name for fk in table.foreign_keys) else ""
                    
                    html_parts.append(f'''
                        <li>
                            <strong>{column.name}</strong> ({column.data_type})
                            <span class="{pk_class}">PK</span> if column.name in table.primary_keys else ""
                            <span class="{fk_class}">FK</span> if any(fk[0] == column.name for fk in table.foreign_keys) else ""
                            {f" - {column.comment}" if column.comment else ""}
                        </li>
                    ''')
                
                html_parts.append('''
                    </ul>
                </div>
                ''')
        
        return '\n'.join(html_parts)
    
    def _save_html(self, content: str, output_path: str):
        """HTML을 파일로 저장"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

if __name__ == "__main__":
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description='Cytoscape ERD HTML 생성기')
    parser.add_argument('--project-name', required=True, help='분석할 프로젝트명 (예: sampleSrc)')
    parser.add_argument('--output', help='출력 파일 경로 (기본값: 프로젝트/report/erd_cytoscape_metadb_YYYYMMDD_HHMMSS.html)')
    args = parser.parse_args()
    
    # 프로젝트 경로 설정
    project_path = f"../project/{args.project_name}"
    
    # 출력 경로 설정
    if args.output:
        output_path = args.output
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f"{project_path}/report/erd_cytoscape_metadb_{timestamp}.html"
    
    # ERD 분석 및 HTML 생성
    from metadb_erd_analyzer import MetaDBERDAnalyzer
    
    analyzer = MetaDBERDAnalyzer(project_path)
    erd_structure = analyzer.analyze_erd()
    
    generator = MetaDBCytoscapeERDGenerator()
    html_content = generator.generate_html(erd_structure, output_path)
    
    print(f"Cytoscape ERD HTML 생성 완료: {len(html_content)} 문자")
    print(f"출력 파일: {output_path}")
