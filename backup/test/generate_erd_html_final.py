#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
최종 ERD HTML 리포트 생성 스크립트
수정된 ERD 데이터를 사용하여 모든 노드와 엣지가 정상적으로 표시되는 HTML을 생성합니다.
"""

import json
import os
from pathlib import Path
from datetime import datetime

def load_erd_data(json_path):
    """ERD JSON 데이터를 로드합니다."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"✅ ERD 데이터 로드 성공:")
            print(f"  - 노드 수: {len(data.get('nodes', {}))}개")
            print(f"  - 엣지 수: {len(data.get('edges', []))}개")
            return data
    except Exception as e:
        print(f"❌ ERD 데이터 로드 실패: {e}")
        return None

def generate_erd_html(erd_data):
    """ERD 데이터를 사용하여 HTML을 생성합니다."""
    
    # JSON 데이터를 문자열로 변환
    erd_data_json = json.dumps(erd_data, ensure_ascii=False, indent=2)
    
    print(f"🔍 JSON 데이터 생성 완료:")
    print(f"  - JSON 길이: {len(erd_data_json)} 문자")
    print(f"  - 노드 키 수: {len(erd_data.get('nodes', {}))}개")
    
    # HTML 템플릿
    html_template = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title>Source Analyzer - ERD 리포트</title>
    <style>
        body, html { 
            margin: 0; 
            height: 100%; 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        #toolbar { 
            padding: 12px; 
            border-bottom: 1px solid #ddd; 
            background: #f8f9fa;
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }
        #cy { 
            width: 100%; 
            height: calc(100% - 80px); 
        }
        
        button {
            background: #007bff;
            border: none;
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        button:hover {
            background: #0056b3;
        }
        
        #search {
            padding: 8px;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 14px;
            min-width: 200px;
        }
        
        .debug-info {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 10px;
            margin: 10px 0;
            font-family: monospace;
            font-size: 12px;
        }
        
        .tooltip {
            position: absolute;
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 0;
            max-width: 400px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            display: none;
            z-index: 2000;
            font-size: 12px;
        }
        
        .tooltip-header {
            background: #f8f9fa;
            padding: 12px;
            border-bottom: 1px solid #dee2e6;
            border-radius: 8px 8px 0 0;
        }
        
        .tooltip-title {
            font-weight: bold;
            font-size: 14px;
            color: #212529;
            margin-bottom: 4px;
        }
        
        .tooltip-subtitle {
            font-size: 11px;
            color: #6c757d;
        }
        
        .tooltip-content {
            padding: 0;
            max-height: 300px;
            overflow-y: auto;
        }
        
        .columns-list {
            list-style: none;
            margin: 0;
            padding: 0;
        }
        
        .column-item {
            padding: 8px 12px;
            border-bottom: 1px solid #f1f3f4;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .column-item:last-child {
            border-bottom: none;
        }
        
        .column-name {
            font-weight: 500;
            color: #212529;
        }
        
        .column-type {
            font-size: 11px;
            color: #6c757d;
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 3px;
        }
        
        .pk-badge {
            background: #28a745;
            color: white;
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 10px;
            margin-left: 8px;
        }
        
        .nullable-badge {
            background: #ffc107;
            color: #212529;
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 10px;
            margin-left: 4px;
        }
    </style>
