# final_review2.md 개선 리포트 (대상: firnal_review2.md)

- 대상 문서: `firnal_review2.md` (오탈자 추정: ‘final’ → ‘firnal’). 현재 리포 내 실사용 파일이 `firnal_review2.md`이므로 이를 기준으로 개선안을 제시합니다.
- 개선 가능 여부: 가능. 문서 구조 정리 + 코드 근거 강화 + 개선 스니펫을 포함해 실효성을 높일 수 있습니다.
- 판단 근거: 문서의 권고사항이 실제 코드의 미완성/간소화 지점과 일치합니다(예: Tree-sitter 메타데이터 부족, JOIN/WHERE 파싱 단순화, 호출관계 해결 한계, 로깅 불일치). 또한 현재는 “그린필드(백지)에서 최초 개발” 전제이므로, 마이그레이션 제약 없이 스키마/설계를 최적화할 수 있습니다.


## 1) 문서 구조/내용 개선안

- 제목·요약 정리: 문서 상단에 목적/범위/주요 결론(Top 3)을 명확히 표기.
- 증거 기반 진술: 각 항목에 코드 경로·함수명·핵심 라인 근거를 붙여 재현 가능한 상태로 기술.
- 실행 가능한 액션: “무엇을, 어디에, 어떻게”까지 포함한 체크리스트화.
- 경로 표기 정규화: 절대경로(`E:\\...`) 대신 리포 상대경로(`phase1/src/...`) 사용.
- 용어·형식 일관화: 섹션 헤더(H2/H3), 리스트 스타일, 코드펜스 등 Markdown 규칙 통일.

예시(문서 서두 교체 제안):

```
# Source Analyzer 최종 리뷰 v2 (개선 제안)

- 목적: 핵심 파서/엔진의 정확도·일관성 점검 및 우선 개선안 제시
- 범위: java_parser.py, jsp_mybatis_parser.py, metadata_engine.py, 관련 DB 모델
- 결론(Top 3):
  1) Tree-sitter 경로에서 클래스/메서드 메타데이터 상세도 보강
  2) 메서드 호출관계의 ‘미해결 엣지’ 저장·해결 루프 강화
  3) SQL JOIN/WHERE 파싱 고도화로 테이블/필터 정확도 개선
```

각 이슈 서술 형식(샘플):

```
## [I-1] Tree-sitter 메타데이터 상세도 부족
- 근거: phase1/src/parsers/java_parser.py (`_extract_*_from_tree_sitter`)에 FQN/수식어/반환타입/시그니처가 placeholder로 남아있음
- 영향: 클래스/메서드 식별 정확도 및 호출관계·요약 품질 저하
- 조치: 섹션 2-A 스니펫 적용(패키지/FQN/수식어/반환타입 추출 보강)
- 완료 기준: Tree-sitter 경로에서도 Javalang 경로와 동등 수준의 메타데이터 확보
```


## 2) 코드 레벨 개선안 및 스니펫

아래 스니펫은 권고사항을 실행 가능한 수준으로 구체화한 것입니다. 실제 반영은 해당 파일에 부분 패치 형태로 적용하세요.

### 2-A. Java 파서(Tree-sitter) 메타데이터 상세도 향상

문제: Tree-sitter 경로에서 클래스 FQN/수식어/어노테이션, 메서드 시그니처/반환타입이 기본값/placeholder로 남아있음.

핵심 개선:
- 패키지 선언(`package_declaration`) 탐색으로 FQN 구성
- `modifiers`, `annotation` 노드 탐색으로 수식어/어노테이션 채움
- 메서드의 `type`/`formal_parameters` 파싱으로 반환타입/시그니처 채움

스니펫(발췌, `phase1/src/parsers/java_parser.py`):

