# phase1/validation/data_quality_validator.py
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from collections import defaultdict, Counter
import json
from datetime import datetime
from pathlib import Path

from ..models.database import DatabaseManager, File, Class, Method, SqlUnit, Edge, DbTable, DbColumn
from sqlalchemy import func, text
import logging

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Validation result with severity and recommendations"""
    check_name: str
    status: str  # 'pass', 'warning', 'error', 'critical'
    message: str
    expected_count: Optional[int] = None
    actual_count: Optional[int] = None
    details: Dict[str, Any] = None
    recommendations: List[str] = None


@dataclass
class DataQualityReport:
    """Comprehensive data quality report"""
    project_id: int
    project_name: str
    timestamp: datetime
    overall_score: float
    results: List[ValidationResult]
    summary: Dict[str, int]
    potential_issues: List[str]


class DataQualityValidator:
    """Comprehensive data quality validation for source analysis projects"""

    def __init__(self, config: Union[str, Dict[str, Any]]):
        # Allow passing a project name string for convenience
        if isinstance(config, str):
            project_name = config
            config = {
                "database": {
                    "project": {
                        "type": "sqlite",
                        "sqlite": {
                            "path": f"./project/{project_name}/data/metadata.db",
                            "wal_mode": True,
                        },
                    }
                }
            }

        self.config = config
        self.dbm = DatabaseManager(config.get('database', {}).get('project', {}))
        self.dbm.initialize()
        
        # Quality thresholds
        self.thresholds = {
            'min_methods_per_class': 1,
            'min_edges_per_project': 10,
            'min_call_edges_ratio': 0.1,  # 10% of edges should be call-related
            'min_files_with_methods': 5,
            'max_duplicate_method_names_ratio': 0.8,  # Max 80% methods with same name
            'min_table_usage_edges': 1,
            'min_sql_units_per_project': 1,
            'expected_edge_types': ['call', 'use_table', 'include', 'extends', 'implements']
        }
    
    def session(self):
        """Get database session"""
        return self.dbm.get_session()
    
    def validate_project(self, project_id: int | None = None, project_name: str = None) -> DataQualityReport:
        """Run comprehensive validation on a project"""
        if project_id is None:
            project_id = 1
        logger.info(f"Starting data quality validation for project {project_id}")
        
        results = []
        session = self.session()
        
        try:
            # Core data structure validation
            results.extend(self._validate_project_structure(session, project_id))
            
            # Edge relationship validation
            results.extend(self._validate_edge_relationships(session, project_id))
            
            # Code analysis completeness
            results.extend(self._validate_code_analysis_completeness(session, project_id))
            
            # Database schema validation
            results.extend(self._validate_database_schema(session, project_id))
            
            # Cross-reference validation
            results.extend(self._validate_cross_references(session, project_id))
            
            # Visualization readiness check
            results.extend(self._validate_visualization_readiness(session, project_id))
            
            # Calculate overall score and generate report
            overall_score = self._calculate_quality_score(results)
            summary = self._generate_summary(results)
            potential_issues = self._identify_potential_issues(results)
            
            return DataQualityReport(
                project_id=project_id,
                project_name=project_name or f"Project {project_id}",
                timestamp=datetime.now(),
                overall_score=overall_score,
                results=results,
                summary=summary,
                potential_issues=potential_issues
            )
            
        finally:
            session.close()
    
    def _validate_project_structure(self, session, project_id: int) -> List[ValidationResult]:
        """Validate basic project structure"""
        results = []
        
        # Check if project has files
        file_count = session.query(File).filter(File.project_id == project_id).count()
        if file_count == 0:
            results.append(ValidationResult(
                check_name="project_has_files",
                status="critical",
                message=f"Project has no files",
                actual_count=file_count,
                recommendations=["Run phase1 analysis on source code"]
            ))
        else:
            results.append(ValidationResult(
                check_name="project_has_files",
                status="pass",
                message=f"Project has {file_count} files",
                actual_count=file_count
            ))
        
        # Check if project has classes
        class_count = session.query(Class).join(File).filter(File.project_id == project_id).count()
        if class_count == 0:
            results.append(ValidationResult(
                check_name="project_has_classes",
                status="warning",
                message=f"Project has no classes",
                actual_count=class_count,
                recommendations=["Verify source code contains classes", "Check file language detection"]
            ))
        else:
            results.append(ValidationResult(
                check_name="project_has_classes",
                status="pass",
                message=f"Project has {class_count} classes",
                actual_count=class_count
            ))
        
        # Check if project has methods
        method_count = session.query(Method).join(Class).join(File).filter(File.project_id == project_id).count()
        if method_count == 0:
            results.append(ValidationResult(
                check_name="project_has_methods",
                status="error",
                message=f"Project has no methods",
                actual_count=method_count,
                recommendations=["Run deeper code analysis", "Check method detection patterns"]
            ))
        else:
            results.append(ValidationResult(
                check_name="project_has_methods",
                status="pass",
                message=f"Project has {method_count} methods",
                actual_count=method_count
            ))
        
        return results
    
    def _validate_edge_relationships(self, session, project_id: int) -> List[ValidationResult]:
        """Validate edge relationships for meaningful connections"""
        results = []
        
        # Get all edges for this project
        all_edges = session.execute(text("""
            SELECT e.edge_kind, COUNT(*) as count
            FROM edges e
            JOIN files f ON (e.src_type = 'file' AND e.src_id = f.file_id)
            WHERE f.project_id = :project_id
            GROUP BY e.edge_kind
        """), {"project_id": project_id}).fetchall()
        
        edge_types = {row[0]: row[1] for row in all_edges}
        total_edges = sum(edge_types.values())
        
        if total_edges == 0:
            results.append(ValidationResult(
                check_name="project_has_edges",
                status="critical",
                message="Project has no relationship edges",
                actual_count=0,
                recommendations=["Run relationship analysis", "Check edge detection configuration"]
            ))
        else:
            results.append(ValidationResult(
                check_name="project_has_edges",
                status="pass",
                message=f"Project has {total_edges} edges across {len(edge_types)} types",
                actual_count=total_edges,
                details={"edge_types": edge_types}
            ))
        
        # Check for meaningful edge types
        meaningful_edges = ['call', 'call_unresolved', 'use_table', 'call_sql', 'include', 'extends', 'implements']
        found_meaningful = [edge_type for edge_type in meaningful_edges if edge_type in edge_types]
        
        if not found_meaningful:
            results.append(ValidationResult(
                check_name="has_meaningful_edges",
                status="error",
                message=f"No meaningful edge types found. Only found: {list(edge_types.keys())}",
                details={"available_types": list(edge_types.keys()), "expected_types": meaningful_edges},
                recommendations=[
                    "Enable call relationship analysis",
                    "Run dependency analysis", 
                    "Check code parsing configuration"
                ]
            ))
        else:
            results.append(ValidationResult(
                check_name="has_meaningful_edges",
                status="pass",
                message=f"Found meaningful edge types: {found_meaningful}",
                details={"found_types": found_meaningful}
            ))
        
        # Check call relationship density
        call_edges = sum(count for edge_type, count in edge_types.items() 
                        if 'call' in edge_type.lower())
        
        if total_edges > 0:
            call_ratio = call_edges / total_edges
            expected_ratio = self.thresholds['min_call_edges_ratio']
            
            if call_ratio < expected_ratio:
                results.append(ValidationResult(
                    check_name="sufficient_call_relationships",
                    status="warning",
                    message=f"Low call relationship density: {call_ratio:.2%} (expected: >{expected_ratio:.1%})",
                    details={"call_edges": call_edges, "total_edges": total_edges, "ratio": call_ratio},
                    recommendations=["Enable method call analysis", "Check call detection patterns"]
                ))
            else:
                results.append(ValidationResult(
                    check_name="sufficient_call_relationships", 
                    status="pass",
                    message=f"Good call relationship density: {call_ratio:.2%}",
                    details={"ratio": call_ratio}
                ))
        
        return results
    
    def _validate_code_analysis_completeness(self, session, project_id: int) -> List[ValidationResult]:
        """Validate completeness of code analysis"""
        results = []
        
        # Check method distribution across classes
        class_method_counts = session.execute(text("""
            SELECT c.class_id, c.name, COUNT(m.method_id) as method_count
            FROM classes c
            JOIN files f ON c.file_id = f.file_id
            LEFT JOIN methods m ON c.class_id = m.class_id
            WHERE f.project_id = :project_id
            GROUP BY c.class_id, c.name
        """), {"project_id": project_id}).fetchall()
        
        if class_method_counts:
            classes_without_methods = [row for row in class_method_counts if row[2] == 0]
            
            if len(classes_without_methods) > len(class_method_counts) * 0.5:  # More than 50% classes without methods
                results.append(ValidationResult(
                    check_name="method_analysis_completeness",
                    status="warning",
                    message=f"{len(classes_without_methods)} out of {len(class_method_counts)} classes have no methods",
                    details={"classes_without_methods": len(classes_without_methods), "total_classes": len(class_method_counts)},
                    recommendations=["Check method detection patterns", "Verify source code quality"]
                ))
            else:
                results.append(ValidationResult(
                    check_name="method_analysis_completeness",
                    status="pass",
                    message=f"Good method coverage: {len(class_method_counts) - len(classes_without_methods)} classes have methods"
                ))
        
        # Check for duplicate method names (could indicate analysis issues)
        method_name_counts = session.execute(text("""
            SELECT m.name, COUNT(*) as count
            FROM methods m
            JOIN classes c ON m.class_id = c.class_id
            JOIN files f ON c.file_id = f.file_id
            WHERE f.project_id = :project_id
            GROUP BY m.name
            HAVING COUNT(*) > 1
            ORDER BY COUNT(*) DESC
        """), {"project_id": project_id}).fetchall()
        
        if method_name_counts:
            total_methods = session.execute(text("""
                SELECT COUNT(*)
                FROM methods m
                JOIN classes c ON m.class_id = c.class_id
                JOIN files f ON c.file_id = f.file_id
                WHERE f.project_id = :project_id
            """), {"project_id": project_id}).scalar()
            
            duplicate_methods = sum(count for _, count in method_name_counts)
            duplicate_ratio = duplicate_methods / total_methods if total_methods > 0 else 0
            
            if duplicate_ratio > self.thresholds['max_duplicate_method_names_ratio']:
                results.append(ValidationResult(
                    check_name="method_name_uniqueness",
                    status="warning",
                    message=f"High duplicate method names: {duplicate_ratio:.2%} (threshold: {self.thresholds['max_duplicate_method_names_ratio']:.1%})",
                    details={"duplicate_ratio": duplicate_ratio, "top_duplicates": method_name_counts[:5]},
                    recommendations=["This is normal for common method names like 'toString', 'equals'"]
                ))
            else:
                results.append(ValidationResult(
                    check_name="method_name_uniqueness",
                    status="pass",
                    message=f"Reasonable method name distribution: {duplicate_ratio:.2%} duplicates"
                ))
        
        return results
    
    def _validate_database_schema(self, session, project_id: int) -> List[ValidationResult]:
        """Validate database schema analysis"""
        results = []
        
        # Check if project has database tables
        table_count = session.query(DbTable).count()
        if table_count == 0:
            results.append(ValidationResult(
                check_name="has_database_schema",
                status="warning",
                message="No database tables found",
                actual_count=0,
                recommendations=["Import database schema CSV files", "Run database analysis"]
            ))
        else:
            results.append(ValidationResult(
                check_name="has_database_schema",
                status="pass",
                message=f"Found {table_count} database tables",
                actual_count=table_count
            ))
            
            # Check table-column relationships
            tables_with_columns = session.execute(text("""
                SELECT t.name, COUNT(c.column_id) as column_count
                FROM db_tables t
                LEFT JOIN db_columns c ON t.name = c.table_name
                GROUP BY t.name
                HAVING COUNT(c.column_id) = 0
            """)).fetchall()
            
            if tables_with_columns:
                results.append(ValidationResult(
                    check_name="table_column_consistency",
                    status="warning", 
                    message=f"{len(tables_with_columns)} tables have no columns",
                    details={"tables_without_columns": [row[0] for row in tables_with_columns]},
                    recommendations=["Check column import process", "Verify CSV file completeness"]
                ))
        
        return results
    
    def _validate_cross_references(self, session, project_id: int) -> List[ValidationResult]:
        """Validate cross-references between different data types"""
        results = []
        
        # Check SQL units to table references
        sql_count = session.query(SqlUnit).join(File).filter(File.project_id == project_id).count()
        if sql_count > 0:
            table_usage_edges = session.execute(text("""
                SELECT COUNT(*)
                FROM edges e
                JOIN sql_units s ON e.src_type = 'sql_unit' AND e.src_id = s.sql_id
                JOIN files f ON s.file_id = f.file_id
                WHERE f.project_id = :project_id AND e.edge_kind = 'use_table'
            """), {"project_id": project_id}).scalar()
            
            if table_usage_edges == 0:
                results.append(ValidationResult(
                    check_name="sql_table_references",
                    status="warning",
                    message=f"Found {sql_count} SQL units but no table usage edges",
                    details={"sql_units": sql_count, "table_edges": table_usage_edges},
                    recommendations=["Enable SQL-table relationship analysis", "Check table reference detection"]
                ))
            else:
                results.append(ValidationResult(
                    check_name="sql_table_references",
                    status="pass",
                    message=f"Good SQL-table relationships: {table_usage_edges} connections for {sql_count} SQL units",
                    details={"sql_units": sql_count, "table_edges": table_usage_edges}
                ))
        
        return results
    
    def _validate_visualization_readiness(self, session, project_id: int) -> List[ValidationResult]:
        """Validate data readiness for different visualization types"""
        results = []
        
        visualizations = {
            'sequence_diagram': {
                'required_edges': ['call', 'call_unresolved', 'use_table'],
                'required_nodes': ['method'],
                'min_nodes': 2
            },
            'dependency_graph': {
                'required_edges': ['include', 'extends', 'implements', 'call'],
                'required_nodes': ['class', 'file'],
                'min_nodes': 5
            },
            'erd_diagram': {
                'required_edges': ['fk_inferred'],
                'required_nodes': ['table'],
                'min_nodes': 2
            }
        }
        
        for viz_type, requirements in visualizations.items():
            # Check node availability
            node_counts = {}
            for node_type in requirements['required_nodes']:
                if node_type == 'method':
                    count = session.query(Method).join(Class).join(File).filter(File.project_id == project_id).count()
                elif node_type == 'class':
                    count = session.query(Class).join(File).filter(File.project_id == project_id).count()
                elif node_type == 'file':
                    count = session.query(File).filter(File.project_id == project_id).count()
                elif node_type == 'table':
                    count = session.query(DbTable).count()
                else:
                    count = 0
                node_counts[node_type] = count
            
            # Check edge availability
            available_edges = session.execute(text("""
                SELECT DISTINCT e.edge_kind
                FROM edges e
                JOIN files f ON (e.src_type = 'file' AND e.src_id = f.file_id)
                WHERE f.project_id = :project_id
            """), {"project_id": project_id}).fetchall()
            
            available_edge_types = [row[0] for row in available_edges]
            missing_edges = [edge_type for edge_type in requirements['required_edges'] 
                           if edge_type not in available_edge_types]
            
            # Evaluate readiness
            min_nodes_met = all(count >= requirements['min_nodes'] for count in node_counts.values())
            has_required_edges = len(missing_edges) < len(requirements['required_edges'])  # At least some required edges
            
            if min_nodes_met and has_required_edges:
                status = "pass"
                message = f"{viz_type} is ready for visualization"
            elif min_nodes_met:
                status = "warning"
                message = f"{viz_type} has sufficient nodes but missing some edge types: {missing_edges}"
            else:
                status = "error"
                message = f"{viz_type} is not ready - insufficient nodes or edges"
            
            results.append(ValidationResult(
                check_name=f"{viz_type}_readiness",
                status=status,
                message=message,
                details={
                    "node_counts": node_counts,
                    "available_edges": available_edge_types,
                    "missing_edges": missing_edges
                },
                recommendations=self._get_viz_recommendations(viz_type, missing_edges, node_counts)
            ))
        
        return results
    
    def _get_viz_recommendations(self, viz_type: str, missing_edges: List[str], node_counts: Dict[str, int]) -> List[str]:
        """Get recommendations for visualization readiness issues"""
        recommendations = []
        
        if viz_type == "sequence_diagram":
            if 'call' in missing_edges and 'call_unresolved' in missing_edges:
                recommendations.append("Enable method call analysis in phase1 configuration")
            if 'use_table' in missing_edges:
                recommendations.append("Enable SQL-table relationship analysis")
            if any(count < 2 for count in node_counts.values()):
                recommendations.append("Ensure source code has sufficient methods for sequence tracing")
        
        elif viz_type == "dependency_graph":
            if missing_edges:
                recommendations.append("Enable dependency analysis for imports and inheritance")
            if node_counts.get('class', 0) < 5:
                recommendations.append("Analyze projects with more classes for better dependency visualization")
        
        elif viz_type == "erd_diagram":
            if 'fk_inferred' in missing_edges:
                recommendations.append("Enable foreign key inference analysis")
            if node_counts.get('table', 0) < 2:
                recommendations.append("Import complete database schema with multiple tables")
        
        return recommendations
    
    def _calculate_quality_score(self, results: List[ValidationResult]) -> float:
        """Calculate overall quality score (0-100)"""
        if not results:
            return 0.0
        
        weights = {'pass': 1.0, 'warning': 0.7, 'error': 0.3, 'critical': 0.0}
        total_weight = sum(weights[result.status] for result in results)
        max_weight = len(results) * 1.0
        
        return (total_weight / max_weight) * 100
    
    def _generate_summary(self, results: List[ValidationResult]) -> Dict[str, int]:
        """Generate summary statistics"""
        summary = Counter(result.status for result in results)
        return dict(summary)
    
    def _identify_potential_issues(self, results: List[ValidationResult]) -> List[str]:
        """Identify potential issues that might cause silent failures"""
        issues = []
        
        # Look for patterns that indicate silent failures
        for result in results:
            if result.status in ['error', 'critical']:
                issues.append(f"Critical: {result.message}")
            elif result.status == 'warning' and 'readiness' in result.check_name:
                issues.append(f"Visualization Risk: {result.message}")
        
        return issues
    
    def generate_report_json(self, report: DataQualityReport, output_path: str):
        """Generate JSON report file"""
        report_data = {
            "project_id": report.project_id,
            "project_name": report.project_name,
            "timestamp": report.timestamp.isoformat(),
            "overall_score": report.overall_score,
            "summary": report.summary,
            "potential_issues": report.potential_issues,
            "results": []
        }
        
        for result in report.results:
            result_data = {
                "check_name": result.check_name,
                "status": result.status,
                "message": result.message
            }
            
            if result.expected_count is not None:
                result_data["expected_count"] = result.expected_count
            if result.actual_count is not None:
                result_data["actual_count"] = result.actual_count
            if result.details:
                result_data["details"] = result.details
            if result.recommendations:
                result_data["recommendations"] = result.recommendations
            
            report_data["results"].append(result_data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Data quality report saved to: {output_path}")