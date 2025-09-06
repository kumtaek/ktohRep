#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
LLM 기반 관계 분석기
복잡한 소스 코드의 컴포넌트 간 관계를 LLM을 통해 분석합니다.
"""

import logging
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from phase1.llm.assist import LLMAssistant

logger = logging.getLogger(__name__)


class RelationshipAnalyzer:
    """LLM 기반 관계 분석기"""
    
    def __init__(self, llm_assistant: LLMAssistant = None):
        self.llm_assistant = llm_assistant or LLMAssistant()
        
    def analyze_java_relationships(self, java_content: str, file_path: str, 
                                 project_context: Dict[str, Any] = None) -> List[Dict]:
        """Java 파일의 관계를 LLM으로 분석"""
        
        prompt = self._build_java_analysis_prompt(java_content, file_path, project_context)
        
        try:
            response = self.llm_assistant.get_completion(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.1  # 일관성을 위해 낮은 temperature
            )
            
            if response:
                relationships = self._parse_relationship_response(response)
                return self._validate_java_relationships(relationships, file_path)
            
        except Exception as e:
            logger.error(f"Java 관계 분석 실패 {file_path}: {e}")
        
        return []
    
    def analyze_mybatis_relationships(self, xml_content: str, file_path: str,
                                   java_interfaces: List[str] = None) -> List[Dict]:
        """MyBatis XML의 관계를 LLM으로 분석"""
        
        prompt = self._build_mybatis_analysis_prompt(xml_content, file_path, java_interfaces)
        
        try:
            response = self.llm_assistant.get_completion(
                prompt=prompt,
                max_tokens=1500,
                temperature=0.1
            )
            
            if response:
                relationships = self._parse_relationship_response(response)
                return self._validate_mybatis_relationships(relationships, file_path)
            
        except Exception as e:
            logger.error(f"MyBatis 관계 분석 실패 {file_path}: {e}")
        
        return []
    
    def analyze_jsp_relationships(self, jsp_content: str, file_path: str,
                                controller_methods: List[str] = None) -> List[Dict]:
        """JSP 파일의 관계를 LLM으로 분석"""
        
        prompt = self._build_jsp_analysis_prompt(jsp_content, file_path, controller_methods)
        
        try:
            response = self.llm_assistant.get_completion(
                prompt=prompt,
                max_tokens=1500,
                temperature=0.1
            )
            
            if response:
                relationships = self._parse_relationship_response(response)
                return self._validate_jsp_relationships(relationships, file_path)
            
        except Exception as e:
            logger.error(f"JSP 관계 분석 실패 {file_path}: {e}")
        
        return []
    
    def analyze_sql_join_relationships(self, sql_content: str, sql_id: str) -> List[Dict]:
        """SQL JOIN 구문의 관계를 LLM으로 분석"""
        
        prompt = self._build_sql_analysis_prompt(sql_content, sql_id)
        
        try:
            response = self.llm_assistant.get_completion(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.1
            )
            
            if response:
                relationships = self._parse_relationship_response(response)
                return self._validate_sql_relationships(relationships, sql_id)
            
        except Exception as e:
            logger.error(f"SQL 관계 분석 실패 {sql_id}: {e}")
        
        return []
    
    def _build_java_analysis_prompt(self, java_content: str, file_path: str, 
                                  project_context: Dict = None) -> str:
        """Java 분석용 프롬프트 생성"""
        
        # 프로젝트 컨텍스트 정보 추가
        context_info = ""
        if project_context:
            known_classes = project_context.get('classes', [])
            known_services = project_context.get('services', [])
            known_controllers = project_context.get('controllers', [])
            
            context_info = f"""
프로젝트 컨텍스트:
- 알려진 클래스들: {', '.join(known_classes[:10])}...
- 서비스 클래스들: {', '.join(known_services)}
- 컨트롤러 클래스들: {', '.join(known_controllers)}
"""
        
        return f"""
Spring Boot + MyBatis 프로젝트의 Java 파일을 분석하여 다른 컴포넌트와의 관계를 찾아주세요.

파일 경로: {file_path}
{context_info}

소스 코드:
```java
{java_content[:3000]}  # 첫 3000자만
```

다음 관계들을 JSON 형태로 분석해주세요:

1. **의존성 주입 관계** (@Autowired, @Inject 등)
   - 어떤 클래스에 어떤 서비스나 매퍼가 주입되는지
   
2. **클래스 참조 관계** (import, 필드 타입, 메서드 파라미터/반환 타입)
   - 이 클래스가 참조하는 다른 프로젝트 내 클래스들
   
3. **Spring MVC 관계** (@Controller, @Service, @Repository 어노테이션 기반)
   - 컨트롤러-서비스, 서비스-매퍼 관계 등
   
4. **메서드 호출 관계** (중요한 비즈니스 로직 메서드만)
   - 이 클래스의 메서드들이 호출하는 외부 메서드들

