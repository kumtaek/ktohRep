"""
AI 분석 리포트 생성기
AI 분석 결과를 바탕으로 다양한 형식의 리포트를 생성합니다.
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from utils.ai_analyzer import AnalysisResult

class AIReportGenerator:
    """AI 분석 리포트 생성기"""
    
    def __init__(self):
        """생성기 초기화"""
        self.logger = logging.getLogger(__name__)
        
    def generate_report(self, result: AnalysisResult, output_path: str = None, 
                       include_metadata: bool = True) -> str:
        """
        AI 분석 리포트 생성
        
        Args:
            result: AI 분석 결과
            output_path: 출력 파일 경로
            include_metadata: 메타데이터 포함 여부
            
        Returns:
            생성된 리포트 내용
        """
        self.logger.info("AI 분석 리포트 생성 시작")
        
        if not result.success:
            return self._generate_error_report(result)
        
        # 리포트 내용 생성
        report_content = self._generate_report_content(result, include_metadata)
        
        # 파일로 저장
        if output_path:
            self._save_report(report_content, output_path)
            self.logger.info(f"AI 리포트 저장 완료: {output_path}")
        
        return report_content
    
    def _generate_error_report(self, result: AnalysisResult) -> str:
        """오류 리포트 생성"""
        content = f"""# ❌ AI 분석 실패 리포트

## 🚨 오류 정보
- **오류 메시지**: {result.error_message}
- **처리 시간**: {result.processing_time:.2f}초
- **발생 시간**: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}

## 🔍 문제 해결 방법
1. **모델 연결 확인**: Ollama 서비스 실행 상태 확인
2. **네트워크 연결**: 인터넷 연결 상태 확인
3. **API 키 확인**: 원격 API 키 유효성 검증
4. **프로젝트 경로**: 분석 대상 프로젝트 경로 확인

## 📞 지원 정보
- **로그 파일**: `./logs/ai_analysis_yyyymmdd_hms.log`
- **설정 파일**: `./config/ai_config.yaml`

---
*이 리포트는 AI 분석 중 오류가 발생하여 자동 생성되었습니다.*
"""
        return content
    
    def _generate_report_content(self, result: AnalysisResult, include_metadata: bool) -> str:
        """리포트 내용 생성"""
        metadata = result.metadata
        
        # 헤더 생성
        content = f"""# 🤖 AI 기반 소스코드 분석 리포트

## 📋 보고서 정보
- **작성일시**: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}
- **분석대상**: `{metadata.get('project_name', 'Unknown')}`
- **분석자**: AI 모델 ({metadata.get('model_name', 'Unknown')})
- **분석 유형**: {metadata.get('analysis_type', 'Unknown').upper()}
- **보고서 유형**: AI 자동 생성

"""
        
        if include_metadata:
            content += self._generate_metadata_section(metadata)
        
        content += "---\n\n"
        
        # AI 분석 결과
        content += "## 🔍 AI 분석 결과\n\n"
        content += result.content
        
        # 결론 및 제언
        content += self._generate_conclusion_section(metadata)
        
        return content
    
    def _generate_metadata_section(self, metadata: Dict[str, Any]) -> str:
        """메타데이터 섹션 생성"""
        content = "## 📊 분석 메타데이터\n\n"
        
        # 기본 정보
        content += "### 📈 **기본 정보**\n"
        content += f"- **🔍 분석 유형**: {metadata.get('analysis_type', 'Unknown')}\n"
        content += f"- **🤖 사용 모델**: {metadata.get('model_name', 'Unknown')}\n"
        content += f"- **📁 프로젝트 경로**: `{metadata.get('project_path', 'Unknown')}`\n"
        content += f"- **⏱️ 처리 시간**: {metadata.get('processing_time', 0):.2f}초\n"
        content += f"- **📅 분석 시간**: {metadata.get('timestamp', 'Unknown')}\n\n"
        
        # 프로젝트 정보
        project_info = metadata.get('project_info', {})
        if project_info:
            content += "### 📁 **프로젝트 정보**\n"
            content += f"- **📋 프로젝트명**: {project_info.get('project_name', 'Unknown')}\n"
            content += f"- **📄 총 파일 수**: {project_info.get('file_count', 0):,}개\n"
            content += f"- **💾 총 크기**: {project_info.get('total_size', 0):,} bytes\n"
            
            # 언어별 파일 수
            languages = project_info.get('languages', {})
            if languages:
                content += "- **🔤 사용 언어**:\n"
                for ext, count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
                    content += f"  - `{ext}`: {count}개\n"
            
            content += "\n"
        
        return content
    
    def _generate_conclusion_section(self, metadata: Dict[str, Any]) -> str:
        """결론 및 제언 섹션 생성"""
        content = "\n---\n\n"
        content += "## 📝 결론 및 제언\n\n"
        
        # 분석 유형별 결론
        analysis_type = metadata.get('analysis_type', '')
        
        if analysis_type == 'erd':
            content += """### 🎯 **ERD 분석 결론**