```diff
--- a/phase1/src/parsers/java_parser.py
+++ b/phase1/src/parsers/java_parser.py
@@
 class JavaParser:
     def __init__(self, config: Dict[str, Any]):
 +        from ..utils.logger import LoggerFactory
 +        self.logger = LoggerFactory.get_parser_logger("java")
@@
 -            except Exception as e:
 -                print(f"Tree-sitter 초기화 실패: {e}")
 +            except Exception as e:
 +                self.logger.warning(f"Tree-sitter 초기화 실패: {e}")
@@
 -            except Exception as e:
 -                print(f"파일 파싱 실패 {file_path}: {e}")
 +            except Exception as e:
 +                self.logger.error(f"파일 파싱 실패: {file_path}", exception=e)
                 return file_obj, [], [], []
@@
 -        except Exception as e:
 -            print(f"Error parsing file {file_path}: {e}")
 +        except Exception as e:
 +            self.logger.error(f"Java 파싱 중 오류: {file_path}", exception=e)
             return file_obj, [], [], []
@@
     def _extract_with_tree_sitter(self, tree, file_obj: File, content: str) -> Tuple[List[Class], List[Method], List[Edge]]:
@@
 -        # 클래스 선언 찾기
 +        # 패키지명 추출
 +        pkg_nodes = self._find_nodes_by_type(tree.root_node, 'package_declaration')
 +        package_name = None
 +        if pkg_nodes:
 +            ident = self._find_nodes_by_type(pkg_nodes[0], 'scoped_identifier') or 
 +                    self._find_nodes_by_type(pkg_nodes[0], 'identifier')
 +            if ident:
 +                package_name = self._get_node_text(ident[0], lines)
 +
 +        # 클래스 선언 찾기
         class_nodes = self._find_nodes_by_type(tree.root_node, 'class_declaration')
         for class_node in class_nodes:
 -            class_obj, class_methods, class_edges = self._extract_class_from_tree_sitter(
 -                class_node, file_obj, lines
 -            )
 +            class_obj, class_methods, class_edges = self._extract_class_from_tree_sitter(
 +                class_node, file_obj, lines, package_name
 +            )
@@
 -    def _extract_class_from_tree_sitter(self, class_node, file_obj: File, lines: List[str]) -> Tuple[Optional[Class], List[Method], List[Edge]]:
 +    def _extract_class_from_tree_sitter(self, class_node, file_obj: File, lines: List[str], package_name: Optional[str] = None) -> Tuple[Optional[Class], List[Method], List[Edge]]:
@@
 -            class_obj = Class(
 +            fqn = f"{package_name}.{class_name}" if package_name else class_name
 +            class_obj = Class(
                 file_id=None,
 -                fqn=class_name,  # 더 정교하게 배포 정보를 추얤야 함
 +                fqn=fqn,
                 name=class_name,
                 start_line=start_line,
                 end_line=end_line,
 -                modifiers=json.dumps([]),  # Tree-sitter에서 modifier 추출 어려움
 -                annotations=json.dumps([])
 +                modifiers=json.dumps(self._extract_modifiers(class_node, lines)),
 +                annotations=json.dumps(self._extract_annotations_ts(class_node, lines))
             )
@@
 -            method_obj = Method(
 +            # 반환 타입
 +            ret_nodes = [c for c in method_node.children if c.type == 'type']
 +            return_type = self._get_node_text(ret_nodes[0], lines) if ret_nodes else 'void'
 +            # 파라미터 시그니처
 +            params = []
 +            for plist in [c for c in method_node.children if c.type == 'formal_parameters']:
 +                for p in self._find_nodes_by_type(plist, 'formal_parameter'):
 +                    tnode = self._find_nodes_by_type(p, 'type')
 +                    pname = self._find_nodes_by_type(p, 'identifier')
 +                    if tnode and pname:
 +                        params.append(f"{self._get_node_text(tnode[0], lines)} {self._get_node_text(pname[0], lines)}")
 +            signature = f"{method_name}({', '.join(params)})"
 +
 +            method_obj = Method(
                 class_id=None,  # 나중에 설정
                 name=method_name,
 -                signature=method_name,  # 더 정교하게 시그니처 추출 필요
 +                signature=signature,
                 start_line=start_line,
                 end_line=end_line,
 -                return_type='unknown',  # Tree-sitter에서 반환 타입 추출 어려움
 +                return_type=return_type,
                 parameters='',
                 modifiers=json.dumps([])
             )
@@
 -        except Exception as e:
 -            print(f"Tree-sitter 메서드 추출 오류: {e}")
 +        except Exception as e:
 +            self.logger.error("Tree-sitter 메서드 추출 오류", exception=e)
             return None, []
 +
 +    def _extract_modifiers(self, node, lines: List[str]) -> List[str]:
 +        mods = []
 +        for child in node.children:
 +            if child.type == 'modifiers':
 +                for m in child.children:
 +                    if m.type.endswith('modifier') or m.type == 'annotation':
 +                        mods.append(self._get_node_text(m, lines))
 +        return mods
 +
 +    def _extract_annotations_ts(self, node, lines: List[str]) -> List[str]:
 +        ann = []
 +        for a in self._find_nodes_by_type(node, 'annotation'):
 +            ann.append(self._get_node_text(a, lines))
 +        return ann
```


