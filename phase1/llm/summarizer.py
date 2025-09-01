#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM 기반 코드 요약 및 메타데이터 향상 모듈
LLM을 사용하여 소스 코드, SQL, 테이블에 대한 한글 요약을 생성합니다.
"""
from typing import Dict, Any, Optional, List
import json
from pathlib import Path
try:
    from ..llm.client import get_client
    from ..models.database import DatabaseManager, File, Class, Method, SqlUnit, DbTable, DbColumn, Join
except ImportError:
    # If relative imports fail, try direct imports
    from llm.client import get_client
    from models.database import DatabaseManager, File, Class, Method, SqlUnit, DbTable, DbColumn, Join
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)


class CodeSummarizer:
    """LLM 기반 코드 요약 및 메타데이터 향상 클래스"""
    
    def __init__(self, config: Dict[str, Any], debug: bool = False):
        self.config = config
        self.llm_config = config.get('llm', {})
        self.debug = debug
        self.dbm = DatabaseManager(config.get('database', {}).get('project', {}))
        self.dbm.initialize()
    
    def session(self):
        """데이터베이스 세션 반환"""
        return self.dbm.get_session()
    
    def _chat_with_debug(self, client, messages: list, **kwargs):
        """한국어 시스템 프롬프트와 디버그 출력을 처리하는 LLM 채팅 헬퍼 메서드"""
        # Add Korean system prompt
        korean_system = {
            "role": "system", 
            "content": "모든 응답을 한국어로 해주세요. 간결하고 명확하게 답변해주세요.\n" + \
                       "딱 필요한 답변만 하고 네, 알겠습니다 같은 군더더기 말은 하지 마세요.\n" + \
                       "만약 이해가 안되거나 답변이 불가한 경우 '-'를 답변주세요."
        }
        
        # Insert system message at the beginning
        messages_with_system = [korean_system] + messages
        
        if self.debug:
            print("=" * 50)
            print("[DEBUG] LLM 요청:")
            for i, msg in enumerate(messages_with_system):
                #print(f"[{msg['role'].upper()}] {msg['content'][:500]}{'...' if len(msg['content']) > 500 else ''}")
                print(f"[{msg['role'].upper()}] {msg['content'][:1500]}")
            #print("=" * 50)
        
        response = client.chat(messages_with_system, **kwargs)
        
        if self.debug:
            print("★★★★★★★★★★★★★★★★★★★★★★ [DEBUG] LLM 응답 ★★★★★★★★★★★★★★★★★★★★★★")
            print(f"{response[:500]}{'...' if len(str(response)) > 500 else ''}")
            print("=" * 50)
            print("\n\n\n\n\n")
            
        return response
    
    def _add_summary_columns_if_needed(self):
        """테이블에 요약 컬럼이 없는 경우 추가"""
        session = self.session()
        try:
            # Add summary column to files table
            try:
                session.execute(text("ALTER TABLE files ADD COLUMN llm_summary TEXT"))
                session.execute(text("ALTER TABLE files ADD COLUMN llm_summary_confidence FLOAT DEFAULT 0.0"))
                session.commit()
                logger.info("Added llm_summary columns to files table")
            except Exception:
                pass  # Column already exists
            
            # Add summary column to classes table
            try:
                session.execute(text("ALTER TABLE classes ADD COLUMN llm_summary TEXT"))
                session.execute(text("ALTER TABLE classes ADD COLUMN llm_summary_confidence FLOAT DEFAULT 0.0"))
                session.commit()
                logger.info("Added llm_summary columns to classes table")
            except Exception:
                pass
            
            # Add summary column to methods table
            try:
                session.execute(text("ALTER TABLE methods ADD COLUMN llm_summary TEXT"))
                session.execute(text("ALTER TABLE methods ADD COLUMN llm_summary_confidence FLOAT DEFAULT 0.0"))
                session.commit()
                logger.info("Added llm_summary columns to methods table")
            except Exception:
                pass
            
            # Add summary column to sql_units table
            try:
                session.execute(text("ALTER TABLE sql_units ADD COLUMN llm_summary TEXT"))
                session.execute(text("ALTER TABLE sql_units ADD COLUMN llm_summary_confidence FLOAT DEFAULT 0.0"))
                session.commit()
                logger.info("Added llm_summary columns to sql_units table")
            except Exception:
                pass
            
            # Add enhanced comment columns to db tables
            try:
                session.execute(text("ALTER TABLE db_tables ADD COLUMN llm_comment TEXT"))
                session.execute(text("ALTER TABLE db_tables ADD COLUMN llm_comment_confidence FLOAT DEFAULT 0.0"))
                session.commit()
                logger.info("Added llm_comment columns to db_tables table")
            except Exception:
                pass
            
            try:
                session.execute(text("ALTER TABLE db_columns ADD COLUMN llm_comment TEXT"))
                session.execute(text("ALTER TABLE db_columns ADD COLUMN llm_comment_confidence FLOAT DEFAULT 0.0"))
                session.commit()
                logger.info("Added llm_comment columns to db_columns table")
            except Exception:
                pass
                
        finally:
            session.close()
    
    def _read_project_file_content(self, file_path: str, max_size: int = 4096) -> str:
        """프로젝트 폴더에서 파일 내용을 읽어옴 (최대 4KB)"""
        if not file_path:
            return ""
            
        # PROJECT/ 접두사가 있는 경우 실제 프로젝트 폴더 경로로 변환
        if file_path.startswith('PROJECT\\') or file_path.startswith('PROJECT/'):
            actual_path = file_path
        else:
            # 상대 경로인 경우 PROJECT 하위에서 찾기
            actual_path = f"PROJECT/{file_path}"
        
        full_path = Path(actual_path)
        if not full_path.exists():
            logger.warning(f"파일을 찾을 수 없음: {full_path}")
            return ""
            
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(max_size)
                if len(content) == max_size:
                    logger.info(f"파일 내용이 4KB로 제한됨: {full_path}")
                return content
        except Exception as e:
            logger.warning(f"파일 읽기 실패 {full_path}: {e}")
            return ""

    def summarize_file(self, file: File) -> Optional[str]:
        """LLM을 사용하여 파일에 대한 요약 생성"""
        try:
            if not self.llm_config.get('enabled', True):
                return None
            
            # 요약 중인 객체 정보 로그 출력
            logger.info(f"[요약 중] 파일 객체: {file.path} (ID: {file.file_id})")
            print(f"DEBUG: 파일 요약 중 - {file.path}")
            
            client = get_client(self.llm_config)
            
            # 프로젝트 폴더에서 파일 내용 읽기 (최대 4KB)
            file_content = self._read_project_file_content(file.path)
            
            # Determine file type and create appropriate prompt
            file_extension = Path(file.path or "").suffix.lower()
            
            if file_extension == '.jsp':
                prompt = f"""다음 JSP 파일을 분석하고 목적과 기능을 간략하게 요약해주세요.