- **데이터베이스 구조**: 체계적인 정규화 및 관계 설계
- **개선 포인트**: 외래키 제약조건 명시, 인덱스 최적화
- **권장사항**: 데이터 사전 구축, 성능 모니터링 강화

"""
        elif analysis_type == 'architecture':
            content += """### 🏗️ **아키텍처 분석 결론**
- **구조적 특징**: 명확한 계층 분리 및 모듈화
- **기술 스택**: 현대적이고 안정적인 기술 선택
- **개선 방향**: 마이크로서비스 전환, 컨테이너화 고려

"""
        elif analysis_type == 'code_quality':
            content += """### ✨ **코드 품질 분석 결론**
- **코드 품질**: 일관된 코딩 스타일 및 가독성
- **테스트 커버리지**: 체계적인 테스트 구조
- **보안성**: 기본적인 보안 패턴 적용

"""
        elif analysis_type == 'comprehensive':
            content += """### 🌟 **종합 분석 결론**
- **전체 평가**: 체계적이고 확장 가능한 구조
- **기술적 우수성**: 현대적인 개발 방법론 적용
- **비즈니스 가치**: 명확한 도메인 모델링

"""
        
        content += """### 🚀 **일반적 개선 제언**
1. **📚 문서화 강화**: API 문서, 아키텍처 문서 보완
2. **🧪 테스트 확대**: 자동화 테스트, 성능 테스트 추가
3. **🔒 보안 강화**: 정기적인 보안 점검, 취약점 스캔
4. **📊 모니터링**: 성능 모니터링, 로깅 체계 구축
5. **🔄 CI/CD**: 지속적 통합/배포 파이프라인 구축

### 📋 **다음 단계**
1. **우선순위 분석**: 개선사항 우선순위 설정
2. **실행 계획**: 단계별 개선 계획 수립
3. **팀 협업**: 개발팀과의 협업 및 리뷰
4. **지속적 개선**: 정기적인 코드 품질 점검

---
"""
        
        # AI 모델 정보
        content += f"""**🤖 이 보고서는 {metadata.get('model_name', 'AI 모델')}을 통해 생성되었습니다.**

---
*AI 분석 결과는 참고용이며, 전문가 검토를 권장합니다.*
"""
        
        return content
    
    def _save_report(self, content: str, output_path: str):
        """리포트를 파일로 저장"""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            self.logger.error(f"AI 리포트 저장 실패: {e}")
            raise
    
    def generate_comparison_report(self, results: List[AnalysisResult], 
                                 output_path: str = None) -> str:
        """여러 분석 결과를 비교하는 리포트 생성"""
        if not results:
            return "비교할 분석 결과가 없습니다."
        
        content = "# 🔍 AI 분석 결과 비교 리포트\n\n"
        content += f"## 📊 비교 대상\n"
        content += f"- **총 분석 수**: {len(results)}개\n"
        content += f"- **생성 시간**: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}\n\n"
        
        # 각 분석 결과 요약
        for i, result in enumerate(results, 1):
            if result.success:
                metadata = result.metadata
                content += f"### 📋 **분석 {i}: {metadata.get('analysis_type', 'Unknown')}**\n"
                content += f"- **모델**: {metadata.get('model_name', 'Unknown')}\n"
                content += f"- **처리 시간**: {metadata.get('processing_time', 0):.2f}초\n"
                content += f"- **프로젝트**: {metadata.get('project_name', 'Unknown')}\n"
                content += f"- **상태**: ✅ 성공\n\n"
            else:
                content += f"### 📋 **분석 {i}: 실패**\n"
                content += f"- **오류**: {result.error_message}\n"
                content += f"- **상태**: ❌ 실패\n\n"
        
        # 비교 분석
        content += "## 🔍 **비교 분석**\n\n"
        
        successful_results = [r for r in results if r.success]
        if len(successful_results) > 1:
            # 처리 시간 비교
            processing_times = [r.processing_time for r in successful_results]
            avg_time = sum(processing_times) / len(processing_times)
            min_time = min(processing_times)
            max_time = max(processing_times)
            
            content += f"### ⏱️ **성능 비교**\n"
            content += f"- **평균 처리 시간**: {avg_time:.2f}초\n"
            content += f"- **최소 처리 시간**: {min_time:.2f}초\n"
            content += f"- **최대 처리 시간**: {max_time:.2f}초\n\n"
            
            # 모델별 성능
            model_performance = {}
            for result in successful_results:
                model = result.metadata.get('model_name', 'Unknown')
                if model not in model_performance:
                    model_performance[model] = []
                model_performance[model].append(result.processing_time)
            
            content += "### 🤖 **모델별 성능**\n"
            for model, times in model_performance.items():
                avg_model_time = sum(times) / len(times)
                content += f"- **{model}**: 평균 {avg_model_time:.2f}초\n"
        
        content += "\n---\n\n"
        content += "**🔍 비교 분석이 완료되었습니다.**\n\n"
        
        # 파일로 저장
        if output_path:
            self._save_report(content, output_path)
        
        return content