### 2-B. 로깅 일원화 (`print` 제거)

문제: 일부 파서에서 `print` 사용. 로깅 시스템(`LoggerFactory`)로 통일 필요.

스니펫(발췌): 위 2-A diff처럼 `print` → `self.logger.*` 대체. `jsp_mybatis_parser.py`도 기본 로거 주입이 없으면 팩토리 사용.

```diff
--- a/phase1/src/parsers/jsp_mybatis_parser.py
+++ b/phase1/src/parsers/jsp_mybatis_parser.py
@@
 -        self.logger = config.get('logger')
 +        self.logger = config.get('logger')
 +        if not self.logger:
 +            from ..utils.logger import LoggerFactory
 +            self.logger = LoggerFactory.get_parser_logger("jsp_mybatis")
```


### 2-C. ‘미해결 호출관계’ 저장·해결 루프 보강

문제:
- 파서가 생성한 call 엣지(dst_id=None)가 저장 단계에서 걸러지면(미저장) `_resolve_method_calls`가 처리할 대상이 사라짐
- 호출 메서드명 등 힌트를 엣지에 보존하는 메커니즘 부재(그린필드에서는 엣지에 JSON 메타데이터 컬럼을 추가 권장)

핵심 개선:
- 저장 단계에서 dst_id가 없어도 ‘call’ 엣지는 저장
- 파서에서 ‘호출된 메서드명’을 힌트로 전달
- 그린필드 권장: `edges.metadata`(JSON) 컬럼을 도입해 힌트를 엣지에 직접 저장(2-F 참고). 기존 코드 호환이 필요하면 `EdgeHint` 테이블을 보조적으로 사용할 수 있음.

스니펫(1) 파서가 호출명 힌트 싣기(`java_parser.py`):

```diff
--- a/phase1/src/parsers/java_parser.py
+++ b/phase1/src/parsers/java_parser.py
@@
 -            method_calls = self._extract_method_calls(node.body)
 -            for call in method_calls:
 +            method_calls = self._extract_method_calls(node.body)
 +            for called_name in method_calls:
                 call_edge = Edge(
                     src_type='method',
                     src_id=None,  # Will be set after method is saved
                     dst_type='method',
                     dst_id=None,  # Need to resolve later
                     edge_kind='call',
                     confidence=0.8  # 메서드 호출은 대체로 명확함
                 )
 +                # 메타데이터(JSON) 또는 보조 힌트로 저장
 +                try:
 +                    import json as _json
 +                    setattr(call_edge, 'metadata', _json.dumps({ 'called_name': called_name }))
 +                except Exception:
 +                    setattr(call_edge, 'called_method_name', called_name)
                 edges.append(call_edge)
```

스니펫(2) 저장 로직에서 ‘미해결 엣지’도 저장 + 힌트 기록(`metadata_engine.py`):

```diff
--- a/phase1/src/database/metadata_engine.py
+++ b/phase1/src/database/metadata_engine.py
@@
 -            # 의존성 엣지 저장 (유효한 엣지만)
 +            # 의존성 엣지 저장: call 엣지는 dst 미해결 상태도 저장하여 후처리 대상이 되도록 함
             confidence_threshold = self.config.get('processing', {}).get('confidence_threshold', 0.5)
             for edge in edges:
                 # 최소 요건: src_id가 결정되어야 저장 가능 → 아래에서 method 저장 이후 src_id 세팅 필요
                 if edge.edge_kind == 'call':
                     session.add(edge)  # dst_id 없어도 저장
 +                    # Edge.metadata(JSON) 사용 권장, 없다면 EdgeHint에 기록
 +                    try:
 +                        getattr(edge, 'metadata')
 +                    except Exception:
 +                        from ..models.database import EdgeHint
 +                        if hasattr(edge, 'called_method_name') and edge.src_id:
 +                            import json as _json
 +                            hint = EdgeHint(
 +                                project_id=file_obj.project_id,
 +                                src_type='method',
 +                                src_id=edge.src_id,
 +                                hint_type='method_call',
 +                                hint=_json.dumps({ 'called_name': getattr(edge, 'called_method_name') }),
 +                                confidence=max(0.3, min(0.8, edge.confidence))
 +                            )
 +                            session.add(hint)
                     saved_counts['edges'] += 1
                 else:
                     if (edge.src_id is not None and edge.dst_id is not None 
                         and edge.src_id != 0 and edge.dst_id != 0
                         and edge.confidence >= confidence_threshold):
                         session.add(edge)
                         saved_counts['edges'] += 1
```