파일: {file.path}
내용:
{file_content[:3000]}...

다음을 포함하여 간결한 요약(1-2문장)을 제공해주세요
:
1. 이 JSP 페이지가 하는 일
2. 주요 기능 또는 목적
3. 핵심 기능 또는 구성요소

요약:"""
            elif file_extension == '.java':
                prompt = f"""다음 Java 파일을 분석하고 목적과 기능을 간략하게 요약해주세요.


파일: {file.path}
내용:
{file_content[:3000]}...

다음을 포함하여 간결한 요약(1-2문장)을 제공해주세요. 
 :
1. 이 Java 클래스/파일이 하는 일
2. 주요 책임
3. 핵심 메서드 또는 기능

요약:"""
            else:
                prompt = f"""
다음 코드 파일을 분석하고 목적과 기능을 간략하게 요약해주세요. 


파일: {file.path}
내용:
{file_content[:3000]}...

이 파일이 하는 일과 주요 목적에 대해 간결한 요약(1-2문장)을 제공해주세요.


요약:"""
            
            # 프롬프트와 답변 디버깅 로그
            if self.debug:
                print(f"DEBUG: 파일 요약 프롬프트 길이: {len(prompt)} 문자")
                print(f"DEBUG: 파일 요약 프롬프트 미리보기: {prompt[:300]}...")
            
            summary = self._chat_with_debug(client, [{"role": "user", "content": prompt}], max_tokens=200, temperature=0.3)
            
            # 요약 결과 로그
            summary_text = summary.strip() if isinstance(summary, str) else str(summary).strip()
            logger.info(f"[요약 완료] 파일: {file.path} -> {summary_text[:100]}...")
            print(f"DEBUG: 파일 요약 결과: {summary_text[:100]}...")
            
            return summary_text
            
        except Exception as e:
            logger.error(f"Failed to summarize file {file.path}: {e}")
            return None
    
    def summarize_method(self, method: Method) -> Optional[str]:
        """LLM을 사용하여 메서드에 대한 요약 생성"""
        try:
            if not self.llm_config.get('enabled', True):
                return None
            
            client = get_client(self.llm_config)
            
            # Get method details - 메소드 소스코드를 프로젝트 폴더에서 읽어옴
            method_code = getattr(method, 'code_snippet', '') or getattr(method, 'source_code', '') or ''
            
            # 만약 코드가 없고 파일 경로가 있다면 프로젝트 폴더에서 읽기 시도
            if not method_code and hasattr(method, 'file') and method.file and method.file.path:
                file_content = self._read_project_file_content(method.file.path)
                # 메소드 이름으로 코드 추출 시도 (간단한 휴리스틱)
                if file_content and method.name:
                    lines = file_content.split('\n')
                    method_start = -1
                    for i, line in enumerate(lines):
                        if method.name in line and ('public' in line or 'private' in line or 'protected' in line):
                            method_start = i
                            break
                    if method_start >= 0:
                        # 메소드 시작부터 최대 50줄까지 추출
                        method_lines = lines[method_start:method_start + 50]
                        method_code = '\n'.join(method_lines)
            
            prompt = f"""
