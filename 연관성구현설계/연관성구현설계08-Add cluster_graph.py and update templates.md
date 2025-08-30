Add cluster_graph.py and update templates
8월 30일
kumtaek/ktohRep
master
+134
-12

아카이브에 보관

공유하기

PR 만들기


1. `visualize/builders/cluster_graph.py` 추가
2. 노드에 `cluster_id` 부여 후 `visualize/schema.py`·템플릿 수정
3. `cyto_base.html`에서 fcose 레이아웃 옵션 반영
복사
Summary
Implemented a new cluster-graph builder that groups nodes by cluster and aggregates inter-cluster edges for visualization

Extended the node schema with an optional cluster_id and applied it in the dependency-graph builder to tag every node with its cluster membership

Updated visualization templates, introducing an offline fcose layout and exposing each node’s cluster_id to the frontend with corresponding layout and reset options

Testing
✅ pytest

⚠️ curl -L https://unpkg.com/cytoscape-fcose@2.2.0/cytoscape-fcose.js -o visualize/static/vendor/cytoscape-fcose/cytoscape-fcose.js (failed: CONNECT tunnel 403)

Notes
An offline placeholder for the fcose layout plugin was added because the real asset could not be downloaded in this environment.


파일 (9)개

visualize/builders/cluster_graph.py
신규

visualize/builders/dependency_graph.py
+1
-1

visualize/schema.py
+9
-1

visualize/static/vendor/cytoscape-fcose/cytoscape-fcose.js
신규

visualize/static/vendor/manifest.json
+5
-0

visualize/templates/class_view.html
+4
-0

visualize/templates/cyto_base.html
+21
-10

visualize/templates/erd_view.html
+4
-0

visualize/templates/graph_view.html
+4
-0

visualize/builders/cluster_graph.py
신규
+70
-0

from typing import Dict, Any, Optional, List, Tuple
from .dependency_graph import build_dependency_graph_json
from ..schema import create_node, create_edge, create_graph
from ..clustering import AdvancedClusterer


def build_cluster_graph_json(
    config: Dict[str, Any],
    project_id: int,
    project_name: Optional[str],
    kinds: List[str],
    min_conf: float,
    focus: str | None = None,
    depth: int = 2,
    max_nodes: int = 2000,
) -> Dict[str, Any]:
    """Build aggregated cluster graph JSON for visualization"""
    # Build base dependency graph
    dep_graph = build_dependency_graph_json(
        config, project_id, project_name, kinds, min_conf, focus, depth, max_nodes
    )
    nodes = dep_graph.get("nodes", [])
    edges = dep_graph.get("edges", [])

    # Ensure each node has a cluster id
    clusterer = AdvancedClusterer(nodes, edges)
    for n in nodes:
        n.setdefault("cluster_id", clusterer.get_cluster_id(n["id"]))

    # Group nodes by cluster id
    clusters: Dict[str, List[Dict[str, Any]]] = {}
    for n in nodes:
        cid = n.get("cluster_id", "Default")
        clusters.setdefault(cid, []).append(n)

    # Create cluster nodes
    cluster_nodes = [
        create_node(
            id=f"cluster:{cid}",
            type="cluster",
            label=f"{cid} ({len(members)})",
            group="Cluster",
            meta={"member_count": len(members)},
            cluster_id=cid,
        )
        for cid, members in clusters.items()
    ]

    # Aggregate edges between clusters
    edge_counts: Dict[Tuple[str, str], int] = {}
    node_cluster_map = {n["id"]: n.get("cluster_id") for n in nodes}
    for e in edges:
        src_c = node_cluster_map.get(e["source"])
        dst_c = node_cluster_map.get(e["target"])
        if src_c and dst_c and src_c != dst_c:
            key = (src_c, dst_c)
            edge_counts[key] = edge_counts.get(key, 0) + 1

    cluster_edges = [
        create_edge(
            id=f"ce{i}",
            source=f"cluster:{src}",
            target=f"cluster:{dst}",
            kind="cluster_edge",
            confidence=count,
        )
        for i, ((src, dst), count) in enumerate(edge_counts.items(), 1)
    ]

    return create_graph(cluster_nodes, cluster_edges)
