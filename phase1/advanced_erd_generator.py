#!/usr/bin/env python3
"""
고급 ERD HTML 생성기 (폐쇄망 대응)
Magic MCP 컴포넌트의 디자인을 참고하여 순수 HTML/CSS/JS로 구현
"""

from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import logging
from metadb_erd_analyzer import ERDStructure, TableInfo, ColumnInfo

class AdvancedERDGenerator:
    """고급 ERD HTML 생성기 (폐쇄망 대응)"""
    
    def __init__(self):
        """생성기 초기화"""
        self.logger = logging.getLogger(__name__)
        
    def generate_html(self, erd_structure: ERDStructure, output_path: str = None) -> str:
        """
        고급 ERD HTML 생성
        
        Args:
            erd_structure: 분석된 ERD 구조
            output_path: 출력 파일 경로 (None이면 문자열 반환)
            
        Returns:
            생성된 HTML 내용
        """
        self.logger.info("고급 ERD HTML 생성 시작")
        
        # HTML 내용 생성
        html_content = self._generate_html_content(erd_structure)
        
        # 파일로 저장
        if output_path:
            self._save_html(html_content, output_path)
            self.logger.info(f"고급 ERD HTML 저장 완료: {output_path}")
        
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
    <title>{project_name} - 고급 ERD 다이어그램</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 2.5em;
            font-weight: 300;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            opacity: 0.8;
            font-size: 1.1em;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            border-left: 4px solid #3498db;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.15);
        }}
        
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .stat-label {{
            color: #7f8c8d;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .erd-container {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .erd-title {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 15px;
            margin-bottom: 25px;
            font-size: 1.8em;
        }}
        
        .canvas-container {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            border: 1px solid #e9ecef;
            position: relative;
            overflow: auto;
            max-height: 80vh;
            width: 100%;
        }}
        
        #erdCanvas {{
            border: 1px solid #ddd;
            background: white;
            cursor: grab;
        }}
        
        #erdCanvas:active {{
            cursor: grabbing;
        }}
        
        .controls {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            border-bottom: 1px solid #e9ecef;
            margin-bottom: 20px;
        }}
        
        .control-btn {{
            background: #3498db;
            color: white;
            border: none;
            padding: 12px 24px;
            margin: 0 8px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
        }}
        
        .control-btn:hover {{
            background: #2980b9;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4);
        }}
        
        .control-btn:active {{
            transform: translateY(0);
        }}
        
        .table-info {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            border: 1px solid #e9ecef;
            transition: all 0.3s ease;
        }}
        
        .table-info:hover {{
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            transform: translateX(5px);
        }}
        
        .table-info h3 {{
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.3em;
        }}
        
        .table-meta {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .meta-item {{
            text-align: center;
            padding: 10px;
            background: white;
            border-radius: 8px;
            border-left: 3px solid #3498db;
        }}
        
        .meta-number {{
            font-size: 1.5em;
            font-weight: bold;
            color: #3498db;
        }}
        
        .meta-label {{
            color: #7f8c8d;
            font-size: 0.8em;
            text-transform: uppercase;
        }}
        
        .column-list {{
            list-style: none;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
        }}
        
        .column-item {{
            background: white;
            padding: 12px;
            border-radius: 8px;
            border-left: 4px solid #27ae60;
            font-family: monospace;
            font-size: 0.9em;
            transition: all 0.3s ease;
        }}
        
        .column-item:hover {{
            transform: translateX(5px);
            box-shadow: 0 3px 15px rgba(0,0,0,0.1);
        }}
        
        .pk-badge {{
            background: #e74c3c;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.7em;
            margin-left: 10px;
            font-weight: bold;
        }}
        
        .fk-badge {{
            background: #3498db;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.7em;
            margin-left: 10px;
            font-weight: bold;
        }}
        
        .footer {{
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 20px;
            border-radius: 15px;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 10px;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .stats-grid {{
                grid-template-columns: 1fr;
            }}
            
            .table-meta {{
                grid-template-columns: 1fr;
            }}
            
            .column-list {{
                grid-template-columns: 1fr;
            }}
        }}
        
        /* 애니메이션 */
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .fade-in-up {{
            animation: fadeInUp 0.6s ease-out;
        }}
        
        @keyframes pulse {{
            0%, 100% {{
                transform: scale(1);
            }}
            50% {{
                transform: scale(1.05);
            }}
        }}
        
        .pulse {{
            animation: pulse 2s infinite;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header fade-in-up">
            <h1>🗄️ {project_name} 데이터베이스 ERD</h1>
            <div class="subtitle">Magic MCP 디자인 기반 고급 ERD 다이어그램</div>
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
            <h2 class="erd-title">🔗 ERD 다이어그램</h2>
            
            <div class="controls">
                <button class="control-btn" onclick="resetView()">🔍 초기화</button>
                <button class="control-btn" onclick="fitView()">📐 맞춤보기</button>
                <button class="control-btn" onclick="toggleLabels()">🏷️ 라벨 토글</button>
                <button class="control-btn" onclick="exportPNG()">📷 PNG 저장</button>
                <button class="control-btn" onclick="toggleAnimation()">✨ 애니메이션</button>
            </div>
            
            <div class="canvas-container">
                <canvas id="erdCanvas" width="1200" height="800"></canvas>
            </div>
        </div>
        
        <div class="erd-container fade-in-up">
            <h2 class="erd-title">📊 테이블 상세 정보</h2>
            {self._generate_table_details_html(erd_structure)}
        </div>
        
        <div class="footer fade-in-up">
            <p>이 문서는 Magic MCP 디자인을 참고하여 폐쇄망 환경에서 동작하도록 구현되었습니다.</p>
            <p>분석 시간: {erd_structure.analysis_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
    
    <script>
        // ERD 캔버스 관련 변수들
        let canvas, ctx;
        let tables = [];
        let relationships = [];
        let isDragging = false;
        let dragStart = {{ x: 0, y: 0 }};
        let offset = {{ x: 0, y: 0 }};
        let scale = 1;
        let showLabels = true;
        let animationEnabled = true;
        
        // ERD 데이터 (Python에서 생성된 데이터)
        const erdData = {{
            tables: {self._generate_erd_data(erd_structure)},
            relationships: {self._generate_relationship_data(erd_structure)}
        }};
        
        // 초기화
        document.addEventListener('DOMContentLoaded', function() {{
            initCanvas();
            drawERD();
            setupEventListeners();
        }});
        
        function initCanvas() {{
            canvas = document.getElementById('erdCanvas');
            ctx = canvas.getContext('2d');
            
            // 고해상도 디스플레이 대응
            const dpr = window.devicePixelRatio || 1;
            const rect = canvas.getBoundingClientRect();
            
            canvas.width = rect.width * dpr;
            canvas.height = rect.height * dpr;
            ctx.scale(dpr, dpr);
            
            canvas.style.width = rect.width + 'px';
            canvas.style.height = rect.height + 'px';
        }}
        
        function drawERD() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // 배경 그리기
            drawBackground();
            
            // 테이블 그리기
            erdData.tables.forEach(table => {{
                drawTable(table);
            }});
            
            // 관계선 그리기
            erdData.relationships.forEach(rel => {{
                drawRelationship(rel);
            }});
        }}
        
        function drawBackground() {{
            // 그라데이션 배경
            const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
            gradient.addColorStop(0, '#f8f9fa');
            gradient.addColorStop(1, '#e9ecef');
            
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, canvas.width, canvas.height);
        }}
        
        function drawTable(table) {{
            const x = table.x + offset.x;
            const y = table.y + offset.y;
            const width = table.width;
            const height = table.height;
            
            // 테이블 박스 그리기
            ctx.save();
            ctx.translate(x, y);
            ctx.scale(scale, scale);
            
            // 그림자
            ctx.shadowColor = 'rgba(0,0,0,0.1)';
            ctx.shadowBlur = 10;
            ctx.shadowOffsetX = 5;
            ctx.shadowOffsetY = 5;
            
            // 테이블 배경
            const gradient = ctx.createLinearGradient(0, 0, 0, height);
            gradient.addColorStop(0, '#ffffff');
            gradient.addColorStop(1, '#f8f9fa');
            
            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, width, height);
            
            // 테이블 테두리
            ctx.shadowColor = 'transparent';
            ctx.strokeStyle = '#3498db';
            ctx.lineWidth = 2;
            ctx.strokeRect(0, 0, width, height);
            
            // 테이블 제목
            ctx.fillStyle = '#2c3e50';
            ctx.font = 'bold 14px Segoe UI';
            ctx.textAlign = 'center';
            ctx.fillText(table.name, width/2, 25);
            
            // 컬럼 목록
            ctx.font = '12px Segoe UI';
            ctx.textAlign = 'left';
            let yOffset = 50;
            
            table.columns.forEach((column, index) => {{
                if (yOffset < height - 20) {{
                    const isPK = table.primaryKeys.includes(column.name);
                    const isFK = table.foreignKeys.includes(column.name);
                    
                    // 컬럼 타입에 따른 색상
                    if (isPK) {{
                        ctx.fillStyle = '#e74c3c';
                    }} else if (isFK) {{
                        ctx.fillStyle = '#3498db';
                    }} else {{
                        ctx.fillStyle = '#7f8c8d';
                    }}
                    
                    ctx.fillText(column.name, 10, yOffset);
                    
                    // 데이터 타입
                    ctx.fillStyle = '#95a5a6';
                    ctx.font = '10px Segoe UI';
                    ctx.fillText(column.data_type, width - 80, yOffset);
                    
                    yOffset += 20;
                }}
            }});
            
            ctx.restore();
        }}
        
        function drawRelationship(rel) {{
            const fromTable = erdData.tables.find(t => t.name === rel.from);
            const toTable = erdData.tables.find(t => t.name === rel.to);
            
            if (!fromTable || !toTable) return;
            
            const fromX = fromTable.x + fromTable.width/2 + offset.x;
            const fromY = fromTable.y + fromTable.height/2 + offset.y;
            const toX = toTable.x + toTable.width/2 + offset.x;
            const toY = toTable.y + toTable.height/2 + offset.y;
            
            ctx.save();
            ctx.translate(offset.x, offset.y);
            ctx.scale(scale, scale);
            
            // 관계선 그리기
            ctx.strokeStyle = '#e74c3c';
            ctx.lineWidth = 2;
            ctx.setLineDash([5, 5]);
            
            ctx.beginPath();
            ctx.moveTo(fromX, fromY);
            ctx.lineTo(toX, toY);
            ctx.stroke();
            
            // 화살표
            const angle = Math.atan2(toY - fromY, toX - fromX);
            const arrowLength = 15;
            
            ctx.setLineDash([]);
            ctx.beginPath();
            ctx.moveTo(toX, toY);
            ctx.lineTo(
                toX - arrowLength * Math.cos(angle - Math.PI/6),
                toY - arrowLength * Math.sin(angle - Math.PI/6)
            );
            ctx.moveTo(toX, toY);
            ctx.lineTo(
                toX - arrowLength * Math.cos(angle + Math.PI/6),
                toY - arrowLength * Math.sin(angle + Math.PI/6)
            );
            ctx.stroke();
            
            ctx.restore();
        }}
        
        function setupEventListeners() {{
            // 마우스 이벤트
            canvas.addEventListener('mousedown', startDrag);
            canvas.addEventListener('mousemove', drag);
            canvas.addEventListener('mouseup', endDrag);
            canvas.addEventListener('wheel', handleZoom);
            
            // 터치 이벤트 (모바일)
            canvas.addEventListener('touchstart', handleTouchStart);
            canvas.addEventListener('touchmove', handleTouchMove);
            canvas.addEventListener('touchend', handleTouchEnd);
        }}
        
        function startDrag(e) {{
            isDragging = true;
            dragStart.x = e.clientX - offset.x;
            dragStart.y = e.clientY - offset.y;
            canvas.style.cursor = 'grabbing';
        }}
        
        function drag(e) {{
            if (!isDragging) return;
            
            offset.x = e.clientX - dragStart.x;
            offset.y = e.clientY - dragStart.y;
            drawERD();
        }}
        
        function endDrag() {{
            isDragging = false;
            canvas.style.cursor = 'grab';
        }}
        
        function handleZoom(e) {{
            e.preventDefault();
            const zoomFactor = e.deltaY > 0 ? 0.9 : 1.1;
            scale = Math.max(0.5, Math.min(2, scale * zoomFactor));
            drawERD();
        }}
        
        function handleTouchStart(e) {{
            e.preventDefault();
            if (e.touches.length === 1) {{
                const touch = e.touches[0];
                startDrag({{
                    clientX: touch.clientX,
                    clientY: touch.clientY
                }});
            }}
        }}
        
        function handleTouchMove(e) {{
            e.preventDefault();
            if (e.touches.length === 1) {{
                const touch = e.touches[0];
                drag({{
                    clientX: touch.clientX,
                    clientY: touch.clientY
                }});
            }}
        }}
        
        function handleTouchEnd(e) {{
            e.preventDefault();
            endDrag();
        }}
        
        // 컨트롤 함수들
        function resetView() {{
            offset.x = 0;
            offset.y = 0;
            scale = 1;
            drawERD();
        }}
        
        function fitView() {{
            // 모든 테이블이 보이도록 조정
            const padding = 50;
            let minX = Math.min(...erdData.tables.map(t => t.x));
            let minY = Math.min(...erdData.tables.map(t => t.y));
            let maxX = Math.max(...erdData.tables.map(t => t.x + t.width));
            let maxY = Math.max(...erdData.tables.map(t => t.y + t.height));
            
            const contentWidth = maxX - minX + padding * 2;
            const contentHeight = maxY - minY + padding * 2;
            
            scale = Math.min(
                (canvas.width - 100) / contentWidth,
                (canvas.height - 100) / contentHeight
            );
            
            offset.x = (canvas.width - contentWidth * scale) / 2 - minX * scale;
            offset.y = (canvas.height - contentHeight * scale) / 2 - minY * scale;
            
            drawERD();
        }}
        
        function toggleLabels() {{
            showLabels = !showLabels;
            drawERD();
        }}
        
        function exportPNG() {{
            const link = document.createElement('a');
            link.download = '{project_name}_ERD.png';
            link.href = canvas.toDataURL();
            link.click();
        }}
        
        function toggleAnimation() {{
            animationEnabled = !animationEnabled;
            if (animationEnabled) {{
                document.body.classList.add('pulse');
            }} else {{
                document.body.classList.remove('pulse');
            }}
        }}
        
        // 초기 맞춤보기
        setTimeout(fitView, 100);
    </script>