스니펫(3) 호출관계 해결 시 `Edge.metadata` 또는 `EdgeHint` 참조(`metadata_engine.py`):

```diff
--- a/phase1/src/database/metadata_engine.py
+++ b/phase1/src/database/metadata_engine.py
@@
     async def _resolve_method_calls(self, session, project_id: int):
@@
 -                    called_method_name = getattr(edge, 'metadata', {}).get('called_method_name', '')
 +                    called_method_name = ''
 +                    # 1) Edge.metadata(JSON) 우선 사용
 +                    try:
 +                        if getattr(edge, 'metadata', None):
 +                            md = _json.loads(edge.metadata)
 +                            called_method_name = md.get('called_name', '')
 +                    except Exception:
 +                        called_method_name = ''
 +                    # 2) EdgeHint 보조 사용(레거시/백업 경로)
 +                    if not called_method_name:
 +                        hint_row = session.query(EdgeHint).filter(
 +                            and_(
 +                                EdgeHint.project_id == project_id,
 +                                EdgeHint.src_type == 'method',
 +                                EdgeHint.src_id == src_method.method_id,
 +                                EdgeHint.hint_type == 'method_call'
 +                            )
 +                        ).order_by(EdgeHint.created_at.desc()).first()
 +                        if hint_row:
 +                            try:
 +                                called_method_name = _json.loads(hint_row.hint).get('called_name', '')
 +                            except Exception:
 +                                called_method_name = ''
```

보충 권장: 메서드 저장 직후 해당 메서드에서 생성된 call 엣지들의 `src_id`를 채우는 루틴을 추가하세요.


### 2-D. 메서드→클래스 ID 매핑의 견고화

문제: `_save_java_analysis_sync`에서 메서드의 `class_id`를 리스트 분할로 할당 → 클래스/메서드 수 불균형 시 오할당.

핵심 개선:
- 파서 단계에서 임시 속성 `owner_fqn`을 메서드에 부여하고, 저장 단계에서 클래스 FQN과 매칭하여 `class_id` 설정.

스니펫(1) 파서에서 `owner_fqn` 부여:

```diff
--- a/phase1/src/parsers/java_parser.py
+++ b/phase1/src/parsers/java_parser.py
@@
         method_obj = Method(
             class_id=None,
             name=node.name,
             signature=signature,
             return_type=return_type,
             start_line=start_line,
             end_line=end_line,
             annotations=json.dumps(annotations)
         )
 +        # 저장 단계 매핑용 임시 속성
 +        setattr(method_obj, 'owner_fqn', class_obj.fqn)
```

스니펫(2) 저장에서 FQN 매칭(`metadata_engine.py`):

```diff
--- a/phase1/src/database/metadata_engine.py
+++ b/phase1/src/database/metadata_engine.py
@@
 -            for class_obj in classes:
 +            # 클래스 저장 및 FQN→ID 매핑 테이블 생성
 +            fqn_to_class_id = {}
 +            for class_obj in classes:
                 class_obj.file_id = file_obj.file_id
                 session.add(class_obj)
                 session.flush()
 +                if class_obj.fqn:
 +                    fqn_to_class_id[class_obj.fqn] = class_obj.class_id
@@
 -                class_methods = [m for m in methods if m.class_id is None]  # 임시로 None인 것들
 -                for method_obj in class_methods[:len(class_methods)//len(classes) if classes else 0]:
 -                    method_obj.class_id = class_obj.class_id
 -                    session.add(method_obj)
 +                class_methods = [m for m in methods if getattr(m, 'owner_fqn', None) == class_obj.fqn]
 +                for method_obj in class_methods:
 +                    method_obj.class_id = class_obj.class_id
 +                    session.add(method_obj)
 +                    session.flush()
 +                    # 메서드 기원 엣지의 src_id 채우기(호출관계 저장용)
 +                    for e in [e for e in edges if e.src_type == 'method' and e.src_id is None]:
 +                        e.src_id = method_obj.method_id
```


### 2-E. SQL JOIN/WHERE 파싱 고도화

문제: `_parse_join_condition`/`_parse_where_conditions`가 “간단 구현” 상태.

핵심 개선:
- `sqlparse` 토큰을 문자열로 평탄화 후 정규식 기반 1차 추출
- 테이블/컬럼/연산자 분리, 스키마 정규화 적용
- WHERE는 AND로 분리, `table.col op value` 패턴 위주 보강(파라미터·리터럴 포함)

