# visualize/builders/relatedness_graph.py
"""
프로페셔널 블루 스타일을 적용한 연관성 시각화 그래프 빌더
연관성 스코어를 기반으로 한 클러스터 기반 네트워크 시각화
"""

from typing import Dict, Any, Optional, List, Tuple
import networkx as nx
from ..data_access import VizDB
from ..schema import create_node, create_edge, create_graph


def _louvain_partition(graph: nx.Graph) -> Dict[str, int]:
    """Run Louvain community detection and return node->cluster mapping."""
    try:
        from networkx.algorithms.community import louvain_communities
        communities = louvain_communities(graph, weight="weight", seed=42)
        return {node: idx for idx, comm in enumerate(communities) for node in comm}
    except Exception:
        try:
            import community as community_louvain
            return community_louvain.best_partition(graph, weight="weight", random_state=42)
        except Exception:
            # Fallback: all nodes in cluster 0
            return {n: 0 for n in graph.nodes()}


def _assign_blue_colors(cluster_id: int) -> Tuple[str, str]:
    """프로페셔널 블루 컬러 팔레트에 따른 클러스터 색상 할당"""
    blue_palette = [
        ("#1976d2", "#0d47a1"),  # 메인 블루
        ("#2196f3", "#1565c0"),  # 액센트 블루  
        ("#42a5f5", "#1976d2"),  # 밝은 블루
        ("#81d4fa", "#42a5f5"),  # 하늘색
        ("#7986cb", "#5c6bc0"),  # 보라색 계열
        ("#64b5f6", "#1e88e5"),  # 중간 블루
        ("#90caf9", "#2196f3"),  # 연한 블루
        ("#bbdefb", "#64b5f6"),  # 아주 연한 블루
    ]
    
    if cluster_id < len(blue_palette):
        return blue_palette[cluster_id]
    else:
        # 추가 클러스터를 위한 순환 색상
        base_idx = cluster_id % len(blue_palette)
        return blue_palette[base_idx]


def _get_node_details(db: VizDB, node_type: str, node_id: int) -> Dict[str, Any]:
    """노드 상세 정보 조회"""
    try:
        if hasattr(db, 'get_node_details'):
            return db.get_node_details(node_type, node_id) or {}
        else:
            # Fallback: 기본적인 상세 정보 구성
            return {'id': node_id, 'type': node_type}
    except Exception:
        return {'id': node_id, 'type': node_type}


def _get_unified_key(node_type: str, details: Dict[str, Any] = None) -> str:
    """중복 제거를 위한 통합 키 생성"""
    if not details:
        return f"unknown_{node_type}"
    
    if node_type == "class":
        # 클래스는 fqn을 기준으로 통합
        fqn = details.get("fqn", details.get("name", f"unknown_class"))
        return f"entity:{fqn}"  # class와 file을 동일하게 처리
    elif node_type == "file":
        # 파일의 경우 클래스명으로 변환하여 통합
        path = details.get("path", f"unknown_file")
        if path.endswith(".java"):
            # Java 파일에서 클래스명 추출
            parts = path.replace("\\", "/").split("/")
            if len(parts) >= 4:  # com/example/service/ClassName.java 형태
                package_parts = []
                for part in parts:
                    if part in ["src", "main", "java"]:
                        continue
                    if part.endswith(".java"):
                        class_name = part.replace(".java", "")
                        package_parts.append(class_name)
                        break
                    package_parts.append(part)
                fqn = ".".join(package_parts)
                return f"entity:{fqn}"  # class와 동일한 키 사용
        return f"file:{path}"
    elif node_type == "method":
        # 메소드는 클래스+메소드명으로 통합
        class_name = details.get("class", "")
        method_name = details.get("name", "")
        return f"method:{class_name}.{method_name}"
    else:
        # 기타 타입은 타입:이름으로 통합
        return f"{node_type}:{details.get('name', details.get('id', 'unknown'))}"


