"""
Comprehensive System Tests for SourceAnalyzer

Tests for silent failure detection, data quality validation, and overall system health.
Includes automated testing for all visualization types and edge cases.
"""

import unittest
import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from visualize.data_access import DatabaseManager
from phase1.validation.data_quality_validator import DataQualityValidator
from phase1.monitoring.silent_failure_detector import SilentFailureDetector
from visualize.analyzers.relationship_analyzer import RelationshipAnalyzer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComprehensiveSystemTests(unittest.TestCase):
    """Comprehensive system health and integrity tests"""
    
    def setUp(self):
        """Setup test environment"""
        self.project_name = "sampleSrc"
        self.db_manager = DatabaseManager(self.project_name)
        self.validator = DataQualityValidator(self.project_name)
        self.detector = SilentFailureDetector(self.project_name)
        
    def test_database_connectivity(self):
        """Test basic database connectivity and data presence"""
        with self.db_manager.get_session() as session:
            # Test basic queries
            node_count = session.execute("SELECT COUNT(*) FROM nodes").scalar()
            edge_count = session.execute("SELECT COUNT(*) FROM edges").scalar()
            
            self.assertGreater(node_count, 0, "Database should contain nodes")
            self.assertGreater(edge_count, 0, "Database should contain edges")
            
            logger.info(f"Database connectivity OK: {node_count} nodes, {edge_count} edges")
    
    def test_data_quality_validation(self):
        """Test comprehensive data quality validation"""
        quality_report = self.validator.validate_project()
        
        # Check report structure
        self.assertIn('overall_score', quality_report)
        self.assertIn('issues', quality_report)
        self.assertIn('recommendations', quality_report)
        
        # Score should be reasonable
        score = quality_report.get('overall_score', 0)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
        
        logger.info(f"Data quality score: {score:.1%}")
        
        # Log issues if any
        issues = quality_report.get('issues', [])
        if issues:
            logger.warning(f"Data quality issues found: {len(issues)}")
            for issue in issues[:3]:  # Show first 3 issues
                logger.warning(f"  - {issue.get('message', 'Unknown issue')}")
    
    def test_silent_failure_detection(self):
        """Test that silent failure detection works correctly"""
        alerts = self.detector.detect_all_failures()
        
        # Check that detector runs without errors
        self.assertIsInstance(alerts, list)
        
        # Generate and verify report structure
        report = self.detector.generate_alert_report()
        self.assertIn('project_name', report)
        self.assertIn('status', report)
        self.assertIn('total_alerts', report)
        
        logger.info(f"Silent failure detection found {len(alerts)} issues")
        
        # Log detected alerts
        for alert in alerts:
            severity = alert.severity.upper()
            logger.info(f"  [{severity}] {alert.component}: {alert.description}")
        
        # Test that the known sequence diagram issue is detected (if present)
        sequence_alerts = [a for a in alerts if a.component == 'sequence_diagram']
        if sequence_alerts:
            method_interaction_alerts = [a for a in sequence_alerts 
                                       if 'no_method_interactions' in a.failure_type]
            if method_interaction_alerts:
                logger.info("✓ Successfully detected sequence diagram silent failure")
    
    def test_sequence_diagram_health(self):
        """Test sequence diagram specific health"""
        try:
            with self.db_manager.get_session() as session:
                method_count = session.execute("SELECT COUNT(*) FROM nodes WHERE type = 'method'").scalar()
                method_edges = session.execute("""
                    SELECT COUNT(*) FROM edges 
                    WHERE source_type = 'method' AND target_type = 'method'
                    AND kind IN ('call', 'call_unresolved')
                """).scalar()
                
                logger.info(f"Sequence diagram health: {method_count} methods, {method_edges} interactions")
                
                # Test for the classic silent failure pattern
                if method_count > 20 and method_edges == 0:
                    logger.warning("⚠️  Classic silent failure detected: many methods but no interactions")
                    self.fail(f"Silent failure: {method_count} methods but 0 interactions")
                
                # Test interaction density
                if method_count > 0:
                    interaction_ratio = method_edges / method_count
                    logger.info(f"Interaction density: {interaction_ratio:.2%}")
                    
                    if interaction_ratio < 0.05:  # Less than 5%
                        logger.warning("⚠️  Very low interaction density detected")
        
        except Exception as e:
            self.fail(f"Sequence diagram health check failed: {e}")
    
    def test_dependency_graph_health(self):
        """Test dependency graph specific health"""
        try:
            with self.db_manager.get_session() as session:
                file_count = session.execute("SELECT COUNT(*) FROM nodes WHERE type = 'file'").scalar()
                file_edges = session.execute("""
                    SELECT COUNT(*) FROM edges 
                    WHERE (source_type = 'file' OR target_type = 'file')
                    AND kind IN ('import', 'include', 'dependency')
                """).scalar()
                
                logger.info(f"Dependency graph health: {file_count} files, {file_edges} dependencies")
                
                if file_count > 10 and file_edges < 5:
                    logger.warning("⚠️  Low file dependency count - may indicate parsing issues")
                    
                # Check for package relationships as fallback
                package_edges = session.execute("""
                    SELECT COUNT(*) FROM edges 
                    WHERE kind = 'package_relation'
                """).scalar()
                
                logger.info(f"Package relationships available: {package_edges}")
        
        except Exception as e:
            self.fail(f"Dependency graph health check failed: {e}")
    
    def test_erd_health(self):
        """Test ERD specific health"""
        try:
            with self.db_manager.get_session() as session:
                table_count = session.execute("SELECT COUNT(*) FROM nodes WHERE type = 'table'").scalar()
                table_relations = session.execute("""
                    SELECT COUNT(*) FROM edges 
                    WHERE (source_type = 'table' OR target_type = 'table')
                    AND kind IN ('foreign_key', 'references', 'uses')
                """).scalar()
                
                logger.info(f"ERD health: {table_count} tables, {table_relations} relationships")
                
                if table_count == 0:
                    logger.info("No tables found - ERD not applicable")
                elif table_count > 5 and table_relations < 2:
                    logger.warning("⚠️  Many tables but few relationships - may need better FK detection")
        
        except Exception as e:
            logger.error(f"ERD health check failed: {e}")
    
    def test_class_diagram_health(self):
        """Test class diagram specific health"""
        try:
            with self.db_manager.get_session() as session:
                class_count = session.execute("SELECT COUNT(*) FROM nodes WHERE type = 'class'").scalar()
                classes_with_methods = session.execute("""
                    SELECT COUNT(DISTINCT parent_id) FROM nodes 
                    WHERE type = 'method' AND parent_id IS NOT NULL
                """).scalar()
                
                logger.info(f"Class diagram health: {class_count} classes, {classes_with_methods} with methods")
                
                if class_count > 0:
                    method_coverage = classes_with_methods / class_count
                    logger.info(f"Method coverage: {method_coverage:.1%}")
                    
                    if method_coverage < 0.3:
                        logger.warning("⚠️  Low method coverage - many empty classes detected")
        
        except Exception as e:
            logger.error(f"Class diagram health check failed: {e}")
    
    def test_relationship_analysis(self):
        """Test relationship analysis functionality"""
        try:
            analyzer = RelationshipAnalyzer(self.project_name)
            
            with self.db_manager.get_session() as session:
                # Test edge type analysis
                edge_types = session.execute("SELECT DISTINCT kind FROM edges").fetchall()
                edge_type_list = [row[0] for row in edge_types]
                
                logger.info(f"Available edge types: {edge_type_list}")
                
                # Test relationship pattern detection
                analysis_result = analyzer.analyze_relationship_patterns(session)
                
                self.assertIn('patterns', analysis_result)
                self.assertIn('recommendations', analysis_result)
                
                logger.info(f"Relationship analysis completed with {len(analysis_result.get('patterns', []))} patterns")
        
        except Exception as e:
            logger.error(f"Relationship analysis failed: {e}")
    
    def test_comprehensive_project_health(self):
        """Comprehensive test of project health across all systems"""
        health_issues = []
        
        # Test each component
        component_tests = [
            ('Database Connection', self._test_database_connection),
            ('Data Quality', self._test_data_quality_summary),
            ('Silent Failure Detection', self._test_silent_failure_summary),
            ('Sequence Diagram', self._test_sequence_summary),
            ('Dependency Graph', self._test_dependency_summary),
            ('ERD', self._test_erd_summary),
            ('Class Diagram', self._test_class_summary)
        ]
        
        test_results = {}
        
        for component_name, test_func in component_tests:
            try:
                logger.info(f"Testing {component_name}...")
                result = test_func()
                test_results[component_name] = result
                
                if not result.get('healthy', True):
                    health_issues.extend(result.get('issues', []))
                
                logger.info(f"✓ {component_name}: {'HEALTHY' if result.get('healthy', True) else 'ISSUES FOUND'}")
                
            except Exception as e:
                logger.error(f"❌ {component_name}: ERROR - {e}")
                health_issues.append(f"{component_name} test failed: {str(e)}")
                test_results[component_name] = {'healthy': False, 'error': str(e)}
        
        # Generate summary
        logger.info(f"\n{'='*60}")
        logger.info(f"PROJECT HEALTH SUMMARY FOR: {self.project_name}")
        logger.info(f"{'='*60}")
        
        if health_issues:
            logger.warning(f"⚠️  Health Issues Found ({len(health_issues)} total):")
            for i, issue in enumerate(health_issues, 1):
                logger.warning(f"  {i}. {issue}")
        else:
            logger.info(f"✅ Project '{self.project_name}' appears healthy")
        
        # Save detailed results
        self._save_health_report(test_results, health_issues)
        
        return len(health_issues) == 0
    
    def _test_database_connection(self) -> Dict[str, Any]:
        """Test basic database connectivity"""
        try:
            with self.db_manager.get_session() as session:
                node_count = session.execute("SELECT COUNT(*) FROM nodes").scalar()
                edge_count = session.execute("SELECT COUNT(*) FROM edges").scalar()
                
                if node_count > 0 and edge_count > 0:
                    return {'healthy': True, 'node_count': node_count, 'edge_count': edge_count}
                else:
                    return {'healthy': False, 'issues': ['Database contains no meaningful data']}
        except Exception as e:
            return {'healthy': False, 'issues': [f'Database connection failed: {e}']}
    
    def _test_data_quality_summary(self) -> Dict[str, Any]:
        """Test overall data quality"""
        try:
            quality_report = self.validator.validate_project()
            score = quality_report.get('overall_score', 0)
            issues = quality_report.get('issues', [])
            
            if score > 0.6:  # Above 60%
                return {'healthy': True, 'score': score}
            else:
                critical_issues = [issue.get('message', 'Unknown') for issue in issues 
                                 if issue.get('severity') == 'high']
                return {'healthy': False, 'issues': critical_issues[:3], 'score': score}
        except Exception as e:
            return {'healthy': False, 'issues': [f'Data quality check failed: {e}']}
    
    def _test_silent_failure_summary(self) -> Dict[str, Any]:
        """Test silent failure detection"""
        try:
            alerts = self.detector.detect_all_failures()
            critical_alerts = [a for a in alerts if a.severity in ['critical', 'high']]
            
            if len(critical_alerts) == 0:
                return {'healthy': True, 'alert_count': len(alerts)}
            else:
                issues = [f"{a.component}: {a.description}" for a in critical_alerts]
                return {'healthy': False, 'issues': issues}
        except Exception as e:
            return {'healthy': False, 'issues': [f'Silent failure detection failed: {e}']}
    
    def _test_sequence_summary(self) -> Dict[str, Any]:
        """Test sequence diagram health summary"""
        try:
            with self.db_manager.get_session() as session:
                method_count = session.execute("SELECT COUNT(*) FROM nodes WHERE type = 'method'").scalar()
                method_edges = session.execute("""
                    SELECT COUNT(*) FROM edges 
                    WHERE source_type = 'method' AND target_type = 'method'
                    AND kind IN ('call', 'call_unresolved')
                """).scalar()
                
                issues = []
                if method_count > 20 and method_edges == 0:
                    issues.append(f"Silent failure: {method_count} methods but 0 interactions")
                
                if method_count > 0 and (method_edges / method_count) < 0.05:
                    issues.append(f"Very low interaction density: {method_edges}/{method_count}")
                
                return {'healthy': len(issues) == 0, 'issues': issues, 
                       'method_count': method_count, 'interaction_count': method_edges}
        except Exception as e:
            return {'healthy': False, 'issues': [f'Sequence health check failed: {e}']}
    
    def _test_dependency_summary(self) -> Dict[str, Any]:
        """Test dependency graph health summary"""
        try:
            with self.db_manager.get_session() as session:
                file_count = session.execute("SELECT COUNT(*) FROM nodes WHERE type = 'file'").scalar()
                file_edges = session.execute("""
                    SELECT COUNT(*) FROM edges 
                    WHERE (source_type = 'file' OR target_type = 'file')
                    AND kind IN ('import', 'include', 'dependency', 'package_relation')
                """).scalar()
                
                issues = []
                if file_count > 10 and file_edges < 5:
                    issues.append(f"Low dependency count: {file_edges} for {file_count} files")
                
                return {'healthy': len(issues) == 0, 'issues': issues}
        except Exception as e:
            return {'healthy': False, 'issues': [f'Dependency health check failed: {e}']}
    
    def _test_erd_summary(self) -> Dict[str, Any]:
        """Test ERD health summary"""
        try:
            with self.db_manager.get_session() as session:
                table_count = session.execute("SELECT COUNT(*) FROM nodes WHERE type = 'table'").scalar()
                
                if table_count == 0:
                    return {'healthy': True, 'note': 'No tables found - ERD not applicable'}
                
                table_relations = session.execute("""
                    SELECT COUNT(*) FROM edges 
                    WHERE (source_type = 'table' OR target_type = 'table')
                """).scalar()
                
                issues = []
                if table_count > 5 and table_relations < 2:
                    issues.append(f"Isolated tables: {table_count} tables but {table_relations} relationships")
                
                return {'healthy': len(issues) == 0, 'issues': issues}
        except Exception as e:
            return {'healthy': False, 'issues': [f'ERD health check failed: {e}']}
    
    def _test_class_summary(self) -> Dict[str, Any]:
        """Test class diagram health summary"""
        try:
            with self.db_manager.get_session() as session:
                class_count = session.execute("SELECT COUNT(*) FROM nodes WHERE type = 'class'").scalar()
                
                if class_count == 0:
                    return {'healthy': True, 'note': 'No classes found'}
                
                classes_with_methods = session.execute("""
                    SELECT COUNT(DISTINCT parent_id) FROM nodes 
                    WHERE type = 'method' AND parent_id IS NOT NULL
                """).scalar()
                
                method_coverage = classes_with_methods / class_count
                issues = []
                
                if method_coverage < 0.3:
                    issues.append(f"Low method coverage: {method_coverage:.1%} of classes have methods")
                
                return {'healthy': len(issues) == 0, 'issues': issues}
        except Exception as e:
            return {'healthy': False, 'issues': [f'Class health check failed: {e}']}
    
    def _save_health_report(self, test_results: Dict[str, Any], health_issues: List[str]):
        """Save comprehensive health report"""
        report = {
            'project_name': self.project_name,
            'timestamp': datetime.now().isoformat(),
            'overall_health': 'healthy' if len(health_issues) == 0 else 'issues_detected',
            'total_issues': len(health_issues),
            'health_issues': health_issues,
            'component_results': test_results,
            'recommendations': self._generate_health_recommendations(health_issues, test_results)
        }
        
        output_path = f"output/{self.project_name}/comprehensive_health_report.json"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Comprehensive health report saved to: {output_path}")
    
    def _generate_health_recommendations(self, health_issues: List[str], 
                                       test_results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on health analysis"""
        recommendations = []
        
        # Check for specific patterns in issues
        sequence_issues = [issue for issue in health_issues if 'sequence' in issue.lower()]
        if sequence_issues:
            recommendations.append("Run code analysis with improved method call extraction")
            recommendations.append("Check if static analysis is capturing all call relationships")
        
        dependency_issues = [issue for issue in health_issues if 'dependency' in issue.lower()]
        if dependency_issues:
            recommendations.append("Improve import/dependency parsing for better file relationships")
            recommendations.append("Verify that package relationships are being extracted correctly")
        
        data_quality_result = test_results.get('Data Quality', {})
        if not data_quality_result.get('healthy', True):
            recommendations.append("Re-run data extraction and analysis phases")
            recommendations.append("Check for incomplete or corrupted analysis results")
        
        if len(health_issues) > 5:
            recommendations.append("Consider re-running the entire analysis pipeline")
            recommendations.append("Review project structure and analysis configuration")
        
        return recommendations


def run_comprehensive_tests(project_name: str = "sampleSrc"):
    """Run all comprehensive tests for a project"""
    print(f"Running comprehensive system tests for project: {project_name}")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add all tests
    test_class = ComprehensiveSystemTests
    test_class.project_name = project_name  # Set project name
    
    test_methods = [
        'test_database_connectivity',
        'test_data_quality_validation', 
        'test_silent_failure_detection',
        'test_sequence_diagram_health',
        'test_dependency_graph_health',
        'test_erd_health',
        'test_class_diagram_health',
        'test_relationship_analysis',
        'test_comprehensive_project_health'
    ]
    
    for method in test_methods:
        suite.addTest(test_class(method))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print(f"\n{'=' * 60}")
    print(f"TEST SUMMARY")
    print(f"{'=' * 60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run comprehensive system tests")
    parser.add_argument("--project-name", default="sampleSrc", help="Project name to test")
    
    args = parser.parse_args()
    
    success = run_comprehensive_tests(args.project_name)
    exit(0 if success else 1)