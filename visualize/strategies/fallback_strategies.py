"""
Intelligent Fallback Visualization Strategies

Provides smart fallback mechanisms when primary visualization data is missing or insufficient.
Ensures meaningful visualizations are always generated, preventing silent failures.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
from dataclasses import dataclass
import json

from visualize.data_access import DatabaseManager


@dataclass
class FallbackStrategy:
    """Represents a fallback strategy for visualization generation"""
    name: str
    description: str
    confidence: float  # 0.0 to 1.0
    data_requirements: List[str]
    generates: str  # Type of visualization data it generates
    priority: int  # Lower number = higher priority


@dataclass
class FallbackResult:
    """Result of applying a fallback strategy"""
    strategy_used: str
    success: bool
    confidence: float
    generated_data: Dict[str, Any]
    warnings: List[str]
    recommendations: List[str]


class VisualizationFallbackEngine:
    """Engine for applying intelligent fallback strategies"""
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.db_manager = DatabaseManager(project_name)
        self.logger = logging.getLogger(__name__)
        
        # Register available fallback strategies
        self.strategies = self._register_strategies()
    
    def _register_strategies(self) -> Dict[str, List[FallbackStrategy]]:
        """Register all available fallback strategies"""
        strategies = {
            'sequence_diagram': [
                FallbackStrategy(
                    name="inferred_method_sequence",
                    description="Create sequential flow from available methods when call data is missing",
                    confidence=0.6,
                    data_requirements=["methods", "classes"],
                    generates="method_interactions",
                    priority=1
                ),
                FallbackStrategy(
                    name="package_based_sequence",
                    description="Generate sequence based on package relationships and file structure",
                    confidence=0.4,
                    data_requirements=["package_relations", "files"],
                    generates="component_interactions",
                    priority=2
                ),
                FallbackStrategy(
                    name="class_hierarchy_sequence",
                    description="Create sequence from class inheritance and composition relationships",
                    confidence=0.5,
                    data_requirements=["classes", "inheritance"],
                    generates="class_interactions",
                    priority=3
                )
            ],
            'dependency_graph': [
                FallbackStrategy(
                    name="package_relationship_graph",
                    description="Use package relationships when file imports are missing",
                    confidence=0.7,
                    data_requirements=["package_relations"],
                    generates="package_dependencies",
                    priority=1
                ),
                FallbackStrategy(
                    name="directory_structure_graph",
                    description="Infer dependencies from directory and file structure patterns",
                    confidence=0.5,
                    data_requirements=["files", "directories"],
                    generates="structural_dependencies",
                    priority=2
                ),
                FallbackStrategy(
                    name="class_usage_graph",
                    description="Generate dependencies based on class and method usage patterns",
                    confidence=0.6,
                    data_requirements=["classes", "methods", "usage_patterns"],
                    generates="usage_dependencies",
                    priority=3
                )
            ],
            'class_diagram': [
                FallbackStrategy(
                    name="method_grouping_classes",
                    description="Group methods into logical classes when class structure is unclear",
                    confidence=0.5,
                    data_requirements=["methods", "files"],
                    generates="inferred_classes",
                    priority=1
                ),
                FallbackStrategy(
                    name="file_based_components",
                    description="Treat files as components when class information is missing",
                    confidence=0.4,
                    data_requirements=["files", "functions"],
                    generates="file_components",
                    priority=2
                )
            ],
            'erd': [
                FallbackStrategy(
                    name="table_naming_inference",
                    description="Infer relationships from table and column naming patterns",
                    confidence=0.6,
                    data_requirements=["tables", "columns"],
                    generates="inferred_relationships",
                    priority=1
                ),
                FallbackStrategy(
                    name="query_pattern_relationships",
                    description="Extract relationships from SQL query patterns",
                    confidence=0.7,
                    data_requirements=["sql_queries", "tables"],
                    generates="query_relationships",
                    priority=2
                )
            ]
        }
        
        return strategies
    
    def get_fallback_for_visualization(self, viz_type: str, available_data: Dict[str, Any], 
                                     primary_failure_reason: str) -> Optional[FallbackResult]:
        """Get the best fallback strategy for a visualization type"""
        self.logger.info(f"Finding fallback for {viz_type}, reason: {primary_failure_reason}")
        
        if viz_type not in self.strategies:
            self.logger.warning(f"No fallback strategies available for visualization type: {viz_type}")
            return None
        
        # Evaluate each strategy
        viable_strategies = []
        for strategy in self.strategies[viz_type]:
            viability = self._evaluate_strategy_viability(strategy, available_data)
            if viability > 0:
                viable_strategies.append((strategy, viability))
        
        if not viable_strategies:
            self.logger.warning(f"No viable fallback strategies found for {viz_type}")
            return None
        
        # Sort by priority and viability
        viable_strategies.sort(key=lambda x: (x[0].priority, -x[1]))
        best_strategy, viability = viable_strategies[0]
        
        self.logger.info(f"Applying fallback strategy: {best_strategy.name} (viability: {viability:.2f})")
        
        # Apply the strategy
        return self._apply_strategy(best_strategy, available_data, viz_type)
    
    def _evaluate_strategy_viability(self, strategy: FallbackStrategy, available_data: Dict[str, Any]) -> float:
        """Evaluate how viable a strategy is given available data"""
        if not strategy.data_requirements:
            return 0.5  # Baseline viability
        
        available_requirements = 0
        total_requirements = len(strategy.data_requirements)
        
        for requirement in strategy.data_requirements:
            if self._check_data_availability(requirement, available_data):
                available_requirements += 1
        
        requirement_ratio = available_requirements / total_requirements
        return requirement_ratio * strategy.confidence
    
    def _check_data_availability(self, requirement: str, available_data: Dict[str, Any]) -> bool:
        """Check if a data requirement is satisfied"""
        try:
            with self.db_manager.get_session() as session:
                if requirement == "methods":
                    count = session.execute("SELECT COUNT(*) FROM nodes WHERE type = 'method'").scalar()
                    return count > 0
                elif requirement == "classes":
                    count = session.execute("SELECT COUNT(*) FROM nodes WHERE type = 'class'").scalar()
                    return count > 0
                elif requirement == "files":
                    count = session.execute("SELECT COUNT(*) FROM nodes WHERE type = 'file'").scalar()
                    return count > 0
                elif requirement == "package_relations":
                    count = session.execute("SELECT COUNT(*) FROM edges WHERE kind = 'package_relation'").scalar()
                    return count > 0
                elif requirement == "inheritance":
                    count = session.execute("SELECT COUNT(*) FROM edges WHERE kind IN ('extends', 'implements')").scalar()
                    return count > 0
                elif requirement == "tables":
                    count = session.execute("SELECT COUNT(*) FROM nodes WHERE type = 'table'").scalar()
                    return count > 0
                elif requirement == "columns":
                    count = session.execute("SELECT COUNT(*) FROM nodes WHERE type = 'column'").scalar()
                    return count > 0
                elif requirement == "sql_queries":
                    # Check if we have any SQL-related edges or nodes
                    count = session.execute("SELECT COUNT(*) FROM edges WHERE kind LIKE '%sql%' OR kind LIKE '%query%'").scalar()
                    return count > 0
                else:
                    return False  # Unknown requirement
        except Exception as e:
            self.logger.error(f"Error checking data availability for {requirement}: {e}")
            return False
    
    def _apply_strategy(self, strategy: FallbackStrategy, available_data: Dict[str, Any], viz_type: str) -> FallbackResult:
        """Apply a specific fallback strategy"""
        try:
            if strategy.name == "inferred_method_sequence":
                return self._apply_inferred_method_sequence(strategy)
            elif strategy.name == "package_based_sequence":
                return self._apply_package_based_sequence(strategy)
            elif strategy.name == "class_hierarchy_sequence":
                return self._apply_class_hierarchy_sequence(strategy)
            elif strategy.name == "package_relationship_graph":
                return self._apply_package_relationship_graph(strategy)
            elif strategy.name == "directory_structure_graph":
                return self._apply_directory_structure_graph(strategy)
            elif strategy.name == "class_usage_graph":
                return self._apply_class_usage_graph(strategy)
            elif strategy.name == "method_grouping_classes":
                return self._apply_method_grouping_classes(strategy)
            elif strategy.name == "file_based_components":
                return self._apply_file_based_components(strategy)
            elif strategy.name == "table_naming_inference":
                return self._apply_table_naming_inference(strategy)
            elif strategy.name == "query_pattern_relationships":
                return self._apply_query_pattern_relationships(strategy)
            else:
                return FallbackResult(
                    strategy_used=strategy.name,
                    success=False,
                    confidence=0.0,
                    generated_data={},
                    warnings=[f"Strategy {strategy.name} not implemented"],
                    recommendations=[]
                )
        except Exception as e:
            self.logger.error(f"Failed to apply strategy {strategy.name}: {e}")
            return FallbackResult(
                strategy_used=strategy.name,
                success=False,
                confidence=0.0,
                generated_data={},
                warnings=[f"Strategy application failed: {str(e)}"],
                recommendations=[]
            )
    
    def _apply_inferred_method_sequence(self, strategy: FallbackStrategy) -> FallbackResult:
        """Apply inferred method sequence fallback strategy"""
        generated_data = {}
        warnings = []
        
        try:
            with self.db_manager.get_session() as session:
                # Get methods grouped by class/file
                methods = session.execute("""
                    SELECT n.id, n.name, n.parent_id, p.name as parent_name, p.type as parent_type
                    FROM nodes n
                    LEFT JOIN nodes p ON n.parent_id = p.id
                    WHERE n.type = 'method'
                    ORDER BY p.name, n.name
                    LIMIT 50
                """).fetchall()
                
                if not methods:
                    return FallbackResult(
                        strategy_used=strategy.name,
                        success=False,
                        confidence=0.0,
                        generated_data={},
                        warnings=["No methods found for sequence inference"],
                        recommendations=["Check method extraction in code analysis phase"]
                    )
                
                # Generate artificial sequence based on method ordering
                participants = []
                interactions = []
                
                # Group methods by parent (class/file)
                parent_methods = defaultdict(list)
                for method in methods:
                    parent_key = f"{method.parent_name or 'Global'}:{method.parent_type or 'file'}"
                    parent_methods[parent_key].append({
                        'id': method.id,
                        'name': method.name,
                        'parent_id': method.parent_id
                    })
                
                # Create participants
                participant_id = 0
                method_to_participant = {}
                
                for parent_key, parent_method_list in parent_methods.items():
                    participant_name = parent_key.split(':')[0]
                    participants.append({
                        'id': f"participant_{participant_id}",
                        'name': participant_name,
                        'type': 'component'
                    })
                    
                    # Map methods to this participant
                    for method in parent_method_list:
                        method_to_participant[method['id']] = f"participant_{participant_id}"
                    
                    participant_id += 1
                
                # Create inferred interactions
                interaction_id = 0
                method_list = list(methods)
                
                for i in range(min(len(method_list) - 1, 20)):  # Limit to 20 interactions
                    current_method = method_list[i]
                    next_method = method_list[i + 1]
                    
                    source_participant = method_to_participant.get(current_method.id, f"participant_0")
                    target_participant = method_to_participant.get(next_method.id, f"participant_0")
                    
                    if source_participant != target_participant:  # Only create cross-component interactions
                        interactions.append({
                            'id': f"interaction_{interaction_id}",
                            'source': source_participant,
                            'target': target_participant,
                            'message': f"{current_method.name} -> {next_method.name}",
                            'type': 'inferred_call',
                            'confidence': strategy.confidence
                        })
                        interaction_id += 1
                
                generated_data = {
                    'type': 'sequence_diagram',
                    'participants': participants,
                    'interactions': interactions,
                    'metadata': {
                        'generation_method': 'inferred_method_sequence',
                        'confidence': strategy.confidence,
                        'total_methods_analyzed': len(methods)
                    }
                }
                
                warnings.append(f"Generated {len(interactions)} inferred interactions from {len(methods)} methods")
                warnings.append("Interactions are artificially created - not based on actual call relationships")
                
                return FallbackResult(
                    strategy_used=strategy.name,
                    success=True,
                    confidence=strategy.confidence,
                    generated_data=generated_data,
                    warnings=warnings,
                    recommendations=[
                        "Improve method call extraction to get real call relationships",
                        "Use this fallback visualization to understand component structure"
                    ]
                )
        
        except Exception as e:
            return FallbackResult(
                strategy_used=strategy.name,
                success=False,
                confidence=0.0,
                generated_data={},
                warnings=[f"Strategy failed: {str(e)}"],
                recommendations=[]
            )
    
    def _apply_package_based_sequence(self, strategy: FallbackStrategy) -> FallbackResult:
        """Apply package-based sequence fallback strategy"""
        try:
            with self.db_manager.get_session() as session:
                # Get package relationships
                package_edges = session.execute("""
                    SELECT e.source_node_id, e.target_node_id, 
                           s.name as source_name, t.name as target_name
                    FROM edges e
                    JOIN nodes s ON e.source_node_id = s.id
                    JOIN nodes t ON e.target_node_id = t.id
                    WHERE e.kind = 'package_relation'
                    LIMIT 30
                """).fetchall()
                
                if not package_edges:
                    return FallbackResult(
                        strategy_used=strategy.name,
                        success=False,
                        confidence=0.0,
                        generated_data={},
                        warnings=["No package relationships found"],
                        recommendations=["Check package analysis in code extraction"]
                    )
                
                # Convert package relationships to sequence diagram format
                participants = []
                interactions = []
                seen_participants = set()
                
                for edge in package_edges:
                    # Add participants
                    for node_name, node_id in [(edge.source_name, edge.source_node_id), 
                                               (edge.target_name, edge.target_node_id)]:
                        if node_id not in seen_participants:
                            participants.append({
                                'id': f"pkg_{node_id}",
                                'name': node_name or f"Component_{node_id}",
                                'type': 'package'
                            })
                            seen_participants.add(node_id)
                    
                    # Add interaction
                    interactions.append({
                        'id': f"pkg_interaction_{len(interactions)}",
                        'source': f"pkg_{edge.source_node_id}",
                        'target': f"pkg_{edge.target_node_id}",
                        'message': "package_dependency",
                        'type': 'package_relation',
                        'confidence': strategy.confidence
                    })
                
                generated_data = {
                    'type': 'sequence_diagram',
                    'participants': participants,
                    'interactions': interactions,
                    'metadata': {
                        'generation_method': 'package_based_sequence',
                        'confidence': strategy.confidence,
                        'package_relationships_used': len(package_edges)
                    }
                }
                
                return FallbackResult(
                    strategy_used=strategy.name,
                    success=True,
                    confidence=strategy.confidence,
                    generated_data=generated_data,
                    warnings=["Sequence generated from package relationships, not method calls"],
                    recommendations=["This shows package-level interactions, not detailed method sequences"]
                )
        
        except Exception as e:
            return FallbackResult(
                strategy_used=strategy.name,
                success=False,
                confidence=0.0,
                generated_data={},
                warnings=[f"Package-based sequence failed: {str(e)}"],
                recommendations=[]
            )
    
    def _apply_package_relationship_graph(self, strategy: FallbackStrategy) -> FallbackResult:
        """Apply package relationship graph fallback strategy"""
        try:
            with self.db_manager.get_session() as session:
                # Get package relationships for dependency graph
                package_edges = session.execute("""
                    SELECT e.source_node_id, e.target_node_id, e.kind,
                           s.name as source_name, t.name as target_name
                    FROM edges e
                    JOIN nodes s ON e.source_node_id = s.id
                    JOIN nodes t ON e.target_node_id = t.id
                    WHERE e.kind = 'package_relation'
                    LIMIT 50
                """).fetchall()
                
                if not package_edges:
                    return FallbackResult(
                        strategy_used=strategy.name,
                        success=False,
                        confidence=0.0,
                        generated_data={},
                        warnings=["No package relationships available for dependency graph"],
                        recommendations=[]
                    )
                
                # Build dependency graph from package relationships
                nodes = []
                edges = []
                seen_nodes = set()
                
                for edge in package_edges:
                    # Add nodes
                    for node_name, node_id in [(edge.source_name, edge.source_node_id), 
                                               (edge.target_name, edge.target_node_id)]:
                        if node_id not in seen_nodes:
                            nodes.append({
                                'id': f"pkg_{node_id}",
                                'name': node_name or f"Package_{node_id}",
                                'type': 'package',
                                'size': 10  # Default size
                            })
                            seen_nodes.add(node_id)
                    
                    # Add edge
                    edges.append({
                        'id': f"pkg_dep_{len(edges)}",
                        'source': f"pkg_{edge.source_node_id}",
                        'target': f"pkg_{edge.target_node_id}",
                        'type': 'package_dependency',
                        'strength': strategy.confidence
                    })
                
                generated_data = {
                    'type': 'dependency_graph',
                    'nodes': nodes,
                    'edges': edges,
                    'metadata': {
                        'generation_method': 'package_relationships',
                        'confidence': strategy.confidence,
                        'relationships_used': len(package_edges)
                    }
                }
                
                return FallbackResult(
                    strategy_used=strategy.name,
                    success=True,
                    confidence=strategy.confidence,
                    generated_data=generated_data,
                    warnings=["Dependency graph based on package relationships, not file imports"],
                    recommendations=["Shows high-level package dependencies"]
                )
        
        except Exception as e:
            return FallbackResult(
                strategy_used=strategy.name,
                success=False,
                confidence=0.0,
                generated_data={},
                warnings=[f"Package relationship graph failed: {str(e)}"],
                recommendations=[]
            )
    
    # Placeholder methods for other strategies
    def _apply_class_hierarchy_sequence(self, strategy: FallbackStrategy) -> FallbackResult:
        """Apply class hierarchy sequence fallback strategy"""
        return self._create_placeholder_result(strategy, "Class hierarchy sequence not fully implemented")
    
    def _apply_directory_structure_graph(self, strategy: FallbackStrategy) -> FallbackResult:
        """Apply directory structure graph fallback strategy"""
        return self._create_placeholder_result(strategy, "Directory structure graph not fully implemented")
    
    def _apply_class_usage_graph(self, strategy: FallbackStrategy) -> FallbackResult:
        """Apply class usage graph fallback strategy"""
        return self._create_placeholder_result(strategy, "Class usage graph not fully implemented")
    
    def _apply_method_grouping_classes(self, strategy: FallbackStrategy) -> FallbackResult:
        """Apply method grouping classes fallback strategy"""
        return self._create_placeholder_result(strategy, "Method grouping classes not fully implemented")
    
    def _apply_file_based_components(self, strategy: FallbackStrategy) -> FallbackResult:
        """Apply file-based components fallback strategy"""
        return self._create_placeholder_result(strategy, "File-based components not fully implemented")
    
    def _apply_table_naming_inference(self, strategy: FallbackStrategy) -> FallbackResult:
        """Apply table naming inference fallback strategy"""
        return self._create_placeholder_result(strategy, "Table naming inference not fully implemented")
    
    def _apply_query_pattern_relationships(self, strategy: FallbackStrategy) -> FallbackResult:
        """Apply query pattern relationships fallback strategy"""
        return self._create_placeholder_result(strategy, "Query pattern relationships not fully implemented")
    
    def _create_placeholder_result(self, strategy: FallbackStrategy, message: str) -> FallbackResult:
        """Create a placeholder result for unimplemented strategies"""
        return FallbackResult(
            strategy_used=strategy.name,
            success=False,
            confidence=0.0,
            generated_data={},
            warnings=[message],
            recommendations=[f"Implement {strategy.name} strategy for better fallback coverage"]
        )
    
    def get_available_strategies(self, viz_type: str) -> List[FallbackStrategy]:
        """Get all available strategies for a visualization type"""
        return self.strategies.get(viz_type, [])
    
    def test_all_strategies(self) -> Dict[str, Any]:
        """Test all strategies to see which ones are viable"""
        test_results = {}
        
        for viz_type, strategies in self.strategies.items():
            test_results[viz_type] = []
            
            for strategy in strategies:
                viability = self._evaluate_strategy_viability(strategy, {})
                test_results[viz_type].append({
                    'name': strategy.name,
                    'viability': viability,
                    'confidence': strategy.confidence,
                    'priority': strategy.priority,
                    'description': strategy.description
                })
        
        return test_results


def main():
    """CLI entry point for testing fallback strategies"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test fallback visualization strategies")
    parser.add_argument("--project-name", required=True, help="Name of the project to test")
    parser.add_argument("--viz-type", help="Specific visualization type to test")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    engine = VisualizationFallbackEngine(args.project_name)
    
    if args.viz_type:
        print(f"\nTesting fallback strategies for {args.viz_type}:")
        strategies = engine.get_available_strategies(args.viz_type)
        for strategy in strategies:
            viability = engine._evaluate_strategy_viability(strategy, {})
            print(f"  - {strategy.name}: viability {viability:.2f}, confidence {strategy.confidence:.2f}")
            print(f"    {strategy.description}")
    else:
        print(f"\nTesting all fallback strategies for project: {args.project_name}")
        results = engine.test_all_strategies()
        
        for viz_type, strategies in results.items():
            print(f"\n{viz_type.upper()}:")
            for strategy in strategies:
                status = "✅" if strategy['viability'] > 0.5 else "⚠️" if strategy['viability'] > 0.3 else "❌"
                print(f"  {status} {strategy['name']}: viability {strategy['viability']:.2f}")


if __name__ == "__main__":
    main()