def _get_node_label(node_type: str, details: Dict[str, Any] = None) -> str:
    """프로페셔널한 노드 라벨 생성"""
    if not details:
        return f"Unknown {node_type}"

    if node_type == "method":
        class_name = details.get("class", "").split(".")[-1] if details.get("class") else "Unknown"
        method_name = details.get("name", "unknown")
        return f"{class_name}.{method_name}()"
    elif node_type == "class":
        class_name = details.get("fqn", details.get("name", "Unknown"))
        return class_name.split(".")[-1] if "." in class_name else class_name
    elif node_type == "file":
        path = details.get("path", "unknown")
        filename = path.split("/")[-1] if "/" in path else path.split("\\")[-1]
        return filename.replace(".java", "").replace(".jsp", "")
    elif node_type == "sql_unit":
        stmt_id = details.get("stmt_id", "unknown")
        mapper_ns = details.get("mapper_ns", "unknown") 
        return f"{mapper_ns}.{stmt_id}"
    elif node_type == "table":
        return details.get("table_name", details.get("name", "Unknown Table"))
    else:
        return f"{node_type}:{details.get('name', 'unknown')}"


def build_relatedness_graph_json(
    config: Dict[str, Any],
    project_id: int,
    project_name: Optional[str] = None,
    min_score: float = 0.5,
    max_nodes: int = 100,
    cluster_method: str = "louvain"
) -> Dict[str, Any]:
    """
    연관성 데이터를 기반으로 프로페셔널 블루 스타일의 네트워크 그래프 생성
    
    Args:
        config: 데이터베이스 설정
        project_id: 프로젝트 ID
        project_name: 프로젝트 이름
        min_score: 최소 연관성 점수 임계값 (0.0-1.0)
        max_nodes: 최대 노드 수 제한
        cluster_method: 클러스터링 방법 (louvain)
        
    Returns:
        시각화를 위한 그래프 JSON 데이터
    """
    db = VizDB(config, project_name)
    
    # 연관성 데이터 조회
    relatedness_pairs = db.fetch_relatedness(project_id, min_score)
    
    if not relatedness_pairs:
        graph = create_graph([], [])
        graph['metadata'].update({
            "cluster_method": cluster_method,
            "total_relations": 0,
            "message": f"연관성 점수 {min_score} 이상인 관계가 없습니다."
        })
        return graph

    # 노드와 엣지 구성
    nodes: Dict[str, Dict[str, Any]] = {}
    edges: List[Dict[str, Any]] = []
    G = nx.Graph()
    # 중복 제거를 위한 식별자 매핑
    unified_nodes: Dict[str, str] = {}  # fqn/path -> unified_key

    # 연관성 데이터를 그래프로 변환
    for rel in relatedness_pairs[:max_nodes * 2]:  # 엣지 수 제한으로 노드 수 간접 제어
        # class-file 간 naming_convention 관계는 중복이므로 먼저 제외
        if (rel.reason == "naming_convention" and 
            ((rel.node1_type == "class" and rel.node2_type == "file") or 
             (rel.node1_type == "file" and rel.node2_type == "class"))):
            continue

        # 노드 정보 조회
        src_details = _get_node_details(db, rel.node1_type, rel.node1_id)
        dst_details = _get_node_details(db, rel.node2_type, rel.node2_id)
        
        # 통합 키 생성
        src_unified = _get_unified_key(rel.node1_type, src_details)
        dst_unified = _get_unified_key(rel.node2_type, dst_details)
        
        # 동일한 엔티티 간의 관계는 제외
        if src_unified == dst_unified:
            continue

        # 소스 노드 처리
        if src_unified in unified_nodes:
            src_key = unified_nodes[src_unified]
            # class가 file보다 우선
            if rel.node1_type == "class" and nodes[src_key]["type"] == "file":
                nodes[src_key]["type"] = "class"
                nodes[src_key]["meta"] = src_details
        else:
            src_key = f"{rel.node1_type}:{rel.node1_id}"
            label = _get_node_label(rel.node1_type, src_details)
            nodes[src_key] = create_node(
                src_key, rel.node1_type, label, "unclustered", src_details
            )
            unified_nodes[src_unified] = src_key

        # 대상 노드 처리
        if dst_unified in unified_nodes:
            dst_key = unified_nodes[dst_unified]
            # class가 file보다 우선
            if rel.node2_type == "class" and nodes[dst_key]["type"] == "file":
                nodes[dst_key]["type"] = "class"
                nodes[dst_key]["meta"] = dst_details
        else:
            dst_key = f"{rel.node2_type}:{rel.node2_id}"
            label = _get_node_label(rel.node2_type, dst_details)
            nodes[dst_key] = create_node(
                dst_key, rel.node2_type, label, "unclustered", dst_details
            )
            unified_nodes[dst_unified] = dst_key
            
        # 엣지 추가 (연관성 스코어를 confidence와 weight로 사용)
        edge_id = f"rel_{rel.relatedness_id}"
        edge_strength = "strong" if rel.score >= 0.8 else "medium" if rel.score >= 0.6 else "weak"
        
        edges.append(create_edge(
            edge_id, src_key, dst_key, "related", 
            rel.score, {
                "reason": rel.reason,
                "strength": edge_strength,
                "relatedness_id": rel.relatedness_id
            }
        ))
        
        G.add_edge(src_key, dst_key, weight=rel.score)

        # 최대 노드 수 제한
        if len(nodes) >= max_nodes:
            break

    # 클러스터링 수행
    if len(G.nodes()) > 1:
        partition = _louvain_partition(G)
        cluster_colors = {}
        
        for node_key, cluster_id in partition.items():
            if node_key in nodes:
                fill_color, border_color = _assign_blue_colors(cluster_id)
                nodes[node_key]["group"] = f"cluster_{cluster_id}"
                nodes[node_key]["cluster_id"] = cluster_id
                
                # 클러스터 색상 정보 저장
                if cluster_id not in cluster_colors:
                    cluster_colors[cluster_id] = {
                        "fill": fill_color,
                        "border": border_color,
                        "name": f"클러스터 {cluster_id + 1}"
                    }

        # 메타데이터에 클러스터 정보 추가
        clusters_metadata = {}
        for cluster_id, colors in cluster_colors.items():
            clusters_metadata[f"cluster_{cluster_id}"] = f"fill:{colors['fill']},stroke:{colors['border']}"

    else:
        clusters_metadata = {"cluster_0": "fill:#1976d2,stroke:#0d47a1"}

    # 최종 그래프 구성
    graph_data = create_graph(list(nodes.values()), edges)
    
    # 프로페셔널 스타일 메타데이터 추가
    graph_data["metadata"] = {
        "cluster_method": cluster_method,
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "total_relations": len(relatedness_pairs),
        "min_score_threshold": min_score,
        "style_theme": "professional_blue",
        "clusters": clusters_metadata,
        "color_scheme": "blue_theme",
        "layout_hint": "fcose_physics"  # fcose 레이아웃 권장
    }

    return graph_data


