# Source Analyzer 정확성 개선 설계 문서

**설계 목표**: 현재 65-75% 정확성을 85%+로 개선  
**설계 원칙**: 단계적 구현, 백워드 호환성, 검증 가능성  
**설계 일시**: 2025-08-28

---

## 1. 아키텍처 설계: 정확성 중심 재구조화

### 1.1 현재 아키텍처 문제점
```
[파일 입력] → [파서들] → [신뢰도 계산] → [메타데이터 저장] → [시각화]
     ↓           ↓          ↓              ↓               ↓
  에러 전파    부정확     검증되지 않음    세션 누수      불일치
```

### 1.2 개선된 아키텍처 설계
```
[파일 입력] → [검증된 파서] → [캘리브레이션된 신뢰도] → [안전한 저장] → [일관성 보장 시각화]
     ↓            ↓               ↓                  ↓                ↓
  오류 회복    Fallback      Ground Truth 기반    세션 관리         검증된 데이터
```

### 1.3 핵심 설계 패턴

#### A. Parser Chain Pattern (정확성 향상)
```python
class ParserChain:
    def __init__(self):
        self.parsers = [
            PrimaryParser(),    # 주 파서 (예: javalang)
            FallbackParser(),   # 보조 파서 (예: tree-sitter)
            RegexParser()       # 최후 수단 (정규식)
        ]
    
    def parse(self, content):
        for parser in self.parsers:
            try:
                result = parser.parse(content)
                if self.validate_result(result):
                    return result.with_confidence(parser.base_confidence)
            except Exception:
                continue
        return EmptyResult()
```

#### B. Confidence Calibration System (신뢰성 확보)
```python
class ConfidenceCalibrator:
    def __init__(self, ground_truth_data):
        self.calibration_map = self.build_calibration_map(ground_truth_data)
    
    def calibrate(self, raw_confidence, context):
        """원시 신뢰도를 실제 정확성과 맞춘 신뢰도로 변환"""
        bucket = self.get_confidence_bucket(raw_confidence, context)
        return self.calibration_map[bucket]['actual_accuracy']
```

#### C. Session-Safe Data Access (안정성 확보)
```python
class SafeMetadataEngine:
    async def process_files_safe(self, files):
        async with self.session_manager() as session:
            semaphore = asyncio.Semaphore(self.max_workers)
            
            async def process_single_file(file_path):
                async with semaphore:
                    return await self.analyze_with_recovery(file_path, session)
            
            results = await asyncio.gather(
                *[process_single_file(f) for f in files],
                return_exceptions=True
            )
            return self.consolidate_results(results)
```

---

## 2. 파서 정확성 개선 설계

### 2.1 Java 파서 현대화 설계

#### 현재 문제점
- javalang: Java 8+ 문법 지원 불완전
- 람다, 스트림, 메서드 레퍼런스 미인식
- 정확성: ~70%

#### 설계 솔루션: Multi-Parser Architecture
```python
class ModernJavaParser:
    def __init__(self):
        self.primary_parser = TreeSitterJavaParser()
        self.fallback_parser = JavalangParser() 
        self.confidence_adjuster = JavaConfidenceAdjuster()
    
    def parse_java_file(self, content):
        # 1차 시도: Tree-sitter (현대 문법 지원)
        try:
            result = self.primary_parser.parse(content)
            if result.completeness > 0.9:
                return result.with_confidence(0.85)
        except:
            pass
            
        # 2차 시도: javalang (안정성 중심)
        try:
            result = self.fallback_parser.parse(content)
            return result.with_confidence(0.70)
        except:
            return self.generate_minimal_result(content)
```

#### 기대 효과: 70% → 85% 정확성

### 2.2 JSP/MyBatis 동적 SQL 처리 설계

#### 현재 문제점
- 정규식 기반 SQL 추출
- 동적 SQL 조합 불완전
- 정확성: ~60%