다음 Java 메서드를 분석하고 기능을 간략하게 요약해주세요.
성능개선이나 더 효율적으로 리팩토링할 수 있는 방법이 있으면 추가적으로 제안해줘도 됩니다.


메서드: {method.name}
클래스: {method.class_fqn if hasattr(method, 'class_fqn') else 'Unknown'}
매개변수: {method.parameters if hasattr(method, 'parameters') else 'Unknown'}
반환 타입: {method.return_type if hasattr(method, 'return_type') else 'Unknown'}

코드:
{method_code[:2000]}...

이 메서드가 하는 일과 목적에 대해 간결한 요약(1문장)을 제공해주세요.

요약:

혹시 리팩토링 제안할 내용이 있으면 간결한 요약(2~3문장)으로 제공해주세요.

개선제안:"""
            
            summary = self._chat_with_debug(client, [{"role": "user", "content": prompt}], max_tokens=150, temperature=0.3)
            return summary.strip() if isinstance(summary, str) else str(summary).strip()
            
        except Exception as e:
            logger.error(f"Failed to summarize method {method.name}: {e}")
            return None
    
    def summarize_sql_unit(self, sql_unit: SqlUnit) -> Optional[str]:
        """LLM을 사용하여 SQL 단위에 대한 요약 생성"""
        try:
            if not self.llm_config.get('enabled', True):
                return None
            
            client = get_client(self.llm_config)
            
            # SQL 내용을 프로젝트 폴더에서 읽어옴
            sql_content = sql_unit.sql_content if sql_unit.sql_content else ''
            
            # SQL 내용이 없고 파일 경로가 있다면 프로젝트 폴더에서 읽기 시도
            if not sql_content and hasattr(sql_unit, 'file') and sql_unit.file and sql_unit.file.path:
                file_content = self._read_project_file_content(sql_unit.file.path)
                # MyBatis XML에서 statement ID로 SQL 추출 시도
                if file_content and sql_unit.stmt_id:
                    import re
                    # MyBatis select/insert/update/delete 태그에서 해당 ID 찾기
                    pattern = rf'<(?:select|insert|update|delete)[^>]*id\s*=\s*["\']?{re.escape(sql_unit.stmt_id)}["\']?[^>]*>(.*?)</(?:select|insert|update|delete)>'
                    match = re.search(pattern, file_content, re.DOTALL | re.IGNORECASE)
                    if match:
                        sql_content = match.group(1).strip()[:2000]  # 최대 2KB
            
            # normalized_fingerprint 백업 사용
            if not sql_content:
                sql_content = getattr(sql_unit, 'normalized_fingerprint', '') or 'SQL 내용 없음'
            
            prompt = f"""
다음 SQL 쿼리/문을 분석하고 기능을 간략하게 요약해주세요.


매퍼 네임스페이스: {sql_unit.mapper_ns}
문 ID: {sql_unit.stmt_id}
문 종류: {sql_unit.stmt_kind}
SQL 내용:
{sql_content[:2000]}...

이 SQL 문이 하는 일과 목적에 대해 간결한 요약(1문장)을 제공해주세요.


요약:"""
            
            summary = self._chat_with_debug(client, [{"role": "user", "content": prompt}], max_tokens=150, temperature=0.3)
            return summary.strip() if isinstance(summary, str) else str(summary).strip()
            
        except Exception as e:
            logger.error(f"Failed to summarize SQL unit {sql_unit.mapper_ns}.{sql_unit.stmt_id}: {e}")
            return None
    
    def enhance_table_comment(self, table: DbTable, related_code_context: str = "") -> Optional[str]:
        """LLM 분석을 사용하여 테이블 주석 향상"""
        try:
            if not self.llm_config.get('enabled', True):
                return None
            
            client = get_client(self.llm_config)
            
            prompt = f"""데이터베이스 테이블을 분석하여 한글로 향상된 설명을 제공해주세요.


