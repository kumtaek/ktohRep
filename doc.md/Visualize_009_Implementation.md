# Source Analyzer 구현 및 개선 현황 보고서 (Visualize_009_Implementation.md)

## 1. 개발 및 개선된 내용

### 1.1. 개발 완료된 주요 기능 및 개선 사항

* **비동기/동기 패턴 혼재 문제 해결**:
  * `phase1/src/database/metadata_engine.py` 파일의 `process_files_parallel` 함수가 완전한 비동기 패턴으로 통일되었습니다. `ThreadPoolExecutor`와 `asyncio`의 혼용 문제를 해결하고, `asyncio.Semaphore`를 이용한 동시 실행 제한 및 `async_session_manager`를 통한 컨텍스트 매니저 기반 세션 관리가 구현되었습니다.
* **노드-엣지 일관성 오류 해결**:
  * `visualize/builders/dependency_graph.py` 파일의 `filter_by_confidence` 함수가 개선되어, 필터링된 노드 집합을 기반으로 엣지를 필터링함으로써 존재하지 않는 노드를 참조하는 엣지 생성을 방지하고 시각화 렌더링 오류를 해결했습니다.
* **정확성 검증 프레임워크 개발**:
  * `AccuracyValidator` 클래스와 `ConfidenceCalibrator` 클래스가 개발되었습니다. 이는 Ground Truth 데이터셋을 기반으로 파서별 정확성을 측정하고, 신뢰도 점수를 실제 정확성과 맞추는 캘리브레이션 시스템을 포함합니다.

### 1.2. 개선이 계획/진행 중인 주요 사항 (아직 개발 완료되지 않음)

* **Java 파서 현대 문법 미지원**:
  * `javalang` 라이브러리의 한계로 인해 Java 8+의 람다, 스트림 API, 메서드 레퍼런스 등이 제대로 인식되지 않는 문제가 있습니다. Tree-sitter Java 파서 또는 Eclipse JDT Core 도입을 통한 현대화가 계획되어 있습니다.
* **[TODO] JSP/MyBatis 동적 SQL 처리 오류**:
  * 정규식 기반 SQL 추출의 한계로 `<if>`, `<choose>`, `<foreach>` 등 동적 SQL 내부의 관계가 누락되는 문제가 있습니다. MyBatis AST 파서 구현 및 조건부 SQL 조합 알고리즘 개선이 계획되어 있습니다.
* **[TODO] 데이터베이스 세션 관리 불완전**:
  * `phase1/src/database/metadata_engine.py`에서 세션 롤백 후 `session.close()`가 누락되어 커넥션 풀 고갈 및 메모리 누수가 발생하는 문제가 있습니다. 완전한 세션 관리 수정이 계획되어 있습니다.
* **신뢰도 공식 검증**:
  * `phase1/src/utils/confidence_calculator.py`의 신뢰도 공식이 경험적 검증 없이 임의로 설정되어 허위 신뢰도를 제공할 가능성이 있습니다. Ground Truth 데이터셋 구축 및 경험적 신뢰도 공식 재검정이 계획되어 있습니다.
* **신뢰도 전파 오류 수정**:
  * `phase1/src/utils/confidence_calculator.py`에서 순환 참조 시 신뢰도가 비현실적으로 높아지는 문제가 있습니다. 순환 참조 처리 로직 수정이 계획되어 있습니다.
* **SQL 핑거프린트 충돌**:
  * `phase1/src/database/metadata_engine.py`에서 단순 해시 기반의 SQL 핑거프린트 생성으로 인해 의미적으로 다른 SQL이 같은 핑거프린트를 가질 수 있는 문제가 있습니다. 의미 기반 분석을 위한 핑거프린트 개선이 계획되어 있습니다.
* **Python 클래스 분석 제한**:
  * `visualize/builders/class_diagram.py`에서 동적 속성 할당(`setattr`, `exec`) 패턴이 미인식되어 동적 클래스 구조가 누락되는 문제가 있습니다. Python 동적 분석 지원이 계획되어 있습니다.
* **[TODO] Mermaid 내보내기 단순화 오류**:
  * `visualize/exporters/mermaid_exporter.py`에서 복잡한 제네릭 타입이나 다중 상속 관계를 단순화하여 중요한 구조 정보가 손실되는 문제가 있습니다. Mermaid 내보내기 정확성 개선이 계획되어 있습니다.
* **[TODO] 트랜잭션 경계 모호성**:
  * `phase1/src/database/metadata_engine.py`에서 자동 커밋 모드에서 부분 실패 시 데이터 일관성 문제가 발생할 수 있습니다. 트랜잭션 경계 명확화가 계획되어 있습니다.
* **[TODO] 문서-구현 불일치 (설정 예제 오류)**:
  * `README.md`의 설정 예제(`parser_type: "ast"`)가 실제 코드에서 무시되는 문제가 있습니다. 문서와 구현 간의 동기화가 계획되어 있습니다.

## 2. 개발이 아직 안된 내용

