# phase1/llm/summarizer.py
from typing import Dict, Any, Optional, List
import json
from pathlib import Path
from ..llm.client import get_client
from ..models.database import DatabaseManager, File, Class, Method, SqlUnit, DbTable, DbColumn
from sqlalchemy import text
import logging

logger = logging.getLogger(__name__)


class CodeSummarizer:
    """LLM-based code summarization and metadata enhancement"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm_config = config.get('llm', {})
        self.dbm = DatabaseManager(config.get('database', {}).get('project', {}))
        self.dbm.initialize()
    
    def session(self):
        """Get database session"""
        return self.dbm.get_session()
    
    def _add_summary_columns_if_needed(self):
        """Add summary columns to tables if they don't exist"""
        session = self.session()
        try:
            # Add summary column to files table
            try:
                session.execute(text("ALTER TABLE files ADD COLUMN llm_summary TEXT"))
                session.commit()
                logger.info("Added llm_summary column to files table")
            except Exception:
                pass  # Column already exists
            
            # Add summary column to classes table
            try:
                session.execute(text("ALTER TABLE classes ADD COLUMN llm_summary TEXT"))
                session.commit()
                logger.info("Added llm_summary column to classes table")
            except Exception:
                pass
            
            # Add summary column to methods table
            try:
                session.execute(text("ALTER TABLE methods ADD COLUMN llm_summary TEXT"))
                session.commit()
                logger.info("Added llm_summary column to methods table")
            except Exception:
                pass
            
            # Add summary column to sql_units table
            try:
                session.execute(text("ALTER TABLE sql_units ADD COLUMN llm_summary TEXT"))
                session.commit()
                logger.info("Added llm_summary column to sql_units table")
            except Exception:
                pass
            
            # Add enhanced comment columns to db tables
            try:
                session.execute(text("ALTER TABLE db_tables ADD COLUMN llm_comment TEXT"))
                session.commit()
                logger.info("Added llm_comment column to db_tables table")
            except Exception:
                pass
            
            try:
                session.execute(text("ALTER TABLE db_columns ADD COLUMN llm_comment TEXT"))
                session.commit()
                logger.info("Added llm_comment column to db_columns table")
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
                prompt = f"""Analyze this JSP file and provide a brief summary of its purpose and functionality.

File: {file.path}
Content:
{file_content[:3000]}...

Provide a concise summary (1-2 sentences) describing:
1. What this JSP page does
2. Its main functionality or purpose
3. Key features or components

Summary:"""
            elif file_extension == '.java':
                prompt = f"""Analyze this Java file and provide a brief summary of its purpose and functionality.

File: {file.path}
Content:
{file_content[:3000]}...

Provide a concise summary (1-2 sentences) describing:
1. What this Java class/file does
2. Its main responsibility
3. Key methods or features

Summary:"""
            else:
                prompt = f"""Analyze this code file and provide a brief summary of its purpose and functionality.

File: {file.path}
Content:
{file_content[:3000]}...

Provide a concise summary (1-2 sentences) describing what this file does and its main purpose.

Summary:"""
            
            summary = client.chat([{"role": "user", "content": prompt}], max_tokens=200, temperature=0.3)
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
            
            prompt = f"""Analyze this Java method and provide a brief summary of its functionality.

Method: {method.name}
Class: {method.class_fqn if hasattr(method, 'class_fqn') else 'Unknown'}
Parameters: {method.parameters if hasattr(method, 'parameters') else 'Unknown'}
Return Type: {method.return_type if hasattr(method, 'return_type') else 'Unknown'}

Code:
{method_code[:2000]}...

Provide a concise summary (1 sentence) describing what this method does and its purpose.

Summary:"""
            
            summary = client.chat([{"role": "user", "content": prompt}], max_tokens=150, temperature=0.3)
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
            
            prompt = f"""Analyze this SQL query/statement and provide a brief summary of its functionality.

Mapper Namespace: {sql_unit.mapper_ns}
Statement ID: {sql_unit.stmt_id}
Statement Kind: {sql_unit.stmt_kind}
SQL Content:
{sql_unit.sql_content[:2000] if sql_unit.sql_content else 'No content available'}...

Provide a concise summary (1 sentence) describing what this SQL statement does and its purpose.

Summary:"""
            
            summary = client.chat([{"role": "user", "content": prompt}], max_tokens=150, temperature=0.3)
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
            
            prompt = f"""Analyze this database table and provide an enhanced comment/description.

Table Name: {table.name}
Current Comment: {table.comment or 'No comment available'}

Related Code Context:
{related_code_context[:1500]}

Based on the table name, existing comment, and related code usage, provide an enhanced comment that describes:
1. The table's purpose and what data it stores
2. Its role in the application
3. Key relationships or business logic

Enhanced Comment:"""
            
            comment = client.chat([{"role": "user", "content": prompt}], max_tokens=200, temperature=0.3)
            return comment.strip() if isinstance(comment, str) else str(comment).strip()
            
        except Exception as e:
            logger.error(f"Failed to enhance table comment for {table.name}: {e}")
            return None
    
    def enhance_column_comment(self, column: DbColumn, table_context: str = "") -> Optional[str]:
        """Enhance column comments using LLM analysis"""
        try:
            if not self.llm_config.get('enabled', True):
                return None
            
            client = get_client(self.llm_config)
            
            prompt = f"""Analyze this database column and provide an enhanced comment/description.

Column Name: {column.column_name}
Data Type: {column.data_type}
Nullable: {column.nullable}
Current Comment: {column.comment or 'No comment available'}

Table Context:
{table_context[:1000]}

Based on the column name, data type, and table context, provide an enhanced comment that describes:
1. What data this column stores
2. Its purpose and business meaning
3. Any constraints or special considerations

Enhanced Comment:"""
            
            comment = client.chat([{"role": "user", "content": prompt}], max_tokens=150, temperature=0.3)
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
                    session.execute(
                        text("UPDATE files SET llm_summary = :summary WHERE file_id = :file_id"),
                        {"summary": summary, "file_id": file.file_id}
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
                    session.execute(
                        text("UPDATE methods SET llm_summary = :summary WHERE method_id = :method_id"),
                        {"summary": summary, "method_id": method.method_id}
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
                    session.execute(
                        text("UPDATE sql_units SET llm_summary = :summary WHERE sql_id = :sql_id"),
                        {"summary": summary, "sql_id": sql_unit.sql_id}
                    )
            
            session.commit()
            logger.info(f"Processed {len(sql_units)} SQL units")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error processing project summaries: {e}")
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
                logger.info(f"Enhancing comment for table: {table.name}")
                
                # Get related code context
                related_sql = session.query(SqlUnit).filter(
                    SqlUnit.sql_content.contains(table.name)
                ).limit(3).all()
                
                context = f"Related SQL queries:\n"
                for sql in related_sql:
                    context += f"- {sql.mapper_ns}.{sql.stmt_id}: {sql.sql_content[:200]}...\n"
                
                enhanced_comment = self.enhance_table_comment(table, context)
                if enhanced_comment:
                    session.execute(
                        text("UPDATE db_tables SET llm_comment = :comment WHERE table_id = :table_id"),
                        {"comment": enhanced_comment, "table_id": table.table_id}
                    )
            
            session.commit()
            logger.info(f"Processed {len(tables)} tables")
            
            # Process columns
            columns = session.query(DbColumn).filter(
                DbColumn.llm_comment.is_(None)
            ).limit(batch_size).all()
            
            for column in columns:
                logger.info(f"Enhancing comment for column: {column.table_name}.{column.column_name}")
                
                # Get table context
                table_info = session.query(DbTable).filter(DbTable.name == column.table_name).first()
                context = f"Table: {column.table_name}\n"
                if table_info and table_info.comment:
                    context += f"Table Comment: {table_info.comment}\n"
                
                enhanced_comment = self.enhance_column_comment(column, context)
                if enhanced_comment:
                    session.execute(
                        text("UPDATE db_columns SET llm_comment = :comment WHERE column_id = :column_id"),
                        {"comment": enhanced_comment, "column_id": column.column_id}
                    )
            
            session.commit()
            logger.info(f"Processed {len(columns)} columns")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error processing table comments: {e}")
            raise
        finally:
            session.close()


def generate_table_specification_md(config: Dict[str, Any], output_path: str):
    """Generate table specification markdown document"""
    summarizer = CodeSummarizer(config)
    session = summarizer.session()
    
    try:
        tables = session.query(DbTable).order_by(DbTable.name).all()
        
        md_content = ["# Database Table Specifications\n"]
        md_content.append(f"Generated from SourceAnalyzer metadata\n")
        md_content.append("---\n")
        
        for table in tables:
            md_content.append(f"## Table: {table.name}\n")
            
            # Table description
            if table.llm_comment:
                md_content.append(f"**Enhanced Description:** {table.llm_comment}\n")
            if table.comment and table.comment != table.llm_comment:
                md_content.append(f"**Original Comment:** {table.comment}\n")
            
            md_content.append("")
            
            # Table columns
            columns = session.query(DbColumn).filter(DbColumn.table_name == table.name).order_by(DbColumn.column_name).all()
            
            if columns:
                md_content.append("| Column | Type | Nullable | Comment | Enhanced Comment |")
                md_content.append("|--------|------|----------|---------|-------------------|")
                
                for col in columns:
                    nullable = "Yes" if col.nullable else "No"
                    original_comment = col.comment or ""
                    enhanced_comment = col.llm_comment or ""
                    
                    md_content.append(f"| {col.column_name} | {col.data_type} | {nullable} | {original_comment} | {enhanced_comment} |")
                
                md_content.append("")
            
            # Primary keys
            pks = session.execute(
                text("SELECT column_name FROM db_pks WHERE table_name = :table_name ORDER BY position"),
                {"table_name": table.name}
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