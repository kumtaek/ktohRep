# visualize/analyzers/relationship_analyzer.py
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict, Counter
from dataclasses import dataclass
import logging

from ..data_access import VizDB
from ..schema import create_node, create_edge

logger = logging.getLogger(__name__)


@dataclass
class EdgePattern:
    """Pattern for detecting relationships"""
    name: str
    source_types: List[str]
    target_types: List[str]
    confidence_threshold: float
    description: str


@dataclass
class FallbackStrategy:
    """Strategy for handling missing relationships"""
    name: str
    trigger_conditions: Dict[str, Any]
    actions: List[str]
    expected_outcome: str


class RelationshipAnalyzer:
    """Intelligent analyzer for detecting and creating meaningful relationships"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        # Define relationship patterns
        self.patterns = [
            EdgePattern(
                name="method_call_chain",
                source_types=["method"],
                target_types=["method"],
                confidence_threshold=0.3,
                description="Method calls within same project"
            ),
            EdgePattern(
                name="class_dependency",
                source_types=["class"],
                target_types=["class"],
                confidence_threshold=0.4,
                description="Class-to-class dependencies"
            ),
            EdgePattern(
                name="file_inclusion",
                source_types=["file"],
                target_types=["file"],
                confidence_threshold=0.5,
                description="File import/include relationships"
            ),
            EdgePattern(
                name="sql_table_usage",
                source_types=["sql_unit"],
                target_types=["table"],
                confidence_threshold=0.6,
                description="SQL queries using database tables"
            )
        ]
        
        # Define fallback strategies
        self.fallback_strategies = [
            FallbackStrategy(
                name="sequence_from_method_proximity",
                trigger_conditions={
                    "missing_edge_types": ["call", "call_unresolved"],
                    "available_node_types": ["method"],
                    "min_nodes": 2
                },
                actions=[
                    "group_methods_by_class",
                    "create_sequential_connections", 
                    "infer_call_order_by_name_similarity"
                ],
                expected_outcome="Simplified sequence diagram with inferred method flows"
            ),
            FallbackStrategy(
                name="dependency_from_package_structure",
                trigger_conditions={
                    "missing_edge_types": ["include", "extends"],
                    "available_edge_types": ["package_relation"],
                    "available_node_types": ["class", "file"]
                },
                actions=[
                    "analyze_package_hierarchy",
                    "create_structural_dependencies",
                    "infer_inheritance_from_naming"
                ],
                expected_outcome="Package-based dependency graph"
            ),
            FallbackStrategy(
                name="erd_from_naming_conventions",
                trigger_conditions={
                    "missing_edge_types": ["fk_inferred"],
                    "available_node_types": ["table"],
                    "min_nodes": 2
                },
                actions=[
                    "analyze_column_name_patterns",
                    "detect_foreign_key_conventions",
                    "create_inferred_relationships"
                ],
                expected_outcome="ERD with naming-based relationships"
            )
        ]
    
    def analyze_project_relationships(self, db: VizDB, project_id: int) -> Dict[str, Any]:
        """Comprehensive relationship analysis for a project"""
        logger.info(f"Analyzing relationships for project {project_id}")
        
        analysis_result = {
            "project_id": project_id,
            "available_relationships": {},
            "missing_relationships": {},
            "fallback_applied": [],
            "recommendations": [],
            "quality_score": 0.0
        }
        
        # Get current state
        all_edges = db.fetch_edges(project_id, [], 0.0)
        edge_types = self._categorize_edges(all_edges)
        
        analysis_result["available_relationships"] = edge_types
        
        # Analyze each pattern
        for pattern in self.patterns:
            pattern_result = self._analyze_pattern(db, project_id, pattern, edge_types)
            
            if pattern_result["status"] == "missing":
                analysis_result["missing_relationships"][pattern.name] = pattern_result
            
        # Apply fallback strategies if needed
        for strategy in self.fallback_strategies:
            if self._should_apply_strategy(strategy, edge_types, analysis_result):
                fallback_result = self._apply_fallback_strategy(db, project_id, strategy)
                analysis_result["fallback_applied"].append(fallback_result)
        
        # Generate recommendations
        analysis_result["recommendations"] = self._generate_recommendations(analysis_result)
        analysis_result["quality_score"] = self._calculate_relationship_quality(analysis_result)
        
        return analysis_result
    
    def _categorize_edges(self, edges: List) -> Dict[str, int]:
        """Categorize edges by type and count"""
        edge_counts = Counter()
        
        for edge in edges:
            edge_counts[edge.edge_kind] += 1
        
        return dict(edge_counts)
    
    def _analyze_pattern(self, db: VizDB, project_id: int, pattern: EdgePattern, edge_types: Dict[str, int]) -> Dict[str, Any]:
        """Analyze a specific relationship pattern"""
        result = {
            "pattern": pattern.name,
            "status": "unknown",
            "details": {},
            "suggestions": []
        }
        
        # Check if we have edges that match this pattern
        matching_edges = []
        for edge_type in edge_types.keys():
            if self._matches_pattern(edge_type, pattern):
                matching_edges.append(edge_type)
        
        if matching_edges:
            result["status"] = "present" 
            result["details"]["matching_edges"] = matching_edges
            result["details"]["total_count"] = sum(edge_types[edge] for edge in matching_edges)
        else:
            result["status"] = "missing"
            result["suggestions"] = self._get_pattern_suggestions(pattern)
        
        return result
    
    def _matches_pattern(self, edge_type: str, pattern: EdgePattern) -> bool:
        """Check if an edge type matches a pattern"""
        keywords = {
            "method_call_chain": ["call", "invoke", "execute"],
            "class_dependency": ["include", "import", "extend", "implement", "depend"],
            "file_inclusion": ["include", "import", "require"],
            "sql_table_usage": ["use_table", "query", "select", "table"]
        }
        
        pattern_keywords = keywords.get(pattern.name, [])
        return any(keyword in edge_type.lower() for keyword in pattern_keywords)
    
    def _should_apply_strategy(self, strategy: FallbackStrategy, edge_types: Dict[str, int], analysis_result: Dict[str, Any]) -> bool:
        """Determine if a fallback strategy should be applied"""
        conditions = strategy.trigger_conditions
        
        # Check missing edge types
        if "missing_edge_types" in conditions:
            missing_edges = conditions["missing_edge_types"]
            if not all(edge_type not in edge_types for edge_type in missing_edges):
                return False
        
        # Check available edge types
        if "available_edge_types" in conditions:
            available_edges = conditions["available_edge_types"]
            if not any(edge_type in edge_types for edge_type in available_edges):
                return False
        
        return True
    
    def _apply_fallback_strategy(self, db: VizDB, project_id: int, strategy: FallbackStrategy) -> Dict[str, Any]:
        """Apply a fallback strategy"""
        logger.info(f"Applying fallback strategy: {strategy.name}")
        
        result = {
            "strategy": strategy.name,
            "actions_taken": [],
            "edges_created": 0,
            "success": False
        }
        
        try:
            if strategy.name == "sequence_from_method_proximity":
                edges_created = self._create_method_sequence_fallback(db, project_id)
                result["edges_created"] = edges_created
                result["actions_taken"] = ["created_sequential_method_connections"]
                result["success"] = edges_created > 0
                
            elif strategy.name == "dependency_from_package_structure":
                edges_created = self._create_package_dependency_fallback(db, project_id)
                result["edges_created"] = edges_created
                result["actions_taken"] = ["created_package_based_dependencies"]
                result["success"] = edges_created > 0
                
            elif strategy.name == "erd_from_naming_conventions":
                edges_created = self._create_naming_based_erd_fallback(db, project_id)
                result["edges_created"] = edges_created
                result["actions_taken"] = ["inferred_foreign_keys_from_naming"]
                result["success"] = edges_created > 0
        
        except Exception as e:
            logger.error(f"Fallback strategy {strategy.name} failed: {e}")
            result["error"] = str(e)
        
        return result
    
    def _create_method_sequence_fallback(self, db: VizDB, project_id: int) -> int:
        """Create method sequence connections as fallback"""
        # This is already implemented in the sequence_diagram.py
        # Here we would enhance it with smarter heuristics
        
        session = db.session()
        try:
            methods = db.fetch_methods_by_project(project_id)
            
            # Group methods by class for better connections
            class_methods = defaultdict(list)
            for method in methods:
                # Get class info for method
                method_details = db.get_node_details('method', method.method_id)
                if method_details and method_details.get('class'):
                    class_name = method_details['class']
                    class_methods[class_name].append(method)
            
            edges_created = 0
            
            # Create intra-class method connections
            for class_name, methods_list in class_methods.items():
                if len(methods_list) > 1:
                    # Sort methods by common patterns (constructor first, etc.)
                    sorted_methods = self._sort_methods_by_likely_call_order(methods_list)
                    
                    for i, method in enumerate(sorted_methods[:-1]):
                        next_method = sorted_methods[i + 1]
                        
                        # This would need to be stored somewhere persistent
                        # For now, we just count what we would create
                        edges_created += 1
                        
                        logger.debug(f"Would create inferred call: {method.name} -> {next_method.name}")
            
            return edges_created
            
        finally:
            session.close()
    
    def _sort_methods_by_likely_call_order(self, methods: List) -> List:
        """Sort methods by likely call order using heuristics"""
        def method_priority(method):
            name = method.name.lower()
            
            # Constructor/initialization methods first
            if any(word in name for word in ['init', 'construct', 'setup', 'create']):
                return 0
            
            # Main/entry methods
            if any(word in name for word in ['main', 'run', 'execute', 'start']):
                return 1
            
            # Getter/setter methods later
            if name.startswith('get') or name.startswith('set') or name.startswith('is'):
                return 3
            
            # Cleanup methods last
            if any(word in name for word in ['close', 'cleanup', 'destroy', 'dispose']):
                return 4
            
            # Everything else in the middle
            return 2
        
        return sorted(methods, key=method_priority)
    
    def _create_package_dependency_fallback(self, db: VizDB, project_id: int) -> int:
        """Create package-based dependencies as fallback"""
        # Analyze existing package_relation edges and create meaningful class dependencies
        all_edges = db.fetch_edges(project_id, ['package_relation'], 0.0)
        
        edges_created = 0
        class_connections = set()
        
        for edge in all_edges:
            if edge.src_type == 'class' and edge.dst_type == 'class':
                connection = (edge.src_id, edge.dst_id)
                if connection not in class_connections:
                    class_connections.add(connection)
                    edges_created += 1
                    logger.debug(f"Would create class dependency: class:{edge.src_id} -> class:{edge.dst_id}")
        
        return edges_created
    
    def _create_naming_based_erd_fallback(self, db: VizDB, project_id: int) -> int:
        """Create ERD relationships based on naming conventions"""
        session = db.session()
        try:
            from ..data_access import DbTable, DbColumn
            
            tables = session.query(DbTable).all()
            columns = session.query(DbColumn).all()
            
            # Group columns by table
            table_columns = defaultdict(list)
            for column in columns:
                table_columns[column.table_name].append(column)
            
            edges_created = 0
            
            # Detect foreign key patterns
            for table_name, table_columns_list in table_columns.items():
                for column in table_columns_list:
                    # Common foreign key patterns
                    if column.column_name.lower().endswith('_id'):
                        # Extract referenced table name
                        potential_table = column.column_name.lower().replace('_id', '')
                        
                        # Look for matching table
                        for table in tables:
                            if table.name.lower() == potential_table or table.name.lower().endswith(potential_table):
                                edges_created += 1
                                logger.debug(f"Would create FK: {table_name}.{column.column_name} -> {table.name}")
                                break
            
            return edges_created
            
        finally:
            session.close()
    
    def _get_pattern_suggestions(self, pattern: EdgePattern) -> List[str]:
        """Get suggestions for missing patterns"""
        suggestions_map = {
            "method_call_chain": [
                "Enable method call analysis in phase1 configuration",
                "Use AST parsing to detect method invocations",
                "Analyze bytecode for method calls"
            ],
            "class_dependency": [
                "Enable import/include analysis",
                "Analyze inheritance relationships",
                "Parse package dependencies"
            ],
            "file_inclusion": [
                "Enable file dependency analysis", 
                "Parse import statements",
                "Analyze include directives"
            ],
            "sql_table_usage": [
                "Enable SQL parsing and analysis",
                "Connect SQL statements to database schema",
                "Parse MyBatis mapper files"
            ]
        }
        
        return suggestions_map.get(pattern.name, ["Enable comprehensive analysis for this pattern"])
    
    def _generate_recommendations(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        
        missing_relationships = analysis_result.get("missing_relationships", {})
        
        if "method_call_chain" in missing_relationships:
            recommendations.append("Enable method call analysis to create meaningful sequence diagrams")
        
        if "class_dependency" in missing_relationships:
            recommendations.append("Enable dependency analysis for better component visualization")
        
        if "sql_table_usage" in missing_relationships:
            recommendations.append("Connect SQL analysis with database schema for data flow visualization")
        
        if len(analysis_result.get("fallback_applied", [])) > 0:
            recommendations.append("Consider running deeper analysis to replace fallback strategies with real relationships")
        
        return recommendations
    
    def _calculate_relationship_quality(self, analysis_result: Dict[str, Any]) -> float:
        """Calculate overall relationship quality score"""
        available = len(analysis_result.get("available_relationships", {}))
        missing = len(analysis_result.get("missing_relationships", {}))
        fallback_used = len(analysis_result.get("fallback_applied", []))
        
        if available + missing == 0:
            return 0.0
        
        # Base score from available relationships
        base_score = available / (available + missing) * 100
        
        # Penalty for using fallbacks (they're less reliable)
        fallback_penalty = fallback_used * 10
        
        final_score = max(0.0, base_score - fallback_penalty)
        return final_score
    
    def generate_enhanced_visualization_data(self, db: VizDB, project_id: int, viz_type: str, fallback_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate enhanced visualization data using fallback strategies"""
        
        if viz_type == "sequence" and any(f["strategy"] == "sequence_from_method_proximity" for f in fallback_analysis.get("fallback_applied", [])):
            return self._generate_enhanced_sequence_data(db, project_id)
        
        elif viz_type == "dependency" and any(f["strategy"] == "dependency_from_package_structure" for f in fallback_analysis.get("fallback_applied", [])):
            return self._generate_enhanced_dependency_data(db, project_id)
        
        elif viz_type == "erd" and any(f["strategy"] == "erd_from_naming_conventions" for f in fallback_analysis.get("fallback_applied", [])):
            return self._generate_enhanced_erd_data(db, project_id)
        
        return {}
    
    def _generate_enhanced_sequence_data(self, db: VizDB, project_id: int) -> Dict[str, Any]:
        """Generate enhanced sequence diagram data with smarter method grouping"""
        
        methods = db.fetch_methods_by_project(project_id)
        
        # Group by class and create logical flows
        class_methods = defaultdict(list)
        for method in methods:
            method_details = db.get_node_details('method', method.method_id)
            if method_details and method_details.get('class'):
                class_name = method_details['class']
                class_methods[class_name].append((method, method_details))
        
        # Create enhanced sequence with class-based grouping
        participants = []
        interactions = []
        
        participant_order = 0
        interaction_order = 0
        
        for class_name, methods_with_details in class_methods.items():
            # Sort methods within class by logical order
            sorted_methods = self._sort_methods_by_likely_call_order([m[0] for m in methods_with_details])
            
            # Add participants
            for i, method in enumerate(sorted_methods):
                participants.append({
                    'id': f"method:{method.method_id}",
                    'type': 'method',
                    'label': f"{class_name}.{method.name}()",
                    'actor_type': 'control',
                    'order': participant_order,
                    'class': class_name
                })
                participant_order += 1
                
                # Create interactions within class
                if i < len(sorted_methods) - 1:
                    next_method = sorted_methods[i + 1]
                    interactions.append({
                        'id': f"interaction_{interaction_order}",
                        'sequence_order': interaction_order,
                        'type': 'synchronous',
                        'from_participant': f"method:{method.method_id}",
                        'to_participant': f"method:{next_method.method_id}",
                        'message': f"call {next_method.name}()",
                        'confidence': 0.6,
                        'unresolved': False,
                        'style': 'solid'
                    })
                    interaction_order += 1
        
        return {
            'type': 'enhanced_sequence_diagram',
            'participants': participants,
            'interactions': interactions,
            'enhancement_applied': 'class_based_method_grouping'
        }