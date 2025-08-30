"""
Confidence Formula Validation Framework
Addresses critical issue #22 from forensic analysis - validates confidence calculations against ground truth data
"""

from typing import Dict, List, Any, Optional, Tuple, Set
import json
import os
import statistics
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path

from .confidence_calculator import ConfidenceCalculator, ParseResult
from .logger import LoggerFactory


@dataclass
class GroundTruthEntry:
    """Ground truth data entry for validation"""
    file_path: str
    parser_type: str
    expected_confidence: float  # Human-verified accuracy
    expected_classes: int
    expected_methods: int
    expected_sql_units: int
    verified_tables: List[str]
    complexity_factors: Dict[str, Any]
    notes: str = ""
    verifier: str = ""
    verification_date: str = ""
    
    def __post_init__(self):
        if not self.verification_date:
            self.verification_date = datetime.now().isoformat()


@dataclass
class ValidationResult:
    """Validation result for a single confidence calculation"""
    ground_truth_id: str
    predicted_confidence: float
    actual_confidence: float
    absolute_error: float
    relative_error: float
    factor_breakdown: Dict[str, float]
    calibrated: bool = False


class ConfidenceValidator:
    """
    Validates confidence formula accuracy against ground truth data
    Provides calibration and improvement recommendations
    """
    
    def __init__(self, config: Dict[str, Any], confidence_calc: ConfidenceCalculator):
        self.config = config
        self.confidence_calc = confidence_calc
        self.logger = LoggerFactory.get_logger("confidence_validator")
        
        # Ground truth data storage
        self.ground_truth_path = config.get('validation', {}).get(
            'ground_truth_path', 'ground_truth_data.json'
        )
        self.ground_truth_data: List[GroundTruthEntry] = []
        
        # Validation thresholds
        validation_config = config.get('validation', {})
        self.error_thresholds = validation_config.get('error_thresholds', {
            'excellent': 0.05,   # <5% error
            'good': 0.10,        # <10% error
            'acceptable': 0.20,  # <20% error
            'poor': 0.20         # >=20% error
        })
        
        # Calibration parameters
        self.calibration_params = {
            'ast_weight_range': (0.2, 0.6),
            'static_weight_range': (0.1, 0.4),
            'db_weight_range': (0.1, 0.3),
            'heuristic_weight_range': (0.05, 0.15)
        }
        
        self.load_ground_truth_data()
    
    def load_ground_truth_data(self):
        """Load ground truth data from JSON file"""
        try:
            if os.path.exists(self.ground_truth_path):
                with open(self.ground_truth_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.ground_truth_data = [
                        GroundTruthEntry(**entry) for entry in data
                    ]
                self.logger.info(f"Loaded {len(self.ground_truth_data)} ground truth entries")
            else:
                self.logger.warning(f"Ground truth file not found: {self.ground_truth_path}")
                self._create_sample_ground_truth()
        except Exception as e:
            self.logger.error(f"Failed to load ground truth data: {e}")
            self.ground_truth_data = []
    
    def save_ground_truth_data(self):
        """Save ground truth data to JSON file"""
        try:
            with open(self.ground_truth_path, 'w', encoding='utf-8') as f:
                json.dump([asdict(entry) for entry in self.ground_truth_data], f, 
                         indent=2, ensure_ascii=False)
            self.logger.info(f"Saved {len(self.ground_truth_data)} ground truth entries")
        except Exception as e:
            self.logger.error(f"Failed to save ground truth data: {e}")
    
    def add_ground_truth_entry(self, entry: GroundTruthEntry):
        """Add a new ground truth entry"""
        self.ground_truth_data.append(entry)
        self.save_ground_truth_data()
    
    def validate_confidence_formula(self) -> Dict[str, Any]:
        """
        Validate confidence formula against all ground truth data
        
        Returns:
            Comprehensive validation report
        """
        if not self.ground_truth_data:
            return {
                'error': 'No ground truth data available for validation',
                'recommendations': ['Create ground truth dataset', 'Run manual verification']
            }
        
        validation_results = []
        
        for gt_entry in self.ground_truth_data:
            # Create ParseResult from ground truth
            parse_result = self._create_parse_result_from_ground_truth(gt_entry)
            
            # Calculate confidence
            predicted_confidence, factors = self.confidence_calc.calculate_parsing_confidence(parse_result)
            
            # Calculate validation metrics
            abs_error = abs(predicted_confidence - gt_entry.expected_confidence)
            rel_error = abs_error / max(gt_entry.expected_confidence, 0.01)
            
            result = ValidationResult(
                ground_truth_id=f"{gt_entry.file_path}:{gt_entry.parser_type}",
                predicted_confidence=predicted_confidence,
                actual_confidence=gt_entry.expected_confidence,
                absolute_error=abs_error,
                relative_error=rel_error,
                factor_breakdown=factors
            )
            
            validation_results.append(result)
        
        # Calculate overall statistics
        return self._generate_validation_report(validation_results)
    
    def calibrate_weights(self) -> Dict[str, Any]:
        """
        Auto-calibrate confidence formula weights to minimize validation error
        
        Returns:
            Calibration results and recommended weight adjustments
        """
        if len(self.ground_truth_data) < 10:
            return {
                'error': 'Need at least 10 ground truth entries for calibration',
                'current_count': len(self.ground_truth_data)
            }
        
        best_weights = self.confidence_calc.weights.copy()
        best_error = float('inf')
        calibration_attempts = []
        
        # Grid search for optimal weights
        import itertools
        
        ast_range = self._generate_weight_range(self.calibration_params['ast_weight_range'])
        static_range = self._generate_weight_range(self.calibration_params['static_weight_range'])
        db_range = self._generate_weight_range(self.calibration_params['db_weight_range'])
        
        for ast_w, static_w, db_w in itertools.product(ast_range, static_range, db_range):
            # Ensure weights sum to reasonable total (0.8-1.2)
            heuristic_w = max(0.05, min(0.15, 1.0 - ast_w - static_w - db_w))
            total_weight = ast_w + static_w + db_w + heuristic_w
            
            if 0.8 <= total_weight <= 1.2:
                # Test these weights
                test_weights = {
                    'ast': ast_w,
                    'static': static_w,
                    'db_match': db_w,
                    'heuristic': heuristic_w
                }
                
                # Calculate error with these weights
                error = self._calculate_validation_error_with_weights(test_weights)
                calibration_attempts.append({
                    'weights': test_weights,
                    'mean_absolute_error': error
                })
                
                if error < best_error:
                    best_error = error
                    best_weights = test_weights
        
        # Analyze calibration results
        current_error = self._calculate_validation_error_with_weights(self.confidence_calc.weights)
        improvement = current_error - best_error
        
        return {
            'current_weights': self.confidence_calc.weights,
            'current_mae': current_error,
            'best_weights': best_weights,
            'best_mae': best_error,
            'improvement': improvement,
            'improvement_percentage': (improvement / current_error) * 100 if current_error > 0 else 0,
            'calibration_attempts': len(calibration_attempts),
            'recommendation': 'apply' if improvement > 0.02 else 'current_weights_adequate'
        }
    
    def generate_confidence_accuracy_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive confidence accuracy report
        Addresses the core validation requirements from forensic analysis
        """
        validation_report = self.validate_confidence_formula()
        calibration_report = self.calibrate_weights()
        
        # Additional analysis
        confidence_distribution = self._analyze_confidence_distribution()
        factor_importance = self._analyze_factor_importance()
        
        return {
            'validation_report': validation_report,
            'calibration_report': calibration_report,
            'confidence_distribution': confidence_distribution,
            'factor_importance': factor_importance,
            'recommendations': self._generate_improvement_recommendations(
                validation_report, calibration_report
            ),
            'generation_timestamp': datetime.now().isoformat()
        }
    
    def _create_parse_result_from_ground_truth(self, gt_entry: GroundTruthEntry) -> ParseResult:
        """Create ParseResult from ground truth entry for testing"""
        return ParseResult(
            file_path=gt_entry.file_path,
            parser_type=gt_entry.parser_type,
            success=True,
            parse_time=1.0,  # Default
            ast_complete=gt_entry.complexity_factors.get('ast_complete', True),
            classes=gt_entry.expected_classes,
            methods=gt_entry.expected_methods,
            sql_units=gt_entry.expected_sql_units,
            matched_patterns=gt_entry.complexity_factors.get('matched_patterns', []),
            total_patterns=gt_entry.complexity_factors.get('total_patterns', 10),
            referenced_tables=gt_entry.verified_tables,
            confirmed_tables=gt_entry.verified_tables,
            db_matches=len(gt_entry.verified_tables) > 0,
            dynamic_sql=gt_entry.complexity_factors.get('dynamic_sql', False),
            reflection_usage=gt_entry.complexity_factors.get('reflection_usage', False),
            complex_expressions=gt_entry.complexity_factors.get('complex_expressions', 0),
            nested_conditions=gt_entry.complexity_factors.get('nested_conditions', 0)
        )
    
    def _generate_validation_report(self, validation_results: List[ValidationResult]) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        if not validation_results:
            return {'error': 'No validation results available'}
        
        # Calculate metrics
        absolute_errors = [r.absolute_error for r in validation_results]
        relative_errors = [r.relative_error for r in validation_results]
        
        # Error distribution
        excellent_count = sum(1 for e in absolute_errors if e <= self.error_thresholds['excellent'])
        good_count = sum(1 for e in absolute_errors if self.error_thresholds['excellent'] < e <= self.error_thresholds['good'])
        acceptable_count = sum(1 for e in absolute_errors if self.error_thresholds['good'] < e <= self.error_thresholds['acceptable'])
        poor_count = sum(1 for e in absolute_errors if e > self.error_thresholds['acceptable'])
        
        return {
            'total_validations': len(validation_results),
            'mean_absolute_error': statistics.mean(absolute_errors),
            'median_absolute_error': statistics.median(absolute_errors),
            'std_absolute_error': statistics.stdev(absolute_errors) if len(absolute_errors) > 1 else 0,
            'mean_relative_error': statistics.mean(relative_errors),
            'error_distribution': {
                'excellent': {'count': excellent_count, 'percentage': excellent_count / len(validation_results)},
                'good': {'count': good_count, 'percentage': good_count / len(validation_results)},
                'acceptable': {'count': acceptable_count, 'percentage': acceptable_count / len(validation_results)},
                'poor': {'count': poor_count, 'percentage': poor_count / len(validation_results)}
            },
            'worst_predictions': sorted(validation_results, key=lambda x: x.absolute_error, reverse=True)[:5],
            'best_predictions': sorted(validation_results, key=lambda x: x.absolute_error)[:5],
            'validation_details': validation_results
        }
    
    def _calculate_validation_error_with_weights(self, weights: Dict[str, float]) -> float:
        """Calculate validation error with specific weight configuration"""
        # Temporarily change weights
        original_weights = self.confidence_calc.weights.copy()
        self.confidence_calc.weights = weights
        
        try:
            errors = []
            for gt_entry in self.ground_truth_data:
                parse_result = self._create_parse_result_from_ground_truth(gt_entry)
                predicted_confidence, _ = self.confidence_calc.calculate_parsing_confidence(parse_result)
                error = abs(predicted_confidence - gt_entry.expected_confidence)
                errors.append(error)
            
            return statistics.mean(errors) if errors else float('inf')
        finally:
            # Restore original weights
            self.confidence_calc.weights = original_weights
    
    def _generate_weight_range(self, weight_range: Tuple[float, float], steps: int = 5) -> List[float]:
        """Generate weight range for grid search"""
        min_w, max_w = weight_range
        step_size = (max_w - min_w) / (steps - 1)
        return [min_w + i * step_size for i in range(steps)]
    
    def _analyze_confidence_distribution(self) -> Dict[str, Any]:
        """Analyze confidence score distribution patterns"""
        if not self.ground_truth_data:
            return {}
        
        expected_confidences = [entry.expected_confidence for entry in self.ground_truth_data]
        
        return {
            'mean_expected_confidence': statistics.mean(expected_confidences),
            'median_expected_confidence': statistics.median(expected_confidences),
            'confidence_range': {
                'min': min(expected_confidences),
                'max': max(expected_confidences),
                'std': statistics.stdev(expected_confidences) if len(expected_confidences) > 1 else 0
            },
            'confidence_bins': self._create_confidence_bins(expected_confidences)
        }
    
    def _create_confidence_bins(self, confidences: List[float]) -> Dict[str, int]:
        """Create confidence bins for distribution analysis"""
        bins = {'0.0-0.2': 0, '0.2-0.4': 0, '0.4-0.6': 0, '0.6-0.8': 0, '0.8-1.0': 0}
        
        for conf in confidences:
            if conf < 0.2:
                bins['0.0-0.2'] += 1
            elif conf < 0.4:
                bins['0.2-0.4'] += 1
            elif conf < 0.6:
                bins['0.4-0.6'] += 1
            elif conf < 0.8:
                bins['0.6-0.8'] += 1
            else:
                bins['0.8-1.0'] += 1
        
        return bins
    
    def _analyze_factor_importance(self) -> Dict[str, float]:
        """Analyze importance of different confidence factors"""
        # This would require more sophisticated analysis
        # For now, return current weights as proxy for importance
        return self.confidence_calc.weights.copy()
    
    def _generate_improvement_recommendations(self, validation_report: Dict[str, Any], 
                                           calibration_report: Dict[str, Any]) -> List[str]:
        """Generate specific improvement recommendations"""
        recommendations = []
        
        # Validation-based recommendations
        if 'mean_absolute_error' in validation_report:
            mae = validation_report['mean_absolute_error']
            if mae > 0.15:
                recommendations.append("High validation error detected - review confidence formula")
            elif mae > 0.10:
                recommendations.append("Moderate validation error - consider weight adjustment")
        
        # Calibration-based recommendations  
        if 'improvement' in calibration_report:
            if calibration_report['improvement'] > 0.02:
                recommendations.append(f"Apply calibrated weights for {calibration_report['improvement_percentage']:.1f}% improvement")
        
        # Distribution-based recommendations
        if len(self.ground_truth_data) < 50:
            recommendations.append("Expand ground truth dataset for better validation")
        
        return recommendations
    
    def _create_sample_ground_truth(self):
        """Create sample ground truth data for testing"""
        sample_data = [
            GroundTruthEntry(
                file_path="test/sample/SimpleClass.java",
                parser_type="javalang",
                expected_confidence=0.92,
                expected_classes=1,
                expected_methods=3,
                expected_sql_units=0,
                verified_tables=[],
                complexity_factors={
                    "ast_complete": True,
                    "total_patterns": 5,
                    "matched_patterns": ["class", "method", "field"],
                    "dynamic_sql": False,
                    "reflection_usage": False,
                    "complex_expressions": 0,
                    "nested_conditions": 1
                },
                notes="Simple Java class with clear structure",
                verifier="system_generated"
            ),
            GroundTruthEntry(
                file_path="test/sample/ComplexSQL.jsp",
                parser_type="jsp_mybatis",
                expected_confidence=0.65,
                expected_classes=0,
                expected_methods=0,
                expected_sql_units=3,
                verified_tables=["users", "orders", "products"],
                complexity_factors={
                    "ast_complete": False,
                    "total_patterns": 8,
                    "matched_patterns": ["select", "join", "where"],
                    "dynamic_sql": True,
                    "reflection_usage": False,
                    "complex_expressions": 2,
                    "nested_conditions": 3
                },
                notes="JSP with complex dynamic SQL",
                verifier="system_generated"
            )
        ]
        
        self.ground_truth_data = sample_data
        self.save_ground_truth_data()
        self.logger.info("Created sample ground truth data")


class ConfidenceCalibrator:
    """
    Applies validated confidence calibration adjustments
    """
    
    def __init__(self, validator: ConfidenceValidator):
        self.validator = validator
        self.logger = LoggerFactory.get_logger("confidence_calibrator")
    
    def apply_calibration(self, confidence_calc: ConfidenceCalculator) -> bool:
        """Apply calibrated weights to confidence calculator"""
        try:
            calibration_result = self.validator.calibrate_weights()
            
            if calibration_result.get('recommendation') == 'apply':
                best_weights = calibration_result['best_weights']
                old_weights = confidence_calc.weights.copy()
                
                confidence_calc.weights = best_weights
                
                self.logger.info(f"Applied calibrated weights: {best_weights}")
                self.logger.info(f"Expected improvement: {calibration_result['improvement_percentage']:.2f}%")
                
                return True
            else:
                self.logger.info("Current weights are adequate - no calibration applied")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to apply calibration: {e}")
            return False