# 소스 분석기 2차 개발 개선안 (Gemini 제안)

## 1. 개요

본 문서는 `1단계_002차_개발내역.md`에 명시된 현재 소스 분석기 시스템의 개발 현황과 `1단계_002차_개발후_1_리뷰.md`에서 도출된 문제점 및 개선 방안, 그리고 `prd_v4.md`의 최종 제품 요구사항을 종합하여, 소스 분석기의 정확성, 성능, 안정성 및 확장성을 대폭 향상시키기 위한 상세 개선 계획을 제시합니다.

## 2. 현재 시스템 분석 및 주요 개선 필요 영역

### 2.1. 현재 시스템의 주요 성과 (1단계_002차_개발내역.md 기반)

*   **통합 로깅 시스템**: `src/utils/logger.py`를 통한 체계적인 로깅 및 오류 추적 기능 구현.
*   **데이터베이스 스키마 확장**: `CodeMetric`, `Duplicate`, `DuplicateInstance`, `ParseResult` 테이블 추가로 품질 지표 및 중복도 분석 기반 마련.
*   **신뢰도 계산 시스템**: `src/utils/improved_confidence_calculator.py`를 통한 AST 품질, 정적 규칙, DB 매칭 등 다면적 신뢰도 평가 로직 구현.
*   **병렬 처리 시스템**: `src/database/metadata_engine.py`에서 `ThreadPoolExecutor`를 활용한 파일 단위 병렬 처리 구현 (성능 지표: 126.9 파일/초).
*   **개선된 예외 처리**: 구체적인 예외 타입별 처리 및 체계적인 오류 보고.
*   **기술적 문제 해결**: Windows 유니코드, DB 세션 초기화, Edge 테이블 제약조건 문제 해결.

### 2.2. 주요 개선 필요 영역 (1단계_002차_개발후_1_리뷰.md 및 prd_v4.md 기반)

현재 시스템은 1차 개선을 통해 안정성과 기본적인 성능을 확보했지만, `prd_v4.md`의 요구사항을 충족하고 `1단계_002차_개발후_1_리뷰.md`에서 지적된 한계를 극복하기 위해 다음과 같은 영역에서 심층적인 개선이 필요합니다.

1.  **파서 정확성 및 확장성**: 정규표현식 기반 JSP/MyBatis 파싱의 한계, 동적 SQL 조합 폭발 문제, 복잡한 SQL 패턴 추출의 한계.
2.  **메타데이터 엔진 성능 및 안정성**: 메모리 집약적 해시 계산, 체계적 로깅 및 에러 보고 강화.
3.  **타입 안정성 및 의존성 분석**: 원시 타입 사용으로 인한 타입 추론 어려움, Spring 어노테이션 및 람다/메서드 참조 미처리로 인한 의존성 분석 불완전성.
4.  **LLM 활용 및 보강 메타정보 생성**: DB 사전 보강 코멘트, LLM 기반 요약 및 취약점 분석, CONFIDENCE 산식 고도화.
5.  **품질 및 보안 분석 고도화**: SAST 통합, OWASP Top 10 취약점 분석, 정교한 코드 품질 메트릭.

## 3. 상세 개선 방안

### 3.1. 파서 정확성 및 확장성 강화

#### 3.1.1. JSP/MyBatis 파서 개선 (`src/parsers/jsp_mybatis_parser.py`)

*   **Tree-Sitter 기반 JSP/Java AST 파서 도입**:
    *   **문제점**: 현재 JSP 파서는 정규표현식 기반으로 스크립틀릿 내 SQL 키워드를 단순 검색하여, JSTL/커스텀 태그, 변수 조합 동적 쿼리 등을 추적하지 못합니다.
    *   **개선 방안**: `prd_v4.md`에서 제안된 Tree-Sitter 기반 파서를 도입하여 JSP의 HTML/스크립틀릿 구조를 AST로 변환하고, 스크립틀릿 내부의 Java 코드를 Java AST로 파싱하여 SQL 생성 문맥을 정확히 추적합니다. 이를 통해 쿼리 문자열이 변수에 저장되거나 메서드를 통해 조합되는 경우까지 포착하여 정확도를 향상시킵니다.
    *   **코드 예시 (개념적 변경)**:
        ```python
        # src/parsers/jsp_mybatis_parser.py (개념적)

        # 기존 정규표현식 기반 SQL 추출 로직 대체
        # def _extract_sql_from_jsp_regex(self, content: str) -> List[SqlUnit]: ...

        # Tree-Sitter 파서 초기화 (Java, JSP grammar 로드)
        from tree_sitter import Language, Parser
        JAVA_LANGUAGE = Language('path/to/my-java.so', 'java')
        JSP_LANGUAGE = Language('path/to/my-jsp.so', 'jsp') # 가상의 JSP grammar

        class JspMybatisParser:
            def __init__(self, ...):
                self.java_parser = Parser()
                self.java_parser.set_language(JAVA_LANGUAGE)
                self.jsp_parser = Parser()
                self.jsp_parser.set_language(JSP_LANGUAGE)
                # ...

            def parse_jsp_file(self, file_path: str, content: str) -> ParseResult:
                jsp_tree = self.jsp_parser.parse(bytes(content, "utf8"))
                # JSP AST 순회: 스크립틀릿 (<%...%>) 노드 찾기
                for node in jsp_tree.root_node.children:
                    if node.type == 'scriptlet': # 가상의 scriptlet 노드 타입
                        java_code = node.text.decode("utf8")
                        java_tree = self.java_parser.parse(bytes(java_code, "utf8"))
                        # Java AST 순회: SQL 문자열 리터럴, 변수 조합 등 추적
                        # ... SQLUnit 객체 생성 로직 ...
                # ...
        ```