응답 형식:
```json
{{
  "relationships": [
    {{
      "type": "dependency|reference|calls|annotation_based",
      "source": "현재 클래스의 FQN",
      "target": "대상 클래스/메서드의 FQN", 
      "relationship": "구체적인 관계 설명",
      "confidence": 0.0-1.0,
      "evidence": "관계를 보여주는 코드 조각"
    }}
  ]
}}
```

중요: 
- 프로젝트 내부 클래스들(com.example.*)만 분석하세요
- Spring Framework 클래스들은 제외하세요
- 확실한 관계만 높은 confidence로 보고하세요
"""
    
    def _build_mybatis_analysis_prompt(self, xml_content: str, file_path: str,
                                     java_interfaces: List[str] = None) -> str:
        """MyBatis 분석용 프롬프트 생성"""
        
        interface_info = ""
        if java_interfaces:
            interface_info = f"관련 Java 인터페이스들: {', '.join(java_interfaces)}"
        
        return f"""
MyBatis XML 매퍼 파일을 분석하여 관계를 찾아주세요.

파일 경로: {file_path}
{interface_info}

XML 내용:
```xml
{xml_content[:2000]}
```

다음 관계들을 분석해주세요:

1. **네임스페이스 관계** (Java 인터페이스와의 연결)
2. **테이블 참조 관계** (FROM, JOIN, UPDATE, INSERT 절의 테이블들)
3. **결과 매핑 관계** (resultType, resultMap과 Java 클래스)
4. **매개변수 관계** (parameterType과 Java 클래스)

응답 형식:
```json
{{
  "relationships": [
    {{
      "type": "implements|references|maps_to|parameter",
      "source": "XML 파일 또는 SQL Unit ID",
      "target": "Java 클래스 FQN 또는 테이블명",
      "relationship": "구체적인 관계 설명",
      "confidence": 0.0-1.0,
      "evidence": "관계를 보여주는 XML 조각"
    }}
  ]
}}
```
"""
    
    def _build_jsp_analysis_prompt(self, jsp_content: str, file_path: str,
                                 controller_methods: List[str] = None) -> str:
        """JSP 분석용 프롬프트 생성"""
        
        controller_info = ""
        if controller_methods:
            controller_info = f"알려진 컨트롤러 메서드들: {', '.join(controller_methods[:10])}"
        
        return f"""
JSP 파일을 분석하여 컨트롤러와의 관계를 찾아주세요.

파일 경로: {file_path}
{controller_info}

JSP 내용:
```jsp
{jsp_content[:2000]}
```

다음 관계들을 분석해주세요:

1. **폼 액션 관계** (form action URL과 컨트롤러 메서드)
2. **URL 참조 관계** (c:url, href, src 등의 URL 패턴)
3. **모델 참조 관계** (EL 표현식 ${model.field}과 Java 모델 클래스)
4. **JSTL 참조 관계** (c:forEach의 items와 컨트롤러가 전달한 데이터)

응답 형식:
```json
{{
  "relationships": [
    {{
      "type": "calls|references|displays",
      "source": "JSP 파일 경로",
      "target": "컨트롤러 메서드 또는 모델 클래스",
      "relationship": "구체적인 관계 설명",
      "confidence": 0.0-1.0,
      "evidence": "관계를 보여주는 JSP 코드 조각"
    }}
  ]
}}
```
"""
    
    def _build_sql_analysis_prompt(self, sql_content: str, sql_id: str) -> str:
        """SQL 분석용 프롬프트 생성"""
        
        return f"""
SQL 쿼리를 분석하여 테이블 간 JOIN 관계를 찾아주세요.

SQL ID: {sql_id}

SQL 쿼리:
```sql
{sql_content}
```

다음 관계들을 분석해주세요:

1. **JOIN 관계** (INNER/LEFT/RIGHT JOIN과 연결 조건)
2. **외래키 관계** (JOIN 조건에서 추론되는 FK 관계)
3. **데이터 흐름 관계** (INSERT → SELECT, UPDATE → SELECT)