테이블명: {table.table_name}
기존 코멘트: {table.table_comment or '코멘트 없음'}

관련 코드 컨텍스트:
{related_code_context[:1500]}

테이블명, 기존 코멘트, 관련 코드 사용을 바탕으로 다음을 포함하는 향상된 설명을 한글로 100자 이내로 작성해주세요
:
1. 테이블의 용도와 저장하는 데이터
2. 애플리케이션에서의 역할
3. 주요 관계나 비즈니스 로직

향상된 설명:"""
            
            comment = self._chat_with_debug(client, [{"role": "user", "content": prompt}], max_tokens=200, temperature=0.3)
            return comment.strip() if isinstance(comment, str) else str(comment).strip()
            
        except Exception as e:
            logger.error(f"Failed to enhance table comment for {table.table_name}: {e}")
            return None
    
    def enhance_column_comment(self, column: DbColumn, table_context: str = "") -> Optional[str]:
        """Enhance column comments using LLM analysis"""
        try:
            if not self.llm_config.get('enabled', True):
                return None
            
            client = get_client(self.llm_config)
            
            prompt = f"""데이터베이스 컬럼을 분석하여 한글로 향상된 설명을 제공해주세요.


컬럼명: {column.column_name}
데이터 타입: {column.data_type}
NULL 허용: {column.nullable}
기존 코멘트: {column.column_comment or '코멘트 없음'}

테이블 컨텍스트:
{table_context[:1000]}

컬럼명, 데이터 타입, 테이블 컨텍스트를 바탕으로 다음을 포함하는 향상된 설명을 한글로 30자 이내로 작성해주세요
:
1. 이 컬럼이 저장하는 데이터
2. 용도와 비즈니스 의미
3. 제약사항이나 특별한 고려사항

향상된 설명:"""
            
            comment = self._chat_with_debug(client, [{"role": "user", "content": prompt}], max_tokens=150, temperature=0.3)
            return comment.strip() if isinstance(comment, str) else str(comment).strip()
            
        except Exception as e:
            logger.error(f"Failed to enhance column comment for {column.column_name}: {e}")
            return None
    
    def analyze_primary_key_candidates(self, table: DbTable, table_context: str = "") -> List[str]:
        """LLM을 사용하여 실질적인 Primary Key 후보를 분석"""
        try:
            if not self.llm_config.get('enabled', True):
                return []
            
            client = get_client(self.llm_config)
            
            # 테이블의 모든 컬럼 정보 수집
            session = self.session()
            try:
                columns = session.query(DbColumn).filter(DbColumn.table_id == table.table_id).all()
                columns_info = []
                for col in columns:
                    col_info = f"- {col.column_name} ({col.data_type}, Nullable: {col.nullable})"
                    if col.column_comment:
                        col_info += f" - {col.column_comment}"
                    columns_info.append(col_info)
                
                columns_text = '\n'.join(columns_info)
                
                prompt = f"""다음 데이터베이스 테이블을 분석하여 실질적인 Primary Key 후보 컬럼을 추천해주세요.

테이블명: {table.table_name}
테이블 설명: {table.table_comment or '설명 없음'}

컬럼 목록:
{columns_text}

관련 코드 컨텍스트:
{table_context[:1000]}

다음 기준으로 Primary Key 후보를 분석해주세요:
1. 고유성이 보장되는 컬럼
2. NULL 값이 없는 컬럼 (NOT NULL)
3. 비즈니스적으로 식별자 역할을 하는 컬럼
4. 컬럼명이 ID, 번호, 코드 등을 나타내는 컬럼

Primary Key로 적합한 컬럼명만 쉼표로 구분하여 나열해주세요. 없으면 '없음'이라고 답변해주세요.