*   **동적 SQL 분기 최적화**:
    *   **문제점**: MyBatis 파서가 `<if>`, `<choose>`, `<foreach>` 태그를 전부 확장하여 조합 폭발을 일으키고, `<trim>`, `<set>` 태그를 무시하여 실제 쿼리와 차이가 발생합니다.
    *   **개선 방안**: 동적 태그를 DFA(결정적 유한 오토마타) 또는 트리 구조로 표현하여 분기 조건을 관리합니다. `<choose>`는 조건별 노드를 생성하고, `<foreach>`는 0회 또는 n회 반복하는 두 가지 패턴으로 제한하여 조합 폭발을 줄입니다. `lxml`의 `iterparse`를 활용하여 XML 파싱 시 줄 번호와 위치 정보를 정확히 기록합니다.
    *   **코드 예시 (개념적 변경)**:
        ```python
        # src/parsers/jsp_mybatis_parser.py (MyBatis 파싱 로직 내)

        from lxml import etree

        class JspMybatisParser:
            # ...
            def _parse_mybatis_xml(self, file_path: str, content: str) -> List[SqlUnit]:
                sql_units = []
                # 기존 superset 확장 로직 대체
                # ...

                # lxml.iterparse를 이용한 스트리밍 파싱 및 위치 정보 기록
                for event, element in etree.iterparse(file_path, events=("start", "end")):
                    if event == "start":
                        line_number = element.sourceline
                        # 동적 태그 처리 로직 (DFA/트리 기반)
                        # ...
                        if element.tag in ['select', 'insert', 'update', 'delete']:
                            # SQL AST 분석 라이브러리 (sqlparse/JSqlParser) 연동
                            raw_sql = etree.tostring(element, method='text', encoding='unicode')
                            # ... _extract_sql_patterns 대신 AST 기반 분석 호출 ...
                            # SqlUnit 생성 시 line_number 활용
                            # sql_units.append(SqlUnit(..., start_line=line_number, ...))
                return sql_units
        ```

*   **SQL AST 분석 라이브러리 도입**:
    *   **문제점**: `_extract_sql_patterns`가 정규표현식 기반으로 `JOIN`과 `WHERE` 절만 단순 매칭하여 서브쿼리, CTE, ANSI JOIN 등 복잡한 SQL을 처리하지 못합니다.
    *   **개선 방안**: `prd_v4.md`에서 제안된 JSqlParser (Java 기반이지만 Python 래퍼 또는 직접 연동 고려) 또는 `sqlparse`, `SQLGlot`와 같은 Python 라이브러리를 도입하여 SQL을 AST로 변환한 뒤 JOIN, 필터 조건, 서브쿼리 등을 구조적으로 추출합니다.
    *   **코드 예시 (`src/parsers/sql_parser.py` 또는 `jsp_mybatis_parser.py` 내 연동)**:
        ```python
        # src/parsers/sql_parser.py (또는 JspMybatisParser 내부 메서드)

        import sqlparse
        from sqlglot import parse_one, exp

        class SqlParser:
            # ...
            def _extract_ast_based_sql_info(self, raw_sql: str) -> Dict:
                parsed_statements = sqlparse.parse(raw_sql)
                if not parsed_statements:
                    return {}

                # sqlparse를 이용한 기본 구조 분석
                # ...

                # SQLGlot을 이용한 고급 AST 분석 (JOIN, WHERE, CTE 등)
                try:
                    expression = parse_one(raw_sql, read='oracle') # Oracle dialect 지원
                    
                    joins = []
                    for join_exp in expression.find_all(exp.Join):
                        left_table = join_exp.left.this.name if isinstance(join_exp.left, exp.Table) else None
                        right_table = join_exp.this.this.name if isinstance(join_exp.this, exp.Table) else None
                        on_condition = join_exp.on.sql() if join_exp.on else None
                        joins.append({'left_table': left_table, 'right_table': right_table, 'on_condition': on_condition})

                    filters = []
                    for where_exp in expression.find_all(exp.Where):
                        # WHERE 절 조건 추출 로직 (복잡도에 따라 재귀 분석 필요)
                        filters.append(where_exp.this.sql())
                    
                    # CTE, Subquery 등 추가 추출
                    # ...

                    return {'joins': joins, 'filters': filters, 'tables': list(expression.find_all(exp.Table))}
                except Exception as e:
                    # 로깅 모듈 사용
                    self.logger.error(f"SQLGlot 파싱 실패: {e} for SQL: {raw_sql[:100]}...")
                    return {}
        ```

#### 3.1.2. Java 파서 개선 (기존 `java_parser.py` 확장)

*   **Spring DI 추적 및 의존성 그래프 고도화**:
    *   **문제점**: Java 파서가 `@Service`, `@Repository`, `@Mapper`, `@Autowired` 등 Spring 어노테이션을 인식하지 못해 의존 관계 그래프가 누락됩니다. 메서드 참조나 람다 표현식 내부 호출도 추적하지 않습니다.
    *   **개선 방안**: JavaParser (또는 Tree-Sitter Java grammar)를 활용하여 AST 분석 시 Spring 어노테이션을 심층 분석하고, `@Autowired` 및 생성자 주입 관계를 메타데이터에 포함시킵니다. 람다식 (`ClassName::method`) 및 스트림 API 내부 호출도 추적하여 실제 호출 경로를 정확하게 파악하고 `edges` 테이블에 저장합니다.
    *   **코드 예시 (`src/parsers/java_parser.py` 내)**:
        ```python
        # src/parsers/java_parser.py

        from javalang import parse
        from javalang.tree import MethodDeclaration, ClassDeclaration, Annotation, ReferenceType, BasicType
        from src.models.database import Class, Method, Edge # 가정

        class JavaParser:
            # ...
            def parse_java_file(self, file_path: str, content: str) -> ParseResult:
                # ... (기존 파싱 로직) ...
                tree = parse.parse(content)
                
                for path, node in tree.filter(ClassDeclaration):
                    class_annotations = [anno.name for anno in node.annotations if isinstance(anno, Annotation)]
                    # Spring DI 어노테이션 (예: @Service, @Repository, @Component) 처리
                    if any(anno in ['Service', 'Repository', 'Component', 'Controller'] for anno in class_annotations):
                        # Class 객체에 어노테이션 정보 추가
                        # ...
                        pass

                    for member in node.body:
                        if isinstance(member, MethodDeclaration):
                            method_annotations = [anno.name for anno in member.annotations if isinstance(anno, Annotation)]
                            # @Autowired, @GetMapping 등 메서드 어노테이션 처리
                            if 'Autowired' in method_annotations:
                                # 의존성 주입 관계를 Edge로 저장
                                # ...
                                pass
                            # HTTP API 엔드포인트 (예: @GetMapping) 추출
                            if any(anno in ['GetMapping', 'PostMapping', 'PutMapping', 'DeleteMapping'] for anno in method_annotations):
                                # API 엔드포인트 정보 추출 및 저장
                                # ...
                                pass

                            # 메서드 호출 및 람다/메서드 참조 추적 (더 복잡한 AST 순회 필요)
                            # javalang.tree.MethodInvocation, javalang.tree.MemberReference 등 활용
                            # ...
                # ...
                return parse_result
        ```