#### 설계 솔루션: Template Engine Simulator
```python
class MyBatisTemplateAnalyzer:
    def __init__(self):
        self.sql_combinator = SQLCombinator()
        self.condition_evaluator = ConditionEvaluator()
    
    def analyze_dynamic_sql(self, xml_content):
        # 1. XML AST 파싱
        ast = self.parse_mybatis_xml(xml_content)
        
        # 2. 조건부 블록 식별
        conditional_blocks = self.extract_conditional_blocks(ast)
        
        # 3. 가능한 SQL 조합 생성
        possible_sqls = self.generate_sql_combinations(conditional_blocks)
        
        # 4. 각 조합의 신뢰도 계산
        return [self.analyze_sql_variant(sql) for sql in possible_sqls]
```

#### 기대 효과: 60% → 85% 정확성

### 2.3 Python 클래스 분석 강화 설계

#### 현재 제한점
- 정적 분석만 지원
- 동적 속성/메서드 미인식

#### 설계 솔루션: Hybrid Analysis
```python
class HybridPythonAnalyzer:
    def analyze_python_module(self, file_path):
        # 정적 분석 (기본)
        static_result = self.static_ast_analysis(file_path)
        
        # 동적 패턴 탐지 (보완)
        dynamic_patterns = self.detect_dynamic_patterns(file_path)
        
        # 결합 분석
        return self.merge_analysis_results(static_result, dynamic_patterns)
    
    def detect_dynamic_patterns(self, file_path):
        """setattr, exec, __getattr__ 등 동적 패턴 탐지"""
        patterns = []
        with open(file_path, 'r') as f:
            content = f.read()
            
        # setattr 패턴
        setattr_calls = re.findall(r'setattr\s*\([^)]+\)', content)
        patterns.extend(self.analyze_setattr_patterns(setattr_calls))
        
        return patterns
```

---

## 3. 신뢰도 시스템 재설계

### 3.1 현재 신뢰도 시스템 문제점
- 경험적 검증 없는 임의 공식
- 순환 참조로 인한 신뢰도 인플레이션
- 실제 정확성과 ±30% 차이 가능

### 3.2 Ground Truth 기반 신뢰도 시스템 설계

#### Ground Truth 데이터셋 설계
```python
class GroundTruthDataset:
    def __init__(self):
        self.datasets = {
            'java_method_calls': {
                'spring_boot_sample': 'verified_method_calls.json',
                'java_design_patterns': 'confirmed_relationships.json'
            },
            'sql_mappings': {
                'mybatis_tutorial': 'verified_sql_mappings.json',
                'hibernate_sample': 'confirmed_orm_mappings.json'
            },
            'class_hierarchies': {
                'python_frameworks': 'confirmed_inheritance.json'
            }
        }
    
    def validate_parser_accuracy(self, parser_type, test_cases):
        """실제 정확성 측정 및 신뢰도 캘리브레이션"""
        results = []
        for test_case in test_cases:
            predicted = self.parse_with_parser(parser_type, test_case.input)
            actual = test_case.expected_output
            
            accuracy = self.calculate_accuracy(predicted, actual)
            confidence = predicted.confidence
            
            results.append({
                'predicted_confidence': confidence,
                'actual_accuracy': accuracy,
                'difference': abs(confidence - accuracy)
            })
        
        return self.build_calibration_function(results)
```

#### 캘리브레이션 함수 설계
```python
def build_calibration_function(self, validation_results):
    """실측 데이터 기반 신뢰도 보정 함수 생성"""
    confidence_buckets = {}
    
    for result in validation_results:
        bucket = round(result['predicted_confidence'], 1)
        if bucket not in confidence_buckets:
            confidence_buckets[bucket] = []
        confidence_buckets[bucket].append(result['actual_accuracy'])
    
    # 각 구간의 평균 실제 정확성 계산
    calibration_map = {}
    for bucket, accuracies in confidence_buckets.items():
        calibration_map[bucket] = {
            'calibrated_confidence': sum(accuracies) / len(accuracies),
            'sample_size': len(accuracies),
            'std_deviation': statistics.stdev(accuracies)
        }
    
    return calibration_map
```

