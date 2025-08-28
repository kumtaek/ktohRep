"""
Source Analyzer 시각화용 Mermaid/Markdown Exporter

기능 개요
- 다이어그램 데이터(nodes, edges)를 Mermaid 문법으로 변환
- 완전한 Markdown 문서(메타데이터, 범례, Mermaid 코드블록 포함) 생성
- Mermaid 코드만(.mmd/.mermaid 확장자) 단독 추출 지원
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import re


class MermaidExporter:
    """Mermaid 다이어그램/Markdown 내보내기 유틸리티"""

    def __init__(self, label_max: int = 20, erd_cols_max: int = 10):
        self.max_label_length = label_max
        self.erd_cols_max = erd_cols_max
        self.node_id_map: Dict[str, str] = {}
        self.id_counter = 1

    def export_to_markdown(self, data: Dict[str, Any], diagram_type: str,
                           title: str | None = None, metadata: Dict[str, Any] | None = None) -> str:
        """
        Mermaid 코드블록을 포함한 완전한 Markdown 문서 생성

        Args:
            data: 시각화 데이터(dict: nodes, edges)
            diagram_type: 'erd' | 'sequence' | 'graph' | 'component'
            title: 문서 제목(미지정 시 기본값 사용)
            metadata: 추가 메타정보(프로젝트, 필터 등)

        Returns:
            Markdown 문자열 전체(메타/범례/코드블록 포함)
        """
        mermaid_content = self.export_mermaid(data, diagram_type)
        return self._build_markdown_document(mermaid_content, diagram_type, title, data, metadata)

    def export_mermaid(self, data: Dict[str, Any], diagram_type: str) -> str:
        """Mermaid 코드만 생성(.mmd 용)"""
        if diagram_type == 'erd':
            return self._export_erd(data)
        elif diagram_type == 'sequence':
            return self._export_sequence(data)
        elif diagram_type in ['graph', 'component']:
            return self._export_graph(data, diagram_type)
        else:
            raise ValueError(f"Unsupported diagram type: {diagram_type}")

    def _build_markdown_document(self, mermaid_content: str, diagram_type: str,
                                 title: str | None, data: Dict[str, Any],
                                 metadata: Dict[str, Any] | None = None) -> str:
        """메타/범례를 포함한 Markdown 문서 구성"""

        # 기본 제목
        if not title:
            title = f"Source Analyzer {diagram_type.upper()} Diagram"

        # 메타데이터 처리
        meta_info = metadata or {}
        project_id = meta_info.get('project_id', 'Unknown')
        generated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 통계
        node_count = len(data.get('nodes', []))
        edge_count = len(data.get('edges', []))

        # Markdown 본문
        md_lines: List[str] = [
            f"# {title}",
            "",
            "## 개요",
            f"- 프로젝트 ID: {project_id}",
            f"- 다이어그램 유형: {diagram_type.upper()}",
            f"- 생성 시각: {generated_at}",
            f"- 노드 수: {node_count}",
            f"- 엣지 수: {edge_count}",
            ""
        ]

        # 필터 정보
        if meta_info.get('filters'):
            md_lines.extend([
                "## 적용된 필터",
                ""
            ])
            for filter_key, filter_value in meta_info['filters'].items():
                if filter_value:
                    md_lines.append(f"- {filter_key}: {filter_value}")
            md_lines.append("")

        # Mermaid 다이어그램
        md_lines.extend([
            "## 다이어그램",
            "",
            "```mermaid",
            mermaid_content,
            "```",
            "",
            "## 범례",
            ""
        ])

        # 유형별 범례
        legend = self._generate_legend(diagram_type, data)
        md_lines.extend(legend)

        # 원본 데이터(소규모 그래프 한정)
        if node_count < 50:
            md_lines.extend([
                "",
                "## 원본 데이터",
                "",
                "<details>",
                "<summary>원본 데이터를 보려면 클릭</summary>",
                "",
                f"노드 목록 ({node_count})",
                "```json"
            ])
            for node in data.get('nodes', [])[:20]:
                md_lines.append(f"  {node['id']}: {node.get('label', 'N/A')} ({node.get('type', 'unknown')})")
            md_lines.extend([
                "```",
                "",
                f"엣지 목록 ({edge_count})",
                "```json"
            ])
            for edge in data.get('edges', [])[:20]:
                md_lines.append(f"  {edge['source']} -> {edge['target']} ({edge.get('kind', 'unknown')})")
            md_lines.extend([
                "```",
                "",
                "</details>"
            ])

        md_lines.extend([
            "",
            "---",
            f"*Source Analyzer v1.1 — 생성 시각: {generated_at}*"
        ])

        return "\n".join(md_lines)

    def _generate_legend(self, diagram_type: str, data: Dict[str, Any]) -> List[str]:
        """다이어그램 유형/데이터 기반 범례 생성"""
        legend: List[str] = []

        if diagram_type == 'erd':
            legend.extend([
                "### ERD 범례",
                "- 실선: 외래키 관계(높은 신뢰도)",
                "- 점선: 추론된 조인 관계",
                "- 굵은 글자: PK 컬럼",
                "- [REQ] 마크: SQLERD 모드의 필수 필터 컬럼"
            ])

        elif diagram_type == 'sequence':
            legend.extend([
                "### 시퀀스 범례",
                "- 실선 화살표: 해석된 메소드 호출",
                "- 점선 화살표: 미해석 호출",
                "- 숫자: 호출 순서"
            ])

        elif diagram_type in ['graph', 'component']:
            edge_types = {edge.get('kind', 'unknown') for edge in data.get('edges', [])}
            legend.extend([
                f"### {diagram_type.title()} 범례",
                ""
            ])
            edge_descriptions = {
                'call': '메소드 호출',
                'use_table': 'DB 테이블 사용',
                'include': '파일 include/import',
                'extends': '상속',
                'implements': '인터페이스 구현',
                'call_unresolved': '미해석 호출(점선)'
            }
            for edge_type in sorted(edge_types):
                desc = edge_descriptions.get(edge_type, edge_type.replace('_', ' ').title())
                legend.append(f"- {edge_type}: {desc}")

        return legend

    def _sanitize_id(self, original_id: str) -> str:
        """Mermaid에서 안전한 ID로 변환"""
        if original_id in self.node_id_map:
            return self.node_id_map[original_id]
        safe = re.sub(r'[^a-zA-Z0-9_]', '_', original_id)
        safe_id = f"n{self.id_counter}_{safe[:10]}"
        self.node_id_map[original_id] = safe_id
        self.id_counter += 1
        return safe_id

    def _sanitize_label(self, label: str) -> str:
        """Mermaid 표시용 라벨 정제"""
        if not label:
            return "Unknown"
        clean = re.sub(r'["|\'`]', '', label)
        if len(clean) > self.max_label_length:
            clean = clean[: self.max_label_length - 3] + '...'
        return clean

    def _export_erd(self, data: Dict[str, Any]) -> str:
        """ERD 데이터를 Mermaid erDiagram 문법으로 변환"""
        lines: List[str] = ["erDiagram"]

        tables_processed: set[str] = set()
        for node in data.get('nodes', []):
            if node.get('type') == 'table':
                table_id = self._sanitize_id(node['id'])
                meta = node.get('meta', {})
                columns = meta.get('columns', [])

                if columns:
                    lines.append(f"  {table_id} {{")
                    for col in columns[: self.erd_cols_max]:
                        col_name = col.get('name', 'unknown')
                        col_type = col.get('data_type', 'VARCHAR')
                        pk_mark = ' PK' if col.get('is_pk') else ''
                        filter_mark = ' "REQ"' if col.get('is_filtered') else ''
                        lines.append(f"    {col_type} {col_name}{pk_mark}{filter_mark}")
                    lines.append("  }")
                else:
                    lines.append(f"  {table_id} {{")
                    lines.append("    varchar id PK")
                    lines.append("  }")

                tables_processed.add(table_id)

        # 관계선
        for edge in data.get('edges', []):
            src_id = self._sanitize_id(edge['source'])
            dst_id = self._sanitize_id(edge['target'])
            if src_id in tables_processed and dst_id in tables_processed:
                edge_kind = edge.get('kind', 'unknown')
                if edge_kind in ['fk_inferred', 'join_inferred']:
                    rel_type = '||--o{'
                else:
                    rel_type = '||--||'
                lines.append(f"  {src_id} {rel_type} {dst_id} : \"{edge_kind}\"")

        return "\n".join(lines)

    def _export_sequence(self, data: Dict[str, Any]) -> str:
        """시퀀스 데이터를 Mermaid sequenceDiagram 문법으로 변환"""
        lines: List[str] = ["sequenceDiagram"]

        participants: set[tuple[str, str]] = set()
        for edge in data.get('edges', []):
            src_node = self._find_node_by_id(data, edge['source'])
            dst_node = self._find_node_by_id(data, edge['target'])
            if src_node:
                participants.add((edge['source'], src_node.get('label', 'Unknown')))
            if dst_node:
                participants.add((edge['target'], dst_node.get('label', 'Unknown')))

        for node_id, label in sorted(participants):
            safe_id = self._sanitize_id(node_id)
            safe_label = self._sanitize_label(label)
            lines.append(f"  participant {safe_id} as {safe_label}")

        lines.append("")

        for edge in sorted(data.get('edges', []), key=lambda x: x.get('sequence_order', 0)):
            src_id = self._sanitize_id(edge['source'])
            dst_id = self._sanitize_id(edge['target'])
            edge_kind = edge.get('kind', 'call')
            confidence = edge.get('confidence', 1.0)
            if edge_kind == 'call_unresolved':
                arrow = '-->>'
            else:
                arrow = '->>'
            conf_percent = int(confidence * 100)
            label = f"{edge_kind} ({conf_percent}%)"
            lines.append(f"  {src_id}{arrow}{dst_id}: {label}")

        return "\n".join(lines)

    def _export_graph(self, data: Dict[str, Any], diagram_type: str) -> str:
        """의존/컴포넌트 그래프를 Mermaid graph 문법으로 변환"""

        lines: List[str]
        if diagram_type == 'component':
            lines = ["graph TB"]
        else:
            lines = ["graph TD"]

        for node in data.get('nodes', []):
            node_id = self._sanitize_id(node['id'])
            label = self._sanitize_label(node.get('label', ''))
            node_type = node.get('type', 'unknown')
            if node_type == 'table':
                shape = f"{node_id}[({label})]"
            elif node_type == 'method':
                shape = f"{node_id}[{label}]"
            elif node_type == 'component':
                shape = f"{node_id}{{{{ {label} }}}}"
            else:
                shape = f"{node_id}({label})"
            lines.append(f"  {shape}")

        lines.append("")

        for edge in data.get('edges', []):
            src_id = self._sanitize_id(edge['source'])
            dst_id = self._sanitize_id(edge['target'])
            edge_kind = edge.get('kind', 'unknown')
            if 'unresolved' in edge_kind:
                lines.append(f"  {src_id} -. {edge_kind} .-> {dst_id}")
            else:
                lines.append(f"  {src_id} -->|{edge_kind}| {dst_id}")

        lines.extend([
            "",
            "  %% Styling",
            "  classDef table fill:#fff3e0,stroke:#ff9800",
            "  classDef method fill:#e3f2fd,stroke:#2196f3",
            "  classDef component fill:#f3e5f5,stroke:#9c27b0"
        ])

        for node in data.get('nodes', []):
            node_id = self._sanitize_id(node['id'])
            node_type = node.get('type', 'unknown')
            if node_type in ['table', 'method', 'component']:
                lines.append(f"  class {node_id} {node_type}")

        return "\n".join(lines)

    def _find_node_by_id(self, data: Dict[str, Any], node_id: str) -> Optional[Dict[str, Any]]:
        """ID로 노드를 조회"""
        for node in data.get('nodes', []):
            if node['id'] == node_id:
                return node
        return None