추천 Primary Key:"""
                
                response = self._chat_with_debug(client, [{"role": "user", "content": prompt}], max_tokens=100, temperature=0.3)
                response_text = response.strip() if isinstance(response, str) else str(response).strip()
                
                # 응답 파싱
                if response_text and response_text.lower() not in ['없음', '-', 'none']:
                    # 쉼표로 구분된 컬럼명들 추출
                    pk_candidates = [col.strip() for col in response_text.split(',')]
                    # 실제 존재하는 컬럼명만 필터링
                    valid_columns = {col.column_name for col in columns}
                    return [pk for pk in pk_candidates if pk in valid_columns]
                
                return []
                
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Failed to analyze PK candidates for {table.table_name}: {e}")
            return []
    
    def process_project_summaries(self, project_id: int, batch_size: int = 10):
        """Process all files, methods, and SQL units for a project"""
        logger.info(f"Starting LLM summarization for project {project_id}")
        
        # Ensure summary columns exist
        self._add_summary_columns_if_needed()
        
        session = self.session()
        try:
            # Process files
            files = session.query(File).filter(
                File.project_id == project_id,
                File.llm_summary.is_(None)
            ).limit(batch_size).all()
            
            for file in files:
                logger.info(f"Summarizing file: {file.path}")
                summary = self.summarize_file(file)
                if summary:
                    # Calculate confidence based on file content availability
                    confidence = 0.8 if Path(file.path or "").exists() else 0.5
                    session.execute(
                        text("UPDATE files SET llm_summary = :summary, llm_summary_confidence = :confidence WHERE file_id = :file_id"),
                        {"summary": summary, "confidence": confidence, "file_id": file.file_id}
                    )
            
            session.commit()
            logger.info(f"Processed {len(files)} files")
            
            # Process methods
            methods = session.query(Method).join(Class).join(File).filter(
                File.project_id == project_id,
                Method.llm_summary.is_(None)
            ).limit(batch_size).all()
            
            for method in methods:
                logger.info(f"Summarizing method: {method.name}")
                summary = self.summarize_method(method)
                if summary:
                    # Calculate confidence based on method code availability
                    confidence = 0.7  # Default confidence for method analysis
                    session.execute(
                        text("UPDATE methods SET llm_summary = :summary, llm_summary_confidence = :confidence WHERE method_id = :method_id"),
                        {"summary": summary, "confidence": confidence, "method_id": method.method_id}
                    )
            
            session.commit()
            logger.info(f"Processed {len(methods)} methods")
            
            # Process SQL units
            sql_units = session.query(SqlUnit).join(File).filter(
                File.project_id == project_id,
                SqlUnit.llm_summary.is_(None)
            ).limit(batch_size).all()
            
            for sql_unit in sql_units:
                logger.info(f"Summarizing SQL unit: {sql_unit.mapper_ns}.{sql_unit.stmt_id}")
                summary = self.summarize_sql_unit(sql_unit)
                if summary:
                    # Calculate confidence based on SQL content availability
                    confidence = 0.9 if hasattr(sql_unit, 'sql_content') and sql_unit.sql_content else 0.4
                    session.execute(
                        text("UPDATE sql_units SET llm_summary = :summary, llm_summary_confidence = :confidence WHERE sql_id = :sql_id"),
                        {"summary": summary, "confidence": confidence, "sql_id": sql_unit.sql_id}
                    )
            
            session.commit()
            logger.info(f"Processed {len(sql_units)} SQL units")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error processing project summaries: {e}")
            raise
        finally:
            session.close()
    
    def analyze_joins_from_sql(self, sql_unit: SqlUnit) -> List[Dict[str, Any]]:
        """Analyze SQL to extract join conditions using LLM"""
        try:
            if not self.llm_config.get('enabled', True):
                return []
            
            client = get_client(self.llm_config)
            
            sql_text = getattr(sql_unit, 'normalized_fingerprint', '') or 'SQL 내용 없음'
            
            prompt = f"""다음 SQL 쿼리를 분석하여 테이블 간 조인 조건을 추출해주세요.


SQL 정보:
- Mapper: {sql_unit.mapper_ns}
- Statement ID: {sql_unit.stmt_id}
- SQL 종류: {sql_unit.stmt_kind}

SQL 내용:
{sql_text[:2000]}

다음 형식으로 조인 조건을 추출해주세요 (조인이 없으면 "조인 없음"이라고 답변)
:
테이블1.컬럼1 = 테이블2.컬럼2
테이블1.컬럼3 = 테이블3.컬럼4