응답 형식:
```json
{{
  "relationships": [
    {{
      "type": "join|foreign_key|data_flow",
      "source": "소스 테이블명",
      "target": "대상 테이블명", 
      "relationship": "조인 조건 또는 관계 설명",
      "confidence": 0.0-1.0,
      "evidence": "관계를 보여주는 SQL 조각"
    }}
  ]
}}
```
"""
    
    def _parse_relationship_response(self, response: str) -> List[Dict]:
        """LLM 응답을 파싱하여 관계 정보 추출"""
        try:
            # JSON 블록 찾기
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # JSON 블록이 없으면 전체 응답에서 JSON 찾기
                json_str = response.strip()
            
            # JSON 파싱
            data = json.loads(json_str)
            
            if isinstance(data, dict) and 'relationships' in data:
                return data['relationships']
            elif isinstance(data, list):
                return data
            else:
                logger.warning("예상되지 않은 응답 형식")
                return []
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON 파싱 실패: {e}")
            logger.debug(f"원본 응답: {response}")
            return []
        except Exception as e:
            logger.error(f"응답 처리 실패: {e}")
            return []
    
    def _validate_java_relationships(self, relationships: List[Dict], file_path: str) -> List[Dict]:
        """Java 관계 검증"""
        validated = []
        
        for rel in relationships:
            # 필수 필드 확인
            if not all(key in rel for key in ['type', 'source', 'target', 'confidence']):
                continue
            
            # 신뢰도 검증
            if not isinstance(rel['confidence'], (int, float)) or not 0 <= rel['confidence'] <= 1:
                rel['confidence'] = 0.5  # 기본값
            
            # 관계 타입 검증
            valid_types = ['dependency', 'reference', 'calls', 'annotation_based', 'import']
            if rel['type'] not in valid_types:
                continue
            
            # 프로젝트 내부 클래스만 허용
            if not (rel['source'].startswith('com.example') or rel['target'].startswith('com.example')):
                continue
            
            # 메타데이터 추가
            rel['analysis_source'] = 'llm'
            rel['file_path'] = file_path
            
            validated.append(rel)
        
        logger.debug(f"Java 관계 검증 완료: {len(relationships)} → {len(validated)}")
        return validated
    
    def _validate_mybatis_relationships(self, relationships: List[Dict], file_path: str) -> List[Dict]:
        """MyBatis 관계 검증"""
        validated = []
        
        for rel in relationships:
            if not all(key in rel for key in ['type', 'source', 'target', 'confidence']):
                continue
            
            if not isinstance(rel['confidence'], (int, float)) or not 0 <= rel['confidence'] <= 1:
                rel['confidence'] = 0.5
            
            valid_types = ['implements', 'references', 'maps_to', 'parameter']
            if rel['type'] not in valid_types:
                continue
            
            rel['analysis_source'] = 'llm'
            rel['file_path'] = file_path
            
            validated.append(rel)
        
        logger.debug(f"MyBatis 관계 검증 완료: {len(relationships)} → {len(validated)}")
        return validated
    
    def _validate_jsp_relationships(self, relationships: List[Dict], file_path: str) -> List[Dict]:
        """JSP 관계 검증"""
        validated = []
        
        for rel in relationships:
            if not all(key in rel for key in ['type', 'source', 'target', 'confidence']):
                continue
            
            if not isinstance(rel['confidence'], (int, float)) or not 0 <= rel['confidence'] <= 1:
                rel['confidence'] = 0.5
            
            valid_types = ['calls', 'references', 'displays']
            if rel['type'] not in valid_types:
                continue
            
            rel['analysis_source'] = 'llm'
            rel['file_path'] = file_path
            
            validated.append(rel)
        
        logger.debug(f"JSP 관계 검증 완료: {len(relationships)} → {len(validated)}")
        return validated
    
    def _validate_sql_relationships(self, relationships: List[Dict], sql_id: str) -> List[Dict]:
        """SQL 관계 검증"""
        validated = []
        
        for rel in relationships:
            if not all(key in rel for key in ['type', 'source', 'target', 'confidence']):
                continue
            
            if not isinstance(rel['confidence'], (int, float)) or not 0 <= rel['confidence'] <= 1:
                rel['confidence'] = 0.5
            
            valid_types = ['join', 'foreign_key', 'data_flow']
            if rel['type'] not in valid_types:
                continue
            
            rel['analysis_source'] = 'llm'
            rel['sql_id'] = sql_id
            
            validated.append(rel)
        
        logger.debug(f"SQL 관계 검증 완료: {len(relationships)} → {len(validated)}")
        return validated


class ProjectContextBuilder:
    """프로젝트 컨텍스트 구축기 - LLM 분석에 필요한 프로젝트 정보 수집"""
    
    def __init__(self, db_session):
        self.db_session = db_session
    
    def build_context(self, project_id: int = 1) -> Dict[str, Any]:
        """프로젝트 컨텍스트 구축"""
        from phase1.models.database import Class, File
        
        # 모든 클래스 정보 수집
        classes = self.db_session.query(Class).all()
        
        context = {
            'classes': [cls.fqn for cls in classes],
            'controllers': [cls.fqn for cls in classes if 'controller' in cls.fqn.lower()],
            'services': [cls.fqn for cls in classes if 'service' in cls.fqn.lower()],
            'mappers': [cls.fqn for cls in classes if 'mapper' in cls.fqn.lower()],
            'models': [cls.fqn for cls in classes if 'model' in cls.fqn.lower()],
        }
        
        # 파일 정보 수집
        files = self.db_session.query(File).all()
        context['files'] = {
            'java': [f.path for f in files if f.language == 'java'],
            'xml': [f.path for f in files if f.language == 'xml'], 
            'jsp': [f.path for f in files if f.language == 'jsp']
        }
        
        logger.info(f"프로젝트 컨텍스트 구축 완료: 클래스 {len(context['classes'])}개")
        return context