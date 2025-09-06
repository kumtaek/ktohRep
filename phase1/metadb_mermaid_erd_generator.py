#!/usr/bin/env python3
"""
메타디비 기반 Mermaid ERD HTML 생성기
메타디비에서 분석한 ERD 구조를 바탕으로 Mermaid 기반 HTML을 생성합니다.
"""

from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import logging
from metadb_erd_analyzer import ERDStructure, TableInfo, ColumnInfo

class MetaDBMermaidERDGenerator:
    """메타디비 기반 Mermaid ERD HTML 생성기"""
    
    def __init__(self):
        """생성기 초기화"""
        self.logger = logging.getLogger(__name__)
        
    def generate_html(self, erd_structure: ERDStructure, output_path: str = None) -> str:
        """
        Mermaid ERD HTML 생성
        
        Args:
            erd_structure: 분석된 ERD 구조
            output_path: 출력 파일 경로 (None이면 문자열 반환)
            
        Returns:
            생성된 HTML 내용
        """
        self.logger.info("메타디비 기반 Mermaid ERD HTML 생성 시작")
        
        # HTML 내용 생성
        html_content = self._generate_html_content(erd_structure)
        
        # 파일로 저장
        if output_path:
            self._save_html(html_content, output_path)
            self.logger.info(f"Mermaid ERD HTML 저장 완료: {output_path}")
        
        return html_content
    
    def _generate_html_content(self, erd_structure: ERDStructure) -> str:
        """HTML 내용 생성"""
        project_name = erd_structure.project_name
        current_time = datetime.now().strftime('%Y년 %m월 %d일 %H:%M')
        
        # Mermaid 다이어그램 생성
        mermaid_diagram = self._generate_mermaid_diagram(erd_structure)
        
        # HTML 템플릿
        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name} - Mermaid ERD</title>
    <!-- 오프라인 환경을 위한 로컬 Mermaid 라이브러리 -->
    <!-- 오프라인 환경 지원 -->
    <script>
        // 오프라인 환경에서는 아래 주석을 해제하고 CDN 링크를 주석 처리하세요
        // <script src="./libs/mermaid.min.js"></script>
        
        // 오프라인 모드 감지 및 자동 전환
        function loadMermaid() {{
            const isOffline = !navigator.onLine || window.location.protocol === 'file:';
            
            if (isOffline) {{
                console.log('Mermaid ERD: 오프라인 모드 감지됨');
                // 오프라인 모드에서는 로컬 파일 사용
                const script = document.createElement('script');
                script.src = './libs/mermaid.min.js';
                script.onerror = function() {{
                    console.error('오프라인 모드: mermaid.min.js 파일을 찾을 수 없습니다.');
                    console.log('다운로드: https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js');
                    console.log('저장 위치: ./libs/mermaid.min.js');
                }};
                document.head.appendChild(script);
            }} else {{
                console.log('Mermaid ERD: 온라인 CDN 사용 중');
                // 온라인 모드에서는 CDN 사용
                const script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js';
                document.head.appendChild(script);
            }}
        }}
        
        // 페이지 로드 시 Mermaid 라이브러리 로드
        loadMermaid();
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
        
        /* 확대/축소 컨트롤 */
        .controls {{
            text-align: center;
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 10px;
        }}
        
        .btn {{
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
        
        .btn:hover {{
            background: #2980b9;
        }}
        
        .btn:active {{
            transform: translateY(1px);
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
        
        /* Mermaid 컨테이너 스타일 */
        .mermaid-container {{
            position: relative;
            overflow: auto;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            background: white;
            min-height: 600px;
            max-height: 80vh;
            width: 100%;
            cursor: grab;
        }}
        
        .mermaid-container:active {{
            cursor: grabbing;
        }}
        
        #erd-diagram {{
            transition: transform 0.2s ease;
            transform-origin: center top;
        }}
        
        /* 사용법 안내 스타일 */
        .usage-guide {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        
        .usage-guide h3 {{
            margin-top: 0;
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        
        .usage-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 15px;
        }}
        
        .usage-item {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }}
        
        .usage-item strong {{
            color: #2c3e50;
            display: block;
            margin-bottom: 10px;
            font-size: 1.1em;
        }}
        
        .usage-item ul {{
            margin: 0;
            padding-left: 20px;
        }}
        
        .usage-item li {{
            margin-bottom: 5px;
            color: #555;
        }}
        
        .usage-item li strong {{
            color: #e74c3c;
            font-weight: bold;
            display: inline;
            margin: 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🗄️ {project_name} 데이터베이스 ERD</h1>
            <div class="subtitle">메타디비 기반 Mermaid ERD 다이어그램</div>
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
        
        <div class="content">
            <div class="section">
                <h2>🔗 ERD 다이어그램</h2>
                
                <!-- 확대/축소 컨트롤 -->
                <div class="controls">
                    <button class="btn" onclick="zoomIn()">🔍 확대</button>
                    <button class="btn" onclick="zoomOut()">🔍 축소</button>
                    <button class="btn" onclick="resetZoom()">🔄 초기화</button>
                    <button class="btn" onclick="downloadSVG()">📷 SVG 저장</button>
                </div>
                
                <!-- 사용법 안내 -->
                <div class="usage-guide">
                    <h3>🎮 사용법 안내</h3>
                    <div class="usage-grid">
                        <div class="usage-item">
                            <strong>🖱️ 마우스 클릭</strong>
                            <ul>
                                <li><strong>드래그</strong>: 다이어그램 이동</li>
                                <li><strong>Ctrl + 휠</strong>: 확대/축소 (10% 단위)</li>
                                <li><strong>일반 휠</strong>: 스크롤</li>
                            </ul>
                        </div>
                        <div class="usage-item">
                            <strong>⌨️ 키보드 단축키</strong>
                            <ul>
                                <li><strong>Ctrl + +</strong>: 확대</li>
                                <li><strong>Ctrl + -</strong>: 축소</li>
                                <li><strong>Ctrl + 0</strong>: 초기화</li>
                            </ul>
                        </div>
                        <div class="usage-item">
                            <strong>🔧 기능</strong>
                            <ul>
                                <li><strong>확대 범위</strong>: 30% ~ 300%</li>
                                <li><strong>단위</strong>: 10%씩 조정</li>
                                <li><strong>SVG 저장</strong>: 벡터 이미지 다운로드</li>
                            </ul>
                        </div>
                    </div>
                </div>
                
                <div class="mermaid-container" id="mermaid-container">
                    <div class="zoom-indicator" id="zoom-indicator">100%</div>
                    <div class="mermaid" id="erd-diagram">
{mermaid_diagram}
                    </div>
                </div>
            </div>
            
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
        // 확대/축소 변수
        let currentZoom = 1;
        let isDragging = false;
        let startX, startY, scrollLeft, scrollTop;
        
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'default',
            flowchart: {{
                useMaxWidth: true,
                htmlLabels: true,
                curve: 'basis'
            }},
            er: {{
                useMaxWidth: true,
                htmlLabels: true
            }}
        }});
        
        // 확대/축소 함수들 (10% 단위)
        function zoomIn() {{
            currentZoom = Math.min(currentZoom + 0.1, 3);
            applyZoom();
        }}
        
        function zoomOut() {{
            currentZoom = Math.max(currentZoom - 0.1, 0.3);
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
                downloadLink.download = '{project_name}_ERD.svg';
                document.body.appendChild(downloadLink);
                downloadLink.click();
                document.body.removeChild(downloadLink);
                URL.revokeObjectURL(svgUrl);
            }}
        }}
        
        // 드래그 및 마우스휠 이벤트 설정
        document.addEventListener('DOMContentLoaded', function() {{
            const container = document.getElementById('mermaid-container');
            
            // 마우스휠로 확대/축소 (Ctrl + 휠)
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
            
            // 드래그 기능
            container.addEventListener('mousedown', function(e) {{
                isDragging = true;
                startX = e.pageX - container.offsetLeft;
                startY = e.pageY - container.offsetTop;
                scrollLeft = container.scrollLeft;
                scrollTop = container.scrollTop;
                container.style.cursor = 'grabbing';
            }});
            
            container.addEventListener('mouseleave', function() {{
                isDragging = false;
                container.style.cursor = 'grab';
            }});
            
            container.addEventListener('mouseup', function() {{
                isDragging = false;
                container.style.cursor = 'grab';
            }});
            
            container.addEventListener('mousemove', function(e) {{
                if (!isDragging) return;
                e.preventDefault();
                const x = e.pageX - container.offsetLeft;
                const y = e.pageY - container.offsetTop;
                const walkX = (x - startX) * 2;
                const walkY = (y - startY) * 2;
                container.scrollLeft = scrollLeft - walkX;
                container.scrollTop = scrollTop - walkY;
            }});
            
            // 기본 커서 설정
            container.style.cursor = 'grab';
        }});
        
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
    </script>
