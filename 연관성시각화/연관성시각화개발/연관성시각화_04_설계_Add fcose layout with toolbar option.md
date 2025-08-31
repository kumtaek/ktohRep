Add fcose layout with toolbar option
8월 30일
kumtaek/ktohRep
master
+51
-33

아카이브에 보관

공유하기

PR 만들기


* Files: `visualize/templates/cyto_base.html`, `visualize/templates/graph_view.html`
* Include `cytoscape-fcose.js` script.
* Modify `layout` configuration to `fcose` with parameters (`idealEdgeLength`, `nodeRepulsion`) influenced by edge `confidence`.
* Add toolbar button or default to fcose; retain dagre as reset option.
복사
Summary
Added the cytoscape-fcose script and a new “Force” toolbar button to enable force-directed graph layouts in the visualization templates

Replaced the default layout with fcose, deriving idealEdgeLength and nodeRepulsion from edge confidence to emphasize stronger relationships

Introduced an applyFcose function to re-run the force-directed layout while retaining a Dagre-based resetView as a fallback option

Testing
✅ pytest


파일 (2)개

visualize/templates/cyto_base.html
+22
-4

visualize/templates/graph_view.html
+29
-29



visualize/templates/cyto_base.html
+22
-4

@@ -66,59 +66,61 @@
        }
        
        .legend {
            display: flex;
            gap: 15px;
            font-size: 12px;
            flex-wrap: wrap;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .legend-color {
            width: 12px;
            height: 12px;
            border-radius: 2px;
        }
    </style>
    <!-- Offline assets -->
    <script src="./static/vendor/cytoscape/cytoscape.min.js"></script>
    <script src="./static/vendor/dagre/dagre.min.js"></script>
    <script src="./static/vendor/cytoscape-dagre/cytoscape-dagre.js"></script>
    <script src="./static/vendor/cytoscape-fcose/cytoscape-fcose.js"></script>
    <script>
        const DATA = __DATA_PLACEHOLDER__;
    </script>
</head>
<body>
    <div id="toolbar">
        <button onclick="cy.fit()" title="Fit to view">🔍 Fit</button>
        <button onclick="cy.center()" title="Center view">🎯 Center</button>
        <button onclick="exportPng()" title="Export as PNG">📷 Export PNG</button>
        <button onclick="applyFcose()" title="Force-directed layout">⚡ Force</button>
        <button onclick="resetView()" title="Reset layout">🔄 Reset</button>
        <input id="search" placeholder="Search nodes..." oninput="searchNode(this.value)" />
        <div class="stats" id="stats">
            Nodes: <span id="node-count">0</span> | 
            Edges: <span id="edge-count">0</span>
        </div>
        <div class="legend" id="legend"></div>
    </div>
    
    <div id="cy"></div>
    
    <div id="info-panel" class="info-panel">
        <h4 id="info-title">Node Info</h4>
        <div id="info-content"></div>
    </div>

    <script>
        // Build Cytoscape elements
        const elements = [];
        
        // Add nodes
        for (const node of DATA.nodes || []) {
            elements.push({
                data: {
                    id: node.id,
@@ -230,54 +232,57 @@
                },
                {
                    selector: 'edge[kind = "fk_inferred"]',
                    style: { 'line-color': '#f44336', 'target-arrow-color': '#f44336' }
                },
                
                // Selected/highlighted styles
                {
                    selector: 'node:selected',
                    style: {
                        'border-width': 3,
                        'border-color': '#ff6b6b',
                        'background-color': '#ffe0e0'
                    }
                },
                {
                    selector: 'edge:selected',
                    style: {
                        'line-color': '#ff6b6b',
                        'target-arrow-color': '#ff6b6b',
                        'width': 4
                    }
                }
            ],
            layout: {
                name: 'dagre',
                rankDir: 'LR',
                nodeSep: 40,
                rankSep: 80,
                name: 'fcose',
                idealEdgeLength: edge => 100 * (1 - (edge.data('confidence') || 0) + 0.1),
                nodeRepulsion: node => {
                    const edges = node.connectedEdges();
                    const avg = edges.length ? edges.reduce((s, e) => s + (e.data('confidence') || 0), 0) / edges.length : 0;
                    return 4500 * (1 - avg + 0.1);
                },
                animate: false
            }
        });

        // Update stats
        document.getElementById('node-count').textContent = DATA.nodes ? DATA.nodes.length : 0;
        document.getElementById('edge-count').textContent = DATA.edges ? DATA.edges.length : 0;

        // Create legend
        function createLegend() {
            const groups = [...new Set((DATA.nodes || []).map(n => n.group))];
            const legend = document.getElementById('legend');
            
            const groupColors = {
                'Controller': '#1976d2',
                'Service': '#388e3c',
                'Repository': '#f57c00',
                'Mapper': '#7b1fa2',
                'JSP': '#d32f2f',
                'DB': '#f9a825',
                'Code': '#616161'
            };
            
            groups.forEach(group => {
                const item = document.createElement('div');
@@ -299,50 +304,63 @@
        createLegend();

        // Event handlers
        function exportPng() {
            const png64 = cy.png({ 
                full: true, 
                scale: 2,
                bg: 'white'
            });
            const link = document.createElement('a');
            link.href = png64;
            link.download = 'graph.png';
            link.click();
        }

        function resetView() {
            cy.layout({
                name: 'dagre',
                rankDir: 'LR',
                nodeSep: 40,
                rankSep: 80,
                animate: true
            }).run();
        }

        function applyFcose() {
            cy.layout({
                name: 'fcose',
                idealEdgeLength: edge => 100 * (1 - (edge.data('confidence') || 0) + 0.1),
                nodeRepulsion: node => {
                    const edges = node.connectedEdges();
                    const avg = edges.length ? edges.reduce((s, e) => s + (e.data('confidence') || 0), 0) / edges.length : 0;
                    return 4500 * (1 - avg + 0.1);
                },
                animate: true
            }).run();
        }

        function searchNode(query) {
            cy.nodes().removeClass('highlighted');
            
            if (!query.trim()) {
                cy.nodes().unselect();
                return;
            }
            
            const matchedNodes = cy.nodes().filter(node => {
                const label = node.data('label') || '';
                const type = node.data('type') || '';
                const group = node.data('group') || '';
                
                return label.toLowerCase().includes(query.toLowerCase()) ||
                       type.toLowerCase().includes(query.toLowerCase()) ||
                       group.toLowerCase().includes(query.toLowerCase());
            });
            
            if (matchedNodes.length > 0) {
                matchedNodes.select();
                cy.fit(matchedNodes, 50);
            }
        }

        // Node click handler
visualize/templates/graph_view.html
+29
-29

@@ -66,125 +66,124 @@
        }
        
        .legend {
            display: flex;
            gap: 15px;
            font-size: 12px;
            flex-wrap: wrap;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .legend-color {
            width: 12px;
            height: 12px;
            border-radius: 2px;
        }
    </style>
    <!-- Offline assets (relative to output dir: output/visualize -> ../static) -->
    <script src="../static/vendor/cytoscape/cytoscape.min.js"></script>
    <script src="../static/vendor/dagre/dagre.min.js"></script>
    <script src="../static/vendor/cytoscape-dagre/cytoscape-dagre.js"></script>
    <script src="../static/vendor/cytoscape-fcose/cytoscape-fcose.js"></script>
    <script>
        const DATA = __DATA_PLACEHOLDER__;
    </script>
    <script>
        document.addEventListener('DOMContentLoaded', function () {
            const btns = [
                { sel: 'button[onclick="cy.fit()"]', text: '화면맞춤', title: '화면에 맞추기' },
                { sel: 'button[onclick="cy.center()"]', text: '중앙정렬', title: '중앙 정렬' },
                { sel: 'button[onclick="exportPng()"]', text: 'PNG 저장', title: 'PNG로 내보내기' },
                { sel: 'button[onclick="resetView()"]', text: '레이아웃 초기화', title: '레이아웃 초기화' },
                { sel: 'button[onclick="togglePhysics()"]', text: '물리 레이아웃', title: '물리 레이아웃 토글' }
                { sel: 'button[onclick="applyFcose()"]', text: '물리 레이아웃', title: '물리 레이아웃 적용' },
                { sel: 'button[onclick="resetView()"]', text: '레이아웃 초기화', title: '레이아웃 초기화' }
            ];
            btns.forEach(b => { const el = document.querySelector(b.sel); if (el) { el.textContent = b.text; el.title = b.title; } });
            const search = document.getElementById('search'); if (search) search.placeholder = '노드 검색...';
            const stats = document.getElementById('stats'); if (stats) stats.innerHTML = '노드: <span id="node-count">0</span> | 엣지: <span id="edge-count">0</span>';
            const h = document.getElementById('info-title'); if (h) h.textContent = '노드 정보';
            document.title = 'Source Analyzer - 의존성 그래프';
        });
    </script>
</head>
<body>
    <div id="toolbar">
        <button onclick="cy.fit()" title="Fit to view">🔍 Fit</button>
        <button onclick="cy.center()" title="Center view">🎯 Center</button>
        <button onclick="exportPng()" title="Export as PNG">📷 Export PNG</button>
        <button onclick="applyFcose()" title="Force layout">⚡ Physics</button>
        <button onclick="resetView()" title="Reset layout">🔄 Reset</button>
        <button onclick="togglePhysics()" title="Toggle physics">⚡ Physics</button>
        <input id="search" placeholder="Search nodes..." oninput="searchNode(this.value)" />
        <div class="stats" id="stats">
            Nodes: <span id="node-count">0</span> | 
            Edges: <span id="edge-count">0</span>
        </div>
        <div class="legend" id="legend"></div>
    </div>
    
    <div id="cy"></div>
    
    <div id="info-panel" class="info-panel">
        <h4 id="info-title">Node Info</h4>
        <div id="info-content"></div>
    </div>

    <script>
        // Build Cytoscape elements
        const elements = [];
        
        // Add nodes
        for (const node of DATA.nodes || []) {
            elements.push({
                data: {
                    id: node.id,
                    label: node.label,
                    type: node.type,
                    group: node.group,
                    meta: node.meta
                }
            });
        }
        
        // Add edges
        for (const edge of DATA.edges || []) {
            elements.push({
                data: {
                    id: edge.id,
                    source: edge.source,
                    target: edge.target,
                    kind: edge.kind,
                    confidence: edge.confidence,
                    meta: edge.meta
                }
            });
        }

        let usePhysics = false;

        // Initialize Cytoscape
        const cy = cytoscape({
            container: document.getElementById('cy'),
            elements: elements,
            style: [
                // Node styles
                {
                    selector: 'node',
                    style: {
                        'label': 'data(label)',
                        'font-size': '10px',
                        'text-wrap': 'wrap',
                        'text-max-width': '150px',
                        'text-valign': 'center',
                        'text-halign': 'center',
                        'background-color': '#f0f0f0',
                        'border-width': 1,
                        'border-color': '#999',
                        'width': 'mapData(label.length, 5, 50, 30, 120)',
                        'height': 'mapData(label.length, 5, 50, 20, 40)',
                        'font-family': 'monospace'
                    }
                },
                
                // Group-specific node colors
@@ -274,54 +273,57 @@
                },
                {
                    selector: 'edge[kind = "mixed"]',
                    style: { 'line-color': '#795548', 'target-arrow-color': '#795548', 'width': 3 }
                },
                
                // Selected/highlighted styles
                {
                    selector: 'node:selected',
                    style: {
                        'border-width': 3,
                        'border-color': '#ff6b6b',
                        'background-color': '#ffe0e0'
                    }
                },
                {
                    selector: 'edge:selected',
                    style: {
                        'line-color': '#ff6b6b',
                        'target-arrow-color': '#ff6b6b',
                        'width': 4
                    }
                }
            ],
            layout: {
                name: 'dagre',
                rankDir: 'LR',
                nodeSep: 40,
                rankSep: 80,
                name: 'fcose',
                idealEdgeLength: edge => 100 * (1 - (edge.data('confidence') || 0) + 0.1),
                nodeRepulsion: node => {
                    const edges = node.connectedEdges();
                    const avg = edges.length ? edges.reduce((s, e) => s + (e.data('confidence') || 0), 0) / edges.length : 0;
                    return 4500 * (1 - avg + 0.1);
                },
                animate: false
            }
        });

        // Update stats
        document.getElementById('node-count').textContent = DATA.nodes ? DATA.nodes.length : 0;
        document.getElementById('edge-count').textContent = DATA.edges ? DATA.edges.length : 0;

        // Create legend
        function createLegend() {
            const groups = [...new Set((DATA.nodes || []).map(n => n.group))];
            const legend = document.getElementById('legend');
            
            const groupColors = {
                'Controller': '#1976d2',
                'Service': '#388e3c',
                'Repository': '#f57c00',
                'Mapper': '#7b1fa2',
                'JSP': '#d32f2f',
                'DB': '#f9a825',
                'Code': '#616161',
                'Entity': '#9c27b0',
                'Util': '#607d8b',
                'Config': '#ff5722'
            };
@@ -337,72 +339,70 @@
                const label = document.createElement('span');
                label.textContent = group;
                
                item.appendChild(color);
                item.appendChild(label);
                legend.appendChild(item);
            });
        }
        
        createLegend();

        // Event handlers
        function exportPng() {
            const png64 = cy.png({ 
                full: true, 
                scale: 2,
                bg: 'white'
            });
            const link = document.createElement('a');
            link.href = png64;
            link.download = 'dependency-graph.png';
            link.click();
        }

        function resetView() {
            const layout = usePhysics ? 'cose' : 'dagre';
            const layoutOptions = usePhysics ? 
                {
                    name: 'cose',
                    animate: true,
                    nodeRepulsion: 4000,
                    idealEdgeLength: 100
                } :
                {
                    name: 'dagre',
                    rankDir: 'LR',
                    nodeSep: 40,
                    rankSep: 80,
                    animate: true
                };
            
            cy.layout(layoutOptions).run();
            cy.layout({
                name: 'dagre',
                rankDir: 'LR',
                nodeSep: 40,
                rankSep: 80,
                animate: true
            }).run();
        }

        function togglePhysics() {
            usePhysics = !usePhysics;
            resetView();
        function applyFcose() {
            cy.layout({
                name: 'fcose',
                idealEdgeLength: edge => 100 * (1 - (edge.data('confidence') || 0) + 0.1),
                nodeRepulsion: node => {
                    const edges = node.connectedEdges();
                    const avg = edges.length ? edges.reduce((s, e) => s + (e.data('confidence') || 0), 0) / edges.length : 0;
                    return 4500 * (1 - avg + 0.1);
                },
                animate: true
            }).run();
        }

        function searchNode(query) {
            cy.nodes().removeClass('highlighted');
            
            if (!query.trim()) {
                cy.nodes().unselect();
                return;
            }
            
            const matchedNodes = cy.nodes().filter(node => {
                const label = node.data('label') || '';
                const type = node.data('type') || '';
                const group = node.data('group') || '';
                
                return label.toLowerCase().includes(query.toLowerCase()) ||
                       type.toLowerCase().includes(query.toLowerCase()) ||
                       group.toLowerCase().includes(query.toLowerCase());
            });
            
            if (matchedNodes.length > 0) {
                matchedNodes.select();
                cy.fit(matchedNodes, 50);
            }
        }
        
        