#### 3.1.3. SQL 패턴 추출 고도화 (`src/parsers/sql_parser.py`)

*   **AST 기반 조인 및 필수 필터 추출**:
    *   **문제점**: 현재 `_extract_sql_patterns`는 정규표현식 기반으로 단순 `JOIN`과 `WHERE` 절만 추출하여 복잡한 서브쿼리, CTE, ANSI JOIN, `IN` 절 등을 처리하지 못합니다.
    *   **개선 방안**: `prd_v4.md`의 요구사항에 따라 `sqlparse` 및 `SQLGlot` 라이브러리를 활용하여 SQL을 AST로 변환하고, 이를 기반으로 조인 조건 (`ON A.col = B.col`), 조인 연쇄, 서브쿼리 조인 조건, 그리고 동적 태그 외부 또는 항상 포함되는 필수 필터 (`DEL_YN <> 'N'`)를 정확하게 추출하여 `joins` 및 `required_filters` 테이블에 저장합니다.
    *   **코드 예시 (`src/parsers/sql_parser.py` 내)**:
        ```python
        # src/parsers/sql_parser.py

        import sqlparse
        from sqlglot import parse_one, exp
        from src.models.database import Join, RequiredFilter # 가정

        class SqlParser:
            # ...
            def extract_advanced_sql_info(self, sql_unit_id: int, raw_sql: str) -> Tuple[List[Join], List[RequiredFilter]]:
                joins = []
                required_filters = []

                try:
                    expression = parse_one(raw_sql, read='oracle') # Oracle dialect
                    
                    # 1. JOIN 조건 추출
                    for join_exp in expression.find_all(exp.Join):
                        left_table = join_exp.left.this.name if isinstance(join_exp.left, exp.Table) else None
                        right_table = join_exp.this.this.name if isinstance(join_exp.this, exp.Table) else None
                        on_condition = join_exp.on.sql() if join_exp.on else None
                        
                        # Join 객체 생성 및 저장 (inferred_pkfk, confidence는 추후 로직 추가)
                        joins.append(Join(
                            sql_id=sql_unit_id,
                            l_table=left_table,
                            l_col=None, # AST에서 컬럼 직접 추출 로직 필요
                            op='=', # ON 조건 분석하여 op 추출
                            r_table=right_table,
                            r_col=None, # AST에서 컬럼 직접 추출 로직 필요
                            inferred_pkfk=0,
                            confidence=0.8 # 초기 신뢰도
                        ))

                    # 2. 필수 필터 추출
                    for where_exp in expression.find_all(exp.Where):
                        # WHERE 절의 AST를 분석하여 '항상 적용되는' 필터 조건 식별
                        # MyBatis 동적 태그 외부 조건 또는 모든 분기 공통 조건
                        # 이 부분은 SQLGlot AST를 깊이 분석하는 로직이 필요
                        filter_condition = where_exp.this.sql()
                        # 예시: 'DEL_YN <> 'N'' 같은 상수 필터
                        if "DEL_YN <> 'N'" in filter_condition: # 실제로는 AST 기반으로 판단
                            required_filters.append(RequiredFilter(
                                sql_id=sql_unit_id,
                                table_name=None, # AST에서 테이블/컬럼 추출
                                column_name=None,
                                op='=',
                                value_repr="'N'",
                                always_applied=1,
                                confidence=1.0
                            ))
                except Exception as e:
                    self.logger.error(f"고급 SQL 정보 추출 실패: {e} for SQL: {raw_sql[:100]}...")

                return joins, required_filters
        ```

#### 3.1.4. PL/SQL 및 기타 언어 지원 (향후 확장)

*   `prd_v4.md`에 명시된 대로, Oracle Stored Procedure/Function 분석을 위해 Python `antlr-plsql` 및 JSQLParser를 활용하고, Python (`ast` 모듈), JavaScript/TypeScript/React/Vue.js (Tree-Sitter, `tsc`, ESLint 등) 지원을 위한 아키텍처를 설계합니다. 이는 2차 개발 이후의 로드맵으로 간주합니다.

### 3.2. 메타데이터 엔진 성능 및 안정성 개선

#### 3.2.1. 병렬 처리 검증 및 최적화 (`src/database/metadata_engine.py`)

