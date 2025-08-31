# tests/visualization_integrity_tests.py
import pytest
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Add project root to path
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from phase1.validation.data_quality_validator import DataQualityValidator, DataQualityReport
from visualize.analyzers.relationship_analyzer import RelationshipAnalyzer
from visualize.data_access import VizDB
from visualize.builders.sequence_diagram import build_sequence_graph_json
from visualize.builders.dependency_graph import build_dependency_graph_json
import yaml

logger = logging.getLogger(__name__)


class VisualizationIntegrityTester:
    """Comprehensive testing for visualization integrity and silent failure detection"""
    
    def __init__(self, config_path: str = None):
        if config_path:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = self._get_default_config()
        
        self.validator = DataQualityValidator(self.config)
        self.analyzer = RelationshipAnalyzer(self.config)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for testing"""
        return {
            'database': {
                'project': {
                    'type': 'sqlite',
                    'sqlite': {
                        'path': './project/sampleSrc/data/metadata.db',
                        'wal_mode': True
                    }
                }
            }
        }
    
    def test_project_comprehensive(self, project_name: str) -> Dict[str, Any]:
        """Run comprehensive tests on a project"""
        test_results = {
            "project_name": project_name,
            "timestamp": None,
            "data_quality": None,
            "relationship_analysis": None,
            "visualization_tests": {},
            "silent_failures": [],
            "overall_health": "unknown"
        }
        
        try:
            # Get project ID
            db = VizDB(self.config, project_name)
            project_id = db.get_project_id_by_name(project_name)
            
            if not project_id:
                test_results["silent_failures"].append(f"Project '{project_name}' not found in database")
                test_results["overall_health"] = "critical"
                return test_results
            
            # Data quality validation
            logger.info(f"Running data quality validation for {project_name}")
            quality_report = self.validator.validate_project(project_id, project_name)
            test_results["data_quality"] = self._serialize_quality_report(quality_report)
            
            # Relationship analysis
            logger.info(f"Running relationship analysis for {project_name}")
            relationship_analysis = self.analyzer.analyze_project_relationships(db, project_id)
            test_results["relationship_analysis"] = relationship_analysis
            
            # Visualization-specific tests
            test_results["visualization_tests"] = self._test_all_visualizations(db, project_id)
            
            # Detect silent failures
            test_results["silent_failures"] = self._detect_silent_failures(test_results)
            
            # Calculate overall health
            test_results["overall_health"] = self._calculate_overall_health(test_results)
            test_results["timestamp"] = quality_report.timestamp.isoformat()
            
        except Exception as e:
            logger.error(f"Comprehensive test failed: {e}")
            test_results["silent_failures"].append(f"Test framework error: {str(e)}")
            test_results["overall_health"] = "critical"
        
        return test_results
    
    def _serialize_quality_report(self, report: DataQualityReport) -> Dict[str, Any]:
        """Serialize quality report for JSON output"""
        return {
            "overall_score": report.overall_score,
            "summary": report.summary,
            "potential_issues": report.potential_issues,
            "results_count": len(report.results),
            "critical_issues": [r.message for r in report.results if r.status == 'critical'],
            "error_issues": [r.message for r in report.results if r.status == 'error'],
            "warning_issues": [r.message for r in report.results if r.status == 'warning']
        }
    
    def _test_all_visualizations(self, db: VizDB, project_id: int) -> Dict[str, Any]:
        """Test all visualization types for data integrity"""
        viz_tests = {}
        
        # Test sequence diagram
        viz_tests["sequence_diagram"] = self._test_sequence_diagram(db, project_id)
        
        # Test dependency graph
        viz_tests["dependency_graph"] = self._test_dependency_graph(db, project_id)
        
        # Test ERD (if applicable)
        viz_tests["erd_diagram"] = self._test_erd_diagram(db, project_id)
        
        # Test class diagram
        viz_tests["class_diagram"] = self._test_class_diagram(db, project_id)
        
        return viz_tests
    
    def _test_sequence_diagram(self, db: VizDB, project_id: int) -> Dict[str, Any]:
        """Test sequence diagram generation and integrity"""
        test_result = {
            "status": "unknown",
            "data_generated": False,
            "participant_count": 0,
            "interaction_count": 0,
            "issues": [],
            "quality_indicators": {}
        }
        
        try:
            # Test with specific start point
            start_files = db.get_files_with_methods(project_id, limit=5)
            
            if not start_files:
                test_result["issues"].append("No files with methods found for sequence diagram")
                test_result["status"] = "error"
                return test_result
            
            # Try to build sequence diagram with first available file
            test_file = start_files[0]['file_path'] if isinstance(start_files[0], dict) else str(start_files[0])
            
            sequence_data = build_sequence_graph_json(
                self.config, project_id, None, 
                start_file=test_file, 
                start_method=None, 
                depth=2, 
                max_nodes=100
            )
            
            test_result["data_generated"] = True
            
            # Analyze generated data
            if sequence_data.get('type') == 'sequence_diagram':
                participants = sequence_data.get('participants', [])
                interactions = sequence_data.get('interactions', [])
                
                test_result["participant_count"] = len(participants)
                test_result["interaction_count"] = len(interactions)
                
                # Quality checks
                if len(participants) == 0:
                    test_result["issues"].append("No participants in sequence diagram")
                
                if len(interactions) == 0:
                    test_result["issues"].append("No interactions in sequence diagram - potential silent failure")
                
                # Check for meaningful content
                unique_participants = len(set(p.get('id') for p in participants))
                if unique_participants != len(participants):
                    test_result["issues"].append("Duplicate participants detected")
                
                # Check interaction quality
                inferred_count = sum(1 for i in interactions if 'inferred' in i.get('message', '').lower())
                if inferred_count == len(interactions):
                    test_result["issues"].append("All interactions are inferred - may indicate missing real call data")
                
                test_result["quality_indicators"] = {
                    "has_real_calls": inferred_count < len(interactions),
                    "participant_diversity": unique_participants / max(len(participants), 1),
                    "interaction_density": len(interactions) / max(len(participants), 1)
                }
            
            # Determine status
            if test_result["issues"]:
                test_result["status"] = "warning" if test_result["interaction_count"] > 0 else "error"
            else:
                test_result["status"] = "pass"
                
        except Exception as e:
            test_result["status"] = "error"
            test_result["issues"].append(f"Sequence diagram generation failed: {str(e)}")
            logger.error(f"Sequence diagram test failed: {e}")
        
        return test_result
    
    def _test_dependency_graph(self, db: VizDB, project_id: int) -> Dict[str, Any]:
        """Test dependency graph generation"""
        test_result = {
            "status": "unknown",
            "data_generated": False,
            "node_count": 0,
            "edge_count": 0,
            "issues": [],
            "quality_indicators": {}
        }
        
        try:
            # Build dependency graph
            dependency_data = build_dependency_graph_json(self.config, project_id, None)
            test_result["data_generated"] = True
            
            nodes = dependency_data.get('nodes', [])
            edges = dependency_data.get('edges', [])
            
            test_result["node_count"] = len(nodes)
            test_result["edge_count"] = len(edges)
            
            # Quality checks
            if len(nodes) == 0:
                test_result["issues"].append("No nodes in dependency graph")
            
            if len(edges) == 0:
                test_result["issues"].append("No edges in dependency graph - potential silent failure")
            
            # Check node types diversity
            node_types = set(n.get('type') for n in nodes)
            if len(node_types) < 2:
                test_result["issues"].append("Low node type diversity - may indicate incomplete analysis")
            
            test_result["quality_indicators"] = {
                "node_type_diversity": len(node_types),
                "connectivity": len(edges) / max(len(nodes), 1),
                "has_meaningful_relationships": len(edges) > 0
            }
            
            # Determine status
            if test_result["issues"]:
                test_result["status"] = "warning" if test_result["edge_count"] > 0 else "error"
            else:
                test_result["status"] = "pass"
                
        except Exception as e:
            test_result["status"] = "error"
            test_result["issues"].append(f"Dependency graph generation failed: {str(e)}")
            logger.error(f"Dependency graph test failed: {e}")
        
        return test_result
    
    def _test_erd_diagram(self, db: VizDB, project_id: int) -> Dict[str, Any]:
        """Test ERD diagram capabilities"""
        test_result = {
            "status": "unknown",
            "has_tables": False,
            "table_count": 0,
            "relationship_count": 0,
            "issues": []
        }
        
        try:
            session = db.session()
            
            # Check for database tables
            from visualize.data_access import DbTable, DbColumn
            table_count = session.query(DbTable).count()
            test_result["table_count"] = table_count
            test_result["has_tables"] = table_count > 0
            
            if table_count == 0:
                test_result["issues"].append("No database tables found - ERD not possible")
                test_result["status"] = "not_applicable"
            else:
                # Check for foreign key relationships
                fk_edges = db.fetch_edges(project_id, ['fk_inferred'], 0.0)
                test_result["relationship_count"] = len(fk_edges)
                
                if len(fk_edges) == 0:
                    test_result["issues"].append("No foreign key relationships found - ERD will be incomplete")
                    test_result["status"] = "warning"
                else:
                    test_result["status"] = "pass"
            
            session.close()
            
        except Exception as e:
            test_result["status"] = "error"
            test_result["issues"].append(f"ERD test failed: {str(e)}")
        
        return test_result
    
    def _test_class_diagram(self, db: VizDB, project_id: int) -> Dict[str, Any]:
        """Test class diagram data availability"""
        test_result = {
            "status": "unknown",
            "class_count": 0,
            "method_count": 0,
            "inheritance_count": 0,
            "issues": []
        }
        
        try:
            # Get class and method counts
            classes = session = db.session()
            
            from visualize.data_access import Class, Method, File
            class_count = session.query(Class).join(File).filter(File.project_id == project_id).count()
            method_count = session.query(Method).join(Class).join(File).filter(File.project_id == project_id).count()
            
            test_result["class_count"] = class_count
            test_result["method_count"] = method_count
            
            # Check for inheritance relationships
            inheritance_edges = db.fetch_edges(project_id, ['extends', 'implements'], 0.0)
            test_result["inheritance_count"] = len(inheritance_edges)
            
            # Quality checks
            if class_count == 0:
                test_result["issues"].append("No classes found for class diagram")
                test_result["status"] = "error"
            elif method_count == 0:
                test_result["issues"].append("Classes have no methods - diagram will be empty")
                test_result["status"] = "warning"
            elif class_count > 0 and method_count > 0:
                test_result["status"] = "pass"
            
            session.close()
            
        except Exception as e:
            test_result["status"] = "error"
            test_result["issues"].append(f"Class diagram test failed: {str(e)}")
        
        return test_result
    
    def _detect_silent_failures(self, test_results: Dict[str, Any]) -> List[str]:
        """Detect potential silent failures across all tests"""
        silent_failures = []
        
        # Check data quality issues
        data_quality = test_results.get("data_quality", {})
        if data_quality.get("overall_score", 0) < 30:
            silent_failures.append("Overall data quality is critically low")
        
        # Check for missing critical relationships
        relationship_analysis = test_results.get("relationship_analysis", {})
        missing_relationships = relationship_analysis.get("missing_relationships", {})
        
        if "method_call_chain" in missing_relationships:
            silent_failures.append("Method call relationships missing - sequence diagrams may be meaningless")
        
        # Check visualization results
        viz_tests = test_results.get("visualization_tests", {})
        
        for viz_type, viz_result in viz_tests.items():
            if viz_result.get("status") == "error":
                silent_failures.append(f"{viz_type} is completely broken")
            elif viz_result.get("status") == "warning":
                issues = viz_result.get("issues", [])
                for issue in issues:
                    if "silent failure" in issue or "meaningless" in issue or "empty" in issue:
                        silent_failures.append(f"{viz_type}: {issue}")
        
        # Check for patterns indicating silent failures
        sequence_result = viz_tests.get("sequence_diagram", {})
        if (sequence_result.get("participant_count", 0) > 0 and 
            sequence_result.get("interaction_count", 0) == 0):
            silent_failures.append("Sequence diagram has participants but no interactions - classic silent failure")
        
        return silent_failures
    
    def _calculate_overall_health(self, test_results: Dict[str, Any]) -> str:
        """Calculate overall health status"""
        silent_failures = test_results.get("silent_failures", [])
        data_quality = test_results.get("data_quality", {})
        
        if len(silent_failures) > 3:
            return "critical"
        elif data_quality.get("overall_score", 0) < 50:
            return "poor"
        elif len(silent_failures) > 0:
            return "warning"
        else:
            return "good"


# Pytest test functions
class TestVisualizationIntegrity:
    """Pytest test class for visualization integrity"""
    
    @pytest.fixture
    def config_path(self):
        """Get config path for testing"""
        return str(Path(__file__).parent.parent / "config" / "config.yaml")
    
    @pytest.fixture
    def tester(self, config_path):
        """Get tester instance"""
        return VisualizationIntegrityTester(config_path)
    
    def test_sample_project_integrity(self, tester):
        """Test the sample project for integrity issues"""
        results = tester.test_project_comprehensive("sampleSrc")
        
        # Assert basic functionality
        assert results["overall_health"] in ["good", "warning", "poor", "critical"]
        assert "data_quality" in results
        assert "visualization_tests" in results
        
        # Log results for analysis
        logger.info(f"Test results: {json.dumps(results, indent=2)}")
        
        # Fail if critical silent failures detected
        silent_failures = results.get("silent_failures", [])
        critical_failures = [f for f in silent_failures if "critical" in f.lower() or "broken" in f.lower()]
        
        assert len(critical_failures) == 0, f"Critical silent failures detected: {critical_failures}"
    
    def test_sequence_diagram_specific(self, tester):
        """Test sequence diagram specifically for silent failure patterns"""
        config = tester.config
        db = VizDB(config, "sampleSrc")
        project_id = db.get_project_id_by_name("sampleSrc")
        
        if project_id:
            result = tester._test_sequence_diagram(db, project_id)
            
            # Should generate some data
            assert result["data_generated"] is True
            
            # Should have participants
            assert result["participant_count"] > 0, "Sequence diagram should have participants"
            
            # Should have some interactions (even if inferred)
            assert result["interaction_count"] > 0, "Sequence diagram should have interactions to be meaningful"
    
    def test_data_quality_validation(self, tester):
        """Test data quality validation system"""
        db = VizDB(tester.config, "sampleSrc")
        project_id = db.get_project_id_by_name("sampleSrc")
        
        if project_id:
            report = tester.validator.validate_project(project_id, "sampleSrc")
            
            # Should generate a report
            assert isinstance(report.overall_score, float)
            assert 0 <= report.overall_score <= 100
            
            # Should have some validation results
            assert len(report.results) > 0
            
            # Should identify potential issues
            assert isinstance(report.potential_issues, list)


def run_comprehensive_test(project_name: str = "sampleSrc", output_file: str = None):
    """Run comprehensive test and optionally save results"""
    
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    tester = VisualizationIntegrityTester(str(config_path))
    
    print(f"Running comprehensive integrity test for project: {project_name}")
    results = tester.test_project_comprehensive(project_name)
    
    print(f"\n=== Test Results ===")
    print(f"Overall Health: {results['overall_health'].upper()}")
    print(f"Silent Failures Detected: {len(results.get('silent_failures', []))}")
    
    if results.get('silent_failures'):
        print("\nSilent Failures:")
        for failure in results['silent_failures']:
            print(f"  - {failure}")
    
    data_quality = results.get('data_quality', {})
    print(f"\nData Quality Score: {data_quality.get('overall_score', 0):.1f}/100")
    
    viz_tests = results.get('visualization_tests', {})
    print(f"\nVisualization Tests:")
    for viz_type, viz_result in viz_tests.items():
        status = viz_result.get('status', 'unknown').upper()
        print(f"  - {viz_type}: {status}")
        
        if viz_result.get('issues'):
            for issue in viz_result['issues']:
                print(f"    └─ {issue}")
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nDetailed results saved to: {output_file}")
    
    return results


if __name__ == "__main__":
    # Run standalone test
    import argparse
    
    parser = argparse.ArgumentParser(description='Run comprehensive visualization integrity tests')
    parser.add_argument('--project', default='sampleSrc', help='Project name to test')
    parser.add_argument('--output', help='Output file for detailed results')
    
    args = parser.parse_args()
    
    run_comprehensive_test(args.project, args.output)