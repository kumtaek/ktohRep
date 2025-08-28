"""
Metadata enhancement engine for resolving edge hints and improving graph completeness.
Implements the enhancement strategies described in the visualization implementation plan.
"""

import json
import re
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session

from ..models.database import (
    EdgeHint, Edge, Method, Class, File, SqlUnit, Join, RequiredFilter, Project
)
from ..utils.logger import get_logger

logger = get_logger(__name__)


class MetadataEnhancementEngine:
    """Engine for enhancing metadata using edge hints and various resolution strategies"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def enhance_project_metadata(self, project_id: int) -> Dict[str, Any]:
        """Enhance metadata for a specific project"""
        logger.info(f"Starting metadata enhancement for project {project_id}")
        
        stats = {
            'method_calls_resolved': 0,
            'includes_resolved': 0,
            'mybatis_includes_resolved': 0,
            'sql_joins_enhanced': 0,
            'total_hints_processed': 0,
            'total_edges_created': 0
        }
        
        # 1. Resolve method calls
        method_call_stats = self._resolve_method_calls(project_id)
        stats.update(method_call_stats)
        
        # 2. Resolve JSP includes
        include_stats = self._resolve_jsp_includes(project_id)
        stats.update(include_stats)
        
        # 3. Resolve MyBatis includes
        mybatis_stats = self._resolve_mybatis_includes(project_id)
        stats.update(mybatis_stats)
        
        # 4. Enhance SQL joins
        join_stats = self._enhance_sql_joins(project_id)
        stats.update(join_stats)
        
        logger.info(f"Metadata enhancement completed for project {project_id}: {stats}")
        return stats
    
    def _resolve_method_calls(self, project_id: int) -> Dict[str, int]:
        """Resolve method call hints into actual edges"""
        logger.info(f"Resolving method calls for project {project_id}")
        
        hints = self.session.query(EdgeHint).filter(
            and_(
                EdgeHint.project_id == project_id,
                EdgeHint.hint_type == 'method_call'
            )
        ).all()
        
        resolved_count = 0
        edges_created = 0
        
        for hint in hints:
            try:
                data = json.loads(hint.hint)
                called_name = data.get('called_name', '').strip()
                arg_count = int(data.get('arg_count', 0))
                line_number = data.get('line')
                
                if not called_name:
                    continue
                
                # Get source method
                src_method = self.session.query(Method).filter(
                    Method.method_id == hint.src_id
                ).first()
                
                if not src_method:
                    continue
                
                # Find target method using resolution strategy
                target_method = self._find_target_method(src_method, called_name, arg_count, project_id)
                
                if target_method:
                    # Create edge
                    confidence = min(1.0, hint.confidence + 0.2)
                    edge = Edge(
                        src_type='method',
                        src_id=hint.src_id,
                        dst_type='method', 
                        dst_id=target_method.method_id,
                        edge_kind='call',
                        confidence=confidence
                    )
                    self.session.add(edge)
                    edges_created += 1
                    resolved_count += 1
                    
                    logger.debug(f"Resolved method call: {src_method.name} -> {target_method.name}")
                else:
                    # Create unresolved edge with lower confidence
                    edge = Edge(
                        src_type='method',
                        src_id=hint.src_id,
                        dst_type='method',
                        dst_id=None,
                        edge_kind='call_unresolved',
                        confidence=max(0.1, hint.confidence - 0.3)
                    )
                    self.session.add(edge)
                    edges_created += 1
                
                # Remove processed hint
                self.session.delete(hint)
                
            except Exception as e:
                logger.warning(f"Error processing method call hint {hint.hint_id}: {e}")
        
        self.session.commit()
        
        return {
            'method_calls_resolved': resolved_count,
            'method_call_edges_created': edges_created,
            'method_call_hints_processed': len(hints)
        }
    
    def _find_target_method(self, src_method: Method, called_name: str, 
                           arg_count: int, project_id: int) -> Optional[Method]:
        """Find target method using resolution hierarchy"""
        
        # Get source class
        src_class = self.session.query(Class).filter(
            Class.class_id == src_method.class_id
        ).first()
        
        if not src_class:
            return None
        
        # Strategy 1: Same class
        candidates = self.session.query(Method).filter(
            and_(
                Method.class_id == src_class.class_id,
                Method.name == called_name
            )
        ).all()
        
        method = self._choose_best_overload(candidates, arg_count)
        if method:
            return method
        
        # Strategy 2: Same package
        if src_class.fqn:
            package = src_class.fqn.rsplit('.', 1)[0]
            candidates = (
                self.session.query(Method)
                .join(Class)
                .join(File)
                .filter(
                    and_(
                        Method.name == called_name,
                        Class.fqn.like(f"{package}.%"),
                        File.project_id == project_id
                    )
                )
                .all()
            )
            
            method = self._choose_best_overload(candidates, arg_count)
            if method:
                return method
        
        # Strategy 3: Global search in project
        candidates = (
            self.session.query(Method)
            .join(Class)
            .join(File)
            .filter(
                and_(
                    Method.name == called_name,
                    File.project_id == project_id
                )
            )
            .all()
        )
        
        return self._choose_best_overload(candidates, arg_count)
    
    def _choose_best_overload(self, candidates: List[Method], arg_count: int) -> Optional[Method]:
        """Choose best method overload based on argument count"""
        if not candidates:
            return None
        
        # Score candidates based on parameter count match
        scored_candidates = []
        for method in candidates:
            param_count = self._extract_param_count(method.signature)
            score = 0
            
            # Exact match gets highest score
            if param_count == arg_count:
                score = 10
            # Close match gets lower score
            elif abs(param_count - arg_count) <= 1:
                score = 5
            # Any match gets minimal score
            else:
                score = 1
            
            scored_candidates.append((score, method))
        
        # Sort by score and return best match
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        return scored_candidates[0][1]
    
    def _extract_param_count(self, signature: str) -> int:
        """Extract parameter count from method signature"""
        if not signature:
            return 0
        
        try:
            # Find parameter section in parentheses
            start = signature.find('(')
            end = signature.rfind(')')
            if start == -1 or end == -1:
                return 0
            
            param_section = signature[start + 1:end].strip()
            if not param_section:
                return 0
            
            # Count parameters by comma separation
            return param_section.count(',') + 1
            
        except Exception:
            return 0
    
    def _resolve_jsp_includes(self, project_id: int) -> Dict[str, int]:
        """Resolve JSP include hints"""
        logger.info(f"Resolving JSP includes for project {project_id}")
        
        hints = self.session.query(EdgeHint).filter(
            and_(
                EdgeHint.project_id == project_id,
                EdgeHint.hint_type == 'jsp_include'
            )
        ).all()
        
        resolved_count = 0
        edges_created = 0
        
        for hint in hints:
            try:
                data = json.loads(hint.hint)
                target_file = data.get('target_file', '').replace('\\', '/')
                
                if not target_file:
                    continue
                
                # Find target file
                target = self.session.query(File).filter(
                    and_(
                        File.project_id == project_id,
                        File.path.like(f"%{target_file}")
                    )
                ).first()
                
                if target:
                    edge = Edge(
                        src_type='file',
                        src_id=hint.src_id,
                        dst_type='file',
                        dst_id=target.file_id,
                        edge_kind='include',
                        confidence=hint.confidence
                    )
                    self.session.add(edge)
                    edges_created += 1
                    resolved_count += 1
                
                self.session.delete(hint)
                
            except Exception as e:
                logger.warning(f"Error processing JSP include hint {hint.hint_id}: {e}")
        
        self.session.commit()
        
        return {
            'includes_resolved': resolved_count,
            'include_edges_created': edges_created,
            'include_hints_processed': len(hints)
        }
    
    def _resolve_mybatis_includes(self, project_id: int) -> Dict[str, int]:
        """Resolve MyBatis include hints"""
        logger.info(f"Resolving MyBatis includes for project {project_id}")
        
        hints = self.session.query(EdgeHint).filter(
            and_(
                EdgeHint.project_id == project_id,
                EdgeHint.hint_type == 'mybatis_include'
            )
        ).all()
        
        resolved_count = 0
        edges_created = 0
        
        for hint in hints:
            try:
                data = json.loads(hint.hint)
                refid = data.get('refid', '')
                namespace = data.get('namespace', '')
                
                if not refid:
                    continue
                
                # Find target SQL fragment
                target_sql = self.session.query(SqlUnit).join(File).filter(
                    and_(
                        File.project_id == project_id,
                        SqlUnit.stmt_id == refid,
                        or_(
                            SqlUnit.mapper_ns == namespace,
                            namespace == ''  # Allow empty namespace for same-file references
                        )
                    )
                ).first()
                
                if target_sql:
                    edge = Edge(
                        src_type='sql_unit',
                        src_id=hint.src_id,
                        dst_type='sql_unit',
                        dst_id=target_sql.sql_id,
                        edge_kind='mybatis_include',
                        confidence=hint.confidence
                    )
                    self.session.add(edge)
                    edges_created += 1
                    resolved_count += 1
                
                self.session.delete(hint)
                
            except Exception as e:
                logger.warning(f"Error processing MyBatis include hint {hint.hint_id}: {e}")
        
        self.session.commit()
        
        return {
            'mybatis_includes_resolved': resolved_count,
            'mybatis_edges_created': edges_created,
            'mybatis_hints_processed': len(hints)
        }
    
    def _enhance_sql_joins(self, project_id: int) -> Dict[str, int]:
        """Enhance SQL joins with PK/FK validation and confidence adjustment"""
        logger.info(f"Enhancing SQL joins for project {project_id}")
        
        joins = (
            self.session.query(Join)
            .join(SqlUnit)
            .join(File)
            .filter(File.project_id == project_id)
            .all()
        )
        
        enhanced_count = 0
        
        # Group joins by table pair for composite key analysis
        from collections import defaultdict
        table_pairs = defaultdict(list)
        
        for join in joins:
            if join.l_table and join.r_table:
                key = (join.l_table.upper(), join.r_table.upper())
                table_pairs[key].append(join)
        
        for (left_table, right_table), join_list in table_pairs.items():
            is_composite = len(join_list) >= 2
            
            for join in join_list:
                original_confidence = join.confidence
                
                # Validate PK/FK relationship
                left_is_pk, right_is_pk = self._validate_pk_fk(
                    join.l_table, join.l_col, join.r_table, join.r_col
                )
                
                # Adjust confidence based on PK/FK status
                new_confidence = original_confidence
                
                if left_is_pk ^ right_is_pk:  # XOR: one side is PK
                    new_confidence = max(new_confidence, 0.85)
                    join.inferred_pkfk = 1
                elif left_is_pk and right_is_pk:  # Both PK (unusual)
                    new_confidence = min(new_confidence, 0.6)
                
                # Boost confidence for composite keys
                if is_composite:
                    new_confidence = min(1.0, new_confidence + 0.05)
                
                if abs(new_confidence - original_confidence) > 0.01:
                    join.confidence = new_confidence
                    enhanced_count += 1
        
        self.session.commit()
        
        return {
            'sql_joins_enhanced': enhanced_count,
            'total_joins_processed': len(joins)
        }
    
    def _validate_pk_fk(self, l_table: str, l_col: str, r_table: str, r_col: str) -> Tuple[bool, bool]:
        """Validate if columns are primary keys"""
        from ..models.database import DbTable, DbPk
        
        def is_primary_key(table_name: str, column_name: str) -> bool:
            if '.' in table_name:
                owner, table = table_name.split('.', 1)
            else:
                owner, table = '', table_name
            
            db_table = self.session.query(DbTable).filter(
                and_(
                    DbTable.table_name == table.upper(),
                    or_(
                        DbTable.owner == owner.upper(),
                        owner == ''
                    )
                )
            ).first()
            
            if not db_table:
                return False
            
            return self.session.query(DbPk).filter(
                and_(
                    DbPk.table_id == db_table.table_id,
                    DbPk.column_name == column_name.upper()
                )
            ).first() is not None
        
        left_is_pk = is_primary_key(l_table, l_col)
        right_is_pk = is_primary_key(r_table, r_col)
        
        return left_is_pk, right_is_pk
    
    def create_edge_hint(self, project_id: int, src_type: str, src_id: int,
                        hint_type: str, hint_data: Dict[str, Any], confidence: float = 0.5) -> EdgeHint:
        """Create a new edge hint"""
        hint = EdgeHint(
            project_id=project_id,
            src_type=src_type,
            src_id=src_id,
            hint_type=hint_type,
            hint=json.dumps(hint_data),
            confidence=confidence
        )
        self.session.add(hint)
        return hint
    
    def get_enhancement_statistics(self, project_id: int) -> Dict[str, Any]:
        """Get statistics about metadata enhancement for a project"""
        
        # Count pending hints
        pending_hints = (
            self.session.query(EdgeHint)
            .filter(EdgeHint.project_id == project_id)
            .count()
        )
        
        # Count edges by type
        edges_by_kind = (
            self.session.query(Edge.edge_kind, func.count(Edge.edge_id))
            .join(File, or_(
                and_(Edge.src_type == 'file', Edge.src_id == File.file_id),
                and_(Edge.dst_type == 'file', Edge.dst_id == File.file_id)
            ))
            .filter(File.project_id == project_id)
            .group_by(Edge.edge_kind)
            .all()
        )
        
        # Count high confidence joins
        high_confidence_joins = (
            self.session.query(Join)
            .join(SqlUnit)
            .join(File)
            .filter(
                and_(
                    File.project_id == project_id,
                    Join.confidence >= 0.8
                )
            )
            .count()
        )
        
        return {
            'pending_hints': pending_hints,
            'edges_by_kind': dict(edges_by_kind),
            'high_confidence_joins': high_confidence_joins,
            'project_id': project_id
        }