*   **문제점**: `1단계_002차_개발후_1_리뷰.md`에서 병렬 처리 미사용이 지적되었으나, `1단계_002차_개발내역.md`에서는 `ThreadPoolExecutor`를 통한 병렬 처리가 구현되었다고 명시되어 있습니다. 이 부분에 대한 명확한 검증과 함께, 실제 대규모 프로젝트에서 병렬 파싱이 효과적으로 작동하는지 확인하고 최적화해야 합니다.
*   **개선 방안**: 현재 구현된 `ThreadPoolExecutor` 기반 병렬 파싱 로직을 재검토하여, `thread_count` 설정이 제대로 반영되고 각 파서 호출이 독립적인 스레드에서 실행되는지 확인합니다. 스레드 간 결과 병합 시 동기화 문제를 방지하고, 큐 크기 및 스레드 수를 설정 파일(`config/config.yaml`)로 유연하게 조정할 수 있도록 개선합니다.
*   **코드 예시 (`src/database/metadata_engine.py` 내)**:
    ```python
    # src/database/metadata_engine.py

    import concurrent.futures
    from typing import List, Dict, Any
    from src.utils.logger import AnalyzerLogger # 가정
    from src.config import Config # 가정

    class MetadataEngine:
        def __init__(self, config: Config):
            self.config = config
            self.logger = AnalyzerLogger()
            self.max_workers = self.config.get('analysis.thread_count', 4) # config에서 스레드 수 로드

        async def analyze_files_parallel(self, file_paths: List[str], project_id: int,
                                       parsers: Dict[str, Any]) -> Dict[str, Any]:
            self.logger.info(f"병렬 파일 분석 시작: {len(file_paths)}개 파일, {self.max_workers}개 워커")
            results = {'success': [], 'failed': []}
            
            # 배치 처리 로직 (기존 코드 유지 또는 개선)
            batches = [file_paths[i:i + self.max_workers * 2] for i in range(0, len(file_paths), self.max_workers * 2)]

            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_batch = {
                    executor.submit(self._analyze_batch_sync, batch, project_id, parsers): batch_idx
                    for batch_idx, batch in enumerate(batches)
                }

                for future in concurrent.futures.as_completed(future_to_batch):
                    batch_idx = future_to_batch[future]
                    try:
                        batch_results = future.result()
                        results['success'].extend(batch_results['success'])
                        results['failed'].extend(batch_results['failed'])
                        self.logger.info(f"배치 {batch_idx+1}/{len(batches)} 완료")
                    except Exception as exc:
                        self.logger.error(f"배치 {batch_idx+1} 처리 중 예외 발생: {exc}", exception=exc)
                        # 실패한 파일들을 failed 목록에 추가하는 로직 필요
            
            self.logger.info(f"병렬 분석 완료: 성공 {len(results['success'])}, 실패 {len(results['failed'])}")
            return results

        def _analyze_batch_sync(self, batch_file_paths: List[str], project_id: int, parsers: Dict[str, Any]) -> Dict[str, Any]:
            # 이 메서드는 각 스레드에서 동기적으로 실행될 파일 분석 로직을 포함
            # 각 파일에 대해 적절한 파서를 호출하고 결과를 수집
            batch_results = {'success': [], 'failed': []}
            for file_path in batch_file_paths:
                try:
                    # 파일 내용 읽기
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 파일 확장자에 따라 적절한 파서 선택 및 호출
                    parser_type = self._get_parser_type(file_path)
                    parser = parsers.get(parser_type)
                    if parser:
                        parse_result = parser.parse_file(file_path, content)
                        batch_results['success'].append(parse_result)
                    else:
                        self.logger.warning(f"지원하지 않는 파일 타입: {file_path}")
                        batch_results['failed'].append({'file_path': file_path, 'reason': 'Unsupported file type'})
                except Exception as e:
                    self.logger.error(f"파일 분석 실패: {file_path} | {e}", exception=e)
                    batch_results['failed'].append({'file_path': file_path, 'reason': str(e)})
            return batch_results

        def _get_parser_type(self, file_path: str) -> str:
            # 파일 확장자에 따라 파서 타입 반환 (예: 'java', 'jsp', 'xml')
            if file_path.endswith('.java'):
                return 'java'
            elif file_path.endswith('.jsp'):
                return 'jsp'
            elif file_path.endswith('.xml'):
                return 'mybatis_xml'
            return 'unknown'
    ```

#### 3.2.2. 스트리밍 해시 계산 (`src/database/metadata_engine.py` 내)

*   **문제점**: 파일 해시 계산 시 전체 파일을 한 번에 읽어 메모리 사용량이 증가하고 대용량 파일 처리 시 성능이 저하됩니다.
*   **개선 방안**: `hashlib.sha256()` 객체에 파일을 4KB 블록 단위로 반복해서 업데이트하는 방식으로 스트리밍 해시를 계산하여 메모리 사용을 최소화합니다.
*   **코드 예시 (`src/database/metadata_engine.py` 내 유틸리티 메서드)**:
    ```python
    # src/database/metadata_engine.py (또는 src/utils/file_utils.py)

    import hashlib
    import os

    class MetadataEngine:
        # ...
        def _calculate_file_hash_stream(self, file_path: str, block_size: int = 4096) -> str:
            hasher = hashlib.sha256()
            try:
                with open(file_path, 'rb') as f:
                    while True:
                        chunk = f.read(block_size)
                        if not chunk:
                            break
                        hasher.update(chunk)
                return hasher.hexdigest()
            except Exception as e:
                self.logger.error(f"파일 해시 계산 실패: {file_path} | {e}", exception=e)
                return "" # 오류 발생 시 빈 문자열 또는 특정 오류 값 반환
    ```

#### 3.2.3. 체계적 로깅 및 에러 보고 강화 (`src/utils/logger.py` 및 파서/엔진 연동)

*   **문제점**: 예외 발생 시 `print` 기반 출력에 머물러 로그 레벨이나 실패 파일 목록을 체계적으로 제공하지 못합니다.
*   **개선 방안**: `logging` 모듈을 사용하여 DEBUG, INFO, WARNING, ERROR, CRITICAL 등 적절한 로그 레벨을 지정하고, 파싱 실패 시 파일 경로, 예외 스택 트레이스, 관련 컨텍스트를 상세히 기록합니다. 파싱 실패한 파일 목록을 별도의 리포트 파일로 저장하거나, 분석 완료 시 요약 보고서에 포함하여 사용자가 후속 조치를 취할 수 있도록 합니다.
*   **코드 예시 (`src/utils/logger.py` 확장 및 사용 예시)**:
    ```python
    # src/utils/logger.py

    import logging
    import os
    from logging.handlers import RotatingFileHandler

    class AnalyzerLogger:
        def __init__(self, log_file='logs/analyzer.log', level=logging.INFO):
            self.logger = logging.getLogger('SourceAnalyzer')
            self.logger.setLevel(level)

            if not self.logger.handlers: # 핸들러 중복 추가 방지
                # 콘솔 핸들러
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
                self.logger.addHandler(console_handler)

                # 파일 핸들러 (로테이션)
                log_dir = os.path.dirname(log_file)
                if not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8')
                file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'))
                self.logger.addHandler(file_handler)

        def debug(self, message, **kwargs):
            self.logger.debug(message, **kwargs)

        def info(self, message, **kwargs):
            self.logger.info(message, **kwargs)

        def warning(self, message, **kwargs):
            self.logger.warning(message, **kwargs)

        def error(self, message, exception=None, **kwargs):
            if exception:
                self.logger.error(message, exc_info=exception, **kwargs)
            else:
                self.logger.error(message, **kwargs)

        def exception(self, message, **kwargs):
            self.logger.exception(message, **kwargs)

    # 사용 예시 (다른 모듈에서)
    # from src.utils.logger import AnalyzerLogger
    # logger = AnalyzerLogger()
    # try:
    #     # ... 파싱 로직 ...
    # except Exception as e:
    #     logger.error(f"파싱 실패: {file_path}", exception=e)
    ```

### 3.3. 타입 안정성 및 의존성 분석 강화

#### 3.3.1. 제네릭 타입 적용 (`src/models/database.py` 및 파서 연동)

