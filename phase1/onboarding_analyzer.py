"""
신규입사자 지원을 위한 통합 분석 시스템
기존 main.py를 확장하여 온보딩 특화 기능 추가
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Dict, Any, List

# 기존 모듈들
from phase1.main import SourceAnalyzer
from phase1.models.database import DatabaseManager

# 신규입사자 지원 모듈들
from phase1.parsers.java.business_context_parser import BusinessContextParser
from phase1.llm.onboarding_chunker import OnboardingChunker, OnboardingChunk
from phase1.utils.onboarding_edge_generator import OnboardingEdgeGenerator

logger = logging.getLogger(__name__)

class OnboardingAnalyzer(SourceAnalyzer):
    """신규입사자 지원 특화 분석기"""
    
    def __init__(self, global_config_path: str, phase_config_path: str, project_name: str = None):
        super().__init__(global_config_path, phase_config_path, project_name)
        
        # 온보딩 특화 컴포넌트 초기화
        self.business_parser = None
        self.onboarding_chunker = OnboardingChunker()
        self.onboarding_edge_generator = None
        
        self.onboarding_results = {
            'business_chunks': [],
            'learning_paths': [],
            'api_endpoints': [],
            'business_flows': 0,
            'complexity_analysis': {}
        }

    def analyze_project_for_onboarding(self, source_path: str, verbose: bool = False) -> Dict[str, Any]:
        """신규입사자를 위한 프로젝트 분석"""
        
        logger.info("=== 신규입사자 지원 프로젝트 분석 시작 ===")
        
        try:
            # 1. 기본 분석 실행
            basic_results = self.analyze_project(source_path, verbose)
            
            if not basic_results.get('success', False):
                logger.error("기본 분석 실패")
                return basic_results
            
            # 2. 비즈니스 맥락 파싱
            logger.info("비즈니스 맥락 분석 중...")
            business_results = self._analyze_business_context(source_path)
            
            # 3. 온보딩 청크 생성
            logger.info("학습용 청크 생성 중...")
            chunking_results = self._create_onboarding_chunks(source_path)
            
            # 4. 온보딩 엣지 생성  
            logger.info("학습 관계 분석 중...")
            edge_results = self._generate_onboarding_edges(source_path)
            
            # 5. 학습 경로 생성
            logger.info("학습 경로 생성 중...")
            learning_paths = self._generate_learning_paths()
            
            # 6. 복잡도 분석
            logger.info("코드 복잡도 분석 중...")
            complexity_analysis = self._analyze_code_complexity()
            
            # 결과 통합
            onboarding_results = {
                'success': True,
                'basic_analysis': basic_results,
                'business_context': business_results,
                'onboarding_chunks': chunking_results,
                'onboarding_edges': edge_results,
                'learning_paths': learning_paths,
                'complexity_analysis': complexity_analysis,
                'recommendations': self._generate_onboarding_recommendations()
            }
            
            logger.info("=== 신규입사자 지원 분석 완료 ===")
            return onboarding_results
            
        except Exception as e:
            logger.error(f"온보딩 분석 중 오류: {e}")
            return {
                'success': False,
                'error': str(e),
                'basic_analysis': basic_results if 'basic_results' in locals() else {}
            }

    def _analyze_business_context(self, source_path: str) -> Dict[str, Any]:
        """비즈니스 맥락 분석"""
        results = {
            'controllers_found': 0,
            'services_found': 0,
            'repositories_found': 0,
            'models_found': 0,
            'business_domains': [],
            'architecture_pattern': 'unknown'
        }
        
        try:
            # Java 파일들 분석
            java_files = list(Path(source_path).rglob('*.java'))
            
            domain_keywords = set()
            layer_counts = {'controller': 0, 'service': 0, 'repository': 0, 'model': 0}
            
            for java_file in java_files:
                try:
                    with open(java_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    file_name = java_file.name.lower()
                    
                    # 계층 분류
                    if 'controller' in file_name:
                        layer_counts['controller'] += 1
                    elif 'service' in file_name:
                        layer_counts['service'] += 1
                    elif 'mapper' in file_name or 'repository' in file_name:
                        layer_counts['repository'] += 1
                    elif 'model' in file_name or 'entity' in file_name:
                        layer_counts['model'] += 1
                    
                    # 도메인 키워드 추출
                    for keyword in ['user', 'order', 'product', 'payment', 'auth']:
                        if keyword in file_name:
                            domain_keywords.add(keyword)
                
                except Exception as e:
                    logger.warning(f"파일 {java_file} 분석 중 오류: {e}")
            
            # 결과 업데이트
            results.update(layer_counts)
            results['business_domains'] = list(domain_keywords)
            
            # 아키텍처 패턴 추론
            if layer_counts['controller'] > 0 and layer_counts['service'] > 0 and layer_counts['repository'] > 0:
                results['architecture_pattern'] = 'MVC_3Layer'
            elif layer_counts['controller'] > 0 and layer_counts['service'] > 0:
                results['architecture_pattern'] = 'MVC_2Layer'
            else:
                results['architecture_pattern'] = 'Simple'
            
        except Exception as e:
            logger.error(f"비즈니스 맥락 분석 중 오류: {e}")
            results['error'] = str(e)
        
        return results

    def _create_onboarding_chunks(self, source_path: str) -> Dict[str, Any]:
        """온보딩용 청크 생성"""
        results = {
            'total_chunks': 0,
            'complexity_distribution': {'beginner': 0, 'intermediate': 0, 'advanced': 0},
            'learning_priorities': {},
            'chunks_by_domain': {}
        }
        
        try:
            java_files = list(Path(source_path).rglob('*.java'))
            all_chunks = []
            
            for java_file in java_files[:5]:  # 샘플로 5개 파일만 처리
                try:
                    with open(java_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 온보딩 청크 생성
                    chunks = self.onboarding_chunker.create_onboarding_chunks(str(java_file), content)
                    all_chunks.extend(chunks)
                    
                except Exception as e:
                    logger.warning(f"청크 생성 중 오류 ({java_file}): {e}")
            
            # 통계 계산
            results['total_chunks'] = len(all_chunks)
            
            for chunk in all_chunks:
                # 복잡도 분포
                if chunk.complexity_level in results['complexity_distribution']:
                    results['complexity_distribution'][chunk.complexity_level] += 1
                
                # 학습 우선순위 분포
                priority_key = f"priority_{chunk.learning_priority}"
                if priority_key not in results['learning_priorities']:
                    results['learning_priorities'][priority_key] = 0
                results['learning_priorities'][priority_key] += 1
            
            self.onboarding_results['business_chunks'] = all_chunks
            
        except Exception as e:
            logger.error(f"온보딩 청크 생성 중 오류: {e}")
            results['error'] = str(e)
        
        return results

    def _generate_onboarding_edges(self, source_path: str) -> Dict[str, Any]:
        """온보딩용 엣지 생성"""
        results = {
            'total_edges': 0,
            'business_flows': 0,
            'api_endpoints': 0,
            'learning_paths': 0,
            'edge_types': {}
        }
        
        try:
            # 데이터베이스 세션 확보
            db_manager = DatabaseManager(self.db_path)
            
            with db_manager.get_session() as session:
                self.onboarding_edge_generator = OnboardingEdgeGenerator(
                    session, source_path, self.project_id
                )
                
                # 온보딩 엣지 생성
                edge_results = self.onboarding_edge_generator.generate_all_edges()
                results.update(edge_results)
            
        except Exception as e:
            logger.error(f"온보딩 엣지 생성 중 오류: {e}")
            results['error'] = str(e)
        
        return results

    def _generate_learning_paths(self) -> List[Dict[str, Any]]:
        """학습 경로 생성"""
        learning_paths = []
        
        try:
            # 청크 기반 학습 순서 생성
            if self.onboarding_results['business_chunks']:
                chunker_sequences = self.onboarding_chunker.generate_learning_sequence(
                    self.onboarding_results['business_chunks']
                )
                
                for i, phase_chunks in enumerate(chunker_sequences, 1):
                    if phase_chunks:
                        path = {
                            'phase': i,
                            'title': self._get_phase_title(i),
                            'chunks': len(phase_chunks),
                            'estimated_time': f"{len(phase_chunks) * 15}분",
                            'description': self._get_phase_description(i, phase_chunks)
                        }
                        learning_paths.append(path)
            
        except Exception as e:
            logger.error(f"학습 경로 생성 중 오류: {e}")
        
        return learning_paths

    def _analyze_code_complexity(self) -> Dict[str, Any]:
        """코드 복잡도 분석"""
        complexity = {
            'overall_level': 'beginner',
            'difficult_files': [],
            'beginner_friendly_files': [],
            'recommendations': []
        }
        
        try:
            chunks = self.onboarding_results.get('business_chunks', [])
            
            if not chunks:
                return complexity
            
            # 복잡도 통계
            complexity_counts = {'beginner': 0, 'intermediate': 0, 'advanced': 0}
            
            for chunk in chunks:
                complexity_counts[chunk.complexity_level] += 1
                
                # 어려운 파일과 쉬운 파일 식별
                if chunk.complexity_level == 'advanced' and chunk.chunk_type == 'class':
                    complexity['difficult_files'].append({
                        'name': chunk.name,
                        'reason': '복잡한 비즈니스 로직 포함'
                    })
                elif chunk.complexity_level == 'beginner' and chunk.learning_priority >= 4:
                    complexity['beginner_friendly_files'].append({
                        'name': chunk.name,
                        'reason': '이해하기 쉬운 구조'
                    })
            
            # 전체 복잡도 레벨 결정
            total_chunks = sum(complexity_counts.values())
            if total_chunks > 0:
                advanced_ratio = complexity_counts['advanced'] / total_chunks
                if advanced_ratio > 0.3:
                    complexity['overall_level'] = 'advanced'
                elif advanced_ratio > 0.1:
                    complexity['overall_level'] = 'intermediate'
                else:
                    complexity['overall_level'] = 'beginner'
            
            # 추천사항 생성
            complexity['recommendations'] = self._generate_complexity_recommendations(complexity_counts)
            
        except Exception as e:
            logger.error(f"복잡도 분석 중 오류: {e}")
        
        return complexity

    def _generate_onboarding_recommendations(self) -> List[str]:
        """온보딩 추천사항 생성"""
        recommendations = []
        
        try:
            chunks = self.onboarding_results.get('business_chunks', [])
            
            if not chunks:
                recommendations.append("코드 분석이 필요합니다.")
                return recommendations
            
            # 학습 시작점 추천
            high_priority_chunks = [c for c in chunks if c.learning_priority >= 4]
            if high_priority_chunks:
                controller_chunks = [c for c in high_priority_chunks if 'controller' in c.name.lower()]
                if controller_chunks:
                    recommendations.append(f"{controller_chunks[0].name}부터 학습을 시작하세요. 이는 시스템의 진입점입니다.")
            
            # 복잡도 기반 추천
            beginner_chunks = [c for c in chunks if c.complexity_level == 'beginner']
            if len(beginner_chunks) > 0:
                recommendations.append(f"초급자 친화적인 코드가 {len(beginner_chunks)}개 있습니다. 이들부터 시작하세요.")
            
            # 도메인 기반 추천
            user_chunks = [c for c in chunks if 'user' in c.name.lower()]
            if user_chunks:
                recommendations.append("사용자 관리 모듈부터 시작하면 시스템 이해에 도움이 됩니다.")
            
            # 아키텍처 추천
            recommendations.append("MVC 패턴을 따르므로 Controller -> Service -> Repository 순서로 학습하세요.")
            
        except Exception as e:
            logger.error(f"추천사항 생성 중 오류: {e}")
        
        return recommendations

    def _get_phase_title(self, phase: int) -> str:
        """단계별 제목 반환"""
        titles = {
            1: "시스템 개요 파악",
            2: "진입점 이해 (Controllers)",  
            3: "핵심 비즈니스 로직",
            4: "데이터 처리 계층",
            5: "세부 구현사항"
        }
        return titles.get(phase, f"Phase {phase}")

    def _get_phase_description(self, phase: int, chunks: List[OnboardingChunk]) -> str:
        """단계별 설명 생성"""
        chunk_names = [c.name for c in chunks[:3]]  # 상위 3개만
        names_str = ", ".join(chunk_names)
        if len(chunks) > 3:
            names_str += f" 외 {len(chunks)-3}개"
        
        descriptions = {
            1: f"프로젝트 전체 구조를 파악합니다: {names_str}",
            2: f"웹 요청이 들어오는 진입점을 학습합니다: {names_str}",
            3: f"핵심 비즈니스 로직을 이해합니다: {names_str}",
            4: f"데이터 저장/조회 방식을 학습합니다: {names_str}",
            5: f"세부 구현 내용을 검토합니다: {names_str}"
        }
        return descriptions.get(phase, f"Phase {phase} 학습")

    def _generate_complexity_recommendations(self, complexity_counts: Dict[str, int]) -> List[str]:
        """복잡도 기반 추천사항"""
        recommendations = []
        
        total = sum(complexity_counts.values())
        if total == 0:
            return recommendations
        
        beginner_ratio = complexity_counts['beginner'] / total
        advanced_ratio = complexity_counts['advanced'] / total
        
        if beginner_ratio > 0.6:
            recommendations.append("초급자가 학습하기에 적합한 프로젝트입니다.")
        elif advanced_ratio > 0.3:
            recommendations.append("일부 복잡한 코드가 있으니 단계적으로 접근하세요.")
        
        if complexity_counts['advanced'] > 0:
            recommendations.append("복잡한 파일들은 멘토와 함께 검토하는 것을 권장합니다.")
        
        return recommendations

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description='신규입사자 지원 소스 분석기')
    parser.add_argument('--project-name', required=True, help='프로젝트 이름')
    parser.add_argument('--source-path', help='소스 코드 경로 (옵션)')
    parser.add_argument('--verbose', action='store_true', help='상세 로그 출력')
    
    args = parser.parse_args()
    
    # 로깅 설정
    log_level = logging.INFO if args.verbose else logging.WARNING
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    try:
        # 설정 파일 경로
        global_config_path = 'config/config.yaml'
        phase_config_path = 'config/phase1/config.yaml'
        
        # 소스 경로 자동 설정
        if not args.source_path:
            args.source_path = f"./PROJECT/{args.project_name}"
        
        # 온보딩 분석기 생성 및 실행
        analyzer = OnboardingAnalyzer(global_config_path, phase_config_path, args.project_name)
        results = analyzer.analyze_project_for_onboarding(args.source_path, args.verbose)
        
        # 결과 출력
        if results.get('success'):
            print("=== 신규입사자 지원 분석 결과 ===")
            print(f"✅ 기본 분석: {results['basic_analysis'].get('files_processed', 0)}개 파일 처리")
            print(f"✅ 학습용 청크: {results['onboarding_chunks']['total_chunks']}개 생성")  
            print(f"✅ 학습 관계: {results['onboarding_edges']['total_edges']}개 추출")
            print(f"✅ 학습 경로: {len(results['learning_paths'])}단계 생성")
            print(f"✅ 복잡도: {results['complexity_analysis']['overall_level']}")
            
            print("\n📚 추천 학습 방법:")
            for rec in results['recommendations']:
                print(f"  • {rec}")
                
        else:
            print("❌ 분석 실패:", results.get('error', '알 수 없는 오류'))
            
    except Exception as e:
        print(f"❌ 실행 중 오류: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()