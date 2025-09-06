"""
LLM 메타데이터 처리기
메타데이터 엔진에서 LLM 관련 기능들을 분리한 모듈
"""

from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from contextlib import contextmanager
import traceback

from phase1.models.database import (
    DatabaseManager, DbTable, DbColumn, SqlUnit, Method, File, Join
)
from phase1.utils.logger import LoggerFactory
from phase1.utils.confidence_calculator import ConfidenceCalculator
from phase1.llm.assist import LlmAssist


class LlmMetadataProcessor:
    """LLM을 사용한 메타데이터 처리 전용 클래스"""
    
    def __init__(self, config: Dict[str, Any], db_manager: DatabaseManager):
        self.config = config
        self.db_manager = db_manager
        self.logger = LoggerFactory.get_engine_logger()
        self.confidence_calculator = ConfidenceCalculator(config)
        self.llm_assist = LlmAssist(config, db_manager=self.db_manager, 
                                   logger=self.logger, confidence_calculator=self.confidence_calculator)

    @contextmanager
    def _get_sync_session(self):
        """동기 데이터베이스 세션 관리"""
        with self.db_manager.get_auto_commit_session() as session:
            yield session

    def llm_enrich_table_and_column_comments(self, *, max_tables: int = 50, max_columns: int = 100, lang: str = 'ko') -> Dict[str, int]:
        """
        LLM을 사용하여 테이블과 컬럼 설명을 풍성하게 만들기
        
        Args:
            max_tables: 처리할 최대 테이블 수
            max_columns: 처리할 최대 컬럼 수
            lang: 언어 ('ko' 또는 'en')
            
        Returns:
            처리 결과 통계
        """
        try:
            with self._get_sync_session() as session:
                stats = {"tables_processed": 0, "columns_processed": 0, "errors": 0}
                
                # 테이블 설명 개선
                tables_query = session.query(DbTable).filter(
                    (DbTable.table_comment.is_(None)) | (DbTable.table_comment == '')
                ).limit(max_tables)
                
                for table in tables_query:
                    try:
                        # LLM을 사용한 테이블 설명 생성
                        enhanced_comment = self.llm_assist.generate_table_comment(
                            table_name=table.table_name,
                            existing_comment=table.table_comment,
                            context=self._get_table_context(session, table),
                            lang=lang
                        )
                        
                        if enhanced_comment:
                            table.table_comment = enhanced_comment
                            stats["tables_processed"] += 1
                            self.logger.info(f"테이블 설명 개선 완료: {table.table_name}")
                            
                    except Exception as e:
                        error_msg = f"테이블 설명 개선 실패 {table.table_name}: {e}"
                        traceback_str = traceback.format_exc()
                        self.logger.error(f"{error_msg}\nTraceback:\n{traceback_str}")
                        stats["errors"] += 1
                        continue
                
                # 컬럼 설명 개선
                columns_query = session.query(DbColumn).filter(
                    (DbColumn.column_comment.is_(None)) | (DbColumn.column_comment == '')
                ).limit(max_columns)
                
                for column in columns_query:
                    try:
                        # LLM을 사용한 컬럼 설명 생성
                        enhanced_comment = self.llm_assist.generate_column_comment(
                            table_name=column.table.table_name if column.table else 'UNKNOWN',
                            column_name=column.column_name,
                            data_type=column.data_type,
                            existing_comment=column.column_comment,
                            context=self._get_column_context(session, column),
                            lang=lang
                        )
                        
                        if enhanced_comment:
                            column.column_comment = enhanced_comment
                            stats["columns_processed"] += 1
                            self.logger.info(f"컬럼 설명 개선 완료: {column.column_name}")
                            
                    except Exception as e:
                        error_msg = f"컬럼 설명 개선 실패 {column.column_name}: {e}"
                        traceback_str = traceback.format_exc()
                        self.logger.error(f"{error_msg}\nTraceback:\n{traceback_str}")
                        stats["errors"] += 1
                        continue
                
                return stats
                
        except Exception as e:
            error_msg = f"LLM 테이블/컬럼 설명 개선 실패: {e}"
            traceback_str = traceback.format_exc()
            self.logger.error(f"{error_msg}\nTraceback:\n{traceback_str}")
            raise

    def llm_summarize_sql_units(self, *, max_items: int = 50, lang: str = 'ko') -> int:
        """
        LLM을 사용하여 SQL 유닛들의 요약 생성
        
        Args:
            max_items: 처리할 최대 항목 수
            lang: 언어 ('ko' 또는 'en')
            
        Returns:
            처리된 항목 수
        """
        try:
            with self._get_sync_session() as session:
                processed = 0
                
                sql_units_query = session.query(SqlUnit).filter(
                    SqlUnit.summary.is_(None)
                ).limit(max_items)
                
                for sql_unit in sql_units_query:
                    try:
                        # LLM을 사용한 SQL 요약 생성
                        summary = self.llm_assist.generate_sql_summary(
                            mapper_ns=sql_unit.mapper_ns,
                            stmt_id=sql_unit.stmt_id,
                            stmt_kind=sql_unit.stmt_kind,
                            sql_content=getattr(sql_unit, 'sql_content', ''),
                            lang=lang
                        )
                        
                        if summary:
                            sql_unit.summary = summary
                            processed += 1
                            self.logger.info(f"SQL 요약 생성 완료: {sql_unit.mapper_ns}.{sql_unit.stmt_id}")
                            
                    except Exception as e:
                        error_msg = f"SQL 요약 생성 실패 {sql_unit.mapper_ns}.{sql_unit.stmt_id}: {e}"
                        traceback_str = traceback.format_exc()
                        self.logger.error(f"{error_msg}\nTraceback:\n{traceback_str}")
                        continue
                
                return processed
                
        except Exception as e:
            error_msg = f"LLM SQL 요약 생성 실패: {e}"
            traceback_str = traceback.format_exc()
            self.logger.error(f"{error_msg}\nTraceback:\n{traceback_str}")
            raise

    def llm_summarize_methods(self, *, max_items: int = 50, lang: str = 'ko') -> int:
        """
        LLM을 사용하여 메소드 요약 생성
        
        Args:
            max_items: 처리할 최대 항목 수
            lang: 언어 ('ko' 또는 'en')
            
        Returns:
            처리된 항목 수
        """
        try:
            with self._get_sync_session() as session:
                processed = 0
                
                methods_query = session.query(Method).filter(
                    Method.summary.is_(None)
                ).limit(max_items)
                
                for method in methods_query:
                    try:
                        # LLM을 사용한 메소드 요약 생성
                        summary = self.llm_assist.generate_method_summary(
                            class_name=method.class_name,
                            method_name=method.method_name,
                            signature=method.signature,
                            body=getattr(method, 'body', ''),
                            lang=lang
                        )
                        
                        if summary:
                            method.summary = summary
                            processed += 1
                            self.logger.info(f"메소드 요약 생성 완료: {method.class_name}.{method.method_name}")
                            
                    except Exception as e:
                        error_msg = f"메소드 요약 생성 실패 {method.class_name}.{method.method_name}: {e}"
                        traceback_str = traceback.format_exc()
                        self.logger.error(f"{error_msg}\nTraceback:\n{traceback_str}")
                        continue
                
                return processed
                
        except Exception as e:
            error_msg = f"LLM 메소드 요약 생성 실패: {e}"
            traceback_str = traceback.format_exc()
            self.logger.error(f"{error_msg}\nTraceback:\n{traceback_str}")
            raise

    def llm_infer_join_keys(self, *, max_items: int = 50) -> int:
        """
        LLM을 사용하여 조인 키 추론
        
        Args:
            max_items: 처리할 최대 항목 수
            
        Returns:
            처리된 항목 수
        """
        try:
            with self._get_sync_session() as session:
                processed = 0
                
                sql_units_query = session.query(SqlUnit).filter(
                    ~session.query(Join.sql_id).filter(Join.sql_id == SqlUnit.sql_id).exists()
                ).limit(max_items)
                
                for sql_unit in sql_units_query:
                    try:
                        # LLM을 사용한 조인 키 추론
                        join_suggestions = self.llm_assist.infer_join_keys(
                            sql_content=getattr(sql_unit, 'sql_content', ''),
                            mapper_ns=sql_unit.mapper_ns,
                            stmt_id=sql_unit.stmt_id
                        )
                        
                        # 추론된 조인 키 저장
                        for suggestion in join_suggestions:
                            join = Join(
                                sql_id=sql_unit.sql_id,
                                l_table=suggestion.get('l_table'),
                                l_col=suggestion.get('l_col'),
                                r_table=suggestion.get('r_table'),
                                r_col=suggestion.get('r_col'),
                                op=suggestion.get('op', '='),
                                confidence=suggestion.get('confidence', 0.5),
                                llm_generated=True
                            )
                            session.add(join)
                        
                        if join_suggestions:
                            processed += 1
                            self.logger.info(f"조인 키 추론 완료: {sql_unit.mapper_ns}.{sql_unit.stmt_id}")
                            
                    except Exception as e:
                        error_msg = f"조인 키 추론 실패 {sql_unit.mapper_ns}.{sql_unit.stmt_id}: {e}"
                        traceback_str = traceback.format_exc()
                        self.logger.error(f"{error_msg}\nTraceback:\n{traceback_str}")
                        continue
                
                return processed
                
        except Exception as e:
            error_msg = f"LLM 조인 키 추론 실패: {e}"
            traceback_str = traceback.format_exc()
            self.logger.error(f"{error_msg}\nTraceback:\n{traceback_str}")
            raise

    def _get_table_context(self, session: Session, table: DbTable) -> str:
        """테이블 컨텍스트 정보 수집"""
        try:
            context_parts = []
            
            # 컬럼 정보
            columns = session.query(DbColumn).filter(DbColumn.table_id == table.table_id).all()
            if columns:
                context_parts.append("컬럼들:")
                for col in columns[:10]:  # 최대 10개까지
                    context_parts.append(f"- {col.column_name} ({col.data_type})")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            self.logger.warning(f"테이블 컨텍스트 수집 실패 {table.table_name}: {e}")
            return ""

    def _get_column_context(self, session: Session, column: DbColumn) -> str:
        """컬럼 컨텍스트 정보 수집"""
        try:
            context_parts = []
            
            # 테이블 정보
            if column.table:
                context_parts.append(f"테이블: {column.table.table_name}")
                if column.table.table_comment:
                    context_parts.append(f"테이블 설명: {column.table.table_comment}")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            self.logger.warning(f"컬럼 컨텍스트 수집 실패 {column.column_name}: {e}")
            return ""