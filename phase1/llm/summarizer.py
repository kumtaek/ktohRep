# phase1/llm/summarizer.py
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
    """LLM-based code summarization and metadata enhancement"""
    
    def __init__(self, config: Dict[str, Any], debug: bool = False):
        self.config = config
        self.llm_config = config.get('llm', {})
        self.debug = debug
        self.dbm = DatabaseManager(config.get('database', {}).get('project', {}))
        self.dbm.initialize()
    
    def session(self):
        """Get database session"""
        return self.dbm.get_session()
    
    def _chat_with_debug(self, client, messages: list, **kwargs):
        """Helper method to handle LLM chat with Korean system prompt and debug output"""
        # Add Korean system prompt
        korean_system = {
            "role": "system", 
            "content": "모든 응답을 한국어로 해주세요. 간결하고 명확하게 답변해주세요."
        }
        
        # Insert system message at the beginning
        messages_with_system = [korean_system] + messages
        
        if self.debug:
            print("=" * 50)
            print("[DEBUG] LLM 요청:")
            for i, msg in enumerate(messages_with_system):
                print(f"[{msg['role'].upper()}] {msg['content'][:200]}{'...' if len(msg['content']) > 200 else ''}")
            print("=" * 50)
        
        response = client.chat(messages_with_system, **kwargs)
        
        if self.debug:
            print("[DEBUG] LLM 응답:")
            print(f"{response[:500]}{'...' if len(str(response)) > 500 else ''}")
            print("=" * 50)
        
        return response
    
    def _add_summary_columns_if_needed(self):
        """Add summary columns to tables if they don't exist"""
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
    
    def summarize_file(self, file: File) -> Optional[str]:
        """Generate summary for a file using LLM"""
        try:
            if not self.llm_config.get('enabled', True):
                return None
            
            client = get_client(self.llm_config)
            
            # Read file content if available
            file_content = ""
            if file.path and Path(file.path).exists():
                try:
                    with open(file.path, 'r', encoding='utf-8', errors='ignore') as f:
                        file_content = f.read()
                except Exception as e:
                    logger.warning(f"Could not read file {file.path}: {e}")
            
            # Determine file type and create appropriate prompt
            file_extension = Path(file.path or "").suffix.lower()
            
            if file_extension == '.jsp':
                prompt = f"""다음 JSP 파일을 분석하고 목적과 기능을 간략하게 요약해주세요.

파일: {file.path}
내용:
{file_content[:3000]}...

다음을 포함하여 간결한 요약(1-2문장)을 제공해주세요:
1. 이 JSP 페이지가 하는 일
2. 주요 기능 또는 목적
3. 핵심 기능 또는 구성요소

요약:"""
            elif file_extension == '.java':
                prompt = f"""다음 Java 파일을 분석하고 목적과 기능을 간략하게 요약해주세요.

파일: {file.path}
내용:
{file_content[:3000]}...

다음을 포함하여 간결한 요약(1-2문장)을 제공해주세요:
1. 이 Java 클래스/파일이 하는 일
2. 주요 책임
3. 핵심 메서드 또는 기능

요약:"""
            else:
                prompt = f"""다음 코드 파일을 분석하고 목적과 기능을 간략하게 요약해주세요.

파일: {file.path}
내용:
{file_content[:3000]}...

이 파일이 하는 일과 주요 목적에 대해 간결한 요약(1-2문장)을 제공해주세요.

요약:"""
            
            summary = self._chat_with_debug(client, [{"role": "user", "content": prompt}], max_tokens=200, temperature=0.3)
            return summary.strip() if isinstance(summary, str) else str(summary).strip()
            
        except Exception as e:
            logger.error(f"Failed to summarize file {file.path}: {e}")
            return None
    
    def summarize_method(self, method: Method) -> Optional[str]:
        """Generate summary for a method using LLM"""
        try:
            if not self.llm_config.get('enabled', True):
                return None
            
            client = get_client(self.llm_config)
            
            # Get method details
            method_code = getattr(method, 'code_snippet', '') or getattr(method, 'source_code', '') or ''
            
            prompt = f"""다음 Java 메서드를 분석하고 기능을 간략하게 요약해주세요.

메서드: {method.name}
클래스: {method.class_fqn if hasattr(method, 'class_fqn') else 'Unknown'}
매개변수: {method.parameters if hasattr(method, 'parameters') else 'Unknown'}
반환 타입: {method.return_type if hasattr(method, 'return_type') else 'Unknown'}

코드:
{method_code[:2000]}...

이 메서드가 하는 일과 목적에 대해 간결한 요약(1문장)을 제공해주세요.

요약:"""
            
            summary = self._chat_with_debug(client, [{"role": "user", "content": prompt}], max_tokens=150, temperature=0.3)
            return summary.strip() if isinstance(summary, str) else str(summary).strip()
            
        except Exception as e:
            logger.error(f"Failed to summarize method {method.name}: {e}")
            return None
    
    def summarize_sql_unit(self, sql_unit: SqlUnit) -> Optional[str]:
        """Generate summary for a SQL unit using LLM"""
        try:
            if not self.llm_config.get('enabled', True):
                return None
            
            client = get_client(self.llm_config)
            
            prompt = f"""다음 SQL 쿼리/문을 분석하고 기능을 간략하게 요약해주세요.

매퍼 네임스페이스: {sql_unit.mapper_ns}
문 ID: {sql_unit.stmt_id}
문 종류: {sql_unit.stmt_kind}
SQL 내용:
{sql_unit.sql_content[:2000] if sql_unit.sql_content else 'No content available'}...

이 SQL 문이 하는 일과 목적에 대해 간결한 요약(1문장)을 제공해주세요.

요약:"""
            
            summary = self._chat_with_debug(client, [{"role": "user", "content": prompt}], max_tokens=150, temperature=0.3)
            return summary.strip() if isinstance(summary, str) else str(summary).strip()
            
        except Exception as e:
            logger.error(f"Failed to summarize SQL unit {sql_unit.mapper_ns}.{sql_unit.stmt_id}: {e}")
            return None
    
    def enhance_table_comment(self, table: DbTable, related_code_context: str = "") -> Optional[str]:
        """Enhance table comments using LLM analysis"""
        try:
            if not self.llm_config.get('enabled', True):
                return None
            
            client = get_client(self.llm_config)
            
            prompt = f"""데이터베이스 테이블을 분석하여 한글로 향상된 설명을 제공해주세요.

테이블명: {table.table_name}
기존 코멘트: {table.table_comment or '코멘트 없음'}

관련 코드 컨텍스트:
{related_code_context[:1500]}

테이블명, 기존 코멘트, 관련 코드 사용을 바탕으로 다음을 포함하는 향상된 설명을 한글로 100자 이내로 작성해주세요:
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

컬럼명, 데이터 타입, 테이블 컨텍스트를 바탕으로 다음을 포함하는 향상된 설명을 한글로 30자 이내로 작성해주세요:
1. 이 컬럼이 저장하는 데이터
2. 용도와 비즈니스 의미
3. 제약사항이나 특별한 고려사항

향상된 설명:"""
            
            comment = self._chat_with_debug(client, [{"role": "user", "content": prompt}], max_tokens=150, temperature=0.3)
            return comment.strip() if isinstance(comment, str) else str(comment).strip()
            
        except Exception as e:
            logger.error(f"Failed to enhance column comment for {column.column_name}: {e}")
            return None
    
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