</body>
</html>"""
        
        return html_content
    
    def _generate_mermaid_diagram(self, erd_structure: ERDStructure) -> str:
        """Mermaid ERD 다이어그램 생성"""
        mermaid_lines = ["erDiagram"]
        
        # 테이블 정의
        for table in erd_structure.tables:
            mermaid_lines.append(f"    {table.name} {{")
            
            # 컬럼 정의
            for column in table.columns:
                pk_marker = " PK" if column.name in table.primary_keys else ""
                fk_marker = " FK" if any(fk[0] == column.name for fk in table.foreign_keys) else ""
                nullable_marker = "" if column.nullable else " NOT NULL"
                
                mermaid_lines.append(f"        {column.data_type} {column.name}{pk_marker}{fk_marker}{nullable_marker}")
            
            mermaid_lines.append("    }")
        
        # 관계 정의
        for table in erd_structure.tables:
            for fk_column, ref_table, ref_column in table.foreign_keys:
                # 참조 테이블명에서 스키마 제거
                ref_table_name = ref_table.split('.')[-1] if '.' in ref_table else ref_table
                
                # 조인키 표기 방식 개선
                if fk_column == ref_column:
                    # 동일한 컬럼명인 경우 하나만 표시
                    join_label = fk_column
                else:
                    # 다른 컬럼명인 경우 기존 방식 유지
                    join_label = f"{fk_column} -> {ref_column}"
                
                mermaid_lines.append(f"    {table.name} ||--o{{ {ref_table_name} : \"{join_label}\"")
        
        return "\n".join(mermaid_lines)
    
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
    
    parser = argparse.ArgumentParser(description='Mermaid ERD HTML 생성기')
    parser.add_argument('--project-name', required=True, help='분석할 프로젝트명 (예: sampleSrc)')
    parser.add_argument('--output', help='출력 파일 경로 (기본값: 프로젝트/report/erd_mermaid_metadb_YYYYMMDD_HHMMSS.html)')
    args = parser.parse_args()
    
    # 프로젝트 경로 설정
    project_path = f"../project/{args.project_name}"
    
    # 출력 경로 설정
    if args.output:
        output_path = args.output
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f"{project_path}/report/erd_mermaid_metadb_{timestamp}.html"
    
    # ERD 분석 및 HTML 생성
    from metadb_erd_analyzer import MetaDBERDAnalyzer
    
    analyzer = MetaDBERDAnalyzer(project_path)
    erd_structure = analyzer.analyze_erd()
    
    generator = MetaDBMermaidERDGenerator()
    html_content = generator.generate_html(erd_structure, output_path)
    
    print(f"Mermaid ERD HTML 생성 완료: {len(html_content)} 문자")
    print(f"출력 파일: {output_path}")