스니펫(`phase1/src/parsers/jsp_mybatis_parser.py`):

```diff
--- a/phase1/src/parsers/jsp_mybatis_parser.py
+++ b/phase1/src/parsers/jsp_mybatis_parser.py
@@
     def _parse_join_condition(self, tokens) -> Optional[Join]:
 -        """JOIN 조건 파싱 (간단 구현)"""
 -        # 실제 구현은 더 복잡해야 함
 -        return None
 +        """JOIN 조건 파싱 (정규식 기반 1차 고도화)"""
 +        try:
 +            text = sqlparse.sql.TokenList(tokens).value if hasattr(sqlparse.sql, 'TokenList') else str(tokens)
 +            text = re.sub(r"\s+", " ", text)
 +            m = re.search(r"([\w\.]+)\s*\.\s*(\w+)\s*(=|!=|>=|<=|<>|<|>)\s*([\w\.]+)\s*\.\s*(\w+)", text, re.I)
 +            if not m:
 +                return None
 +            l_table_raw, l_col, op, r_table_raw, r_col = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
 +            j = Join(
 +                sql_id=None,
 +                l_table=self._normalize_table_name(l_table_raw),
 +                l_col=l_col,
 +                op=op,
 +                r_table=self._normalize_table_name(r_table_raw),
 +                r_col=r_col,
 +                confidence=0.8
 +            )
 +            return j
 +        except Exception as e:
 +            if self.logger:
 +                self.logger.debug(f"JOIN 파싱 실패: {e}")
 +            return None
@@
     def _parse_where_conditions(self, tokens) -> List[RequiredFilter]:
 -        """WHERE 조건 파싱 (간단 구현)"""
 -        # 실제 구현은 더 복잡해야 함
 -        return []
 +        """WHERE 조건 파싱 (정규식 기반 1차 고도화)"""
 +        results: List[RequiredFilter] = []
 +        try:
 +            text = sqlparse.sql.TokenList(tokens).value if hasattr(sqlparse.sql, 'TokenList') else str(tokens)
 +            # 조건 분할(단순 AND 분해)
 +            parts = re.split(r"\bAND\b", text, flags=re.I)
 +            for p in parts:
 +                p = p.strip()
 +                if not p:
 +                    continue
 +                # table.col op value
 +                m = re.search(r"([\w\.]+)\s*\.\s*(\w+)\s*(=|!=|>=|<=|<>|<|>|LIKE)\s*(.+)$", p, re.I)
 +                if not m:
 +                    continue
 +                t_raw, col, op, rhs = m.group(1), m.group(2), m.group(3).upper(), m.group(4).strip()
 +                # 값 표현 정규화(:param, #{}, ${}, 'N', 숫자 등)
 +                rhs = re.sub(r":\w+", ":PARAM", rhs)
 +                rhs = re.sub(r"#\{[^}]+\}", "#{PARAM}", rhs)
 +                rhs = re.sub(r"\$\{[^}]+\}", "${PARAM}", rhs)
 +                # 리터럴 따옴표 제거(보수적으로)
 +                rhs = rhs.strip().strip("'\"")
 +                results.append(RequiredFilter(
 +                    sql_id=None,
 +                    table_name=self._normalize_table_name(t_raw),
 +                    column_name=col,
 +                    op=op,
 +                    value_repr=rhs,
 +                    always_applied=0,
 +                    confidence=0.7
 +                ))
 +        except Exception as e:
 +            if self.logger:
 +                self.logger.debug(f"WHERE 파싱 실패: {e}")
 +        return results
```


### 2-F. 스키마(그린필드) 확장안 — 정확도와 일관성을 위한 최소 스키마 추가

그린필드 전제에서는 스키마 확장이 용이하므로, 아래 변경을 권장합니다.

- 목적: 미해결 호출 힌트/파라미터/수식어/인덱스 등을 스키마에 직접 반영해 정확도·성능·일관성 강화
- 변경 요약:
  - `edges.metadata`(JSON) 추가: `called_name`, `arg_count`, `receiver_fqn`, `src_fqn` 등 저장
  - `edges.created_at` 추가 및 인덱스: `(src_type,src_id)`, `(dst_type,dst_id)`, `(edge_kind)`
  - `methods.parameters`, `methods.modifiers` 추가: 파라미터 문자열/수식어 보관
  - (선택) `java_imports` 추가: 파일/클래스 단위 import 목록 보관해 해상도 향상

스니펫(`phase1/src/models/database.py`):