### 3.3 순환 참조 해결 설계
```python
class CircularSafeConfidencePropagator:
    def propagate_confidence(self, start_node, max_depth=5):
        """순환 참조 안전한 신뢰도 전파"""
        visited_paths = {}  # (from_node, to_node, depth) -> confidence
        
        def safe_propagate(node, depth, path):
            if depth > max_depth:
                return 0.1  # 깊이 제한
            
            path_key = tuple(sorted(path))
            if path_key in visited_paths:
                # 순환 탐지 시 페널티 적용
                return visited_paths[path_key] * 0.8
            
            # 정상 전파
            confidence = self.calculate_node_confidence(node)
            visited_paths[path_key] = confidence
            
            return confidence
        
        return safe_propagate(start_node, 0, [start_node])
```

---

## 4. 시각화 일관성 보장 설계

### 4.1 노드-엣지 일관성 검증 시스템
```python
class VisualizationValidator:
    def validate_and_clean(self, nodes, edges):
        """노드-엣지 일관성 보장"""
        # 1. 유효한 노드 ID 집합 생성
        valid_node_ids = {node.id for node in nodes}
        
        # 2. 엣지 유효성 검사
        valid_edges = []
        orphaned_edges = []
        
        for edge in edges:
            if (edge.source in valid_node_ids and 
                edge.target in valid_node_ids):
                valid_edges.append(edge)
            else:
                orphaned_edges.append(edge)
        
        # 3. 검증 보고서 생성
        validation_report = {
            'total_nodes': len(nodes),
            'total_edges': len(edges),
            'valid_edges': len(valid_edges),
            'orphaned_edges': len(orphaned_edges),
            'consistency_ratio': len(valid_edges) / len(edges) if edges else 1.0
        }
        
        return valid_edges, validation_report
```

### 4.2 Mermaid 내보내기 정확성 개선
```python
class AccurateMermaidExporter:
    def export_with_preservation(self, data, diagram_type):
        """정보 손실 최소화 Mermaid 내보내기"""
        
        # 1. 라벨 길이 동적 조정
        max_label_length = self.calculate_optimal_label_length(data)
        
        # 2. 중요 정보 우선 보존
        preserved_relationships = self.prioritize_relationships(data.edges)
        
        # 3. 다단계 상세도 지원
        return {
            'summary': self.generate_summary_diagram(data, max_label_length),
            'detailed': self.generate_detailed_diagram(data),
            'metadata': self.generate_metadata_supplement(data)
        }
```

---

## 5. 구현 단계별 계획

### Phase 1: Critical Fixes (Week 1-3)
```yaml
Week 1:
  - 데이터베이스 세션 관리 수정
  - 비동기 패턴 통일
  - 기본 테스트 프레임워크 구축

Week 2:
  - Ground Truth 데이터셋 초기 구축
  - 신뢰도 캘리브레이션 시스템 기본 구현
  - 순환 참조 해결

Week 3:
  - 노드-엣지 일관성 검증 시스템
  - 기본 검증 및 안정성 테스트
```

### Phase 2: Parser Accuracy (Week 4-9)
```yaml
Week 4-5:
  - Tree-sitter Java 파서 통합
  - Parser Chain 패턴 구현

Week 6-7:
  - MyBatis AST 파서 구현
  - 동적 SQL 분석 알고리즘

Week 8-9:
  - Python 동적 분석 보강
  - 통합 테스트 및 성능 최적화
```

### Phase 3: Quality & Documentation (Week 10-12)
```yaml
Week 10:
  - Mermaid 내보내기 정확성 개선
  - 시각화 품질 향상

Week 11:
  - 문서-구현 동기화
  - API 문서 완성

Week 12:
  - 종합 검증 및 성능 테스트
  - 배포 준비
```

---

## 6. 검증 및 품질 보증 설계

### 6.1 자동화된 정확성 회귀 테스트
```python
class AccuracyRegressionTest:
    def setup_continuous_validation(self):
        """CI/CD 파이프라인에 정확성 검증 통합"""
        test_suite = {
            'parser_accuracy': self.test_all_parsers,
            'confidence_calibration': self.test_confidence_accuracy,
            'visualization_consistency': self.test_visualization_integrity,
            'end_to_end_accuracy': self.test_full_pipeline
        }
        
        return test_suite
    
    def test_all_parsers(self):
        """모든 파서의 최소 정확성 보장"""
        min_accuracy = 0.80
        
        for parser_name, parser in self.parsers.items():
            accuracy = self.measure_parser_accuracy(parser)
            assert accuracy >= min_accuracy, f"{parser_name} accuracy {accuracy} below threshold {min_accuracy}"
```

