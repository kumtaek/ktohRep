#!/usr/bin/env python3
"""
Magic MCP 스타일 고급 ERD HTML 생성기
Database With REST API 컴포넌트의 디자인을 그대로 적용
"""

from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import logging
from metadb_erd_analyzer import ERDStructure, TableInfo, ColumnInfo

class MagicStyleERDGenerator:
    """Magic MCP 스타일 고급 ERD HTML 생성기"""
    
    def __init__(self):
        """생성기 초기화"""
        self.logger = logging.getLogger(__name__)
        
    def generate_html(self, erd_structure: ERDStructure, output_path: str = None) -> str:
        """
        Magic MCP 스타일 ERD HTML 생성
        
        Args:
            erd_structure: 분석된 ERD 구조
            output_path: 출력 파일 경로 (None이면 문자열 반환)
            
        Returns:
            생성된 HTML 내용
        """
        self.logger.info("Magic MCP 스타일 ERD HTML 생성 시작")
        
        # HTML 내용 생성
        html_content = self._generate_html_content(erd_structure)
        
        # 파일로 저장
        if output_path:
            self._save_html(html_content, output_path)
            self.logger.info(f"Magic MCP 스타일 ERD HTML 저장 완료: {output_path}")
        
        return html_content
    
    def _generate_html_content(self, erd_structure: ERDStructure) -> str:
        """HTML 내용 생성"""
        project_name = erd_structure.project_name
        current_time = datetime.now().strftime('%Y년 %m월 %d일 %H:%M')
        
        # HTML 템플릿
        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name} - Magic MCP 스타일 ERD</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0f0f23;
            min-height: 100vh;
            color: #ffffff;
            overflow-x: auto;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            padding: 40px;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 40px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.3);
            border: 1px solid #2d3748;
        }}
        
        .header h1 {{
            font-size: 3em;
            font-weight: 300;
            margin-bottom: 15px;
            background: linear-gradient(45deg, #00d4ff, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .header .subtitle {{
            opacity: 0.9;
            font-size: 1.2em;
            color: #a0aec0;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 15px 35px rgba(0,0,0,0.2);
            border: 1px solid #2d3748;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }}
        
        .stat-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
            transition: left 0.5s;
        }}
        
        .stat-card:hover::before {{
            left: 100%;
        }}
        
        .stat-card:hover {{
            transform: translateY(-10px) scale(1.02);
            box-shadow: 0 25px 50px rgba(0,0,0,0.4);
            border-color: #00d4ff;
        }}
        
        .stat-number {{
            font-size: 3em;
            font-weight: bold;
            background: linear-gradient(45deg, #00d4ff, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 15px;
        }}
        
        .stat-label {{
            color: #a0aec0;
            font-size: 1em;
            text-transform: uppercase;
            letter-spacing: 2px;
            font-weight: 500;
        }}
        
        .erd-container {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 40px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.3);
            border: 1px solid #2d3748;
            overflow: hidden;
        }}
        
        .erd-title {{
            color: #ffffff;
            border-bottom: 3px solid #00d4ff;
            padding-bottom: 20px;
            margin-bottom: 30px;
            font-size: 2.2em;
            text-align: center;
        }}
        
        .controls {{
            background: rgba(45, 55, 72, 0.5);
            padding: 25px;
            text-align: center;
            border-bottom: 1px solid #2d3748;
            margin-bottom: 30px;
            border-radius: 15px;
        }}
        
        .control-btn {{
            background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            margin: 0 10px;
            border-radius: 12px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 500;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 8px 25px rgba(0, 212, 255, 0.3);
            position: relative;
            overflow: hidden;
        }}
        
        .control-btn::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }}
        
        .control-btn:hover::before {{
            left: 100%;
        }}
        
        .control-btn:hover {{
            background: linear-gradient(135deg, #0099cc 0%, #006699 100%);
            transform: translateY(-3px);
            box-shadow: 0 12px 35px rgba(0, 212, 255, 0.4);
        }}
        
        .control-btn:active {{
            transform: translateY(-1px);
        }}
        
        .erd-diagram {{
            background: #0f0f23;
            border-radius: 15px;
            padding: 30px;
            border: 1px solid #2d3748;
            position: relative;
            min-height: 600px;
            overflow: hidden;
        }}
        
        .table-node {{
            position: absolute;
            background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
            border: 2px solid #00d4ff;
            border-radius: 15px;
            padding: 20px;
            min-width: 220px;
            max-width: 250px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: move;
        }}
        
        .table-node:hover {{
            transform: scale(1.05);
            box-shadow: 0 20px 40px rgba(0,0,0,0.4);
            border-color: #ff6b6b;
        }}
        
        .table-header {{
            background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
            color: white;
            padding: 10px 15px;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 15px;
        }}
        
        .column-list {{
            list-style: none;
        }}
        
        .column-item {{
            background: rgba(255,255,255,0.05);
            margin: 8px 0;
            padding: 10px 15px;
            border-radius: 8px;
            border-left: 3px solid #4a5568;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            transition: all 0.3s ease;
        }}
        
        .column-item:hover {{
            background: rgba(255,255,255,0.1);
            border-left-color: #00d4ff;
        }}
        
        .pk-badge {{
            background: #ff6b6b;
            color: white;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.7em;
            margin-left: 10px;
            font-weight: bold;
        }}
        
        .fk-badge {{
            background: #00d4ff;
            color: white;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.7em;
            margin-left: 10px;
            font-weight: bold;
        }}
        
        .relationship-line {{
            position: absolute;
            background: linear-gradient(90deg, #ff6b6b, #00d4ff);
            height: 4px;
            border-radius: 2px;
            transform-origin: left center;
            box-shadow: 0 0 15px rgba(255, 107, 107, 0.6);
            z-index: 1;
            filter: drop-shadow(0 0 8px rgba(0, 212, 255, 0.4));
        }}
        
        .relationship-line::after {{
            content: '';
            position: absolute;
            right: -12px;
            top: -5px;
            width: 0;
            height: 0;
            border-left: 12px solid #00d4ff;
            border-top: 6px solid transparent;
            border-bottom: 6px solid transparent;
            filter: drop-shadow(0 0 5px rgba(0, 212, 255, 0.6));
        }}
        
        .table-info {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border-radius: 15px;
            padding: 25px;
            margin: 25px 0;
            border: 1px solid #2d3748;
            transition: all 0.3s ease;
        }}
        
        .table-info:hover {{
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transform: translateX(5px);
            border-color: #00d4ff;
        }}
        
        .table-info h3 {{
            color: #00d4ff;
            margin-bottom: 20px;
            font-size: 1.5em;
            border-bottom: 2px solid #2d3748;
            padding-bottom: 10px;
        }}
        
        .table-meta {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            margin-bottom: 25px;
        }}
        
        .meta-item {{
            text-align: center;
            padding: 15px;
            background: rgba(45, 55, 72, 0.5);
            border-radius: 12px;
            border: 1px solid #2d3748;
            transition: all 0.3s ease;
        }}
        
        .meta-item:hover {{
            border-color: #00d4ff;
            background: rgba(45, 55, 72, 0.8);
        }}
        
        .meta-number {{
            font-size: 1.8em;
            font-weight: bold;
            color: #00d4ff;
            margin-bottom: 8px;
        }}
        
        .meta-label {{
            color: #a0aec0;
            font-size: 0.8em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .footer {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            text-align: center;
            padding: 30px;
            border-radius: 20px;
            font-size: 1em;
            border: 1px solid #2d3748;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 15px;
            }}
            
            .header h1 {{
                font-size: 2.2em;
            }}
            
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
            
            .table-meta {{
                grid-template-columns: 1fr;
            }}
            
            .control-btn {{
                margin: 5px;
                padding: 12px 20px;
                font-size: 14px;
            }}
        }}
        
        /* 애니메이션 */
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(40px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .fade-in-up {{
            animation: fadeInUp 0.8s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        @keyframes float {{
            0%, 100% {{
                transform: translateY(0px);
            }}
            50% {{
                transform: translateY(-10px);
            }}
        }}
        
        .float {{
            animation: float 3s ease-in-out infinite;
        }}
        
        @keyframes glow {{
            0%, 100% {{
                box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
            }}
            50% {{
                box-shadow: 0 0 30px rgba(0, 212, 255, 0.6);
            }}
        }}
        
        .glow {{
            animation: glow 2s ease-in-out infinite;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header fade-in-up">
            <h1>🗄️ {project_name} 데이터베이스 ERD</h1>
            <div class="subtitle">Magic MCP 스타일 고급 ERD 다이어그램</div>
            <div class="subtitle">생성일시: {current_time}</div>
        </div>
        
        <div class="stats-grid fade-in-up">
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
        
        <div class="erd-container fade-in-up">
            <h2 class="erd-title">🔗 Magic MCP 스타일 ERD 다이어그램</h2>
            
            <div class="controls">
                <button class="control-btn" onclick="resetLayout()">🔍 레이아웃 초기화</button>
                <button class="control-btn" onclick="autoLayout()">📐 자동 배치</button>
                <button class="control-btn" onclick="toggleGlow()">✨ 글로우 효과</button>
                <button class="control-btn" onclick="exportSVG()">📷 SVG 저장</button>
                <button class="control-btn" onclick="toggleAnimation()">🎭 애니메이션</button>
            </div>
            
            <div class="erd-diagram" id="erdDiagram">
                {self._generate_table_nodes_html(erd_structure)}
                {self._generate_relationship_lines_html(erd_structure)}
            </div>
        </div>
        
        <div class="erd-container fade-in-up">
            <h2 class="erd-title">📊 테이블 상세 정보</h2>
            {self._generate_table_details_html(erd_structure)}
        </div>
        
        <div class="footer fade-in-up">
            <p>이 문서는 Magic MCP의 Database With REST API 컴포넌트 디자인을 적용하여 구현되었습니다.</p>
            <p>분석 시간: {erd_structure.analysis_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
    
    <script>
        // 테이블 노드 드래그 기능
        let isDragging = false;
        let currentDragElement = null;
        let dragOffset = {{ x: 0, y: 0 }};
        
        // 초기화
        document.addEventListener('DOMContentLoaded', function() {{
            setupDragAndDrop();
            setupAnimations();
        }});
        
        function setupDragAndDrop() {{
            const tableNodes = document.querySelectorAll('.table-node');
            
            tableNodes.forEach(node => {{
                node.addEventListener('mousedown', startDrag);
                node.addEventListener('touchstart', startDrag);
            }});
            
            document.addEventListener('mousemove', drag);
            document.addEventListener('touchmove', drag);
            document.addEventListener('mouseup', endDrag);
            document.addEventListener('touchend', endDrag);
        }}
        
        function startDrag(e) {{
            e.preventDefault();
            isDragging = true;
            currentDragElement = e.target.closest('.table-node');
            
            const rect = currentDragElement.getBoundingClientRect();
            const clientX = e.type === 'mousedown' ? e.clientX : e.touches[0].clientX;
            const clientY = e.type === 'mousedown' ? e.clientY : e.touches[0].clientY;
            
            dragOffset.x = clientX - rect.left;
            dragOffset.y = clientY - rect.top;
            
            currentDragElement.style.zIndex = '1000';
        }}
        
        function drag(e) {{
            if (!isDragging || !currentDragElement) return;
            
            e.preventDefault();
            const clientX = e.type === 'mousemove' ? e.clientX : e.touches[0].clientX;
            const clientY = e.type === 'mousemove' ? e.clientY : e.touches[0].clientY;
            
            const newX = clientX - dragOffset.x;
            const newY = clientY - dragOffset.y;
            
            currentDragElement.style.left = newX + 'px';
            currentDragElement.style.top = newY + 'px';
            
            updateRelationshipLines();
        }}
        
        function endDrag() {{
            if (currentDragElement) {{
                currentDragElement.style.zIndex = '1';
                currentDragElement = null;
            }}
            isDragging = false;
        }}
        
        function updateRelationshipLines() {{
            const lines = document.querySelectorAll('.relationship-line');
            lines.forEach(line => {{
                const fromTable = line.getAttribute('data-from');
                const toTable = line.getAttribute('data-to');
                
                const fromNode = document.querySelector(`[data-table="${{fromTable}}"]`);
                const toNode = document.querySelector(`[data-table="${{toTable}}"]`);
                
                if (fromNode && toNode) {{
                    const fromRect = fromNode.getBoundingClientRect();
                    const toRect = toNode.getBoundingClientRect();
                    const diagramRect = document.getElementById('erdDiagram').getBoundingClientRect();
                    
                    const fromX = fromRect.left + fromRect.width / 2 - diagramRect.left;
                    const fromY = fromRect.top + fromRect.height / 2 - diagramRect.top;
                    const toX = toRect.left + toRect.width / 2 - diagramRect.left;
                    const toY = toRect.top + toRect.height / 2 - diagramRect.top;
                    
                    const length = Math.sqrt(Math.pow(toX - fromX, 2) + Math.pow(toY - fromY, 2));
                    const angle = Math.atan2(toY - fromY, toX - fromX) * 180 / Math.PI;
                    
                    line.style.width = length + 'px';
                    line.style.left = fromX + 'px';
                    line.style.top = fromY + 'px';
                    line.style.transform = `rotate(${{angle}}deg)`;
                }}
            }});
        }}
        
        function setupAnimations() {{
            const tableNodes = document.querySelectorAll('.table-node');
            tableNodes.forEach((node, index) => {{
                node.style.animationDelay = (index * 0.1) + 's';
                node.classList.add('fade-in-up');
            }});
        }}
        
        // 컨트롤 함수들
        function resetLayout() {{
            const tableNodes = document.querySelectorAll('.table-node');
            tableNodes.forEach((node, index) => {{
                const row = Math.floor(index / 4);
                const col = index % 4;
                node.style.left = (col * 320 + 80) + 'px';
                node.style.top = (row * 280 + 80) + 'px';
            }});
            updateRelationshipLines();
        }}
        
        function autoLayout() {{
            // 자동 레이아웃 알고리즘 (간단한 그리드)
            const tableNodes = document.querySelectorAll('.table-node');
            const cols = Math.ceil(Math.sqrt(tableNodes.length));
            
            tableNodes.forEach((node, index) => {{
                const row = Math.floor(index / cols);
                const col = index % cols;
                node.style.left = (col * 280 + 50) + 'px';
                node.style.top = (row * 220 + 50) + 'px';
            }});
            updateRelationshipLines();
        }}
        
        function toggleGlow() {{
            const tableNodes = document.querySelectorAll('.table-node');
            tableNodes.forEach(node => {{
                node.classList.toggle('glow');
            }});
        }}
        
        function exportSVG() {{
            // SVG 내보내기 기능 (간단한 구현)
            alert('SVG 내보내기 기능은 개발 중입니다.');
        }}
        
        function toggleAnimation() {{
            const tableNodes = document.querySelectorAll('.table-node');
            tableNodes.forEach(node => {{
                node.classList.toggle('float');
            }});
        }}
        
        // 초기 레이아웃 설정
        setTimeout(() => {{
            autoLayout();
        }}, 100);
    </script>
</body>
</html>"""
        
        return html_content
    
    def _generate_table_nodes_html(self, erd_structure: ERDStructure) -> str:
        """테이블 노드 HTML 생성"""
        html_parts = []
        
        # 테이블 위치 계산 (Magic MCP 스타일 레이아웃)
        cols = 4
        for i, table in enumerate(erd_structure.tables):
            row = i // cols
            col = i % cols
            
            html_parts.append(f'''
            <div class="table-node" data-table="{table.name}" style="left: {col * 320 + 80}px; top: {row * 280 + 80}px;">
                <div class="table-header">{table.name}</div>
                <ul class="column-list">
            ''')
            
            for column in table.columns:
                pk_badge = f'<span class="pk-badge">PK</span>' if column.name in table.primary_keys else ""
                fk_badge = f'<span class="fk-badge">FK</span>' if any(fk[0] == column.name for fk in table.foreign_keys) else ""
                
                html_parts.append(f'''
                    <li class="column-item">
                        {column.name} ({column.data_type})
                        {pk_badge}
                        {fk_badge}
                    </li>
                ''')
            
            html_parts.append('''
                </ul>
            </div>
            ''')
        
        return '\n'.join(html_parts)
    
    def _generate_relationship_lines_html(self, erd_structure: ERDStructure) -> str:
        """관계선 HTML 생성"""
        html_parts = []
        
        for table in erd_structure.tables:
            for fk_column, ref_table, ref_column in table.foreign_keys:
                # 참조 테이블명에서 스키마 제거
                ref_table_name = ref_table.split('.')[-1] if '.' in ref_table else ref_table
                
                html_parts.append(f'''
                <div class="relationship-line" 
                     data-from="{table.name}" 
                     data-to="{ref_table_name}"
                     style="width: 200px; left: 0px; top: 0px; transform: rotate(0deg);">
                </div>
                ''')
        
        return '\n'.join(html_parts)
    
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
                    
                    <div class="table-meta">
                        <div class="meta-item">
                            <div class="meta-number">{len(table.columns)}</div>
                            <div class="meta-label">컬럼</div>
                        </div>
                        <div class="meta-item">
                            <div class="meta-number">{len(table.primary_keys)}</div>
                            <div class="meta-label">기본키</div>
                        </div>
                        <div class="meta-item">
                            <div class="meta-number">{len(table.foreign_keys)}</div>
                            <div class="meta-label">외래키</div>
                        </div>
                        <div class="meta-item">
                            <div class="meta-number">{table.status}</div>
                            <div class="meta-label">상태</div>
                        </div>
                    </div>
                    
                    <h4>📝 컬럼 목록</h4>
                    <ul class="column-list">
                ''')
                
                for column in table.columns:
                    pk_badge = f'<span class="pk-badge">PK</span>' if column.name in table.primary_keys else ""
                    fk_badge = f'<span class="fk-badge">FK</span>' if any(fk[0] == column.name for fk in table.foreign_keys) else ""
                    comment_text = f"<br><small>{column.comment}</small>" if column.comment else ""
                    
                    html_parts.append(f'''
                        <li class="column-item">
                            <strong>{column.name}</strong> ({column.data_type})
                            {pk_badge}
                            {fk_badge}
                            {comment_text}
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
    # 테스트
    from metadb_erd_analyzer import MetaDBERDAnalyzer
    
    analyzer = MetaDBERDAnalyzer("../project/sampleSrc")
    erd_structure = analyzer.analyze_erd()
    
    generator = MagicStyleERDGenerator()
    html_content = generator.generate_html(erd_structure, "../project/sampleSrc/report/erd_magic_style_20250904.html")
    
    print(f"Magic MCP 스타일 ERD HTML 생성 완료: {len(html_content)} 문자")