*   **문제점**: 서비스 및 매퍼 계층에 `List`, `Map` 등 제네릭이 없는 원시 타입이 남아 있어 메타데이터 변환 시 실제 리턴 타입을 정확히 추론하기 어렵습니다.
*   **개선 방안**: `src/models/database.py`에 정의된 모델 클래스 및 파서에서 추출하는 타입 정보에 제네릭 파라미터를 명시적으로 적용합니다. 예를 들어, `List<String>`, `Map<String, Object>`, `Optional<Customer>`와 같이 명확한 타입을 사용하도록 파서를 개선하고, MyBatis XML의 `resultType`도 정확하게 기재하도록 유도합니다.
*   **코드 예시 (`src/models/database.py` 내 모델 정의 개선)**:
    ```python
    # src/models/database.py

    from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import relationship

    Base = declarative_base()

    class Method(Base):
        __tablename__ = 'methods'
        method_id = Column(Integer, primary_key=True)
        class_id = Column(Integer, ForeignKey('classes.class_id'))
        name = Column(String(255), nullable=False)
        signature = Column(Text, nullable=False)
        return_type = Column(String(255)) # 제네릭 포함 타입 (예: 'List<Customer>', 'Optional<String>')
        start_line = Column(Integer)
        end_line = Column(Integer)
        annotations = Column(Text) # JSON 형태의 어노테이션 목록 (예: '["@GetMapping", "@Transactional"]')

        # ... (다른 필드 및 관계) ...

    class SqlUnit(Base):
        __tablename__ = 'sql_units'
        sql_id = Column(Integer, primary_key=True)
        file_id = Column(Integer, ForeignKey('files.file_id'))
        origin = Column(String(255)) # MyBatis XML 파일 경로 또는 JSP 파일 경로
        mapper_ns = Column(String(255))
        stmt_id = Column(String(255))
        start_line = Column(Integer)
        end_line = Column(Integer)
        stmt_kind = Column(String(50))
        normalized_fingerprint = Column(Text)
        # MyBatis XML의 resultType/parameterType 정보 추가
        result_type = Column(String(255)) # 예: 'com.example.model.Customer'
        parameter_type = Column(String(255)) # 예: 'com.example.model.OrderFilter'

        # ... (다른 필드 및 관계) ...
    ```

#### 3.3.2. 호출·의존 그래프 고도화 (`src/parsers/java_parser.py`, `jsp_mybatis_parser.py` 등)

*   **문제점**: Service/Repository 계층 어노테이션 미처리, 람다식/메서드 참조 미추적으로 의존 관계 그래프가 불완전합니다.
*   **개선 방안**: `prd_v4.md`의 요구사항에 따라 Java 파서에 Spring DI 관계 (어노테이션, 생성자 주입) 및 람다식/메서드 참조 추적 기능을 추가합니다. JSP 파서는 `<jsp:include>` 및 백엔드 Java 코드와의 연동 관계를 분석합니다. MyBatis 파서는 `<include>`, `<sql>` 참조 관계를 추출합니다. 이 모든 의존성 정보를 `edges` 테이블에 `call`, `use_table`, `call_sql`, `calls_sp` 등 구체적인 `edge_kind`와 함께 방향성, 가중치, CONFIDENCE를 저장하여 고도화된 호출·의존 그래프를 구축합니다.
*   **코드 예시 (`src/parsers/java_parser.py` 내 Edge 생성 로직)**:
    ```python
    # src/parsers/java_parser.py (parse_java_file 메서드 내)

    from src.models.database import Edge # 가정

    class JavaParser:
        # ...
        def _extract_dependencies(self, tree, file_id, classes, methods) -> List[Edge]:
            edges = []
            # ... (기존 로직) ...

            # 1. Spring DI (예: @Autowired 필드)
            for path, node in tree.filter(javalang.tree.FieldDeclaration):
                if any(anno.name == 'Autowired' for anno in node.annotations):
                    # 현재 클래스 -> 주입되는 타입 간의 의존성 Edge 생성
                    current_class_id = self._get_class_id_from_node(node, classes)
                    injected_type_name = node.declarators[0].type.name # 예: CustomerService
                    injected_class_id = self._get_class_id_by_name(injected_type_name, classes)
                    if current_class_id and injected_class_id:
                        edges.append(Edge(
                            src_type='class', src_id=current_class_id,
                            dst_type='class', dst_id=injected_class_id,
                            edge_kind='depends_on_di', confidence=0.9
                        ))

            # 2. 메서드 호출 (클래스 내부, 외부)
            for path, node in tree.filter(javalang.tree.MethodInvocation):
                caller_method_id = self._get_method_id_from_node(node, methods) # 호출하는 메서드
                called_method_name = node.member # 호출되는 메서드 이름
                # 호출되는 메서드의 클래스/메서드 ID를 찾아 Edge 생성
                # ... (복잡한 타입 추론 및 스코프 분석 필요) ...
                if caller_method_id and called_method_id:
                    edges.append(Edge(
                        src_type='method', src_id=caller_method_id,
                        dst_type='method', dst_id=called_method_id,
                        edge_kind='call', confidence=0.95
                    ))

            # 3. 람다식 및 메서드 참조 (예: stream().map(ClassName::method))
            # javalang.tree.LambdaExpression, javalang.tree.MemberReference 노드 분석
            # ... (고급 AST 분석 로직 필요) ...

            return edges

        # 헬퍼 메서드 (클래스/메서드 ID를 이름/노드에서 찾는 로직)
        def _get_class_id_from_node(self, node, classes): # ...
            pass
        def _get_method_id_from_node(self, node, methods): # ...
            pass
        def _get_class_id_by_name(self, name, classes): # ...
            pass
    ```

### 3.4. LLM 활용 및 보강 메타정보 생성

#### 3.4.1. DB 사전 보강 코멘트 생성 (LLM 기반)

