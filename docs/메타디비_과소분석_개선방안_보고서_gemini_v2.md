# 메타디비 과소분석 개선방안 보고서 (Gemini 제안) v2

**작성일**: 2025-01-27  
**작성자**: Gemini AI Assistant  
**분석 기반**: 메타디비 과소분석 개선방안 보고서

---

## 1. 개요

본 문서는 메타디비 과소분석 문제(관계 누락률 높음)를 해결하기 위한 구체적이고 즉시 적용 가능한 기술적 방안을 제시합니다. 

핵심 목표는 누락된 **컴포넌트(메서드)**와 **핵심 관계(Import, Calls)** 분석 로직을 구현하여, 수작업 분석 데이터에 근접한 수준으로 분석 커버리지를 끌어올리는 것입니다.

## 2. 상세 개선 방안

Java 파서 파일에 아래 3가지 개선안을 적용합니다.

### 2.1. 컴포넌트 세분화 구현 (메서드 컴포넌트 추출)

**문제점:**
클래스 내의 개별 메서드들이 독립된 컴포넌트로 식별되지 않아, 전체 컴포넌트 수가 부족하고 메서드 간 `calls` 관계 생성이 불가능합니다.

**해결 방안:**
`_extract_basic_structure` 함수로 추출된 각 메서드를 `components` 테이블에 저장합니다. 컴포넌트 중복 방지 로직을 포함하여 동일한 메서드가 중복 저장되지 않도록 합니다.

**소스 코드 수정 예시:**

**대상 파일:** Java 파서 파일

메서드 컴포넌트 추가 로직을 아래와 같이 강화합니다.

```python
# 메서드 컴포넌트 추가
for method_info in structure_info['methods']:
    parent_class = method_info.get('parent_class')
    parent_component_id = component_ids.get(parent_class)
    
    if parent_component_id:
        # 컴포넌트가 이미 존재하는지 확인
        existing_id = self.metadata_engine.find_component(
            project_id=project_id,
            file_id=file_id,
            component_name=method_info['name'],
            component_type='method',
            parent_component_id=parent_component_id
        )

        if existing_id:
            method_id = existing_id
        else:
            # 존재하지 않을 때만 새로 추가
            method_id = self.metadata_engine.add_component(
                project_id=project_id,
                file_id=file_id,
                component_name=method_info['name'],
                component_type='method',
                line_start=method_info.get('line_start'),
                line_end=method_info.get('line_end'),
                parent_component_id=parent_component_id
            )
        
        # component_ids 딕셔너리에 '클래스명.메서드명' 형태로 저장
        component_ids[f"{parent_class}.{method_info['name']}"] = method_id
```

### 2.2. Import 관계 분석 구현

**문제점:**
`import` 관계가 전혀 분석되지 않아, 파일 간의 가장 기본적인 의존성 파악이 누락되고 있습니다.

**해결 방안:**
파일 내용에서 `import` 구문을 정규식으로 모두 추출하고, `import`된 대상이 프로젝트 내부에 존재하는 다른 클래스일 경우 `imports` 관계를 생성합니다.

**소스 코드 수정 예시:**

**대상 파일:** Java 파서 파일

1. **파일 내용 관계 분석 함수에 import 분석 로직 호출 추가:**

    ```python
    def _analyze_file_content_relationships(self, project_id: int, file_path: str, content: str, component_ids: Dict, global_existing_relationships: set):
        # ... (기존 current_class, src_component_id 추출 로직) ...
        
        # 실제 import 관계 분석
        self._analyze_actual_imports(project_id, content, src_component_id, component_ids, global_existing_relationships)

        # ... (기존 다른 분석 함수 호출) ...
    ```

2. **`_analyze_actual_imports` 함수 신규 추가:**
    Java 파서 클래스 내에 아래 함수를 새로 추가합니다.

    ```python
    def _analyze_actual_imports(self, project_id: int, content: str, src_component_id: int, component_ids: Dict, existing_relationships: set):
        """실제 import 구문을 분석하여 관계를 생성합니다."""
        if not src_component_id:
            return

        import_pattern = re.compile(r'import\s+([a-zA-Z0-9_.]+)(?:\.\*)?;')
        matches = import_pattern.finditer(content)

        for match in matches:
            imported_path = match.group(1)
            imported_class_name = imported_path.split('.')[-1]

            dst_component_id = component_ids.get(imported_class_name)

            if dst_component_id and dst_component_id != src_component_id:
                relationship_key = (src_component_id, dst_component_id, 'imports')
                if relationship_key not in existing_relationships:
                    existing_relationships.add(relationship_key)
                    self.metadata_engine.add_relationship(
                        project_id, src_component_id, dst_component_id,
                        'imports', confidence=0.9
                    )
    ```

