"""
Data Completeness Metrics and Reporting System

Provides comprehensive metrics on data completeness, analysis coverage,
and relationship extraction quality across all project components.
"""

import json
import logging
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from collections import defaultdict, Counter
import sqlite3

from visualize.data_access import DatabaseManager


@dataclass
class CompletenessMetric:
    """Represents a completeness metric"""
    category: str
    metric_name: str
    value: float  # 0.0 to 1.0
    description: str
    expected_range: Tuple[float, float]
    status: str  # 'excellent', 'good', 'warning', 'critical'
    recommendations: List[str]


@dataclass
class ComponentCompleteness:
    """Completeness assessment for a specific component"""
    component_name: str
    overall_score: float
    metrics: List[CompletenessMetric]
    data_points: Dict[str, Any]
    issues: List[str]


class CompletenessReporter:
    """Generate comprehensive completeness metrics and reports"""
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.db_manager = DatabaseManager(project_name)
        self.logger = logging.getLogger(__name__)
        
        # Define metric thresholds
        self.thresholds = {
            'excellent': 0.9,
            'good': 0.7,
            'warning': 0.5,
            'critical': 0.3
        }
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate a comprehensive completeness report"""
        self.logger.info(f"Generating completeness report for project: {self.project_name}")
        
        report = {
            'project_name': self.project_name,
            'timestamp': datetime.now().isoformat(),
            'overall_completeness': 0.0,
            'component_assessments': {},
            'summary_metrics': {},
            'data_distribution': {},
            'quality_indicators': {},
            'recommendations': []
        }
        
        try:
            # Assess each component
            components = [
                'code_structure',
                'method_relationships',
                'file_dependencies', 
                'database_schema',
                'visualization_readiness'
            ]
            
            component_scores = []
            
            for component in components:
                assessment = self._assess_component_completeness(component)
                report['component_assessments'][component] = asdict(assessment)
                component_scores.append(assessment.overall_score)
            
            # Calculate overall completeness
            report['overall_completeness'] = sum(component_scores) / len(component_scores)
            
            # Generate summary metrics
            report['summary_metrics'] = self._generate_summary_metrics()
            
            # Analyze data distribution
            report['data_distribution'] = self._analyze_data_distribution()
            
            # Generate quality indicators
            report['quality_indicators'] = self._generate_quality_indicators()
            
            # Generate recommendations
            report['recommendations'] = self._generate_completeness_recommendations(
                report['component_assessments'], report['overall_completeness']
            )
            
            self.logger.info(f"Completeness report generated. Overall score: {report['overall_completeness']:.1%}")
            
        except Exception as e:
            self.logger.error(f"Failed to generate completeness report: {e}")
            report['error'] = str(e)
        
        return report
    
    def _assess_component_completeness(self, component: str) -> ComponentCompleteness:
        """Assess completeness for a specific component"""
        if component == 'code_structure':
            return self._assess_code_structure_completeness()
        elif component == 'method_relationships':
            return self._assess_method_relationships_completeness()
        elif component == 'file_dependencies':
            return self._assess_file_dependencies_completeness()
        elif component == 'database_schema':
            return self._assess_database_schema_completeness()
        elif component == 'visualization_readiness':
            return self._assess_visualization_readiness()
        else:
            return ComponentCompleteness(
                component_name=component,
                overall_score=0.0,
                metrics=[],
                data_points={},
                issues=[f"Unknown component: {component}"]
            )
    
    def _assess_code_structure_completeness(self) -> ComponentCompleteness:
        """Assess code structure analysis completeness"""
        metrics = []
        data_points = {}
        issues = []
        
        try:
            with self.db_manager.get_session() as session:
                # Get basic counts
                file_count = session.execute("SELECT COUNT(*) FROM nodes WHERE type = 'file'").scalar()
                class_count = session.execute("SELECT COUNT(*) FROM nodes WHERE type = 'class'").scalar()
                method_count = session.execute("SELECT COUNT(*) FROM nodes WHERE type = 'method'").scalar()
                function_count = session.execute("SELECT COUNT(*) FROM nodes WHERE type = 'function'").scalar()
                
                data_points.update({
                    'file_count': file_count,
                    'class_count': class_count,
                    'method_count': method_count,
                    'function_count': function_count
                })
                
                # File coverage metric
                files_with_content = session.execute("""
                    SELECT COUNT(DISTINCT parent_id) FROM nodes 
                    WHERE parent_id IS NOT NULL AND type IN ('class', 'method', 'function')
                """).scalar()
                
                file_coverage = files_with_content / max(file_count, 1)
                metrics.append(CompletenessMetric(
                    category='code_structure',
                    metric_name='file_analysis_coverage',
                    value=file_coverage,
                    description=f"{files_with_content}/{file_count} files have extracted code elements",
                    expected_range=(0.7, 1.0),
                    status=self._get_metric_status(file_coverage),
                    recommendations=self._get_file_coverage_recommendations(file_coverage)
                ))
                
                # Class-method relationship completeness
                if class_count > 0:
                    classes_with_methods = session.execute("""
                        SELECT COUNT(DISTINCT parent_id) FROM nodes 
                        WHERE type = 'method' AND parent_id IS NOT NULL
                    """).scalar()
                    
                    class_method_coverage = classes_with_methods / class_count
                    metrics.append(CompletenessMetric(
                        category='code_structure',
                        metric_name='class_method_coverage',
                        value=class_method_coverage,
                        description=f"{classes_with_methods}/{class_count} classes have extracted methods",
                        expected_range=(0.6, 1.0),
                        status=self._get_metric_status(class_method_coverage, {'warning': 0.3, 'critical': 0.1}),
                        recommendations=self._get_class_method_recommendations(class_method_coverage)
                    ))
                
                # Method complexity distribution
                method_complexity = self._analyze_method_complexity_distribution(session)
                if method_complexity:
                    metrics.append(CompletenessMetric(
                        category='code_structure',
                        metric_name='method_complexity_distribution',
                        value=method_complexity.get('distribution_quality', 0.5),
                        description=f"Method complexity analysis: {method_complexity.get('summary', 'Available')}",
                        expected_range=(0.5, 1.0),
                        status=self._get_metric_status(method_complexity.get('distribution_quality', 0.5)),
                        recommendations=['Analyze method complexity for refactoring opportunities']
                    ))
                
                # Calculate overall score
                overall_score = sum(m.value for m in metrics) / max(len(metrics), 1)
                
        except Exception as e:
            self.logger.error(f"Code structure assessment failed: {e}")
            issues.append(f"Assessment failed: {e}")
            overall_score = 0.0
        
        return ComponentCompleteness(
            component_name='code_structure',
            overall_score=overall_score,
            metrics=metrics,
            data_points=data_points,
            issues=issues
        )
    
    def _assess_method_relationships_completeness(self) -> ComponentCompleteness:
        """Assess method relationship extraction completeness"""
        metrics = []
        data_points = {}
        issues = []
        
        try:
            with self.db_manager.get_session() as session:
                # Get method relationship counts
                total_methods = session.execute("SELECT COUNT(*) FROM nodes WHERE type = 'method'").scalar()
                
                call_edges = session.execute("""
                    SELECT COUNT(*) FROM edges WHERE kind = 'call'
                """).scalar()
                
                unresolved_calls = session.execute("""
                    SELECT COUNT(*) FROM edges WHERE kind = 'call_unresolved'
                """).scalar()
                
                total_calls = call_edges + unresolved_calls
                
                data_points.update({
                    'total_methods': total_methods,
                    'resolved_calls': call_edges,
                    'unresolved_calls': unresolved_calls,
                    'total_calls': total_calls
                })
                
                # Call resolution rate
                if total_calls > 0:
                    resolution_rate = call_edges / total_calls
                    metrics.append(CompletenessMetric(
                        category='method_relationships',
                        metric_name='call_resolution_rate',
                        value=resolution_rate,
                        description=f"{call_edges}/{total_calls} method calls are resolved",
                        expected_range=(0.6, 1.0),
                        status=self._get_metric_status(resolution_rate, {'warning': 0.4, 'critical': 0.2}),
                        recommendations=self._get_call_resolution_recommendations(resolution_rate)
                    ))
                
                # Method connectivity
                if total_methods > 0:
                    methods_with_calls = session.execute("""
                        SELECT COUNT(DISTINCT source_node_id) FROM edges 
                        WHERE kind IN ('call', 'call_unresolved') 
                        AND source_type = 'method'
                    """).scalar()
                    
                    method_connectivity = methods_with_calls / total_methods
                    metrics.append(CompletenessMetric(
                        category='method_relationships',
                        metric_name='method_connectivity',
                        value=method_connectivity,
                        description=f"{methods_with_calls}/{total_methods} methods have outgoing calls",
                        expected_range=(0.3, 0.8),
                        status=self._get_metric_status(method_connectivity, {'warning': 0.2, 'critical': 0.1}),
                        recommendations=['Methods should have meaningful call relationships for sequence diagrams']
                    ))
                
                # Call chain depth analysis
                chain_depth = self._analyze_call_chain_depth(session)
                if chain_depth:
                    metrics.append(CompletenessMetric(
                        category='method_relationships',
                        metric_name='call_chain_depth',
                        value=min(chain_depth.get('average_depth', 0) / 5.0, 1.0),  # Normalize to max depth of 5
                        description=f"Average call chain depth: {chain_depth.get('average_depth', 0):.1f}",
                        expected_range=(0.4, 1.0),
                        status=self._get_metric_status(min(chain_depth.get('average_depth', 0) / 5.0, 1.0)),
                        recommendations=['Good call chain depth enables meaningful sequence analysis']
                    ))
                
                overall_score = sum(m.value for m in metrics) / max(len(metrics), 1)
                
        except Exception as e:
            self.logger.error(f"Method relationships assessment failed: {e}")
            issues.append(f"Assessment failed: {e}")
            overall_score = 0.0
        
        return ComponentCompleteness(
            component_name='method_relationships',
            overall_score=overall_score,
            metrics=metrics,
            data_points=data_points,
            issues=issues
        )
    
    def _assess_file_dependencies_completeness(self) -> ComponentCompleteness:
        """Assess file dependency extraction completeness"""
        metrics = []
        data_points = {}
        issues = []
        
        try:
            with self.db_manager.get_session() as session:
                file_count = session.execute("SELECT COUNT(*) FROM nodes WHERE type = 'file'").scalar()
                
                # Import relationships
                import_edges = session.execute("""
                    SELECT COUNT(*) FROM edges 
                    WHERE kind IN ('import', 'include', 'dependency')
                """).scalar()
                
                # Package relationships
                package_edges = session.execute("""
                    SELECT COUNT(*) FROM edges WHERE kind = 'package_relation'
                """).scalar()
                
                total_file_relationships = import_edges + package_edges
                
                data_points.update({
                    'file_count': file_count,
                    'import_edges': import_edges,
                    'package_edges': package_edges,
                    'total_file_relationships': total_file_relationships
                })
                
                # File connectivity
                if file_count > 1:
                    connectivity_ratio = total_file_relationships / (file_count * (file_count - 1) / 2)
                    connectivity_ratio = min(connectivity_ratio, 1.0)  # Cap at 100%
                    
                    metrics.append(CompletenessMetric(
                        category='file_dependencies',
                        metric_name='file_connectivity',
                        value=connectivity_ratio,
                        description=f"{total_file_relationships} relationships among {file_count} files",
                        expected_range=(0.1, 0.5),
                        status=self._get_metric_status(connectivity_ratio, {
                            'excellent': 0.3, 'good': 0.2, 'warning': 0.1, 'critical': 0.05
                        }),
                        recommendations=self._get_file_connectivity_recommendations(connectivity_ratio)
                    ))
                
                # Import vs package relationship balance
                if total_file_relationships > 0:
                    import_ratio = import_edges / total_file_relationships
                    metrics.append(CompletenessMetric(
                        category='file_dependencies',
                        metric_name='import_relationship_balance',
                        value=import_ratio,
                        description=f"{import_ratio:.1%} of file relationships are explicit imports",
                        expected_range=(0.3, 1.0),
                        status=self._get_metric_status(import_ratio, {'warning': 0.2, 'critical': 0.1}),
                        recommendations=['Higher import relationship ratio indicates better dependency parsing']
                    ))
                
                overall_score = sum(m.value for m in metrics) / max(len(metrics), 1)
                
        except Exception as e:
            self.logger.error(f"File dependencies assessment failed: {e}")
            issues.append(f"Assessment failed: {e}")
            overall_score = 0.0
        
        return ComponentCompleteness(
            component_name='file_dependencies',
            overall_score=overall_score,
            metrics=metrics,
            data_points=data_points,
            issues=issues
        )
    
    def _assess_database_schema_completeness(self) -> ComponentCompleteness:
        """Assess database schema analysis completeness"""
        metrics = []
        data_points = {}
        issues = []
        
        try:
            with self.db_manager.get_session() as session:
                table_count = session.execute("SELECT COUNT(*) FROM nodes WHERE type = 'table'").scalar()
                column_count = session.execute("SELECT COUNT(*) FROM nodes WHERE type = 'column'").scalar()
                
                data_points.update({
                    'table_count': table_count,
                    'column_count': column_count
                })
                
                if table_count == 0:
                    metrics.append(CompletenessMetric(
                        category='database_schema',
                        metric_name='schema_availability',
                        value=0.0,
                        description="No database tables found",
                        expected_range=(0.0, 1.0),
                        status='not_applicable',
                        recommendations=['Database schema analysis not applicable for this project']
                    ))
                    overall_score = 0.0  # Not applicable
                else:
                    # Table-column relationship completeness
                    tables_with_columns = session.execute("""
                        SELECT COUNT(DISTINCT parent_id) FROM nodes 
                        WHERE type = 'column' AND parent_id IS NOT NULL
                    """).scalar()
                    
                    table_column_coverage = tables_with_columns / table_count
                    metrics.append(CompletenessMetric(
                        category='database_schema',
                        metric_name='table_column_coverage',
                        value=table_column_coverage,
                        description=f"{tables_with_columns}/{table_count} tables have extracted columns",
                        expected_range=(0.8, 1.0),
                        status=self._get_metric_status(table_column_coverage),
                        recommendations=['All tables should have column information for complete ERD']
                    ))
                    
                    # Foreign key relationships
                    fk_edges = session.execute("""
                        SELECT COUNT(*) FROM edges 
                        WHERE kind IN ('foreign_key', 'references')
                    """).scalar()
                    
                    # Estimate expected FK relationships (very rough heuristic)
                    expected_fks = max(table_count // 3, 1)  # Expect at least 1 FK per 3 tables
                    fk_completeness = min(fk_edges / expected_fks, 1.0)
                    
                    metrics.append(CompletenessMetric(
                        category='database_schema',
                        metric_name='foreign_key_completeness',
                        value=fk_completeness,
                        description=f"{fk_edges} foreign key relationships found",
                        expected_range=(0.5, 1.0),
                        status=self._get_metric_status(fk_completeness, {'warning': 0.3, 'critical': 0.1}),
                        recommendations=['Foreign key relationships are essential for meaningful ERD']
                    ))
                    
                    overall_score = sum(m.value for m in metrics) / len(metrics)
                
        except Exception as e:
            self.logger.error(f"Database schema assessment failed: {e}")
            issues.append(f"Assessment failed: {e}")
            overall_score = 0.0
        
        return ComponentCompleteness(
            component_name='database_schema',
            overall_score=overall_score,
            metrics=metrics,
            data_points=data_points,
            issues=issues
        )
    
    def _assess_visualization_readiness(self) -> ComponentCompleteness:
        """Assess readiness for visualization generation"""
        metrics = []
        data_points = {}
        issues = []
        
        try:
            with self.db_manager.get_session() as session:
                # Check data availability for each visualization type
                viz_readiness = {}
                
                # Sequence diagram readiness
                method_count = session.execute("SELECT COUNT(*) FROM nodes WHERE type = 'method'").scalar()
                method_calls = session.execute("""
                    SELECT COUNT(*) FROM edges 
                    WHERE kind IN ('call', 'call_unresolved') AND source_type = 'method'
                """).scalar()
                
                seq_readiness = 1.0 if (method_count > 0 and method_calls > 0) else 0.5 if method_count > 0 else 0.0
                viz_readiness['sequence_diagram'] = seq_readiness
                
                # Dependency graph readiness
                file_count = session.execute("SELECT COUNT(*) FROM nodes WHERE type = 'file'").scalar()
                file_deps = session.execute("""
                    SELECT COUNT(*) FROM edges 
                    WHERE kind IN ('import', 'include', 'dependency', 'package_relation')
                """).scalar()
                
                dep_readiness = 1.0 if (file_count > 0 and file_deps > 0) else 0.5 if file_count > 0 else 0.0
                viz_readiness['dependency_graph'] = dep_readiness
                
                # ERD readiness
                table_count = session.execute("SELECT COUNT(*) FROM nodes WHERE type = 'table'").scalar()
                table_rels = session.execute("""
                    SELECT COUNT(*) FROM edges 
                    WHERE kind IN ('foreign_key', 'references')
                """).scalar()
                
                erd_readiness = 1.0 if (table_count > 0 and table_rels > 0) else 0.5 if table_count > 0 else 0.0
                viz_readiness['erd'] = erd_readiness
                
                # Class diagram readiness
                class_count = session.execute("SELECT COUNT(*) FROM nodes WHERE type = 'class'").scalar()
                class_methods = session.execute("""
                    SELECT COUNT(*) FROM nodes 
                    WHERE type = 'method' AND parent_id IS NOT NULL
                """).scalar()
                
                class_readiness = 1.0 if (class_count > 0 and class_methods > 0) else 0.5 if class_count > 0 else 0.0
                viz_readiness['class_diagram'] = class_readiness
                
                data_points['visualization_readiness'] = viz_readiness
                
                # Overall visualization readiness
                overall_viz_readiness = sum(viz_readiness.values()) / len(viz_readiness)
                metrics.append(CompletenessMetric(
                    category='visualization_readiness',
                    metric_name='overall_visualization_readiness',
                    value=overall_viz_readiness,
                    description=f"Ready to generate {sum(1 for v in viz_readiness.values() if v >= 0.8)}/4 visualization types",
                    expected_range=(0.6, 1.0),
                    status=self._get_metric_status(overall_viz_readiness),
                    recommendations=self._get_visualization_readiness_recommendations(viz_readiness)
                ))
                
                # Check for silent failure potential
                silent_failure_risk = self._assess_silent_failure_risk(session)
                metrics.append(CompletenessMetric(
                    category='visualization_readiness',
                    metric_name='silent_failure_risk',
                    value=1.0 - silent_failure_risk,  # Invert so higher is better
                    description=f"Silent failure risk assessment: {silent_failure_risk:.1%}",
                    expected_range=(0.7, 1.0),
                    status=self._get_metric_status(1.0 - silent_failure_risk),
                    recommendations=['Monitor for visualizations that generate without meaningful content']
                ))
                
                overall_score = sum(m.value for m in metrics) / len(metrics)
                
        except Exception as e:
            self.logger.error(f"Visualization readiness assessment failed: {e}")
            issues.append(f"Assessment failed: {e}")
            overall_score = 0.0
        
        return ComponentCompleteness(
            component_name='visualization_readiness',
            overall_score=overall_score,
            metrics=metrics,
            data_points=data_points,
            issues=issues
        )
    
    def _generate_summary_metrics(self) -> Dict[str, Any]:
        """Generate high-level summary metrics"""
        summary = {}
        
        try:
            with self.db_manager.get_session() as session:
                # Basic entity counts
                entity_counts = {}
                for entity_type in ['file', 'class', 'method', 'function', 'table', 'column']:
                    count = session.execute(f"SELECT COUNT(*) FROM nodes WHERE type = '{entity_type}'").scalar()
                    entity_counts[entity_type] = count
                
                summary['entity_counts'] = entity_counts
                
                # Relationship counts
                relationship_counts = {}
                edge_types = session.execute("SELECT kind, COUNT(*) FROM edges GROUP BY kind").fetchall()
                for edge_type, count in edge_types:
                    relationship_counts[edge_type] = count
                
                summary['relationship_counts'] = relationship_counts
                
                # Analysis coverage
                total_nodes = sum(entity_counts.values())
                total_edges = sum(relationship_counts.values())
                
                summary['analysis_coverage'] = {
                    'total_nodes': total_nodes,
                    'total_edges': total_edges,
                    'node_to_edge_ratio': total_edges / max(total_nodes, 1),
                    'connectivity_density': total_edges / max(total_nodes * (total_nodes - 1) / 2, 1) if total_nodes > 1 else 0
                }
                
        except Exception as e:
            self.logger.error(f"Failed to generate summary metrics: {e}")
            summary['error'] = str(e)
        
        return summary
    
    def _analyze_data_distribution(self) -> Dict[str, Any]:
        """Analyze distribution patterns in the data"""
        distribution = {}
        
        try:
            with self.db_manager.get_session() as session:
                # Node type distribution
                node_types = session.execute("""
                    SELECT type, COUNT(*) as count 
                    FROM nodes 
                    GROUP BY type 
                    ORDER BY count DESC
                """).fetchall()
                
                distribution['node_types'] = {node_type: count for node_type, count in node_types}
                
                # Edge kind distribution
                edge_kinds = session.execute("""
                    SELECT kind, COUNT(*) as count 
                    FROM edges 
                    GROUP BY kind 
                    ORDER BY count DESC
                """).fetchall()
                
                distribution['edge_kinds'] = {kind: count for kind, count in edge_kinds}
                
                # File extension analysis
                file_extensions = session.execute("""
                    SELECT 
                        CASE 
                            WHEN name LIKE '%.java' THEN 'java'
                            WHEN name LIKE '%.py' THEN 'python'
                            WHEN name LIKE '%.js' THEN 'javascript'
                            WHEN name LIKE '%.ts' THEN 'typescript'
                            WHEN name LIKE '%.sql' THEN 'sql'
                            ELSE 'other'
                        END as extension,
                        COUNT(*) as count
                    FROM nodes 
                    WHERE type = 'file'
                    GROUP BY extension
                    ORDER BY count DESC
                """).fetchall()
                
                distribution['file_types'] = {ext: count for ext, count in file_extensions}
                
        except Exception as e:
            self.logger.error(f"Failed to analyze data distribution: {e}")
            distribution['error'] = str(e)
        
        return distribution
    
    def _generate_quality_indicators(self) -> Dict[str, Any]:
        """Generate quality indicators for the data"""
        indicators = {}
        
        try:
            with self.db_manager.get_session() as session:
                # Completeness indicators
                indicators['completeness'] = self._calculate_completeness_indicators(session)
                
                # Consistency indicators
                indicators['consistency'] = self._calculate_consistency_indicators(session)
                
                # Relationship quality indicators
                indicators['relationships'] = self._calculate_relationship_quality_indicators(session)
                
        except Exception as e:
            self.logger.error(f"Failed to generate quality indicators: {e}")
            indicators['error'] = str(e)
        
        return indicators
    
    def save_report(self, report: Dict[str, Any], output_path: Optional[str] = None) -> str:
        """Save the completeness report to a JSON file"""
        if output_path is None:
            output_path = f"output/{self.project_name}/completeness_report.json"
        
        # Ensure directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Completeness report saved to: {output_path}")
        return output_path
    
    # Helper methods
    def _get_metric_status(self, value: float, custom_thresholds: Optional[Dict[str, float]] = None) -> str:
        """Determine metric status based on value"""
        thresholds = custom_thresholds or self.thresholds
        
        if value >= thresholds.get('excellent', 0.9):
            return 'excellent'
        elif value >= thresholds.get('good', 0.7):
            return 'good'
        elif value >= thresholds.get('warning', 0.5):
            return 'warning'
        else:
            return 'critical'
    
    def _get_file_coverage_recommendations(self, coverage: float) -> List[str]:
        """Get recommendations for file coverage"""
        if coverage < 0.5:
            return [
                "Many files lack extracted code elements - check parsing configuration",
                "Verify that source file types are properly recognized",
                "Review file exclusion patterns"
            ]
        elif coverage < 0.8:
            return [
                "Some files may not be fully analyzed",
                "Check for unsupported language constructs"
            ]
        else:
            return ["File analysis coverage is good"]
    
    def _get_class_method_recommendations(self, coverage: float) -> List[str]:
        """Get recommendations for class-method coverage"""
        if coverage < 0.3:
            return [
                "Most classes appear empty - check method extraction logic",
                "Verify that class definitions are properly parsed"
            ]
        elif coverage < 0.7:
            return [
                "Some classes may be missing method information",
                "Check for interface vs implementation class handling"
            ]
        else:
            return ["Class-method relationships are well captured"]
    
    def _get_call_resolution_recommendations(self, resolution_rate: float) -> List[str]:
        """Get recommendations for call resolution"""
        if resolution_rate < 0.4:
            return [
                "High number of unresolved method calls",
                "Improve method resolution accuracy",
                "Check import/namespace handling"
            ]
        elif resolution_rate < 0.7:
            return [
                "Some method calls remain unresolved",
                "Review external library call resolution"
            ]
        else:
            return ["Method call resolution is good"]
    
    def _get_file_connectivity_recommendations(self, connectivity: float) -> List[str]:
        """Get recommendations for file connectivity"""
        if connectivity < 0.05:
            return [
                "Very low file connectivity - check import parsing",
                "Verify that dependency relationships are extracted"
            ]
        elif connectivity < 0.15:
            return [
                "File dependencies could be better captured",
                "Review package and import analysis"
            ]
        else:
            return ["File connectivity appears reasonable"]
    
    def _get_visualization_readiness_recommendations(self, readiness: Dict[str, float]) -> List[str]:
        """Get recommendations for visualization readiness"""
        recommendations = []
        
        for viz_type, score in readiness.items():
            if score < 0.5:
                if viz_type == 'sequence_diagram':
                    recommendations.append("Sequence diagrams need method call relationships")
                elif viz_type == 'dependency_graph':
                    recommendations.append("Dependency graphs need file relationship data")
                elif viz_type == 'erd':
                    recommendations.append("ERD needs table and foreign key information")
                elif viz_type == 'class_diagram':
                    recommendations.append("Class diagrams need class and method information")
        
        if not recommendations:
            recommendations.append("All visualization types appear ready for generation")
        
        return recommendations
    
    def _analyze_method_complexity_distribution(self, session) -> Optional[Dict[str, Any]]:
        """Analyze method complexity distribution"""
        try:
            # Simple heuristic based on method count and relationships
            method_count = session.execute("SELECT COUNT(*) FROM nodes WHERE type = 'method'").scalar()
            
            if method_count == 0:
                return None
            
            # Analyze method call patterns as complexity indicator
            methods_with_many_calls = session.execute("""
                SELECT COUNT(DISTINCT source_node_id) FROM edges 
                WHERE kind IN ('call', 'call_unresolved') 
                AND source_type = 'method'
                GROUP BY source_node_id
                HAVING COUNT(*) > 5
            """).fetchall()
            
            high_complexity_ratio = len(methods_with_many_calls) / method_count
            
            return {
                'distribution_quality': min(high_complexity_ratio * 2, 1.0),  # Normalize
                'summary': f"{len(methods_with_many_calls)} high-complexity methods detected"
            }
        
        except Exception:
            return None
    
    def _analyze_call_chain_depth(self, session) -> Optional[Dict[str, Any]]:
        """Analyze call chain depth"""
        try:
            # Simple analysis of call chain patterns
            call_edges = session.execute("""
                SELECT source_node_id, target_node_id FROM edges 
                WHERE kind IN ('call', 'call_unresolved')
            """).fetchall()
            
            if not call_edges:
                return None
            
            # Build adjacency list and calculate average path lengths
            from collections import defaultdict, deque
            
            graph = defaultdict(list)
            for source, target in call_edges:
                graph[source].append(target)
            
            depths = []
            for start_node in list(graph.keys())[:20]:  # Sample 20 nodes
                visited = set()
                queue = deque([(start_node, 0)])
                max_depth = 0
                
                while queue and len(visited) < 50:  # Limit search
                    node, depth = queue.popleft()
                    if node in visited:
                        continue
                    visited.add(node)
                    max_depth = max(max_depth, depth)
                    
                    for neighbor in graph[node]:
                        if neighbor not in visited:
                            queue.append((neighbor, depth + 1))
                
                depths.append(max_depth)
            
            avg_depth = sum(depths) / len(depths) if depths else 0
            
            return {
                'average_depth': avg_depth,
                'max_depth': max(depths) if depths else 0,
                'samples_analyzed': len(depths)
            }
        
        except Exception:
            return None
    
    def _assess_silent_failure_risk(self, session) -> float:
        """Assess risk of silent failures in visualizations"""
        risk_factors = []
        
        try:
            # Check for sequence diagram silent failure pattern
            method_count = session.execute("SELECT COUNT(*) FROM nodes WHERE type = 'method'").scalar()
            method_calls = session.execute("""
                SELECT COUNT(*) FROM edges 
                WHERE kind IN ('call', 'call_unresolved') AND source_type = 'method'
            """).scalar()
            
            if method_count > 20 and method_calls == 0:
                risk_factors.append(0.8)  # High risk
            elif method_count > 0 and method_calls == 0:
                risk_factors.append(0.5)  # Medium risk
            
            # Check for isolated components
            total_nodes = session.execute("SELECT COUNT(*) FROM nodes").scalar()
            total_edges = session.execute("SELECT COUNT(*) FROM edges").scalar()
            
            if total_nodes > 100 and total_edges < 50:
                risk_factors.append(0.6)  # Medium-high risk
            
            # Check for empty visualizations potential
            viz_types_ready = 0
            if method_count > 0 and method_calls > 0:
                viz_types_ready += 1
            
            file_count = session.execute("SELECT COUNT(*) FROM nodes WHERE type = 'file'").scalar()
            file_deps = session.execute("SELECT COUNT(*) FROM edges WHERE kind IN ('import', 'dependency', 'package_relation')").scalar()
            if file_count > 0 and file_deps > 0:
                viz_types_ready += 1
            
            if viz_types_ready < 2:
                risk_factors.append(0.4)  # Medium risk
            
            return max(risk_factors) if risk_factors else 0.1  # Low baseline risk
        
        except Exception:
            return 0.5  # Unknown risk
    
    def _calculate_completeness_indicators(self, session) -> Dict[str, float]:
        """Calculate completeness indicators"""
        indicators = {}
        
        # Node completeness (nodes with complete information)
        total_nodes = session.execute("SELECT COUNT(*) FROM nodes").scalar()
        nodes_with_parent = session.execute("SELECT COUNT(*) FROM nodes WHERE parent_id IS NOT NULL").scalar()
        
        if total_nodes > 0:
            indicators['hierarchical_completeness'] = nodes_with_parent / total_nodes
        
        return indicators
    
    def _calculate_consistency_indicators(self, session) -> Dict[str, float]:
        """Calculate consistency indicators"""
        indicators = {}
        
        # Edge consistency (edges pointing to existing nodes)
        total_edges = session.execute("SELECT COUNT(*) FROM edges").scalar()
        
        if total_edges > 0:
            valid_edges = session.execute("""
                SELECT COUNT(*) FROM edges e 
                WHERE EXISTS (SELECT 1 FROM nodes n1 WHERE n1.id = e.source_node_id)
                AND EXISTS (SELECT 1 FROM nodes n2 WHERE n2.id = e.target_node_id)
            """).scalar()
            
            indicators['edge_referential_integrity'] = valid_edges / total_edges
        
        return indicators
    
    def _calculate_relationship_quality_indicators(self, session) -> Dict[str, float]:
        """Calculate relationship quality indicators"""
        indicators = {}
        
        # Relationship diversity
        edge_types = session.execute("SELECT COUNT(DISTINCT kind) FROM edges").scalar()
        indicators['relationship_type_diversity'] = min(edge_types / 10.0, 1.0)  # Normalize to max 10 types
        
        return indicators
    
    def _generate_completeness_recommendations(self, component_assessments: Dict[str, Any], overall_score: float) -> List[str]:
        """Generate overall recommendations based on completeness analysis"""
        recommendations = []
        
        if overall_score < 0.5:
            recommendations.append("Overall data completeness is critically low - consider re-running analysis")
        
        # Component-specific recommendations
        for component, assessment in component_assessments.items():
            score = assessment.get('overall_score', 0)
            if score < 0.5:
                if component == 'method_relationships':
                    recommendations.append("Improve method call extraction and resolution")
                elif component == 'file_dependencies':
                    recommendations.append("Enhance file dependency and import parsing")
                elif component == 'code_structure':
                    recommendations.append("Review code structure analysis completeness")
        
        if overall_score > 0.8:
            recommendations.append("Data completeness is good - ready for comprehensive visualization")
        
        return recommendations


def main():
    """CLI entry point for completeness reporting"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate data completeness report")
    parser.add_argument("--project-name", required=True, help="Name of the project to analyze")
    parser.add_argument("--output", help="Output path for the report (optional)")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    reporter = CompletenessReporter(args.project_name)
    report = reporter.generate_comprehensive_report()
    
    # Display summary
    overall_score = report.get('overall_completeness', 0)
    print(f"\n📊 Data Completeness Report for '{args.project_name}'")
    print(f"Overall Completeness Score: {overall_score:.1%}")
    
    # Show component scores
    print(f"\nComponent Assessments:")
    components = report.get('component_assessments', {})
    for component, assessment in components.items():
        score = assessment.get('overall_score', 0)
        status = "✅" if score > 0.7 else "⚠️" if score > 0.5 else "❌"
        print(f"  {status} {component}: {score:.1%}")
    
    # Show top recommendations
    recommendations = report.get('recommendations', [])
    if recommendations:
        print(f"\nTop Recommendations:")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"  {i}. {rec}")
    
    # Save detailed report
    report_path = reporter.save_report(report, args.output)
    print(f"\nDetailed report saved to: {report_path}")


if __name__ == "__main__":
    main()