def get_relatedness_summary(
    config: Dict[str, Any],
    project_id: int,
    project_name: Optional[str] = None
) -> Dict[str, Any]:
    """연관성 데이터 요약 통계"""
    db = VizDB(config, project_name)
    relatedness_pairs = db.fetch_relatedness(project_id, 0.0)
    
    if not relatedness_pairs:
        return {"total_pairs": 0, "score_distribution": {}}
    
    scores = [rel.score for rel in relatedness_pairs]
    score_ranges = {
        "매우 강함 (0.8-1.0)": len([s for s in scores if s >= 0.8]),
        "강함 (0.6-0.8)": len([s for s in scores if 0.6 <= s < 0.8]),
        "보통 (0.4-0.6)": len([s for s in scores if 0.4 <= s < 0.6]),
        "약함 (0.2-0.4)": len([s for s in scores if 0.2 <= s < 0.4]),
        "매우 약함 (0.0-0.2)": len([s for s in scores if s < 0.2])
    }
    
    reason_counts = {}
    for rel in relatedness_pairs:
        reason = rel.reason
        reason_counts[reason] = reason_counts.get(reason, 0) + 1
    
    return {
        "total_pairs": len(relatedness_pairs),
        "score_distribution": score_ranges,
        "reason_distribution": reason_counts,
        "avg_score": sum(scores) / len(scores) if scores else 0,
        "max_score": max(scores) if scores else 0,
        "min_score": min(scores) if scores else 0
    }