추출된 조인 조건:"""
            
            response = self._chat_with_debug(client, [{"role": "user", "content": prompt}], max_tokens=300, temperature=0.3)
            response_text = response.strip() if isinstance(response, str) else str(response).strip()
            
            # Parse the response to extract joins
            joins = []
            if response_text and "조인 없음" not in response_text.lower():
                lines = response_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if '=' in line and '.' in line:
                        try:
                            left, right = line.split('=', 1)
                            left_parts = left.strip().split('.')
                            right_parts = right.strip().split('.')
                            
                            if len(left_parts) == 2 and len(right_parts) == 2:
                                joins.append({
                                    'l_table': left_parts[0].strip(),
                                    'l_col': left_parts[1].strip(),
                                    'r_table': right_parts[0].strip(),
                                    'r_col': right_parts[1].strip(),
                                    'op': '=',
                                    'confidence': 0.8,
                                    'llm_generated': True
                                })
                        except Exception:
                            continue
            
            return joins
            
        except Exception as e:
            logger.error(f"Failed to analyze joins for SQL {sql_unit.mapper_ns}.{sql_unit.stmt_id}: {e}")
            return []
    
    def process_missing_joins(self, project_id: int, batch_size: int = 10):
        """Process SQL units that don't have join information"""
        logger.info("Starting join analysis for SQL units without joins")
        
        session = self.session()
        try:
            # Find SQL units that don't have joins but might need them
            sql_units_without_joins = session.query(SqlUnit).join(File).filter(
                File.project_id == project_id,
                ~SqlUnit.sql_id.in_(session.query(Join.sql_id))
            ).limit(batch_size * 3).all()  # Process more since many might not have joins
            
            for sql_unit in sql_units_without_joins:
                logger.info(f"Analyzing joins for SQL: {sql_unit.mapper_ns}.{sql_unit.stmt_id}")
                
                joins = self.analyze_joins_from_sql(sql_unit)
                
                # Save detected joins to database
                for join_info in joins:
                    session.execute(
                        text("""INSERT INTO joins (sql_id, l_table, l_col, op, r_table, r_col, inferred_pkfk, confidence) 
                                VALUES (:sql_id, :l_table, :l_col, :op, :r_table, :r_col, :inferred_pkfk, :confidence)"""),
                        {
                            "sql_id": sql_unit.sql_id,
                            "l_table": join_info['l_table'],
                            "l_col": join_info['l_col'],
                            "op": join_info['op'],
                            "r_table": join_info['r_table'],
                            "r_col": join_info['r_col'],
                            "inferred_pkfk": 1,  # Mark as LLM-inferred
                            "confidence": join_info['confidence']
                        }
                    )
            
            session.commit()
            logger.info(f"Processed {len(sql_units_without_joins)} SQL units for join analysis")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error processing joins: {e}")
            raise
        finally:
            session.close()
    
    def process_table_comments(self, batch_size: int = 10):
        """Process and enhance table/column comments"""
        logger.info("Starting table comment enhancement")
        
        session = self.session()
        try:
            # Process tables
            tables = session.query(DbTable).filter(
                DbTable.llm_comment.is_(None)
            ).limit(batch_size).all()
            
            for table in tables:
                logger.info(f"Enhancing comment for table: {table.table_name}")
                
                # Get related code context (using SQL content or normalized_fingerprint)
                related_sql = []
                try:
                    # Try to find SQL units that reference this table name
                    related_sql = session.query(SqlUnit).filter(
                        SqlUnit.normalized_fingerprint.contains(table.table_name)
                    ).limit(3).all()
                except Exception:
                    # If that fails, just get any SQL units as context
                    related_sql = session.query(SqlUnit).limit(3).all()
                
                context = f"Related SQL queries:\n"
                for sql in related_sql:
                    sql_text = getattr(sql, 'sql_content', '') or getattr(sql, 'normalized_fingerprint', '') or 'No SQL content'
                    context += f"- {sql.mapper_ns}.{sql.stmt_id}: {sql_text[:200]}...\n"
                
                enhanced_comment = self.enhance_table_comment(table, context)
                if enhanced_comment:
                    # Higher confidence when we have related SQL context
                    confidence = 0.8 if related_sql else 0.6
                    session.execute(
                        text("UPDATE db_tables SET llm_comment = :comment, llm_comment_confidence = :confidence WHERE table_id = :table_id"),
                        {"comment": enhanced_comment, "confidence": confidence, "table_id": table.table_id}
                    )
            
            session.commit()
            logger.info(f"Processed {len(tables)} tables")
            
            # Process columns - process all columns without LLM comment
            all_columns = session.query(DbColumn).filter(
                DbColumn.llm_comment.is_(None)
            ).all()
            
            logger.info(f"Found {len(all_columns)} columns to process")
            
            # Process in batches 
            for i in range(0, len(all_columns), batch_size):
                batch_columns = all_columns[i:i + batch_size]
                logger.info(f"Processing column batch {i//batch_size + 1}: {len(batch_columns)} columns")
                
                for column in batch_columns:
                    logger.info(f"Enhancing comment for column: {column.column_name}")
                    
                    # Get table context
                    table_info = session.query(DbTable).filter(DbTable.table_id == column.table_id).first()
                    table_name = table_info.table_name if table_info else 'Unknown'
                    context = f"Table: {table_name}\n"
                    if table_info and table_info.table_comment:
                        context += f"Table Comment: {table_info.table_comment}\n"
                    
                    enhanced_comment = self.enhance_column_comment(column, context)
                    if enhanced_comment:
                        # Higher confidence when we have table context
                        confidence = 0.7 if table_info and table_info.table_comment else 0.5
                        session.execute(
                            text("UPDATE db_columns SET llm_comment = :comment, llm_comment_confidence = :confidence WHERE column_id = :column_id"),
                            {"comment": enhanced_comment, "confidence": confidence, "column_id": column.column_id}
                        )
                
                session.commit()
                logger.info(f"Processed batch of {len(batch_columns)} columns")
            
            logger.info(f"Total processed: {len(all_columns)} columns")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error processing table comments: {e}")
            raise
        finally:
            session.close()