```diff
 class Method(Base):
     __tablename__ = 'methods'
@@
     method_id = Column(Integer, primary_key=True)
     class_id = Column(Integer, ForeignKey('classes.class_id'), nullable=False)
     name = Column(String(255), nullable=False)
     signature = Column(Text)
     return_type = Column(String(255))
     start_line = Column(Integer)
     end_line = Column(Integer)
     annotations = Column(Text)  # JSON array of annotations
 +    parameters = Column(Text)   # JSON or string-joined parameter list
 +    modifiers = Column(Text)    # JSON array of modifiers

 class Edge(Base):
     __tablename__ = 'edges'
@@
     edge_id = Column(Integer, primary_key=True)
     src_type = Column(String(50), nullable=False)  # method, class, sql_unit, etc.
     src_id = Column(Integer, nullable=False)
     dst_type = Column(String(50), nullable=False)
     dst_id = Column(Integer, nullable=True)  # Allow NULL for unresolved edges
     edge_kind = Column(String(50), nullable=False)  # call, use_table, use_column, etc.
     confidence = Column(Float, default=1.0)
 +    metadata = Column(Text)  # JSON: { called_name, arg_count, receiver_fqn, src_fqn, ... }
 +    created_at = Column(DateTime, default=datetime.utcnow)
 +
 +# Recommended indexes (SQLAlchemy Index objects)
 +Index('ix_edges_src', Edge.src_type, Edge.src_id)
 +Index('ix_edges_dst', Edge.dst_type, Edge.dst_id)
 +Index('ix_edges_kind', Edge.edge_kind)

 # (Optional) Java import table to help resolution
 +class JavaImport(Base):
 +    __tablename__ = 'java_imports'
 +    import_id = Column(Integer, primary_key=True)
 +    file_id = Column(Integer, ForeignKey('files.file_id'), nullable=False)
 +    class_fqn = Column(Text)  # imported FQN
 +    static = Column(Integer, default=0)
```

엔진 반영 포인트:
- call 엣지 저장 시 `edge.metadata`에 `{'called_name': ..., 'arg_count': ..., 'receiver_fqn': ...}` 저장
- `_resolve_method_calls`에서 `metadata` 사용해 (동일 클래스 → import/패키지 고려 → 전역) 순으로 매칭, 파라미터 개수/시그니처를 추가 힌트로 사용
- 인덱스 덕에 대규모 프로젝트에서도 탐색 비용 감소


## 3) 우선순위·테스트 가이드

- 우선순위(P1→P3):
  - P1: 2-F(스키마 확장) + 2-C(미해결 호출 저장/해결 루프) + 2-D(메서드→클래스 매핑)
  - P2: 2-A(Tree-sitter 메타데이터 보강) + 2-B(로깅 일원화)
  - P3: 2-E(SQL JOIN/WHERE 파싱 고도화)

- 테스트 포인트:
  - Java 샘플(메서드 호출, 오버로드 포함)로 call 엣지 저장 후 `_resolve_method_calls` 해상도 향상 여부 확인
  - MyBatis/JSP 샘플로 JOIN/WHERE 추출 결과(테이블/컬럼/연산자/값) 검증
  - 로깅 라우팅 및 로그 파일 생성 확인


## 4) 그린필드 전제 하 개선 설계 (마이그레이션 제약 없음)

- 스키마 추가 권장: `edges.metadata`, `methods.parameters/modifiers`, 인덱스 3종, (선택)`java_imports`
- 파서/엔진 설계는 위 스키마를 전제로 단순·직관적으로 구성 가능(우회용 `EdgeHint` 불필요)
- 구현 난이도: 낮음(모델 정의 + 저장/해결 경로에 직렬화/역직렬화만 추가)
- 파일명 정리: `firnal_review2.md` → `final_review2.md`로 통일 권장(링크 갱신 포함)


## 5) 결론

- 현 문서의 권고사항은 코드 현실(미저장 call 엣지, 호출명 힌트 부재, TS 메타데이터 부족, JOIN/WHERE 간소화, 로깅 불일치)과 정합합니다.
- 그린필드 전제에서는 본 리포트의 스니펫·스키마 확장을 적용해 문서-코드 간 갭을 실질적으로 해소할 수 있으며, 호출관계/DB관계 정확도와 로깅·유지보수성이 개선됩니다.
- 원하시면 위 권고를 코드에 패치 적용하고, 샘플 기반의 동작 검증(간단 테스트)까지 이어서 수행하겠습니다.