### 6.2 실시간 정확성 모니터링
```python
class AccuracyMonitor:
    def monitor_production_accuracy(self):
        """프로덕션 환경에서 정확성 실시간 모니터링"""
        
        # 샘플링 기반 정확성 추적
        sample_rate = 0.01  # 1% 샘플링
        
        for analysis_result in self.production_stream:
            if random.random() < sample_rate:
                predicted_confidence = analysis_result.confidence
                
                # 사용자 피드백 또는 휴리스틱 기반 실제 정확성 추정
                estimated_accuracy = self.estimate_actual_accuracy(analysis_result)
                
                # 신뢰도-정확성 차이 모니터링
                difference = abs(predicted_confidence - estimated_accuracy)
                
                if difference > 0.2:  # 20% 이상 차이시 알림
                    self.alert_accuracy_drift(analysis_result, difference)
```

---

## 7. 예상 성과 및 검증 기준

### 7.1 정량적 목표
| 메트릭 | 현재 | 목표 | 검증 방법 |
|--------|------|------|-----------|
| Java Parser 정확성 | 70% | 85% | Ground Truth 테스트 |
| JSP/MyBatis Parser | 60% | 85% | 수동 검증된 프로젝트 |
| 시각화 일관성 | 80% | 95% | 자동 일관성 검사 |
| 신뢰도 캘리브레이션 | 검증안됨 | ±10% | Cross-validation |
| 시스템 안정성 | 메모리 누수 | 누수 제거 | 장기 실행 테스트 |

### 7.2 정성적 목표
- **사용자 신뢰도 향상**: 허위 신뢰도 제거
- **유지보수성 개선**: 모듈화된 파서 아키텍처
- **확장성 확보**: 새로운 언어 파서 쉬운 추가

### 7.3 성공 기준
1. **정확성 목표 달성**: 전체 시스템 85% 이상
2. **안정성 확보**: 24시간 연속 실행 시 메모리 누수 없음
3. **신뢰성 확보**: 신뢰도-정확성 차이 10% 이내
4. **성능 유지**: 기존 대비 처리 속도 10% 이내 감소

---

## 8. 위험 요소 및 완화 전략

### 8.1 기술적 위험
- **호환성 문제**: Tree-sitter 파서 통합 시 기존 코드와 충돌
  - *완화*: Adapter 패턴으로 인터페이스 통일
  
- **성능 저하**: 다중 파서 사용으로 인한 처리 시간 증가
  - *완화*: 병렬 처리 및 캐싱 전략

### 8.2 데이터 위험  
- **Ground Truth 부족**: 충분한 검증 데이터 확보 어려움
  - *완화*: 오픈소스 프로젝트 활용, 점진적 데이터셋 확장

### 8.3 일정 위험
- **복잡성 과소평가**: 구현 복잡도 예상보다 높음
  - *완화*: MVP 우선 접근, 단계적 기능 추가

---

## 결론

이 설계 문서는 Source Analyzer의 정확성을 65-75%에서 85%+로 향상시키기 위한 포괄적인 로드맵을 제시합니다. 

**핵심 설계 원칙**:
1. **검증 가능한 개선**: Ground Truth 데이터 기반
2. **단계적 구현**: 위험 최소화
3. **시스템 안정성**: Critical 이슈 우선 해결
4. **장기적 확장성**: 모듈화된 아키텍처

**예상 ROI**:
- 구현 투자: 10-12주
- 정확성 개선: +15-20%
- 유지보수 비용: 50% 감소
- 사용자 신뢰도: 대폭 향상

이 설계를 통해 Source Analyzer는 프로토타입에서 **엔터프라이즈급 정적 분석 도구**로 발전할 수 있습니다.