### 2.3. 메서드 호출(Calls) 관계 분석 구현

**문제점:**
`Calls` 관계가 전혀 분석되지 않아, 서비스 흐름과 데이터 플로우 파악에 치명적인 누락이 발생하고 있습니다.

**해결 방안:**
`_analyze_actual_method_calls` 함수의 로직을 강화하여, 정규식으로 메서드 호출 패턴을 찾고 유의미한 `calls` 관계를 추출합니다. 현재 구조의 한계(호출 대상의 정확한 타입 식별 불가)를 인지하고, 이름 기반으로 관계를 연결하되 신뢰도를 조정합니다.

**소스 코드 수정 예시:**

**대상 파일:** Java 파서 파일

메서드 호출 분석 함수의 로직을 아래와 같이 확인 및 강화합니다.

```python
def _analyze_actual_method_calls(self, project_id: int, content: str, current_class: str, src_component_id: int, component_ids: Dict, existing_relationships: set):
    """실제 메서드 호출 분석 - 노이즈 제거 버전"""
    # Java 키워드, Object 메서드, getter/setter, 유틸리티 메서드 필터링 목록은 그대로 유지

    method_call_pattern = re.compile(r'\b([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)\s*\(')
    matches = method_call_pattern.finditer(content)

    for match in matches:
        caller_variable = match.group(1)
        called_method = match.group(2)

        # 필터링 로직 (예: 키워드, getter/setter 등 제외)
        # if self._is_java_keyword(called_method) or ... : continue

        # 호출된 메서드(callee)의 ID를 찾음
        dst_component_id = None
        for key, comp_id in component_ids.items():
            if '.' in key and key.endswith('.' + called_method):
                dst_component_id = comp_id
                break # 첫 번째 매칭되는 컴포넌트 사용

        if not dst_component_id or dst_component_id == src_component_id:
            continue
        
        relationship_key = (src_component_id, dst_component_id, 'calls')
        if relationship_key in existing_relationships:
            continue
        
        existing_relationships.add(relationship_key)
        
        self.metadata_engine.add_relationship(
            project_id, src_component_id, dst_component_id,
            'calls', confidence=0.7 # 정규식 기반이므로 신뢰도는 다소 낮게 설정
        )
```

## 3. 구현 우선순위

### Phase 1: 핵심 관계 복구 (1주)
1. **Import 관계 분석** (우선순위: 높음)
2. **메서드 호출 분석** (우선순위: 높음)
3. **컴포넌트 세분화** (우선순위: 중간)

### Phase 2: 고급 분석 (2주)
1. **AST 파서 도입** (우선순위: 높음)
2. **SQL Unit 분석** (우선순위: 중간)
3. **JSP 컴포넌트 분석** (우선순위: 낮음)

## 4. 검증 기준

### 1. 수작업 분석 대비 성능
- **과소**: 0% (절대 과소 불가)
- **과대**: 30% 이내 (수용 가능)
- **정확도**: 95% 이상

### 2. 관계 유형별 검증
- **Import**: 수작업 수준 ± 10% 허용 오차
- **Calls**: 수작업 수준 ± 10% 허용 오차
- **Dependency**: 수작업 수준 ± 10% 허용 오차

### 3. 품질 검증
- **신뢰도**: 0.8 이상
- **일관성**: 100% (기계적 일관성)
- **완전성**: 100% (누락 없음)

## 5. 결론

위에 제시된 3가지 핵심 개선안(컴포넌트 세분화, Import 관계, Calls 관계 분석)을 Java 파서에 적용하면, 보고서에서 지적된 심각한 **과소 분석 문제를 해결**하고 수작업 분석 수준에 근접하는 풍부하고 의미 있는 분석 결과를 도출할 수 있을 것입니다.

---

**작성자**: AI Assistant  
**작성일**: 2025-01-27  
**분석 대상**: 메타디비 스키마 및 현재 데이터 현황  
**현재 상태**: 컴포넌트 38개, 관계 22개  
**목표 상태**: 수작업 분석 수준 달성