*   **문제점**: `prd_v4.md`에서 DB 사전 코멘트가 부실/오류일 수 있다고 지적하며, 소스 기반 의미 보강 코멘트 생성을 요구합니다.
*   **개선 방안**: 각 데이터베이스 컬럼에 대해, 소스 코드 전체에서 해당 컬럼을 사용하는 모든 SQL 쿼리와 Java 메서드를 역추적하여 종합적인 사용 맥락을 메타정보에 수집합니다. 수집된 실제 사용 맥락을 근거로, LLM에게 해당 컬럼의 역할과 의미를 설명하는 고품질의 한글 코멘트를 생성하도록 요청합니다. 생성된 코멘트 제안은 `summaries` 테이블에 `db_comment_suggestion` 타입으로 저장합니다.
*   **코드 예시 (개념적 워크플로우)**:
    ```python
    # src/llm_enrichment/db_comment_generator.py (가상)

    from src.models.database import Summary, DbColumn # 가정
    from src.database.metadata_engine import MetadataEngine # 가정
    from src.llm_client import LLMClient # LLM API 클라이언트 가정
    from src.utils.logger import AnalyzerLogger

    class DbCommentGenerator:
        def __init__(self, metadata_engine: MetadataEngine, llm_client: LLMClient):
            self.metadata_engine = metadata_engine
            self.llm_client = llm_client
            self.logger = AnalyzerLogger()

        async def generate_db_column_comments(self, project_id: int):
            db_columns = self.metadata_engine.get_all_db_columns(project_id)
            for column in db_columns:
                # 1. 해당 컬럼의 사용 맥락 수집 (SQL, Java 코드에서 역추적)
                usage_contexts = self.metadata_engine.get_column_usage_contexts(project_id, column.column_id)
                
                if not usage_contexts:
                    self.logger.info(f"컬럼 {column.table_name}.{column.column_name}에 대한 사용 맥락 없음. 코멘트 생성 스킵.")
                    continue

                # 2. LLM 프롬프트 구성
                prompt = self._build_prompt(column, usage_contexts)
                
                # 3. LLM 호출 (비동기)
                try:
                    llm_response = await self.llm_client.generate(prompt, model="qwen2.5-7b", temperature=0.2)
                    comment_content = llm_response.get('text', '').strip()

                    if comment_content:
                        # 4. summaries 테이블에 저장
                        summary = Summary(
                            target_type='db_column',
                            target_id=column.column_id,
                            summary_type='db_comment_suggestion',
                            lang='ko',
                            content=comment_content,
                            confidence=0.7 # LLM 생성 코멘트 초기 신뢰도
                        )
                        self.metadata_engine.save_summary(summary)
                        self.logger.info(f"컬럼 {column.table_name}.{column.column_name} 코멘트 생성 및 저장 완료.")
                except Exception as e:
                    self.logger.error(f"컬럼 {column.table_name}.{column.column_name} 코멘트 생성 실패: {e}", exception=e)

        def _build_prompt(self, column: DbColumn, contexts: List[Dict]) -> str:
            # LLM에 전달할 프롬프트 구성 로직
            # 예: "다음은 데이터베이스 컬럼의 사용 맥락입니다. 이 컬럼의 역할과 의미를 설명하는 한글 코멘트를 50자 이내로 생성해주세요."
            # ...
            return f"컬럼: {column.table_name}.{column.column_name}
사용 맥락: {contexts}
역할/의미 설명 (한글, 50자 이내):"
    ```

#### 3.4.2. 보강 메타정보 저장 및 CONFIDENCE 산식 고도화

*   **문제점**: `prd_v4.md`는 LLM 보강 이력 및 CONFIDENCE 전 구간 추적을 요구하며, 규칙 기반 결과가 불충분할 경우 LLM 보강을 통해 메타DB에 직접 추가하도록 명시합니다.
*   **개선 방안**: `summaries`, `enrichment_logs`, `vulnerability_fixes` 테이블을 활용하여 LLM이 생성한 요약, 취약점 정보, 그리고 LLM 추론 전/후의 신뢰도 변화 (`pre_conf`, `post_conf`), 사용 모델, 프롬프트, 파라미터 등을 상세히 기록합니다. `src/utils/improved_confidence_calculator.py`의 CONFIDENCE 산식을 `prd_v4.md`에 제시된 `conf = w_ast*q_ast + w_static*q_static + w_db*q_db + w_llm*q_llm` 형태로 고도화하고, 동적 SQL/리플렉션 복잡도에 따른 감점 로직을 추가합니다.
*   **코드 예시 (`src/utils/improved_confidence_calculator.py` 개선)**:
    ```python
    # src/utils/improved_confidence_calculator.py

    from typing import Dict, Tuple
    from src.models.database import ParseResult # 가정

    class ImprovedConfidenceCalculator:
        def __init__(self, weights: Dict[str, float] = None):
            self.weights = weights if weights else {
                'ast': 0.3,        # AST 품질 (파싱 성공 여부, 구조적 완전성)
                'static': 0.25,    # 정적 규칙 (명명 규칙, 코드 스타일 등)
                'db_match': 0.2,   # DB 스키마 매칭 (테이블/컬럼 존재 여부)
                'heuristic': 0.15, # 휴리스틱 (복잡도, 패턴 일치 등)
                'llm': 0.1         # LLM 보강 신뢰도 (LLM 추론 결과의 자체 신뢰도)
            }
            self.logger = AnalyzerLogger()

        def calculate_parsing_confidence(self, parse_result: ParseResult) -> Tuple[float, Dict[str, float]]:
            # 각 지표 점수 계산 (0.0 ~ 1.0)
            ast_score = self._calculate_ast_score(parse_result)
            static_score = self._calculate_static_score(parse_result)
            db_score = self._calculate_db_match_score(parse_result)
            heuristic_score = self._calculate_heuristic_score(parse_result)
            llm_score = parse_result.llm_confidence if hasattr(parse_result, 'llm_confidence') else 0.0 # LLM 보강 시

            # CONFIDENCE 산식 적용
            base_confidence = (
                self.weights['ast'] * ast_score +
                self.weights['static'] * static_score +
                self.weights['db_match'] * db_score +
                self.weights['heuristic'] * heuristic_score +
                self.weights['llm'] * llm_score
            )

            # 동적 SQL/리플렉션/표현식 복잡도에 따른 감점 로직 추가
            complexity_penalty = self._calculate_complexity_penalty(parse_result)
            final_confidence = max(0.0, min(1.0, base_confidence - complexity_penalty))

            scores = {
                'ast_score': ast_score,
                'static_score': static_score,
                'db_match_score': db_score,
                'heuristic_score': heuristic_score,
                'llm_score': llm_score,
                'complexity_penalty': complexity_penalty
            }
            return final_confidence, scores

        def _calculate_ast_score(self, parse_result: ParseResult) -> float:
            # AST 파싱 성공 여부, 구조적 완전성 등을 기반으로 점수 계산
            # ...
            return 0.0

        def _calculate_static_score(self, parse_result: ParseResult) -> float:
            # 명명 규칙, 코드 스타일, 기본적인 오류 패턴 등을 기반으로 점수 계산
            # ...
            return 0.0

        def _calculate_db_match_score(self, parse_result: ParseResult) -> float:
            # 추출된 테이블/컬럼이 DB 스키마에 존재하는지 여부 등을 기반으로 점수 계산
            # ...
            return 0.0

        def _calculate_heuristic_score(self, parse_result: ParseResult) -> float:
            # 코드 복잡도, 특정 패턴 일치 여부 등을 기반으로 점수 계산
            # ...
            return 0.0

        def _calculate_complexity_penalty(self, parse_result: ParseResult) -> float:
            # 동적 SQL, 리플렉션 사용, 복잡한 표현식 등에 따라 감점 부여
            # 예: parse_result.has_dynamic_sql, parse_result.reflection_usage 등
            penalty = 0.0
            if hasattr(parse_result, 'has_dynamic_sql') and parse_result.has_dynamic_sql:
                penalty += 0.1 # 동적 SQL 사용 시 감점
            # ...
            return penalty

        def update_confidence_after_llm_enrichment(self, original_confidence: float, llm_evidence_quality: float, model_strength: float) -> float:
            # LLM 보강 후 신뢰도 업데이트 로직 (prd_v4.md의 post_conf = min(1.0, conf + delta(model, evidence)) 구현)
            delta = llm_evidence_quality * model_strength * 0.2 # 예시 delta 계산
            post_conf = min(1.0, original_confidence + delta)
            return post_conf
    ```