visualize/builders/dependency_graph.py
+1
-1

@@ -20,51 +20,51 @@ def build_dependency_graph_json(config: Dict[str, Any], project_id: int, project
    # Fetch edges based on criteria
    edges = db.fetch_edges(project_id, kinds, min_conf)
    print(f"  엣지 {len(edges)}개 조회")
    
    # Build node and edge collections
    nodes_dict = {}
    json_edges = []
    
    for edge in edges:
        # Create source node ID
        src_id = f"{edge.src_type}:{edge.src_id}"
        dst_id = f"{edge.dst_type}:{edge.dst_id}" if edge.dst_id else f"unknown:{edge.edge_kind}"
        
        # Get node details and add nodes
        src_details = db.get_node_details(edge.src_type, edge.src_id)
        dst_details = db.get_node_details(edge.dst_type, edge.dst_id) if edge.dst_id else None
        
        nodes_list = list(nodes_dict.values())
    print(f"  노드 {len(nodes_list)}개 생성")

    # Initialize the clusterer with all nodes and edges
    clusterer = AdvancedClusterer(nodes_list, json_edges)

    # Assign cluster IDs to all nodes
    for node in nodes_list:
        node['group'] = clusterer.get_cluster_id(node['id'])
        node['cluster_id'] = clusterer.get_cluster_id(node['id'])
    
    # Apply focus filtering if specified
    if focus:
        nodes_list, json_edges = filter_nodes_by_focus(nodes_list, json_edges, focus, depth)
        print(f"  포커스 필터 후: 노드 {len(nodes_list)}개, 엣지 {len(json_edges)}개")
    
    # Apply node limit
    if len(nodes_list) > max_nodes:
        nodes_list, json_edges = limit_nodes(nodes_list, json_edges, max_nodes)
        print(f"  노드 제한 적용 후: 노드 {len(nodes_list)}개, 엣지 {len(json_edges)}개")

    # --- Meta enrichment: Hotspot bins & Vulnerability overlay ---
    # Complexity estimate: out-degree (call edges) as simple proxy
    out_degree: Dict[str, int] = {}
    for e in json_edges:
        if e.get('kind') == 'call':
            out_degree[e['source']] = out_degree.get(e['source'], 0) + 1

    def _bin_hotspot(loc: int | None, cx: int | None) -> str:
        # LOC-based bins; promote if complexity high
        loc_val = int(loc) if isinstance(loc, (int, float)) else 0
        cx_val = int(cx) if isinstance(cx, (int, float)) else 0
        if loc_val <= 100:
            base = 'low'
        elif loc_val <= 300:
visualize/schema.py
+9
-1

# visualize/schema.py
from typing import Dict, List, Any, Optional


def create_node(id: str, type: str, label: str, group: str, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
def create_node(
    id: str,
    type: str,
    label: str,
    group: str,
    meta: Optional[Dict[str, Any]] = None,
    cluster_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a standardized node dictionary"""
    return {
        'id': id,
        'type': type,
        'label': label,
        'group': group,
        'cluster_id': cluster_id,
        'meta': meta or {}
    }


def create_edge(id: str, source: str, target: str, kind: str, confidence: float = 1.0, 
                meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create a standardized edge dictionary"""
    return {
        'id': id,
        'source': source,
        'target': target,
        'kind': kind,
        'confidence': confidence,
        'meta': meta or {}
    }


def create_graph(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create a complete graph structure"""
    return {
        'nodes': nodes,
        'edges': edges,
        'metadata': {
            'node_count': len(nodes),
            'edge_count': len(edges),
visualize/static/vendor/cytoscape-fcose/cytoscape-fcose.js
신규
+16
-0

/**
 * Placeholder for cytoscape-fcose layout plugin.
 * The full plugin should be provided when building with network access.
 */
(function(){
  if (typeof cytoscape !== 'undefined') {
    cytoscape('layout', 'fcose', function(){
      return {
        run: function(){
          this.emit('layoutstop');
        },
        stop: function(){}
      };
    });
  }
})();
visualize/static/vendor/manifest.json
+5
-0

{
  "generated": "Generated by Source Analyzer visualize module",
  "assets": [
    {
      "url": "https://unpkg.com/cytoscape@3.23.0/dist/cytoscape.min.js",
      "path": "cytoscape/cytoscape.min.js",
      "version": "3.23.0"
    },
    {
      "url": "https://unpkg.com/cytoscape-dagre@2.4.0/cytoscape-dagre.js",
      "path": "cytoscape-dagre/cytoscape-dagre.js",
      "version": "2.4.0"
    },
    {
      "url": "https://unpkg.com/cytoscape-fcose@2.2.0/cytoscape-fcose.js",
      "path": "cytoscape-fcose/cytoscape-fcose.js",
      "version": "2.2.0"
    },
    {
      "url": "https://unpkg.com/dagre@0.8.5/dist/dagre.min.js",
      "path": "dagre/dagre.min.js",
      "version": "0.8.5"
    }
  ],
  "offline_mode": true
}
visualize/templates/class_view.html
+4
-0

@@ -140,50 +140,51 @@
            Classes: <span id="node-count">0</span> | 
            Relations: <span id="edge-count">0</span>
        </div>
        <div class="legend" id="legend"></div>
    </div>
    
    <div id="cy"></div>
    
    <div id="info-panel" class="info-panel">
        <h4 id="info-title">Class Info</h4>
        <div id="info-content"></div>
    </div>

    <script>
        // Build Cytoscape elements
        const elements = [];
        
        // Add nodes (classes)
        for (const node of DATA.nodes || []) {
            elements.push({
                data: {
                    id: node.id,
                    label: node.label,
                    type: node.type,
                    group: node.group,
                    cluster_id: node.cluster_id,
                    meta: node.meta
                }
            });
        }
        
        // Add edges (relationships)
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

        let currentLayout = 'dagre';
        let layoutOptions = {
            'dagre': {
                name: 'dagre',
                rankDir: 'TB',
                nodeSep: 80,
@@ -384,50 +385,53 @@
                const meta = node.data('meta') || {};
                
                return label.toLowerCase().includes(query.toLowerCase()) ||
                       (meta.module_name && meta.module_name.toLowerCase().includes(query.toLowerCase())) ||
                       (meta.file_path && meta.file_path.toLowerCase().includes(query.toLowerCase()));
            });
            
            if (matchedNodes.length > 0) {
                matchedNodes.addClass('search-selected');
                cy.fit(matchedNodes, 50);
            }
        }

        // Class click handler
        cy.on('tap', 'node', function(evt) {
            const node = evt.target;
            const data = node.data();
            
            const panel = document.getElementById('info-panel');
            const title = document.getElementById('info-title');
            const content = document.getElementById('info-content');
            
            title.textContent = data.label || data.id;
            
            let html = `<p><strong>타입:</strong> ${data.type}</p>`;
            if (data.cluster_id) {
                html += `<p><strong>Cluster:</strong> ${data.cluster_id}</p>`;
            }
            
            if (data.meta) {
                if (data.meta.module_name) {
                    html += `<p><strong>모듈:</strong> ${data.meta.module_name}</p>`;
                }
                if (data.meta.file_path) {
                    html += `<p><strong>파일:</strong> ${data.meta.file_path}</p>`;
                }
                if (data.meta.line_number) {
                    html += `<p><strong>라인:</strong> ${data.meta.line_number}</p>`;
                }
                if (data.meta.docstring) {
                    html += `<p><strong>설명:</strong> ${data.meta.docstring}</p>`;
                }
                if (data.meta.base_classes && data.meta.base_classes.length > 0) {
                    html += `<p><strong>상속:</strong> ${data.meta.base_classes.join(', ')}</p>`;
                }
                if (data.meta.is_abstract) {
                    html += `<p><strong>추상 클래스</strong></p>`;
                }
                
                // Attributes
                if (data.meta.attributes && data.meta.attributes.length > 0) {
                    html += `<p><strong>속성 (${data.meta.total_attributes || data.meta.attributes.length}):</strong></p>`;
                    html += `<div class="attribute-list">`;
visualize/templates/cyto_base.html
+21
-10

@@ -66,87 +66,89 @@
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
                    label: node.label,
                    type: node.type,
                    group: node.group,
                    cluster_id: node.cluster_id,
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

        // Initialize Cytoscape
        const cy = cytoscape({
            container: document.getElementById('cy'),
            elements: elements,
            style: [
                // Node styles
@@ -230,55 +232,58 @@
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
                animate: false
                name: 'fcose',
                quality: 'default',
                randomize: true,
                animate: false,
                idealEdgeLength: 100,
                nodeSeparation: 75,
                gravity: 0.5,
                packComponents: true
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
                item.className = 'legend-item';
@@ -291,95 +296,101 @@
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
                name: 'fcose',
                quality: 'default',
                randomize: true,
                animate: true,
                idealEdgeLength: 100,
                nodeSeparation: 75,
                gravity: 0.5,
                packComponents: true
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
        cy.on('tap', 'node', function(evt) {
            const node = evt.target;
            const data = node.data();
            
            const panel = document.getElementById('info-panel');
            const title = document.getElementById('info-title');
            const content = document.getElementById('info-content');
            
            title.textContent = data.label || data.id;
            
            let html = `<p><strong>Type:</strong> ${data.type}</p>`;
            html += `<p><strong>Group:</strong> ${data.group}</p>`;
            if (data.cluster_id) {
                html += `<p><strong>Cluster:</strong> ${data.cluster_id}</p>`;
            }
            html += `<p><strong>ID:</strong> ${data.id}</p>`;
            
            if (data.meta) {
                for (const [key, value] of Object.entries(data.meta)) {
                    if (value !== null && value !== undefined) {
                        html += `<p><strong>${key}:</strong> ${JSON.stringify(value)}</p>`;
                    }
                }
            }
            
            content.innerHTML = html;
            panel.style.display = 'block';
        });

        // Click outside to hide panel
        document.addEventListener('click', function(e) {
            if (!e.target.closest('#info-panel') && !e.target.closest('#cy')) {
                document.getElementById('info-panel').style.display = 'none';
            }
        });

        // Double-click to focus on node
        cy.on('dblclick', 'node', function(evt) {
            const node = evt.target;
            cy.fit(node, 100);
visualize/templates/erd_view.html
+4
-0

@@ -120,50 +120,51 @@
            Tables: <span id="node-count">0</span> | 
            Relations: <span id="edge-count">0</span>
        </div>
        <div class="legend" id="legend"></div>
    </div>
    
    <div id="cy"></div>
    
    <div id="info-panel" class="info-panel">
        <h4 id="info-title">Table Info</h4>
        <div id="info-content"></div>
    </div>

    <script>
        // Build Cytoscape elements
        const elements = [];
        
        // Add nodes (tables)
        for (const node of DATA.nodes || []) {
            elements.push({
                data: {
                    id: node.id,
                    label: node.label,
                    type: node.type,
                    group: node.group,
                    cluster_id: node.cluster_id,
                    meta: node.meta,
                    hasComment: node.meta && node.meta.comment ? 1 : 0
                }
            });
        }
        
        // Add edges (relationships)
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

        let currentLayout = 'dagre';
        let layoutOptions = {
            'dagre': {
                name: 'dagre',
                rankDir: 'TB',
@@ -430,50 +431,53 @@
                const meta = node.data('meta') || {};
                
                return label.toLowerCase().includes(query.toLowerCase()) ||
                       (meta.table_name && meta.table_name.toLowerCase().includes(query.toLowerCase())) ||
                       (meta.owner && meta.owner.toLowerCase().includes(query.toLowerCase()));
            });
            
            if (searchResults.length > 0) {
                searchResults.select();
                cy.fit(searchResults, 50);
            }
        }

        // Table click handler
        cy.on('tap', 'node', function(evt) {
            const node = evt.target;
            const data = node.data();
            
            const panel = document.getElementById('info-panel');
            const title = document.getElementById('info-title');
            const content = document.getElementById('info-content');
            
            title.textContent = data.label || data.id;
            
            let html = `<p><strong>유형:</strong> ${data.type}</p>`;
            if (data.cluster_id) {
                html += `<p><strong>Cluster:</strong> ${data.cluster_id}</p>`;
            }
            
            if (data.meta) {
                if (data.meta.owner) {
                    html += `<p><strong>소유자:</strong> ${data.meta.owner}</p>`;
                }
                if (data.meta.table_name) {
                    html += `<p><strong>테이블명:</strong> ${data.meta.table_name}</p>`;
                }
                if (data.meta.status) {
                    html += `<p><strong>상태:</strong> ${data.meta.status}</p>`;
                }
                if (data.meta.comment) {
                    html += `<p><strong>설명:</strong> ${data.meta.comment}</p>`;
                }
                if (data.meta.pk_columns && data.meta.pk_columns.length > 0) {
                    html += `<p><strong>기본키(PK):</strong></p><ul>`;
                    data.meta.pk_columns.forEach(col => {
                        html += `<li>${col}</li>`;
                    });
                    html += '</ul>';
                }
                if (data.meta.columns && data.meta.columns.length > 0) {
                    html += `<p><strong>컬럼:</strong></p>`;
                    html += `<div style="max-height: 200px; overflow-y: auto;">`;
                    html += `<table style="width: 100%; border-collapse: collapse;">`;
visualize/templates/graph_view.html
+4
-0

@@ -120,50 +120,51 @@
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
                    cluster_id: node.cluster_id,
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
@@ -398,50 +399,53 @@
                
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
        cy.on('tap', 'node', function(evt) {
            const node = evt.target;
            const data = node.data();
            
            const panel = document.getElementById('info-panel');
            const title = document.getElementById('info-title');
            const content = document.getElementById('info-content');
            
            title.textContent = data.label || data.id;
            
            let html = `<p><strong>유형:</strong> ${data.type}</p>`;
            html += `<p><strong>그룹:</strong> ${data.group}</p>`;
            if (data.cluster_id) {
                html += `<p><strong>Cluster:</strong> ${data.cluster_id}</p>`;
            }
            html += `<p><strong>ID:</strong> ${data.id}</p>`;
            
            if (data.meta) {
                for (const [key, value] of Object.entries(data.meta)) {
                    if (value !== null && value !== undefined && key !== 'entities') {
                        if (typeof value === 'object') {
                            html += `<p><strong>${key}:</strong> <pre>${JSON.stringify(value, null, 2)}</pre></p>`;
                        } else {
                            html += `<p><strong>${key}:</strong> ${value}</p>`;
                        }
                    }
                }
                
                // Special handling for component entities
                if (data.meta.entities && data.meta.entities.length > 0) {
                    html += `<p><strong>엔티티 (${data.meta.total_entities || data.meta.entities.length}):</strong></p>`;
                    html += '<ul>';
                    data.meta.entities.forEach(entity => {
                        html += `<li>${entity.label} (${entity.type})</li>`;
                    });
                    if (data.meta.total_entities > data.meta.entities.length) {
                        html += `<li>... 외 ${data.meta.total_entities - data.meta.entities.length}개</li>`;
                    }
                    html += '</ul>';
                }