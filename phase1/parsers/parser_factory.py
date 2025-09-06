"""
파서 팩토리
데이터베이스 타입과 쿼리 타입에 따라 적절한 파서를 생성하고 관리합니다.
"""

from typing import Dict, Any, Optional, Type
from parsers.base_parser import BaseParser
from parsers.oracle.oracle_select_parser import OracleSelectParser
from parsers.oracle.oracle_update_parser import OracleUpdateParser
from parsers.oracle.oracle_delete_parser import OracleDeleteParser
from parsers.oracle.oracle_insert_parser import OracleInsertParser
from parsers.oracle.oracle_truncate_parser import OracleTruncateParser
from parsers.oracle.oracle_merge_parser import OracleMergeParser
from parsers.spring.spring_parser import SpringParser
from parsers.jpa.jpa_parser import JPAParser
from parsers.mybatis.mybatis_parser import MyBatisParser
from parsers.jsp.jsp_parser import JSPParser
from parsers.java.javaparser_enhanced import JavaParserEnhanced as JavaParser
from pathlib import Path
import asyncio

class ParserFactory:
    """파서 생성 및 관리 팩토리"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        파서 팩토리 초기화
        
        Args:
            config: 설정 딕셔너리
        """
        self.config = config
        self._parsers = {}
        self._register_parsers()
    
    def _register_parsers(self):
        """사용 가능한 파서들을 등록"""
        self._parsers = {
            'oracle': {
                'select': OracleSelectParser,
                'update': OracleUpdateParser,
                'delete': OracleDeleteParser,
                'insert': OracleInsertParser,
                'truncate': OracleTruncateParser,
                'merge': OracleMergeParser,
            },
            'spring': {
                'framework': SpringParser,
            },
            'jpa': {
                'persistence': JPAParser,
            },
            'mybatis': {
                'mapper': MyBatisParser,
            },
            'jsp': {
                'pages': JSPParser,
            },
            'java': {
                'source': JavaParser,
            },
            # 향후 추가될 데이터베이스들
            # 'postgresql': {
            #     'select': PostgreSQLSelectParser,
            #     'update': PostgreSQLUpdateParser,
            # },
            # 'mssql': {
            #     'select': MSSQLSelectParser,
            #     'update': MSSQLUpdateParser,
            # }
        }
    
    def get_parser(self, db_type: str, query_type: str) -> Optional[BaseParser]:
        """
        지정된 데이터베이스 타입과 쿼리 타입에 맞는 파서를 반환
        
        Args:
            db_type: 데이터베이스 타입 (예: 'oracle', 'postgresql', 'mssql')
            query_type: 쿼리 타입 (예: 'select', 'update', 'delete', 'insert')
            
        Returns:
            해당하는 파서 인스턴스 또는 None
        """
        if db_type not in self._parsers:
            return None
        
        if query_type not in self._parsers[db_type]:
            return None
        
        parser_class = self._parsers[db_type][query_type]
        return parser_class(self.config)
    
    def get_available_parsers(self) -> Dict[str, list]:
        """
        사용 가능한 파서 목록을 반환
        
        Returns:
            사용 가능한 파서 목록
        """
        return {
            db_type: list(parsers.keys())
            for db_type, parsers in self._parsers.items()
        }
    
    def auto_detect_parser(self, content: str, file_extension: str = '') -> Optional[BaseParser]:
        """
        컨텐츠를 분석하여 자동으로 적절한 파서를 선택
        
        Args:
            content: 분석할 컨텐츠
            file_extension: 파일 확장자
            
        Returns:
            적절한 파서 인스턴스 또는 None
        """
        # 파일 확장자 기반 파서 선택
        if file_extension.lower() in ['sql', 'ora']:
            # SQL 파일인 경우 쿼리 타입 자동 감지
            query_type = self._detect_query_type(content)
            if query_type:
                return self.get_parser('oracle', query_type)
        elif file_extension.lower() in ['java']:
            # Java 파일인 경우 Java 파서 선택
            return self.get_parser('java', 'source')
        elif file_extension.lower() in ['xml']:
            # XML 파일인 경우 MyBatis 또는 Spring 파서 선택
            if self._is_mybatis_file(content):
                return self.get_parser('mybatis', 'mapper')
            elif 'spring' in content.lower() or 'bean' in content.lower():
                return self.get_parser('spring', 'framework')
        elif file_extension.lower() in ['jsp']:
            # JSP 파일인 경우 JSP 파서 선택
            return self.get_parser('jsp', 'pages')
        
        # 컨텐츠 기반 파서 선택
        query_type = self._detect_query_type(content)
        if query_type:
            return self.get_parser('oracle', query_type)
        
        # Spring 관련 컨텐츠 감지
        if '@Component' in content or '@Service' in content or '@Repository' in content:
            return self.get_parser('spring', 'framework')
        
        # JPA 관련 컨텐츠 감지
        if '@Entity' in content or '@Table' in content or '@Column' in content:
            return self.get_parser('jpa', 'persistence')
        
        # MyBatis 관련 컨텐츠 감지
        if '<select' in content or '<insert' in content or '<update' in content:
            return self.get_parser('mybatis', 'mapper')
        
        # JSP 관련 컨텐츠 감지
        if '<%' in content or '<jsp:' in content or '<c:' in content:
            return self.get_parser('jsp', 'pages')
        
        return None
    
    def _is_mybatis_file(self, content: str) -> bool:
        """
        XML 파일이 MyBatis 파일인지 판별
        
        Args:
            content: XML 파일 내용
            
        Returns:
            MyBatis 파일 여부
        """
        mybatis_indicators = [
            'mybatis', 'mapper', 'namespace', 
            '<select', '<insert', '<update', '<delete',
            '#{', '${', '<if', '<foreach', '<choose'
        ]
        
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in mybatis_indicators)
    
    def _detect_query_type(self, content: str) -> Optional[str]:
        """
        컨텐츠를 분석하여 쿼리 타입을 자동 감지
        
        Args:
            content: 분석할 컨텐츠
            
        Returns:
            감지된 쿼리 타입 또는 None
        """
        content_upper = content.upper().strip()
        
        # SELECT 쿼리 감지
        if content_upper.startswith('SELECT'):
            return 'select'
        
        # UPDATE 쿼리 감지
        if content_upper.startswith('UPDATE'):
            return 'update'
        
        # DELETE 쿼리 감지
        if content_upper.startswith('DELETE'):
            return 'delete'
        
        # INSERT 쿼리 감지
        if content_upper.startswith('INSERT'):
            return 'insert'
        
        # TRUNCATE 쿼리 감지
        if content_upper.startswith('TRUNCATE'):
            return 'truncate'
        
        # MERGE 쿼리 감지
        if content_upper.startswith('MERGE'):
            return 'merge'
        
        return None
    
    def parse_with_best_parser(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        최적의 파서를 자동 선택하여 파싱 수행
        
        Args:
            content: 분석할 컨텐츠
            context: 컨텍스트 정보
            
        Returns:
            파싱된 메타데이터
        """
        # 자동 파서 선택
        parser = self.auto_detect_parser(content, context.get('file_extension', ''))
        
        if parser:
            return parser.parse_content(content, context)
        else:
            # 파서를 찾을 수 없는 경우 기본 정보만 반환
            return {
                'error': 'No suitable parser found',
                'content_preview': content[:200] + '...' if len(content) > 200 else content,
                'file_metadata': {
                    'file_path': context.get('file_path', ''),
                    'file_name': context.get('file_name', ''),
                    'file_extension': context.get('file_extension', ''),
                    'parser_type': 'unknown',
                    'confidence': 'none'
                }
            }

    async def parse(self, content: str, file_path: str) -> Any:
        """
        파일 경로와 내용을 기반으로 적절한 파서를 선택하여 파싱 수행
        
        Args:
            content: 분석할 파일 내용
            file_path: 파일 경로
            
        Returns:
            파싱된 메타데이터
        """
        file_extension = Path(file_path).suffix.lower()
        
        # 자동 파서 선택
        parser = self.auto_detect_parser(content, file_extension)
        
        if parser:
            try:
                # 파서가 async parse 메서드를 지원하는지 확인
                if hasattr(parser, 'parse') and asyncio.iscoroutinefunction(parser.parse):
                    return await parser.parse(content, file_path)
                elif hasattr(parser, 'parse'):
                    return parser.parse(content, file_path)
                elif hasattr(parser, 'parse_content'):
                    return parser.parse_content(content, {'file_path': file_path, 'file_extension': file_extension})
                else:
                    raise ValueError(f"파서 {type(parser)}에 적절한 parse 메서드가 없습니다")
            except Exception as e:
                # 파서 실행 중 오류 발생 시 기본 정보 반환
                return {
                    'error': f'Parser execution failed: {str(e)}',
                    'content_preview': content[:200] + '...' if len(content) > 200 else content,
                    'file_metadata': {
                        'file_path': file_path,
                        'file_name': Path(file_path).name,
                        'file_extension': file_extension,
                        'parser_type': 'unknown',
                        'confidence': 'none'
                    }
                }
        else:
            # 파서를 찾을 수 없는 경우 기본 정보만 반환
            return {
                'error': 'No suitable parser found',
                'content_preview': content[:200] + '...' if len(content) > 200 else content,
                'file_metadata': {
                    'file_path': file_path,
                    'file_name': Path(file_path).name,
                    'file_extension': file_extension,
                    'parser_type': 'unknown',
                    'confidence': 'none'
                }
            }