</body>
</html>"""
        
        return html_content
    
    def _generate_erd_data(self, erd_structure: ERDStructure) -> str:
        """ERD 데이터 생성 (JavaScript용)"""
        tables_data = []
        
        # 테이블 위치 계산 (그리드 레이아웃)
        cols = 4
        for i, table in enumerate(erd_structure.tables):
            row = i // cols
            col = i % cols
            
            table_data = {
                'name': table.name,
                'x': col * 300 + 50,
                'y': row * 250 + 50,
                'width': 280,
                'height': 200,
                'columns': [{'name': col.name, 'data_type': col.data_type} for col in table.columns],
                'primaryKeys': table.primary_keys,
                'foreignKeys': [fk[0] for fk in table.foreign_keys]
            }
            tables_data.append(table_data)
        
        return str(tables_data).replace("'", '"')
    
    def _generate_relationship_data(self, erd_structure: ERDStructure) -> str:
        """관계 데이터 생성 (JavaScript용)"""
        relationships = []
        
        for table in erd_structure.tables:
            for fk_column, ref_table, ref_column in table.foreign_keys:
                # 참조 테이블명에서 스키마 제거
                ref_table_name = ref_table.split('.')[-1] if '.' in ref_table else ref_table
                
                rel = {
                    'from': table.name,
                    'to': ref_table_name,
                    'fromColumn': fk_column,
                    'toColumn': ref_column
                }
                relationships.append(rel)
        
        return str(relationships).replace("'", '"')
    
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
                    pk_class = "pk-badge" if column.name in table.primary_keys else ""
                    fk_class = "fk-badge" if any(fk[0] == column.name for fk in table.foreign_keys) else ""
                    
                    pk_badge = f'<span class="{pk_class}">PK</span>' if column.name in table.primary_keys else ""
                    fk_badge = f'<span class="{fk_class}">FK</span>' if any(fk[0] == column.name for fk in table.foreign_keys) else ""
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
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description='고급 ERD HTML 생성기')
    parser.add_argument('--project-name', required=True, help='분석할 프로젝트명 (예: sampleSrc)')
    parser.add_argument('--output', help='출력 파일 경로 (기본값: 프로젝트/report/erd_advanced_YYYYMMDD_HHMMSS.html)')
    args = parser.parse_args()
    
    # 프로젝트 경로 설정
    project_path = f"../project/{args.project_name}"
    
    # 출력 경로 설정
    if args.output:
        output_path = args.output
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = f"{project_path}/report/erd_advanced_{timestamp}.html"
    
    # ERD 분석 및 HTML 생성
    from metadb_erd_analyzer import MetaDBERDAnalyzer
    
    analyzer = MetaDBERDAnalyzer(project_path)
    erd_structure = analyzer.analyze_erd()
    
    generator = AdvancedERDGenerator()
    html_content = generator.generate_html(erd_structure, output_path)
    
    print(f"고급 ERD HTML 생성 완료: {len(html_content)} 문자")
    print(f"출력 파일: {output_path}")