</head>
<body>
    <div id="toolbar">
        <button onclick="resetView()">초기화</button>
        <button onclick="exportPNG()">PNG 내보내기</button>
        <button onclick="toggleLayout()">레이아웃 변경</button>
        <input type="text" id="search" placeholder="테이블 검색..." onkeyup="searchTables()">
        <span id="stats"></span>
    </div>
    
    <!-- 디버깅 정보 표시 -->
    <div class="debug-info">
        <strong>디버깅 정보:</strong><br>
        <span id="debug-info"></span>
    </div>
    
    <div id="cy"></div>
    
    <div class="tooltip" id="tooltip">
        <div class="tooltip-header">
            <div class="tooltip-title" id="tooltip-title"></div>
            <div class="tooltip-subtitle" id="tooltip-subtitle"></div>
        </div>
        <div class="tooltip-content">
            <ul class="columns-list" id="tooltip-columns"></ul>
        </div>
    </div>

    <script src="https://unpkg.com/cytoscape@3.28.1/dist/cytoscape.min.js"></script>
    <script src="https://unpkg.com/dagre@0.8.5/dist/dagre.min.js"></script>
    <script src="https://unpkg.com/cytoscape-dagre@2.5.0/cytoscape-dagre.js"></script>
    
    <script>
        // ERD 데이터
        const erdData = {erd_data_json};
        
        // 디버깅 정보 표시
        document.getElementById('debug-info').innerHTML = 
            `노드 수: ${Object.keys(erdData.nodes).length}개, 엣지 수: ${erdData.edges.length}개<br>` +
            `노드 목록: ${Object.keys(erdData.nodes).join(', ')}`;
        
        console.log('ERD 데이터 로드됨:', erdData);
        console.log('노드 수:', Object.keys(erdData.nodes).length);
        console.log('엣지 수:', erdData.edges.length);
        
        // Cytoscape 초기화
        const cy = cytoscape({
            container: document.getElementById('cy'),
            elements: {
                nodes: [],
                edges: []
            },
            style: [
                {
                    selector: 'node',
                    style: {
                        'background-color': '#007bff',
                        'label': 'data(label)',
                        'color': 'white',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'width': '120px',
                        'height': '60px',
                        'font-size': '12px',
                        'font-weight': 'bold',
                        'border-width': 2,
                        'border-color': '#0056b3'
                    }
                },
                {
                    selector: 'edge',
                    style: {
                        'width': 2,
                        'line-color': '#6c757d',
                        'target-arrow-color': '#6c757d',
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier',
                        'label': 'data(label)',
                        'font-size': '10px',
                        'text-rotation': 'autorotate'
                    }
                },
                {
                    selector: 'node[type="table"]',
                    style: {
                        'background-color': '#28a745',
                        'border-color': '#1e7e34'
                    }
                }
            ],
            layout: {
                name: 'dagre',
                rankDir: 'TB',
                nodeSep: 50,
                edgeSep: 20,
                rankSep: 100
            }
        });
        
        console.log('Cytoscape 초기화 완료');
        
        // 노드 추가
        console.log('노드 추가 시작...');
        Object.values(erdData.nodes).forEach((node, index) => {
            console.log(`노드 ${index + 1} 추가:`, node.id);
            cy.add({
                group: 'nodes',
                data: {
                    id: node.id,
                    label: node.label,
                    type: node.type,
                    meta: node.meta
                }
            });
        });
        console.log('노드 추가 완료');
        
        // 엣지 추가
        console.log('엣지 추가 시작...');
        erdData.edges.forEach((edge, index) => {
            console.log(`엣지 ${index + 1} 추가:`, edge.source, '->', edge.target);
            cy.add({
                group: 'edges',
                data: {
                    id: edge.id,
                    source: edge.source,
                    target: edge.target,
                    label: edge.label,
                    meta: edge.meta
                }
            });
        });
        console.log('엣지 추가 완료');
        
        // 레이아웃 적용
        console.log('레이아웃 적용 시작...');
        cy.layout({ name: 'dagre' }).run();
        console.log('레이아웃 적용 완료');
        
        // 통계 업데이트
        document.getElementById('stats').textContent = 
            `테이블: ${Object.keys(erdData.nodes).length}개, 관계: ${erdData.edges.length}개`;
        
        // 노드 클릭 이벤트
        cy.on('tap', 'node', function(evt) {
            const node = evt.target;
            const meta = node.data('meta');
            showTooltip(node, meta);
        });
        
        // 툴팁 표시
        function showTooltip(node, meta) {
            const tooltip = document.getElementById('tooltip');
            const title = document.getElementById('tooltip-title');
            const subtitle = document.getElementById('tooltip-subtitle');
            const columns = document.getElementById('tooltip-columns');
            
            title.textContent = meta.table_name;
            subtitle.textContent = `${meta.owner} 스키마 - ${meta.status}`;
            
            columns.innerHTML = '';
            meta.columns.forEach(col => {
                const li = document.createElement('li');
                li.className = 'column-item';
                
                const nameSpan = document.createElement('span');
                nameSpan.className = 'column-name';
                nameSpan.textContent = col.name;
                
                const typeSpan = document.createElement('span');
                typeSpan.className = 'column-type';
                typeSpan.textContent = col.data_type;
                
                li.appendChild(nameSpan);
                li.appendChild(typeSpan);
                
                if (col.is_pk) {
                    const pkBadge = document.createElement('span');
                    pkBadge.className = 'pk-badge';
                    pkBadge.textContent = 'PK';
                    li.appendChild(pkBadge);
                }
                
                if (col.nullable) {
                    const nullableBadge = document.createElement('span');
                    nullableBadge.className = 'nullable-badge';
                    nullableBadge.textContent = 'NULL';
                    li.appendChild(nullableBadge);
                }
                
                columns.appendChild(li);
            });
            
            tooltip.style.display = 'block';
        }
        
        // 툴팁 숨기기
        cy.on('tap', function(evt) {
            if (evt.target === cy) {
                document.getElementById('tooltip').style.display = 'none';
            }
        });
        
        // 마우스 움직임에 따른 툴팁 위치 조정
        cy.on('mouseover', 'node', function(evt) {
            const tooltip = document.getElementById('tooltip');
            const pos = evt.renderedPosition;
            tooltip.style.left = (pos.x + 20) + 'px';
            tooltip.style.top = (pos.y - 20) + 'px';
        });
        
        // 기능 함수들
        function resetView() {
            cy.fit();
        }
        
        function exportPNG() {
            const png = cy.png();
            const link = document.createElement('a');
            link.download = 'erd_diagram.png';
            link.href = png;
            link.click();
        }
        
        function toggleLayout() {
            const layouts = ['dagre', 'circle', 'grid'];
            const currentLayout = cy.layout().name;
            const nextIndex = (layouts.indexOf(currentLayout) + 1) % layouts.length;
            const nextLayout = layouts[nextIndex];
            
            cy.layout({ name: nextLayout }).run();
        }
        
        function searchTables() {
            const searchTerm = document.getElementById('search').value.toLowerCase();
            
            cy.nodes().forEach(node => {
                const label = node.data('label').toLowerCase();
                if (label.includes(searchTerm)) {
                    node.style('background-color', '#ffc107');
                    node.style('border-color', '#e0a800');
                } else {
                    node.style('background-color', '#28a745');
                    node.style('border-color', '#1e7e34');
                }
            });
        }
        
        console.log('ERD 초기화 완료');
    </script>
