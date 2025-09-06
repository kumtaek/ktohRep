"""
Java Parser (Context7 기반)
Context7 라이브러리 문서를 참조하여 개발된 개선된 Java 파서
"""

import re
from typing import Dict, Any, List, Tuple
from .java_parser_context7 import JavaParserContext7

class JavaParser(JavaParserContext7):
    """Java 소스 코드 전용 파서 - 재현율 우선"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.confidence = 0.95  # Context7 기반으로 높은 신뢰도
        
        # Java 키워드
        self.java_keywords = {
            'abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch', 'char', 'class', 'const',
            'continue', 'default', 'do', 'double', 'else', 'enum', 'extends', 'final', 'finally', 'float',
            'for', 'goto', 'if', 'implements', 'import', 'instanceof', 'int', 'interface', 'long', 'native',
            'new', 'package', 'private', 'protected', 'public', 'return', 'short', 'static', 'strictfp',
            'super', 'switch', 'synchronized', 'this', 'throw', 'throws', 'transient', 'try', 'void',
            'volatile', 'while', 'true', 'false', 'null'
        }
        
        # Java 어노테이션 패턴
        self.annotation_patterns = [
            re.compile(r'@(\w+)(?:\(([^)]*)\))?', re.IGNORECASE),
            re.compile(r'@(\w+)\s*\{([^}]*)\}', re.IGNORECASE | re.DOTALL),
        ]
        
        # SQL 관련 패턴
        self.sql_patterns = {
            'string_literals': [
                re.compile(r'"([^"]*(?:SELECT|FROM|WHERE|JOIN|UPDATE|INSERT|DELETE|CREATE|ALTER|DROP)[^"]*)"', re.IGNORECASE),
                re.compile(r"'([^']*(?:SELECT|FROM|WHERE|JOIN|UPDATE|INSERT|DELETE|CREATE|ALTER|DROP)[^']*)'", re.IGNORECASE),
            ],
            'string_builder': [
                re.compile(r'StringBuilder\s+\w+\s*=\s*new\s+StringBuilder\s*\(([^)]*)\)', re.IGNORECASE),
                re.compile(r'(\w+)\.append\s*\(([^)]*)\)', re.IGNORECASE),
            ],
            'query_methods': [
                re.compile(r'(\w+)\.(?:createQuery|createNativeQuery|createSQLQuery)\s*\(([^)]*)\)', re.IGNORECASE),
                re.compile(r'(\w+)\.(?:find|findBy|findAll|save|update|delete)\s*\(([^)]*)\)', re.IGNORECASE),
            ]
        }
    
    def _get_parser_type(self) -> str:
        return 'java'
    
    def parse_content(self, content: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Java 소스 코드를 파싱하여 메타데이터 추출 (재현율 우선)
        
        Args:
            content: Java 소스 코드
            context: 컨텍스트 정보
            
        Returns:
            파싱된 메타데이터
        """
        # Java 파서는 정규화 없이 원본 컨텐츠 사용 (정규화가 메소드 구조를 깨뜨림)
        normalized_content = content
        
        result = {
            'classes': self._extract_classes_aggressive(normalized_content),
            'methods': self._extract_methods_aggressive(normalized_content),
            'variables': self._extract_variables_aggressive(normalized_content),
            'annotations': self._extract_annotations_aggressive(normalized_content),
            'sql_strings': self._extract_sql_strings_aggressive(normalized_content),
            'imports': self._extract_imports_aggressive(normalized_content),
            'packages': self._extract_packages_aggressive(normalized_content),
            'dependencies': self._extract_dependencies_aggressive(normalized_content),
            'file_metadata': self._extract_file_metadata(context),
            'confidence': self.confidence
        }
        
        return result
    
    def _extract_classes_aggressive(self, content: str) -> List[Dict[str, Any]]:
        """클래스를 공격적으로 추출 (재현율 우선, 중복 제거)"""
        classes = []
        seen_classes = set()  # 중복 제거를 위한 집합
        
        # 클래스 선언 패턴들
        class_patterns = [
            r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?\s*\{',
            r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{',
            r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?class\s+(\w+)\s*\{',
        ]
        
        for pattern in class_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                class_name = match.group(1)
                
                # 중복 제거
                if class_name in seen_classes:
                    continue
                seen_classes.add(class_name)
                
                extends_class = match.group(2) if len(match.groups()) > 1 and match.group(2) else None
                implements_interfaces = match.group(3) if len(match.groups()) > 2 and match.group(3) else None
                
                classes.append({
                    'name': class_name,
                    'extends': extends_class,
                    'implements': implements_interfaces.split(',') if implements_interfaces else [],
                    'type': 'class'
                })
        
        # 인터페이스 선언 패턴
        interface_patterns = [
            r'(?:public\s+)?interface\s+(\w+)(?:\s+extends\s+([^{]+))?\s*\{',
            r'(?:public\s+)?interface\s+(\w+)\s*\{',
        ]
        
        for pattern in interface_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                interface_name = match.group(1)
                extends_interfaces = match.group(2) if len(match.groups()) > 1 and match.group(2) else None
                
                classes.append({
                    'name': interface_name,
                    'extends': extends_interfaces.split(',') if extends_interfaces else [],
                    'implements': [],
                    'type': 'interface'
                })
        
        return classes
    
    def _extract_methods_aggressive(self, content: str) -> List[Dict[str, Any]]:
        """메서드를 공격적으로 추출 (재현율 우선)"""
        methods = []
        
        # 메서드 선언 패턴들 (검증된 버전)
        method_patterns = [
            # 일반 메소드 패턴 (어노테이션 포함, 중괄호로 끝나는 것만)
            r'(?:@\w+(?:\([^)]*\))?\s*\n\s*)*(?:public|private|protected|static)\s+(\w+)\s+(\w+)\s*\(([^)]*)\)\s*\{',
        ]
        
        for pattern in method_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if len(match.groups()) < 3:
                    continue  # 그룹이 부족하면 건너뛰기
                    
                return_type = match.group(1)
                method_name = match.group(2)
                parameters = match.group(3)
                throws_exceptions = match.group(4) if len(match.groups()) > 3 and match.group(4) else None
                
                # 매개변수 파싱
                param_list = []
                if parameters and parameters.strip():
                    param_parts = [p.strip() for p in parameters.split(',')]
                    for param in param_parts:
                        if param:
                            param_list.append(param)
                
                methods.append({
                    'name': method_name,
                    'return_type': return_type,
                    'parameters': param_list,
                    'throws': throws_exceptions.split(',') if throws_exceptions and hasattr(throws_exceptions, 'split') else [],
                    'modifiers': self._extract_method_modifiers(match.group(0))
                })
        
        return methods
    
    def _extract_variables_aggressive(self, content: str) -> List[Dict[str, Any]]:
        """변수를 공격적으로 추출 (재현율 우선)"""
        variables = []
        
        # 변수 선언 패턴들
        variable_patterns = [
            r'(?:public|private|protected|static|final|volatile|transient)?\s*(?:<[^>]+>\s+)?(\w+)\s+(\w+)\s*=\s*([^;]+);',
            r'(?:public|private|protected|static|final|volatile|transient)?\s*(?:<[^>]+>\s+)?(\w+)\s+(\w+)\s*;',
            r'(\w+)\s+(\w+)\s*=\s*([^;]+);',
        ]
        
        for pattern in variable_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                var_type = match.group(1)
                var_name = match.group(2)
                var_value = match.group(3) if len(match.groups()) > 2 and match.group(3) else None
                
                if not self._is_keyword(var_type) and not self._is_java_keyword(var_type):
                    variables.append({
                        'name': var_name,
                        'type': var_type,
                        'value': var_value,
                        'modifiers': self._extract_variable_modifiers(match.group(0))
                    })
        
        return variables
    
    def _extract_annotations_aggressive(self, content: str) -> List[Dict[str, Any]]:
        """어노테이션을 공격적으로 추출 (재현율 우선)"""
        annotations = []
        
        for pattern in self.annotation_patterns:
            matches = pattern.finditer(content)
            for match in matches:
                annotation_name = match.group(1)
                annotation_value = match.group(2) if len(match.groups()) > 1 and match.group(2) else None
                
                annotations.append({
                    'name': annotation_name,
                    'value': annotation_value,
                    'full_text': match.group(0)
                })
        
        return annotations
    
    def _extract_sql_strings_aggressive(self, content: str) -> List[Dict[str, Any]]:
        """SQL 문자열을 공격적으로 추출 (재현율 우선)"""
        sql_strings = []
        
        # 1. 문자열 리터럴에서 SQL 추출
        for pattern in self.sql_patterns['string_literals']:
            matches = pattern.finditer(content)
            for match in matches:
                sql_content = match.group(1)
                sql_strings.append({
                    'type': 'string_literal',
                    'content': sql_content,
                    'confidence': 'high'
                })
        
        # 2. StringBuilder에서 SQL 추출
        for pattern in self.sql_patterns['string_builder']:
            matches = pattern.finditer(content)
            for match in matches:
                sql_content = match.group(1) if len(match.groups()) > 0 else match.group(0)
                sql_strings.append({
                    'type': 'string_builder',
                    'content': sql_content,
                    'confidence': 'medium'
                })
        
        # 3. JPA/Hibernate 쿼리 메서드에서 SQL 추출
        for pattern in self.sql_patterns['query_methods']:
            matches = pattern.finditer(content)
            for match in matches:
                method_name = match.group(1)
                query_content = match.group(2) if len(match.groups()) > 1 else match.group(0)
                sql_strings.append({
                    'type': 'query_method',
                    'method': method_name,
                    'content': query_content,
                    'confidence': 'medium'
                })
        
        return sql_strings
    
    def _extract_imports_aggressive(self, content: str) -> List[str]:
        """import 문을 공격적으로 추출 (재현율 우선)"""
        imports = []
        
        import_pattern = r'import\s+(?:static\s+)?([^;]+);'
        matches = re.finditer(import_pattern, content, re.IGNORECASE)
        
        for match in matches:
            import_statement = match.group(1).strip()
            imports.append(import_statement)
        
        return imports
    
    def _extract_packages_aggressive(self, content: str) -> List[str]:
        """package 문을 공격적으로 추출 (재현율 우선)"""
        packages = []
        
        package_pattern = r'package\s+([^;]+);'
        matches = re.finditer(package_pattern, content, re.IGNORECASE)
        
        for match in matches:
            package_name = match.group(1).strip()
            packages.append(package_name)
        
        return packages
    
    def _extract_dependencies_aggressive(self, content: str) -> List[Dict[str, str]]:
        """의존성을 공격적으로 추출 (재현율 우선)"""
        dependencies = []
        
        # import 문에서 의존성 추출
        import_pattern = r'import\s+(?:static\s+)?([^;]+);'
        matches = re.finditer(import_pattern, content, re.IGNORECASE)
        
        for match in matches:
            import_statement = match.group(1).strip()
            
            # 패키지 구조 분석
            if '.' in import_statement:
                parts = import_statement.split('.')
                if len(parts) >= 2:
                    package_name = '.'.join(parts[:-1])
                    class_name = parts[-1]
                    
                    dependencies.append({
                        'package': package_name,
                        'class': class_name,
                        'full_import': import_statement,
                        'type': 'import'
                    })
        
        return dependencies
    
    def _extract_method_modifiers(self, method_declaration: str) -> List[str]:
        """메서드 수정자 추출"""
        modifiers = []
        
        modifier_keywords = ['public', 'private', 'protected', 'static', 'final', 'abstract', 'synchronized', 'native', 'strictfp']
        
        for keyword in modifier_keywords:
            if re.search(r'\b' + keyword + r'\b', method_declaration, re.IGNORECASE):
                modifiers.append(keyword)
        
        return modifiers
    
    def _extract_variable_modifiers(self, variable_declaration: str) -> List[str]:
        """변수 수정자 추출"""
        modifiers = []
        
        modifier_keywords = ['public', 'private', 'protected', 'static', 'final', 'volatile', 'transient']
        
        for keyword in modifier_keywords:
            if re.search(r'\b' + keyword + r'\b', variable_declaration, re.IGNORECASE):
                modifiers.append(keyword)
        
        return modifiers
    
    def _is_java_keyword(self, word: str) -> bool:
        """Java 키워드인지 확인"""
        return word.lower() in self.java_keywords
    
    def _is_keyword(self, word: str) -> bool:
        """키워드인지 확인 (Java 키워드와 SQL 키워드 포함)"""
        return self._is_java_keyword(word) or self._is_sql_keyword(word)
    
    def _is_sql_keyword(self, word: str) -> bool:
        """SQL 키워드인지 확인"""
        sql_keywords = {
            'select', 'from', 'where', 'join', 'inner', 'left', 'right', 'outer',
            'update', 'set', 'insert', 'into', 'values', 'delete', 'create', 'alter',
            'drop', 'truncate', 'merge', 'union', 'order', 'by', 'group', 'having',
            'distinct', 'count', 'sum', 'avg', 'max', 'min', 'case', 'when', 'then',
            'else', 'end', 'and', 'or', 'not', 'in', 'exists', 'between', 'like',
            'is', 'null', 'as', 'asc', 'desc', 'limit', 'offset'
        }
        return word.lower() in sql_keywords
    
    def _remove_comments(self, content: str) -> str:
        """Java 주석 제거"""
        # 한 줄 주석 제거
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        # 블록 주석 제거
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        return content
    
    def _get_database_type(self) -> str:
        """데이터베이스 타입 반환"""
        return "java"
    
    def parse_sql(self, sql_content: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """SQL 파싱 (Java에서는 SQL 문자열 추출)"""
        sql_units = []
        
        # SQL 문자열 패턴 찾기
        sql_patterns = [
            r'["\']([^"\']*(?:SELECT|FROM|WHERE|JOIN|UPDATE|INSERT|DELETE|CREATE|ALTER|DROP|TRUNCATE|MERGE)[^"\']*)["\']',
            r'String\s+sql\s*=\s*["\']([^"\']*)["\']',
            r'StringBuilder\s+\w+\s*=\s*new\s+StringBuilder\s*\(["\']([^"\']*)["\']'
        ]
        
        for pattern in sql_patterns:
            matches = re.finditer(pattern, sql_content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                sql_text = match.group(1) if len(match.groups()) > 0 else match.group(0)
                if sql_text and any(keyword in sql_text.upper() for keyword in ['SELECT', 'FROM', 'WHERE', 'UPDATE', 'INSERT', 'DELETE']):
                    sql_units.append({
                        'sql_content': sql_text,
                        'sql_type': self._determine_sql_type(sql_text),
                        'unique_id': self._generate_unique_id('sql', sql_text)
                    })
        
        return sql_units
    
    def _determine_sql_type(self, sql_content: str) -> str:
        """SQL 타입 결정"""
        sql_upper = sql_content.upper().strip()
        if sql_upper.startswith('SELECT'):
            return 'SELECT'
        elif sql_upper.startswith('UPDATE'):
            return 'UPDATE'
        elif sql_upper.startswith('INSERT'):
            return 'INSERT'
        elif sql_upper.startswith('DELETE'):
            return 'DELETE'
        elif sql_upper.startswith('CREATE'):
            return 'CREATE'
        elif sql_upper.startswith('ALTER'):
            return 'ALTER'
        elif sql_upper.startswith('DROP'):
            return 'DROP'
        elif sql_upper.startswith('TRUNCATE'):
            return 'TRUNCATE'
        elif sql_upper.startswith('MERGE'):
            return 'MERGE'
        else:
            return 'UNKNOWN'