위 '개선이 계획/진행 중인 주요 사항'에 언급된 모든 항목들은 아직 개발이 완료되지 않은 내용들입니다. 특히, 파서의 현대 문법 지원, 동적 SQL 처리, 신뢰도 공식의 검증 및 전파 오류 수정, 데이터베이스 세션 관리의 완전성, SQL 핑거프린트의 의미 기반 개선, Python 동적 클래스 분석, Mermaid 내보내기 정확성, 트랜잭션 경계 명확화, 문서-구현 동기화 등은 핵심적인 정확성 및 안정성 개선을 위해 개발이 필요한 부분입니다.

## 3. 새로 설치된 항목 및 오프라인 설치 방법

보고서 내용 중 **"Tree-sitter Java 파서 도입 (1순위)"** 이 언급되어, 새로운 파서 라이브러리 또는 도구의 설치가 필요함을 시사합니다. Tree-sitter는 구문 분석기 생성 도구로, 특정 언어의 파서를 사용하려면 해당 언어의 Tree-sitter 문법을 설치해야 합니다.

### Tree-sitter Java 파서 오프라인 설치 방법 (일반적인 접근)

Tree-sitter 파서는 일반적으로 C/C++로 작성된 문법 파일을 컴파일하여 사용합니다. Python에서 이를 사용하려면 `tree-sitter` Python 라이브러리와 함께 해당 언어의 컴파일된 문법 파일을 로드해야 합니다.

1. **필수 도구 준비**:
   
   * **Python 환경**: `pip`가 설치된 Python 3.x 환경.
   * **C/C++ 컴파일러**: `gcc`, `clang` (Linux/macOS) 또는 `MSVC` (Windows)와 같은 C/C++ 컴파일러가 시스템에 설치되어 있어야 합니다. (오프라인 환경에 미리 설치 필요)
   * **`git`**: Tree-sitter 문법 저장소를 클론하는 데 필요합니다. (오프라인 환경에 미리 설치 필요)

2. **Tree-sitter Python 라이브러리 설치**:
   
   * 인터넷 연결이 가능한 환경에서 `pip download tree-sitter` 명령을 사용하여 `tree-sitter` 패키지와 그 의존성(`pytree-sitter` 등)을 다운로드합니다.
   * 다운로드된 `.whl` 파일들을 오프라인 환경으로 옮긴 후, `pip install --no-index --find-links=. tree-sitter` 명령으로 설치합니다.

3. **Java Tree-sitter 문법 다운로드**:
   
   * 인터넷 연결이 가능한 환경에서 Tree-sitter Java 문법 저장소 (예: `https://github.com/tree-sitter/tree-sitter-java`)를 `git clone` 합니다.
   * 클론된 저장소 폴더를 오프라인 환경으로 옮깁니다.

4. **Java 문법 컴파일 및 로드**:
   
   * 오프라인 환경에서 Python 스크립트를 통해 다운로드한 Java 문법을 컴파일하고 로드합니다.
   
   * 예시 코드:
     
     ```python
     from tree_sitter import Language, Parser
     import os
     
     # Tree-sitter Java 문법 저장소 경로 (오프라인 환경에 옮긴 경로)
     JAVA_LANGUAGE_PATH = 'path/to/tree-sitter-java'
     BUILD_DIR = 'build' # 컴파일된 라이브러리가 저장될 디렉토리
     
     # 빌드 디렉토리 생성
     os.makedirs(BUILD_DIR, exist_ok=True)
     
     # Java 언어 문법 컴파일
     # 이 과정에서 C/C++ 컴파일러가 필요합니다.
     Language.build_library(
         # 컴파일된 라이브러리 파일 경로
         os.path.join(BUILD_DIR, 'java_language.so'), # Linux/macOS: .so, Windows: .dll
         # 문법 소스 코드 경로
         [
             JAVA_LANGUAGE_PATH
         ]
     )
     
     # 컴파일된 언어 로드
     JAVA_LANGUAGE = Language(os.path.join(BUILD_DIR, 'java_language.so'), 'java')
     
     # 파서 생성 및 사용 예시
     parser = Parser()
     parser.set_language(JAVA_LANGUAGE)
     
     tree = parser.parse(bytes("class MyClass { void method() {} }", "utf8"))
     print(tree.root_node.sexp())
     ```
   
   * `Language.build_library` 함수가 C/C++ 컴파일러를 사용하여 `.so` (Linux/macOS) 또는 `.dll` (Windows) 파일을 생성합니다. 이 파일이 Tree-sitter Java 파서의 핵심입니다.

5. **컴파일된 라이브러리 배포**:
   
   * 한 번 컴파일된 `.so` 또는 `.dll` 파일은 다른 오프라인 환경으로 복사하여 사용할 수 있습니다. 즉, 모든 환경에서 컴파일러가 필요하지는 않으며, 개발 환경에서 한 번 컴파일 후 배포 환경으로 옮길 수 있습니다.

이러한 단계를 통해 인터넷 연결 없이 Tree-sitter Java 파서를 Source Analyzer 프로젝트에 통합할 수 있습니다.
