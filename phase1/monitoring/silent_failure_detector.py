"""
Silent Failure Detection System

Detects and alerts on failures that don't raise exceptions but produce meaningless results.
Monitors visualization generation, data processing, and analysis quality.
"""

import logging
import json
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import sqlite3
from collections import defaultdict

from visualize.data_access import DatabaseManager
from phase1.validation.data_quality_validator import DataQualityValidator


@dataclass
class SilentFailureAlert:
    """Represents a detected silent failure"""
    timestamp: str
    component: str
    failure_type: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    expected_result: str
    actual_result: str
    context: Dict[str, Any]
    recommendations: List[str]


class SilentFailureDetector:
    """Detects silent failures across the SourceAnalyzer system"""
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.db_manager = DatabaseManager(project_name)
        self.validator = DataQualityValidator(project_name)
        self.alerts: List[SilentFailureAlert] = []
        self.logger = logging.getLogger(__name__)
        
        # Thresholds for detecting failures
        self.thresholds = {
            'min_sequence_interactions': 5,
            'min_dependency_edges': 10,
            'min_erd_relationships': 3,
            'min_class_methods': 1,
            'min_file_functions': 1,
            'max_empty_visualizations': 2,
            'min_code_coverage': 0.5,  # 50% of files should have analysis
            'max_unresolved_calls': 0.8  # 80% unresolved calls is problematic
        }
    
    def detect_all_failures(self) -> List[SilentFailureAlert]:
        """Run comprehensive silent failure detection"""
        self.alerts.clear()
        
        self.logger.info(f"Starting silent failure detection for project: {self.project_name}")
        
        # Run all detection methods
        self._detect_sequence_diagram_failures()
        self._detect_dependency_graph_failures()
        self._detect_erd_failures()
        self._detect_class_diagram_failures()
        self._detect_data_completeness_failures()
        self._detect_visualization_generation_failures()
        self._detect_analysis_quality_failures()
        
        self.logger.info(f"Silent failure detection complete. Found {len(self.alerts)} issues.")
        return self.alerts
    
    def _detect_sequence_diagram_failures(self):
        """Detect silent failures in sequence diagram generation"""
        try:
            with self.db_manager.get_session() as session:
                # Get sequence diagram specific data
                method_edges = session.execute("""
                    SELECT COUNT(*) FROM edges 
                    WHERE source_type = 'method' AND target_type = 'method'
                    AND kind IN ('call', 'call_unresolved')
                """).scalar()
                
                method_count = session.execute("""
                    SELECT COUNT(*) FROM nodes WHERE type = 'method'
                """).scalar()
                
                # Check for sequence diagram silent failure pattern
                if method_count > 20 and method_edges == 0:
                    self._add_alert(
                        component="sequence_diagram",
                        failure_type="no_method_interactions",
                        severity="high",
                        description=f"Found {method_count} methods but 0 method-to-method call relationships",
                        expected_result=f"Expected at least {self.thresholds['min_sequence_interactions']} method interactions",
                        actual_result=f"Found {method_edges} method interactions",
                        context={"method_count": method_count, "method_edges": method_edges},
                        recommendations=[
                            "Check if code analysis phase properly extracted method calls",
                            "Verify that method resolution is working correctly",
                            "Consider implementing fallback strategies for method sequence generation"
                        ]
                    )
                
                # Check for low interaction density
                if method_count > 0:
                    interaction_ratio = method_edges / method_count
                    if interaction_ratio < 0.1:  # Less than 10% interaction ratio
                        self._add_alert(
                            component="sequence_diagram",
                            failure_type="low_interaction_density",
                            severity="medium",
                            description=f"Very low method interaction density: {interaction_ratio:.2%}",
                            expected_result="Expected higher method interaction density for meaningful sequences",
                            actual_result=f"{method_edges} interactions for {method_count} methods",
                            context={"interaction_ratio": interaction_ratio},
                            recommendations=[
                                "Review method call extraction accuracy",
                                "Check if static analysis is capturing all call relationships"
                            ]
                        )
        
        except Exception as e:
            self.logger.error(f"Error detecting sequence diagram failures: {e}")
    
    def _detect_dependency_graph_failures(self):
        """Detect silent failures in dependency graph generation"""
        try:
            with self.db_manager.get_session() as session:
                file_count = session.execute("SELECT COUNT(*) FROM nodes WHERE type = 'file'").scalar()
                file_edges = session.execute("""
                    SELECT COUNT(*) FROM edges 
                    WHERE (source_type = 'file' OR target_type = 'file')
                    AND kind IN ('import', 'include', 'dependency')
                """).scalar()
                
                if file_count > 10 and file_edges < self.thresholds['min_dependency_edges']:
                    self._add_alert(
                        component="dependency_graph",
                        failure_type="insufficient_dependencies",
                        severity="medium",
                        description=f"Found {file_count} files but only {file_edges} dependency relationships",
                        expected_result=f"Expected at least {self.thresholds['min_dependency_edges']} file dependencies",
                        actual_result=f"Found {file_edges} file dependencies",
                        context={"file_count": file_count, "file_edges": file_edges},
                        recommendations=[
                            "Check import/include statement parsing",
                            "Verify file dependency extraction is working",
                            "Review project structure for expected dependencies"
                        ]
                    )
        
        except Exception as e:
            self.logger.error(f"Error detecting dependency graph failures: {e}")
    
    def _detect_erd_failures(self):
        """Detect silent failures in ERD generation"""
        try:
            with self.db_manager.get_session() as session:
                table_count = session.execute("SELECT COUNT(*) FROM nodes WHERE type = 'table'").scalar()
                table_relations = session.execute("""
                    SELECT COUNT(*) FROM edges 
                    WHERE (source_type = 'table' OR target_type = 'table')
                    AND kind IN ('foreign_key', 'references', 'uses')
                """).scalar()
                
                if table_count > 5 and table_relations < self.thresholds['min_erd_relationships']:
                    self._add_alert(
                        component="erd",
                        failure_type="isolated_tables",
                        severity="medium",
                        description=f"Found {table_count} tables but only {table_relations} relationships",
                        expected_result=f"Expected at least {self.thresholds['min_erd_relationships']} table relationships",
                        actual_result=f"Found {table_relations} table relationships",
                        context={"table_count": table_count, "table_relations": table_relations},
                        recommendations=[
                            "Check foreign key constraint detection",
                            "Verify table relationship analysis",
                            "Review SQL parsing for relationship extraction"
                        ]
                    )
        
        except Exception as e:
            self.logger.error(f"Error detecting ERD failures: {e}")
    
    def _detect_class_diagram_failures(self):
        """Detect silent failures in class diagram generation"""
        try:
            with self.db_manager.get_session() as session:
                class_count = session.execute("SELECT COUNT(*) FROM nodes WHERE type = 'class'").scalar()
                classes_with_methods = session.execute("""
                    SELECT COUNT(DISTINCT parent_id) FROM nodes 
                    WHERE type = 'method' AND parent_id IS NOT NULL
                """).scalar()
                
                if class_count > 0:
                    method_coverage = classes_with_methods / class_count
                    if method_coverage < 0.3:  # Less than 30% of classes have methods
                        self._add_alert(
                            component="class_diagram",
                            failure_type="empty_classes",
                            severity="medium",
                            description=f"Only {method_coverage:.1%} of classes have extracted methods",
                            expected_result="Expected most classes to have at least one method",
                            actual_result=f"{classes_with_methods}/{class_count} classes have methods",
                            context={"method_coverage": method_coverage},
                            recommendations=[
                                "Check method extraction from class definitions",
                                "Verify class-method relationship parsing",
                                "Review code analysis completeness"
                            ]
                        )
        
        except Exception as e:
            self.logger.error(f"Error detecting class diagram failures: {e}")
    
    def _detect_data_completeness_failures(self):
        """Detect failures in data completeness and coverage"""
        try:
            quality_report = self.validator.validate_project()
            overall_score = quality_report.get('overall_score', 0)
            
            if overall_score < 0.6:  # Less than 60% quality score
                issues = quality_report.get('issues', [])
                critical_issues = [issue for issue in issues if issue.get('severity') == 'high']
                
                self._add_alert(
                    component="data_completeness",
                    failure_type="low_quality_score",
                    severity="high" if len(critical_issues) > 0 else "medium",
                    description=f"Overall project quality score is {overall_score:.1%}",
                    expected_result="Expected quality score above 60%",
                    actual_result=f"Quality score: {overall_score:.1%}",
                    context={"quality_report": quality_report},
                    recommendations=[
                        "Review data extraction completeness",
                        "Check for missing analysis phases",
                        "Verify project structure integrity"
                    ]
                )
        
        except Exception as e:
            self.logger.error(f"Error detecting data completeness failures: {e}")
    
    def _detect_visualization_generation_failures(self):
        """Detect failures in visualization file generation"""
        try:
            output_dir = Path(f"output/{self.project_name}/visualize")
            if not output_dir.exists():
                self._add_alert(
                    component="visualization_generation",
                    failure_type="missing_output_directory",
                    severity="high",
                    description="Visualization output directory does not exist",
                    expected_result="Expected output directory with visualization files",
                    actual_result="No output directory found",
                    context={"expected_path": str(output_dir)},
                    recommendations=[
                        "Check visualization generation process",
                        "Verify output directory creation",
                        "Run visualization commands to generate output"
                    ]
                )
                return
            
            # Check for empty visualization files
            empty_files = []
            visualization_files = list(output_dir.glob("*.html")) + list(output_dir.glob("*.md"))
            
            for file_path in visualization_files:
                if file_path.stat().st_size < 1000:  # Less than 1KB suggests empty/minimal content
                    empty_files.append(file_path.name)
            
            if len(empty_files) > self.thresholds['max_empty_visualizations']:
                self._add_alert(
                    component="visualization_generation",
                    failure_type="empty_visualization_files",
                    severity="medium",
                    description=f"Found {len(empty_files)} potentially empty visualization files",
                    expected_result="Expected meaningful content in all visualization files",
                    actual_result=f"Files with minimal content: {', '.join(empty_files)}",
                    context={"empty_files": empty_files},
                    recommendations=[
                        "Check data availability for each visualization type",
                        "Verify visualization generation logic",
                        "Review fallback strategies for missing data"
                    ]
                )
        
        except Exception as e:
            self.logger.error(f"Error detecting visualization generation failures: {e}")
    
    def _detect_analysis_quality_failures(self):
        """Detect failures in code analysis quality"""
        try:
            with self.db_manager.get_session() as session:
                # Check for high percentage of unresolved calls
                total_calls = session.execute("""
                    SELECT COUNT(*) FROM edges WHERE kind IN ('call', 'call_unresolved')
                """).scalar()
                
                unresolved_calls = session.execute("""
                    SELECT COUNT(*) FROM edges WHERE kind = 'call_unresolved'
                """).scalar()
                
                if total_calls > 0:
                    unresolved_ratio = unresolved_calls / total_calls
                    if unresolved_ratio > self.thresholds['max_unresolved_calls']:
                        self._add_alert(
                            component="code_analysis",
                            failure_type="high_unresolved_calls",
                            severity="medium",
                            description=f"{unresolved_ratio:.1%} of method calls are unresolved",
                            expected_result=f"Expected less than {self.thresholds['max_unresolved_calls']:.1%} unresolved calls",
                            actual_result=f"{unresolved_calls}/{total_calls} calls are unresolved",
                            context={"unresolved_ratio": unresolved_ratio},
                            recommendations=[
                                "Improve method resolution accuracy",
                                "Check import/namespace handling",
                                "Review external library call resolution"
                            ]
                        )
        
        except Exception as e:
            self.logger.error(f"Error detecting analysis quality failures: {e}")
    
    def _add_alert(self, component: str, failure_type: str, severity: str, 
                   description: str, expected_result: str, actual_result: str,
                   context: Dict[str, Any], recommendations: List[str]):
        """Add a new silent failure alert"""
        alert = SilentFailureAlert(
            timestamp=datetime.now().isoformat(),
            component=component,
            failure_type=failure_type,
            severity=severity,
            description=description,
            expected_result=expected_result,
            actual_result=actual_result,
            context=context,
            recommendations=recommendations
        )
        self.alerts.append(alert)
        
        # Log the alert
        log_level = {
            'low': logging.INFO,
            'medium': logging.WARNING,
            'high': logging.ERROR,
            'critical': logging.CRITICAL
        }.get(severity, logging.WARNING)
        
        self.logger.log(log_level, f"Silent failure detected in {component}: {description}")
    
    def generate_alert_report(self) -> Dict[str, Any]:
        """Generate a comprehensive alert report"""
        if not self.alerts:
            return {
                "project_name": self.project_name,
                "timestamp": datetime.now().isoformat(),
                "status": "healthy",
                "total_alerts": 0,
                "alerts": []
            }
        
        # Categorize alerts by severity
        alerts_by_severity = defaultdict(list)
        for alert in self.alerts:
            alerts_by_severity[alert.severity].append(alert)
        
        # Categorize alerts by component
        alerts_by_component = defaultdict(list)
        for alert in self.alerts:
            alerts_by_component[alert.component].append(alert)
        
        return {
            "project_name": self.project_name,
            "timestamp": datetime.now().isoformat(),
            "status": "issues_detected",
            "total_alerts": len(self.alerts),
            "severity_breakdown": {
                severity: len(alerts) for severity, alerts in alerts_by_severity.items()
            },
            "component_breakdown": {
                component: len(alerts) for component, alerts in alerts_by_component.items()
            },
            "alerts": [asdict(alert) for alert in self.alerts],
            "recommendations": self._generate_summary_recommendations()
        }
    
    def _generate_summary_recommendations(self) -> List[str]:
        """Generate high-level recommendations based on detected failures"""
        recommendations = []
        
        # Component-specific recommendations
        components_with_issues = set(alert.component for alert in self.alerts)
        
        if "sequence_diagram" in components_with_issues:
            recommendations.append("Review and improve method call extraction in code analysis phase")
        
        if "dependency_graph" in components_with_issues:
            recommendations.append("Enhance import/dependency parsing for better file relationships")
        
        if "erd" in components_with_issues:
            recommendations.append("Improve database schema analysis and foreign key detection")
        
        if "data_completeness" in components_with_issues:
            recommendations.append("Run comprehensive data validation and fix extraction issues")
        
        # Severity-based recommendations
        critical_alerts = [alert for alert in self.alerts if alert.severity == 'critical']
        if critical_alerts:
            recommendations.append("Address critical issues immediately - system may be producing meaningless results")
        
        high_alerts = [alert for alert in self.alerts if alert.severity == 'high']
        if len(high_alerts) > 3:
            recommendations.append("Multiple high-severity issues detected - consider re-running analysis with improved settings")
        
        return recommendations
    
    def save_alert_report(self, output_path: Optional[str] = None) -> str:
        """Save the alert report to a JSON file"""
        if output_path is None:
            output_path = f"output/{self.project_name}/silent_failure_report.json"
        
        report = self.generate_alert_report()
        
        # Ensure directory exists
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Silent failure report saved to: {output_path}")
        return output_path


def main():
    """CLI entry point for silent failure detection"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Detect silent failures in SourceAnalyzer projects")
    parser.add_argument("--project-name", required=True, help="Name of the project to analyze")
    parser.add_argument("--output", help="Output path for the report (optional)")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    detector = SilentFailureDetector(args.project_name)
    alerts = detector.detect_all_failures()
    
    if alerts:
        print(f"\n🚨 Found {len(alerts)} silent failure issues in project '{args.project_name}'")
        
        # Group by severity
        by_severity = defaultdict(list)
        for alert in alerts:
            by_severity[alert.severity].append(alert)
        
        for severity in ['critical', 'high', 'medium', 'low']:
            if severity in by_severity:
                print(f"\n{severity.upper()} ({len(by_severity[severity])} issues):")
                for alert in by_severity[severity]:
                    print(f"  • {alert.component}: {alert.description}")
    else:
        print(f"✅ No silent failures detected in project '{args.project_name}'")
    
    # Save detailed report
    report_path = detector.save_alert_report(args.output)
    print(f"\nDetailed report saved to: {report_path}")


if __name__ == "__main__":
    main()