</body>
</html>"""
    
    # HTML 생성
    html_content = html_template.replace('{erd_data_json}', erd_data_json)
    
    return html_content

def save_erd_html(html_content, output_path):
    """ERD HTML을 파일로 저장합니다."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ ERD HTML 저장 완료: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ ERD HTML 저장 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    print("=" * 80)
    print("🚀 최종 ERD HTML 리포트 생성")
    print("=" * 80)
    
    # 최신 수정된 ERD JSON 파일 찾기
    json_dir = Path("./project/sampleSrc/report")
    json_files = list(json_dir.glob("erd_data_fixed_*.json"))
    
    if not json_files:
        print("❌ 수정된 ERD JSON 파일을 찾을 수 없습니다.")
        print(f"📁 찾는 경로: {json_dir}")
        return
    
    # 가장 최신 파일 선택
    latest_json = max(json_files, key=lambda x: x.stat().st_mtime)
    print(f"📁 사용할 ERD 데이터: {latest_json}")
    
    # ERD 데이터 로드
    erd_data = load_erd_data(latest_json)
    
    if not erd_data:
        print("❌ ERD 데이터 로드 실패")
        return
    
    # ERD HTML 생성
    print("🔍 ERD HTML 생성 중...")
    html_content = generate_erd_html(erd_data)
    
    # 새로운 폴더 구조에 맞춰 HTML 파일 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_path = json_dir / f"erd_final_{timestamp}.html"
    
    if save_erd_html(html_content, html_path):
        print(f"\n🎉 최종 ERD HTML 리포트 생성 완료!")
        print(f"📁 저장 위치: {html_path}")
        print(f"📊 리포트 내용:")
        print(f"  - 테이블 수: {len(erd_data['nodes'])}개")
        print(f"  - 관계 수: {len(erd_data['edges'])}개")
        print(f"  - 인터랙티브 기능: 검색, 툴팁, 레이아웃 변경 등")
        print(f"  - 디버깅 정보: 콘솔 로그 및 화면 표시")
        
        # 브라우저에서 열기
        print(f"\n🌐 브라우저에서 ERD 리포트 열기...")
        os.startfile(html_path)
    else:
        print("❌ ERD HTML 리포트 생성 실패")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