### 3.5. 품질 및 보안 분석 고도화

#### 3.5.1. SAST 통합 및 취약점 분석 (신규 모듈 및 파서 연동)

*   **문제점**: `prd_v4.md`는 OWASP Top 10에 초점을 맞춘 보안 취약점 분석 및 SAST 통합을 요구합니다.
*   **개선 방안**: CodeQL이나 Semgrep과 같은 오픈소스 SAST 도구를 오프라인 모드로 실행하여 SQL Injection, XSS, 경로 조작 등 다양한 취약 패턴을 정적 분석합니다. 특히 MyBatis 매퍼 파일에서 `${...}` 패턴을 탐지하여 SQL Injection 취약점을 식별합니다. SAST 보고서를 기반으로 LLM이 수정 제안을 생성하도록 하여 `vulnerability_fixes` 테이블에 신뢰도와 함께 구체적인 보안 개선 방안 (취약점 유형, 심각도, OWASP/CWE 분류, 참조 URL, 설명, 변경 전/후 코드)을 저장합니다.
*   **코드 예시 (개념적 워크플로우 및 `vulnerability_fixes` 테이블 활용)**:
    ```python
    # src/security_analyzer/sast_integrator.py (가상)

    import subprocess
    import json
    from typing import List, Dict
    from src.models.database import VulnerabilityFix # 가정
    from src.database.metadata_engine import MetadataEngine # 가정
    from src.llm_client import LLMClient # LLM API 클라이언트 가정
    from src.utils.logger import AnalyzerLogger

    class SASTIntegrator:
        def __init__(self, metadata_engine: MetadataEngine, llm_client: LLMClient):
            self.metadata_engine = metadata_engine
            self.llm_client = llm_client
            self.logger = AnalyzerLogger()
            self.semgrep_path = "path/to/semgrep" # Semgrep 실행 파일 경로

        async def run_sast_analysis(self, project_root: str, project_id: int):
            self.logger.info(f"Semgrep SAST 분석 시작: {project_root}")
            try:
                # Semgrep 실행 (오프라인 규칙 사용)
                # 예: semgrep --config=auto --json --output=sast_report.json project_root
                command = [
                    self.semgrep_path,
                    "--config=auto", # 또는 커스텀 규칙 파일 경로
                    "--json",
                    f"--output={project_root}/sast_report.json",
                    project_root
                ]
                result = subprocess.run(command, capture_output=True, text=True, check=True)
                self.logger.info(f"Semgrep SAST 분석 완료. 결과: {result.stdout}")

                # SAST 보고서 파싱 및 취약점 추출
                with open(f"{project_root}/sast_report.json", 'r', encoding='utf-8') as f:
                    sast_report = json.load(f)
                
                for finding in sast_report.get('results', []):
                    # 취약점 정보 추출
                    vulnerability_type = finding.get('check_id', 'unknown')
                    severity = finding.get('extra', {}).get('severity', 'medium').lower()
                    start_line = finding.get('start', {}).get('line')
                    end_line = finding.get('end', {}).get('line')
                    file_path = finding.get('path')
                    description = finding.get('extra', {}).get('message', 'No description')
                    
                    # LLM을 통해 수정 제안 생성
                    fix_description, original_code, fixed_code = await self._generate_fix_with_llm(file_path, start_line, end_line, description)

                    # VulnerabilityFix 객체 생성 및 저장
                    v_fix = VulnerabilityFix(
                        target_type='file', # 또는 'method', 'sql_unit' 등
                        target_id=self.metadata_engine.get_file_id_by_path(project_id, file_path), # 파일 ID 조회
                        vulnerability_type=vulnerability_type,
                        severity=severity,
                        owasp_category=None, # Semgrep 결과에서 매핑 필요
                        cwe_id=None, # Semgrep 결과에서 매핑 필요
                        reference_urls=json.dumps([]), # 관련 URL 추가
                        description=description,
                        fix_description=fix_description,
                        original_code=original_code,
                        fixed_code=fixed_code,
                        start_line=start_line,
                        end_line=end_line,
                        confidence=0.8, # SAST 도구의 신뢰도
                        created_at=None # 자동 생성
                    )
                    self.metadata_engine.save_vulnerability_fix(v_fix)
                    self.logger.info(f"취약점 {vulnerability_type} ({file_path}:{start_line}) 저장 완료.")

            except subprocess.CalledProcessError as e:
                self.logger.error(f"Semgrep SAST 실행 실패: {e.stderr}", exception=e)
            except Exception as e:
                self.logger.error(f"SAST 분석 중 오류 발생: {e}", exception=e)

        async def _generate_fix_with_llm(self, file_path: str, start_line: int, end_line: int, vuln_description: str) -> Tuple[str, str, str]:
            # LLM에 취약점 설명과 코드 스니펫을 전달하여 수정 제안을 받음
            # 실제 코드 스니펫을 읽어오는 로직 필요
            original_code_snippet = "..." # read_file로 해당 라인 범위 읽기
            prompt = f"다음 코드에서 발견된 취약점 '{vuln_description}'에 대한 수정 방안을 설명하고, 변경 전/후 코드를 제시해주세요.
원본 코드:
```
{original_code_snippet}
```"
            
            try:
                llm_response = await self.llm_client.generate(prompt, model="qwen2.5-7b", temperature=0.2)
                # LLM 응답에서 fix_description, original_code, fixed_code 파싱
                # 이 부분은 LLM 응답 형식을 정의하고 파싱하는 로직이 필요
                fix_description = "LLM이 제안한 수정 방안..."
                fixed_code = "LLM이 제안한 수정 코드..."
                return fix_description, original_code_snippet, fixed_code
            except Exception as e:
                self.logger.error(f"LLM 기반 수정 제안 생성 실패: {e}", exception=e)
                return "LLM 수정 제안 생성 실패", original_code_snippet, ""
    ```