def generate_source_specification_md(config: Dict[str, Any], output_path: str):
    """Generate source code specification markdown document"""
    summarizer = CodeSummarizer(config)
    session = summarizer.session()
    
    try:
        # Get all files with LLM summaries
        files = session.query(File).filter(File.llm_summary.isnot(None)).order_by(File.path).all()
        
        md_content = ["# 소스코드 명세서\n"]
        md_content.append("SourceAnalyzer LLM 분석으로 생성된 소스코드 명세서\n")
        md_content.append("---\n")
        
        # Group by file type
        file_groups = {
            'JSP': [f for f in files if f.path and f.path.endswith('.jsp')],
            'Java': [f for f in files if f.path and f.path.endswith('.java')],
            'Other': [f for f in files if f.path and not (f.path.endswith('.jsp') or f.path.endswith('.java'))]
        }
        
        for group_name, group_files in file_groups.items():
            if not group_files:
                continue
                
            md_content.append(f"## {group_name} 파일\n")
            
            for file in group_files:
                # 파일 경로에서 PROJECT 접두사 제거
                display_path = file.path
                if display_path and display_path.startswith('PROJECT\\'):
                    display_path = display_path[8:]  # 'PROJECT\' 제거
                
                md_content.append(f"### {display_path}\n")
                
                # File summary (마크다운 표 깨짐 방지)
                if file.llm_summary:
                    cleaned_summary = file.llm_summary.replace('|', '\\|').replace('\n', ' ')
                    # '알겠습니다' 같은 불필요한 응답 제거
                    if cleaned_summary.strip() not in ['알겠습니다', '알겠습니다.', 'OK', 'ok', '네', '네.']:
                        md_content.append(f"**파일 설명:** {cleaned_summary}\n")
                
                # File details
                md_content.append(f"- **언어:** {file.language or 'Unknown'}")
                md_content.append(f"- **라인 수:** {file.loc or 0}")
                if hasattr(file, 'llm_summary_confidence') and file.llm_summary_confidence:
                    md_content.append(f"- **분석 신뢰도:** {file.llm_summary_confidence:.2f}")
                
                # Get classes in this file
                classes = session.query(Class).filter(Class.file_id == file.file_id).all()
                if classes:
                    md_content.append(f"\n**클래스 목록:**")
                    for clazz in classes:
                        # Unknown 클래스명 필터링
                        class_name = clazz.name if clazz.name and clazz.name.strip() not in ['Unknown', 'unknown', 'UNKNOWN'] else ''
                        if class_name:
                            class_info = f"- **{class_name}**"
                            if clazz.llm_summary:
                                cleaned_class_summary = clazz.llm_summary.replace('|', '\\|').replace('\n', ' ')
                                # 불필요한 응답 제거
                                if cleaned_class_summary.strip() not in ['알겠습니다', '알겠습니다.', 'OK', 'ok', '네', '네.']:
                                    class_info += f": {cleaned_class_summary}"
                            md_content.append(class_info)
                        
                        # Get methods in this class (Unknown 클래스만 해당되는 경우만 처리)
                        if class_name:  # Unknown이 아닌 클래스만
                            methods = session.query(Method).filter(Method.class_id == clazz.class_id).all()
                            if methods:
                                for method in methods:
                                    method_info = f"  - `{method.name}()`"
                                    if method.llm_summary:
                                        cleaned_method_summary = method.llm_summary.replace('|', '\\|').replace('\n', ' ')
                                        # 불필요한 응답 제거
                                        if cleaned_method_summary.strip() not in ['알겠습니다', '알겠습니다.', 'OK', 'ok', '네', '네.']:
                                            method_info += f": {cleaned_method_summary}"
                                    md_content.append(method_info)
                
                # Get SQL units in this file
                sql_units = session.query(SqlUnit).filter(SqlUnit.file_id == file.file_id).all()
                if sql_units:
                    md_content.append(f"\n**SQL 쿼리 목록:**")
                    for sql in sql_units:
                        sql_info = f"- **{sql.mapper_ns}.{sql.stmt_id}** ({sql.stmt_kind})"
                        if sql.llm_summary:
                            cleaned_sql_summary = sql.llm_summary.replace('|', '\\|').replace('\n', ' ')
                            # 불필요한 응답 제거
                            if cleaned_sql_summary.strip() not in ['알겠습니다', '알겠습니다.', 'OK', 'ok', '네', '네.']:
                                sql_info += f": {cleaned_sql_summary}"
                        md_content.append(sql_info)
                
                md_content.append("\n---\n")
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_content))
        
        print(f"Source specification saved to: {output_path}")
        
    finally:
        session.close()