다음 형식으로 조인 조건을 추출해주세요 (조인이 없으면 "조인 없음"이라고 답변):
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
            llm_comment = getattr(table, 'llm_comment', None)
            if llm_comment:
                md_content.append(f"**LLM_Description:** {llm_comment}\n")
            if table.table_comment and table.table_comment != llm_comment:
                md_content.append(f"**Original Comment:** {table.table_comment}\n")
            
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
                md_content.append("| Column | Type | Nullable | Comment | Enhanced Comment |")
                md_content.append("|--------|------|----------|---------|-------------------|")
                
                for col in columns:
                    nullable = "Yes" if col.nullable == 'Y' else "No"
                    original_comment = col.column_comment or ""
                    enhanced_comment = getattr(col, 'llm_comment', None) or ""
                    
                    # 마크다운 표 깨짐 방지: 파이프 문자와 줄바꿈 제거
                    original_comment = original_comment.replace('|', '\\|').replace('\n', ' ')
                    enhanced_comment = enhanced_comment.replace('|', '\\|').replace('\n', ' ')
                    
                    md_content.append(f"| {col.column_name} | {col.data_type} | {nullable} | {original_comment} | {enhanced_comment} |")
                
                md_content.append("")
            
            # Primary keys
            pks = session.execute(
                text("SELECT column_name FROM db_pk WHERE table_id = :table_id ORDER BY pk_pos"),
                {"table_id": table.table_id}
            ).fetchall()
            
            if pks:
                pk_cols = [pk[0] for pk in pks]
                md_content.append(f"**Primary Key:** {', '.join(pk_cols)}\n")
            
            md_content.append("---\n")
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_content))
        
        print(f"Table specification saved to: {output_path}")
        
    finally:
        session.close()