#### 3.5.2. 정교한 코드 품질 메트릭 분석 기능 확장 (신규 모듈 및 파서 연동)

*   **문제점**: `prd_v4.md`는 PMD의 중복 코드 탐지(CPD), 순환 복잡도 등 다양한 코드 품질 지표 분석 및 `duplicates`, `duplicate_instances` 테이블 저장을 요구합니다.
*   **개선 방안**: JavaParser (또는 Tree-Sitter) AST를 기반으로 순환 복잡도(Cyclomatic Complexity)를 계산하는 로직을 구현하고 `code_metrics` 테이블에 저장합니다. 중복 코드 탐지는 외부 도구 (예: PMD CPD)를 연동하거나 자체 알고리즘을 구현하여 `duplicates` 및 `duplicate_instances` 테이블에 저장합니다.
*   **코드 예시 (순환 복잡도 계산 로직 - `src/code_quality_analyzer/complexity_calculator.py` 가상)**:
    ```python
    # src/code_quality_analyzer/complexity_calculator.py (가상)

    from javalang import parse
    from javalang.tree import MethodDeclaration, IfStatement, ForStatement, WhileStatement, DoStatement, SwitchStatement, CatchClause

    class CyclomaticComplexityCalculator:
        def calculate_method_complexity(self, method_node: MethodDeclaration) -> int:
            complexity = 1 # 기본 복잡도 (진입점)
            
            # 제어 흐름 노드 순회 및 복잡도 증가
            for path, node in method_node.filter(
                (IfStatement, ForStatement, WhileStatement, DoStatement, SwitchStatement, CatchClause)
            ):
                complexity += 1
            
            # 논리 연산자 (&&, ||)도 복잡도에 기여할 수 있으나, AST 순회로 더 깊은 분석 필요
            # ...

            return complexity

        def analyze_file_complexity(self, file_content: str) -> Dict[str, int]:
            method_complexities = {}
            try:
                tree = parse.parse(file_content)
                for path, node in tree.filter(MethodDeclaration):
                    method_name = node.name
                    complexity = self.calculate_method_complexity(node)
                    method_complexities[method_name] = complexity
            except Exception as e:
                self.logger.error(f"파일 복잡도 분석 실패: {e}", exception=e)
            return method_complexities

    # 사용 예시 (JavaParser에서 메서드 파싱 후 호출)
    # complexity_calculator = CyclomaticComplexityCalculator()
    # for method_node in parsed_java_methods:
    #     complexity = complexity_calculator.calculate_method_complexity(method_node)
    #     # code_metrics 테이블에 저장
    ```

## 4. 결론 및 향후 계획

### 4.1. 기대 효과

위에 제시된 상세 개선 방안들을 적용함으로써 소스 분석기는 다음과 같은 효과를 얻을 수 있습니다.

*   **정확도 대폭 향상**: Tree-Sitter 및 AST 기반 파서 도입으로 JSP/MyBatis 동적 SQL, 복잡한 SQL 구문, Spring DI 관계, 람다식 호출 등을 정확하게 분석하여 메타정보의 신뢰도를 높입니다.
*   **성능 및 효율성 증대**: 병렬 처리 최적화, 스트리밍 해시 계산, 체계적 로깅으로 대규모 프로젝트 분석 시간을 단축하고 메모리 사용량을 절감합니다.
*   **안정성 강화**: 구체적인 예외 처리 및 상세 로깅으로 운영 환경에서의 문제 진단 및 해결이 용이해집니다.
*   **기능 완성도 및 확장성**: LLM 기반 DB 코멘트, 취약점 분석, 코드 품질 메트릭 도입으로 `prd_v4.md`의 핵심 요구사항을 충족하며, 향후 PL/SQL, Python, JS/TS 등 다양한 언어/프레임워크 지원을 위한 견고한 기반을 마련합니다.
*   **보안 강화**: SAST 통합 및 취약점 분석을 통해 잠재적인 보안 문제를 조기에 식별하고 개선 방안을 제시합니다.

### 4.2. 향후 개발 로드맵 (prd_v4.md 기반)

본 개선안의 구현 이후, `prd_v4.md`에 제시된 다음 단계의 개발을 진행합니다.

1.  **Oracle Stored Procedure/Function 분석 기능 확장**: `antlr-plsql` 및 JSQLParser를 활용한 PL/SQL 파싱 및 SP/SF 간 호출 관계 분석.
2.  **DB 사전 확장**: ALL_VIEWS, ALL_PROCEDURES 등 추가 DB 스키마 정보 로드.
3.  **다양한 언어/프레임워크 지원**: Python, JavaScript/TypeScript/React/Vue.js 분석 기능 구현.
4.  **LLM 기반 지능형 분석 고도화**: 오류 발생 가능 부분, 테이블 설계 문제점 등을 LLM으로 파악하여 메타 테이블에 저장.
5.  **변경 분석 기능**: 수정 전/후 비교를 통한 변경 내역 요약 및 영향 분석.
6.  **UI/시각화 대시보드**: 의존성 그래프, 코드 메트릭 차트, 코드 품질 위반 유형 차트, DB 스키마 시각화 등 구현.

이러한 개선을 통해 소스 분석기는 단순한 메타데이터 추출 도구를 넘어, 개발 및 운영 전반에 걸쳐 강력한 통찰력과 자동화된 지원을 제공하는 핵심 에이전트로 발전할 것입니다.