def generate_table_specification_md(config: Dict[str, Any], output_path: str):
    """Generate table specification markdown document"""
    summarizer = CodeSummarizer(config)
    session = summarizer.session()
    
    try:
        tables = session.query(DbTable).order_by(DbTable.table_name).all()
        
        md_content = ["# Database Table Specifications\n"]
        md_content.append(f"Generated from SourceAnalyzer metadata\n")
        md_content.append("---\n")
        
        for table in tables:
            md_content.append(f"## Table: {table.table_name}\n")
            
            # Table description
            if table.table_comment:
                md_content.append(f"**Original Comment:** {table.table_comment}\n")
            llm_comment = getattr(table, 'llm_comment', None)
            if llm_comment:
                md_content.append(f"**LLM_Description:** {llm_comment}\n")
            
            md_content.append("")
            
            # Table columns (with deduplication)
            columns_dict = {}
            columns_query = session.query(DbColumn).filter(DbColumn.table_id == table.table_id).order_by(DbColumn.column_name).all()
            for col in columns_query:
                # Keep the first occurrence or the one with a comment
                if col.column_name not in columns_dict or (col.column_comment and not columns_dict[col.column_name].column_comment):
                    columns_dict[col.column_name] = col
            columns = list(columns_dict.values())
            
            if columns:
                md_content.append("| Column | Type | Nullable | Comment | LLM_Column |")
                md_content.append("|--------|------|----------|---------|------------|")
                
                for col in columns:
                    nullable = "Yes" if col.nullable == 'Y' else "No"
                    original_comment = col.column_comment or ""
                    enhanced_comment = getattr(col, 'llm_comment', None) or ""
                    
                    # 마크다운 표 깨짐 방지: 파이프 문자와 줄바꿈 제거
                    original_comment = original_comment.replace('|', '\\|').replace('\n', ' ')
                    enhanced_comment = enhanced_comment.replace('|', '\\|').replace('\n', ' ')
                    
                    md_content.append(f"| {col.column_name} | {col.data_type} | {nullable} | {original_comment} | {enhanced_comment} |")
                
                md_content.append("")
            
            # Primary keys (기존 CSV)
            pks = session.execute(
                text("SELECT column_name FROM db_pk WHERE table_id = :table_id ORDER BY pk_pos"),
                {"table_id": table.table_id}
            ).fetchall()
            
            if pks:
                pk_cols = [pk[0] for pk in pks]
                md_content.append(f"**Primary Key:** {', '.join(pk_cols)}\n")
            
            # LLM이 추론한 Primary Key 추가
            # 관련 SQL 컨텍스트 수집
            related_sql = []
            try:
                related_sql = session.query(SqlUnit).filter(
                    SqlUnit.normalized_fingerprint.contains(table.table_name)
                ).limit(3).all()
            except Exception:
                pass
                
            context = f"Related SQL queries:\n"
            for sql in related_sql:
                sql_text = getattr(sql, 'sql_content', '') or getattr(sql, 'normalized_fingerprint', '') or 'No SQL content'
                context += f"- {sql.mapper_ns}.{sql.stmt_id}: {sql_text[:200]}...\n"
            
            # LLM PK 분석 실행
            try:
                summarizer_instance = CodeSummarizer({"llm": self.config.get('llm', {})})
                llm_pk_candidates = summarizer_instance.analyze_primary_key_candidates(table, context)
                if llm_pk_candidates:
                    md_content.append(f"**LLM_PK:** {', '.join(llm_pk_candidates)}\n")
                else:
                    md_content.append(f"**LLM_PK:** 분석된 후보 없음\n")
            except Exception as e:
                logger.warning(f"LLM PK 분석 실패 for {table.table_name}: {e}")
                md_content.append(f"**LLM_PK:** 분석 실패\n")
            
            md_content.append("---\n")
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_content))
        
        print(f"Table specification saved to: {output_path}")
        
    finally:
        session.close()