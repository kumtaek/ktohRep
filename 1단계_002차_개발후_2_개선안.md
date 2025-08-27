# 2차 개발 개선안

본 문서는 1단계 2차 개발을 통해 수행된 소스 분석기 개선사항을 기반으로 추가적으로 수정·보완해야 할 사항과 앞으로의 발전 방향을 정리한 문서입니다. 기존 구현을 분석하여 발견된 문제점을 요약하고, 이를 해결하기 위한 구체적인 개선 방안을 제시합니다.

## 1. 병렬 처리 및 성능 개선

### 현황 요약

2차 개발 과정에서 대용량 프로젝트를 더 빠르게 분석하기 위해 병렬 처리 기능이 도입되었습니다. `asyncio`와 `ThreadPoolExecutor`를 활용하여 여러 파일을 동시에 처리하도록 하였고, `batch_size`만큼 파일을 묶어 워커 스레드에게 전달하는 구조를 사용합니다. 이 덕분에 기본적인 처리 속도는 향상되었으나 구현 방식이 곳곳에 중복되어 있습니다【204981712268303†L51-L60】.

### 문제점

* `main.py`(또는 `improved_main.py`)와 `metadata_engine.py`에 병렬 처리 로직이 중복되어 있습니다. 예를 들어 `main.py`에서는 `asyncio.gather`와 세마포어를 사용하고, `metadata_engine.py`는 별도의 `_analyze_batch_sync`를 스레드풀로 실행합니다. 이러한 중복은 유지보수를 어렵게 합니다.
* 스레드풀에서 데이터베이스 세션을 다루는 과정이 안전하게 분리되어 있지 않습니다. 세션 객체가 스레드 사이에 공유되는 경우 문제가 발생할 수 있습니다.
* `max_workers`와 `batch_size`가 설정 파일에 고정되어 있는데, 프로젝트 규모나 시스템 사양에 따라 자동으로 조정되지 않습니다.

### 개선 방안

1. **병렬 처리 로직 일원화**: 병렬 처리를 `metadata_engine.analyze_files_parallel`에만 두고, `main.py`에서는 이를 단순히 호출하도록 변경합니다. 이를 통해 동일한 기능의 반복을 제거하고 인터페이스를 명확히 할 수 있습니다.
2. **세션 안전성 확보**: 스레드풀 내에서 데이터베이스 세션을 각 스레드에서 독립적으로 생성·종료하도록 하여 세션 공유 문제를 방지합니다.
3. **동적 워커 수 조정**: `max_workers`와 `batch_size`를 CPU 코어 수나 파일 수에 따라 동적으로 조정하는 옵션을 제공하고, 설정 파일을 통해 기본값을 커스터마이징하도록 합니다.

```python
# main.py 병렬 처리 호출부 단순화 예시
# (기존의 asyncio.gather 로직 제거)
results = await self.metadata_engine.analyze_files_parallel(
    source_files, project_id,
    {
        'java': self.java_parser,
        'jsp_mybatis': self.jsp_mybatis_parser,
        'sql': self.sql_parser,
    }
)
# 이후 결과 집계 및 요약 처리
```

## 2. 신뢰도 계산 기능 개선

### 현황 요약

2차 개발 버전에서는 파싱 결과의 정확도를 평가하기 위해 **신뢰도 점수(Confidence)**를 도입했습니다. AST 구성 여부, 정적 패턴 매칭 결과, DB 스키마 매칭 결과, 휴리스틱 요소 등을 가중 평균해 0.0~1.0 범위의 점수를 계산하고, 동적 SQL 사용 및 리플렉션과 같은 복잡도 요인에 패널티를 부과합니다【204981712268303†L37-L49】.

### 문제점

* 신뢰도 점수는 계산되지만, 분석 결과를 필터링하거나 사용자에게 알려주는 등 실질적인 활용이 이루어지지 않습니다.
* 요인별 가중치와 패널티 값이 하드코딩되어 있어 프로젝트 특성에 따라 조정하기 어렵습니다.
* AST 품질 외에도 파서가 기록하는 경고나 에러의 종류, 중첩 조건문 깊이 등 복잡도 요인이 추가적으로 고려되어야 하지만 반영되지 않고 있습니다.

### 개선 방안

1. **신뢰도 활용**: 계산된 점수를 일정 임계치와 비교하여 저장 여부를 결정하거나, 낮은 신뢰도 파일에 대해 경고를 남기도록 합니다. 예를 들어 `min_confidence_to_save` 값을 설정 파일에 추가하여 그보다 낮은 결과는 DB에 저장하지 않거나 별도 테이블에 보관하도록 합니다.
2. **설정 유연화**: `confidence.weights`와 패널티 값을 설정 파일에서 조정할 수 있도록 문서화하고, 사용자(프로젝트 관리자)가 쉽게 튜닝할 수 있게 합니다.
3. **요인 세분화**: AST 성공 여부와 정적 규칙 외에도 파싱 경고 수, 동적 코드 사용, 매직 넘버 사용 등 다양한 요인을 추가하여 신뢰도 계산을 더 현실적으로 만듭니다.

```python
# 신뢰도 활용 예시 (metadata_engine 내부)
confidence, factors = self.confidence_calculator.calculate_parsing_confidence(parse_result_data)
min_conf = self.config.get('confidence', {}).get('min_confidence_to_save', 0.2)
if confidence < min_conf:
    self.logger.warning(
        f"신뢰도 낮음({confidence:.2f}) - 결과 저장하지 않음: {file_path}"
    )
    return None  # 낮은 신뢰도 결과는 저장하지 않음
```

## 3. 의존성 그래프 및 DB 연계 기능 개선

### 현황 요약

소스 분석기는 클래스·메서드·SQL 간 의존 관계를 추출하여 그래프로 저장하고, MyBatis XML의 조인/필터 정보를 DB 스키마와 연계하는 기능을 갖추고 있습니다. 또한 동일한 패턴의 조인을 발견해 PK-FK 관계를 추론하는 로직도 도입되었습니다【204981712268303†L94-L97】【204981712268303†L139-L146】.

### 문제점

* 메서드 호출 관계 해소를 위한 `_resolve_method_calls` 함수가 미구현 상태(`pass`)입니다. 호출 엣지의 대상 메서드를 찾지 못해 `dst_id`가 비어있는 경우가 많습니다.
* MyBatis 매퍼 파일에 여러 `<select>` 문이 있을 때, 조인/필터 매핑이 정확하지 않아 모든 조인 정보가 첫 번째 쿼리에 묶이는 오류가 발생합니다.
* DB 스키마 조회 시 스키마 이름이 코드에 하드코딩되어 있어 다른 환경에 적용하기 어렵습니다.
* 복잡한 조인 패턴을 루프 안에서 반복적으로 처리해 성능이 떨어질 수 있습니다.

### 개선 방안

1. **메서드 호출 해소 구현**: `_resolve_method_calls`를 구현하여 호출 엣지의 `dst_id`를 찾아 채웁니다. 간단히 메서드 이름 기준으로 동일 프로젝트 내 메서드를 검색하되, 클래스/패키지 정보까지 활용하여 오탐률을 줄입니다.
2. **정확한 SQL 매핑**: 파서가 각 SQL 구문별로 조인/필터 목록을 속성으로 갖도록 변경하고, 저장 시 해당 SQL에 속한 정보만 기록하도록 합니다.
3. **유연한 스키마 설정**: DB 스키마 이름을 설정 파일에서 읽어 오도록 수정하고, 기본값을 프로젝트 환경에 맞게 지정합니다.
4. **성능 개선**: 복잡한 조인 패턴 분석을 파이썬 루프에서 처리하는 대신 데이터베이스 질의나 프로시저로 옮겨 속도를 높일 수 있는지 검토합니다.

```python
# 예시: 메서드 호출 해소 간단 구현
for edge in unresolved_calls:
    if edge.src_type == 'method':
        src_method = session.query(Method).get(edge.src_id)
        if src_method:
            target = session.query(Method).filter(
                Method.name == edge.called_name,
                Method.class_name == edge.called_class
            ).first()
            if target:
                edge.dst_id = target.method_id
                session.add(edge)
```

## 4. 증분 분석 모드 구현

### 현황 요약

2차 개선안에서 명령행 인자로 `--incremental` 플래그를 도입해 이전 분석 이후 변경된 파일만 다시 분석하는 기능을 구상했습니다. 하지만 현재 구현은 플래그만 존재하고 실질적인 증분 분석 로직이 적용되지 않았습니다【204981712268303†L151-L154】.

### 문제점

* 변경 파일을 식별하는 로직이 없어서 `--incremental` 옵션을 사용해도 전체 파일을 분석합니다.
* 최초 실행 시에는 이전 기록이 없어 증분 분석이 불가능하므로 처리 방식을 정의할 필요가 있습니다.

### 개선 방안

1. **변경 감지 로직 추가**: 파일의 해시값이나 마지막 수정 시각을 DB에 저장하고, 실행 시점의 값과 비교하여 변경된 파일만 선별합니다.
2. **증분 모드 분기**: 인자로 `--incremental`이 주어지면 변경된 파일 목록만 수집하여 분석하도록 `analyze_project`의 흐름을 분기합니다. 최초 분석 시에는 플래그를 무시하고 전체 분석을 수행합니다.
3. **분석 후 정보 업데이트**: 증분 분석이 끝나면 각 파일의 최신 해시와 수정 시각을 DB에 업데이트합니다.

```python
if args.incremental:
    project = self.db_manager.get_project_by_path(project_root)
    if project:
        modified_files = []
        for file_path in self._collect_source_files(project_root):
            db_file = self.db_manager.get_file(project.project_id, file_path)
            if not db_file or os.path.getmtime(file_path) > db_file.mtime:
                modified_files.append(file_path)
        source_files = modified_files
        self.logger.info(f"증분 분석 대상 파일 수: {len(source_files)}")
    else:
        self.logger.info("초회 분석이므로 전체 파일을 분석합니다.")
```

## 5. 로깅 및 예외 처리 개선

### 현황 요약

개선된 로깅 시스템이 도입되어 파일별 오류를 로깅하고, `PerformanceLogger`를 통해 주요 단계의 실행 시간을 측정합니다. 그러나 초기화 단계에서 일부 오류를 `print`로 출력하는 부분이 남아 있으며, 진행 상황을 한 눈에 볼 수 있는 기능이 부족합니다【204981712268303†L63-L76】.

### 문제점

* 예외가 발생해도 `print`로 처리하여 로그 파일에 기록되지 않는 경우가 있습니다.
* `analysis_results['errors']`에 오류 메시지와 파일만 기록되어 있어, 예외 종류나 트레이스 정보를 확인하기 어렵습니다.
* 대규모 프로젝트 분석 시 진행률을 알기 어려워 사용자 경험이 떨어집니다.

### 개선 방안

1. **로그 일관성 유지**: 모든 예외 처리에서 로거를 사용하도록 통일하고, 심각도에 따라 `critical`/`error`/`warning` 등을 구분합니다.
2. **예외 정보 세분화**: `errors` 목록에 예외 타입과 메시지를 구조화하여 저장하고, 필요하다면 스택 트레이스도 포함시킵니다.
3. **진행률 표시**: 전체 파일 수 대비 현재 처리 중인 파일의 비율을 주기적으로 로그로 출력하거나 프로그레스 바 라이브러리를 활용해 CLI에서 시각화합니다.

```python
try:
    # 분석 로직
    result = await analyzer.analyze_project(target_path)
except FileNotFoundError as e:
    logger.critical(f"파일을 찾을 수 없습니다: {e}")
    raise
except yaml.YAMLError as e:
    logger.critical(f"설정 파일 파싱 실패: {e}")
    raise
except Exception as e:
    logger.exception("예상치 못한 오류 발생", exc_info=e)
    raise
```

## 6. 코드 구조 및 유지보수성 개선

### 현황 요약

현재 코드베이스는 여러 단계의 개선 작업이 누적되면서 파일과 클래스가 중복되고, 단일 클래스가 너무 많은 책임을 지고 있습니다. 예를 들어 `main.py`와 `improved_main.py`가 공존하며, `SourceAnalyzer` 클래스가 파일 수집부터 DB 저장까지 모든 역할을 담당하고 있습니다.

### 문제점

* 동일 기능을 수행하는 파일(`main.py`, `improved_main.py`)이 둘 이상 있어 혼란을 초래합니다.
* 단일 클래스에 많은 책임이 몰려 있어 수정이 어려우며, 테스트 코드 작성도 용이하지 않습니다.
* Docstring과 주석이 최신 구현을 반영하지 않는 경우가 있습니다.

### 개선 방안

1. **중복 제거**: 개선된 기능을 기존 메인 모듈로 통합하고, 필요 없는 파일(예: `improved_main.py`)을 제거합니다. `ImprovedConfidenceCalculator` 등 "Improved" 접두어가 붙은 클래스는 기존 버전을 대체하도록 리팩터링합니다.
2. **모듈 분리**: 소스 수집, 병렬 처리 관리, 결과 집계 등을 각각 별도의 모듈/클래스로 분리하여 단일 책임 원칙을 적용합니다. 예를 들어 `AnalysisRunner` 클래스를 신설해 병렬 분석만 담당하도록 합니다.
3. **문서화 및 주석 최신화**: 모든 공개 메서드에 Docstring을 추가하고, 변경사항에 맞춰 개발 문서를 업데이트합니다. 사용자가 참고하는 `개발내역.md` 등 문서도 최신 내용을 반영해야 합니다.
4. **테스트 코드 작성**: 리팩터링 후 주요 기능에 대한 단위 테스트를 마련하여 회귀를 방지합니다.

## 7. 테스트 샘플 소스 구성

개선된 기능들을 검증하고 시연하기 위해 `PROJECT` 디렉터리에 세 가지 예제 프로젝트를 제공합니다. 각각의 예제는 서로 다른 시나리오를 다루어 분석기의 다양한 기능을 시험할 수 있게 합니다.

### 예제 1 – Java 메서드 호출 관계 테스트

두 개의 클래스가 서로 메서드를 호출하는 간단한 자바 프로젝트입니다. `ClassA`가 `ClassB`의 `doWork()` 메서드를 호출하는 구조를 갖습니다. 분석 후 호출 엣지가 올바르게 생성되고, 개선된 `_resolve_method_calls` 구현을 통해 `dst_id`가 채워지는지 확인할 수 있습니다.

```
// ClassA.java
public class ClassA {
    public void start() {
        ClassB b = new ClassB();
        b.doWork();  // ClassB의 메서드 호출
    }
}

// ClassB.java
public class ClassB {
    public void doWork() {
        System.out.println("Working...");
    }
}
```

### 예제 2 – MyBatis 조인 및 필터 테스트

하나의 MyBatis 매퍼 XML과 관련된 DAO 클래스로 구성된 프로젝트입니다. XML 내부에 두 개의 `<select>` 쿼리가 있으며, 각 쿼리는 다른 조인과 필터 조건을 가지고 있습니다. 첫 번째 쿼리는 `USER`와 `ORDER` 테이블을 조인하고, 두 번째 쿼리는 `PRODUCT` 테이블을 조회하며 `DEL_YN = 'N'`이라는 필수 필터가 포함됩니다. 개선된 매핑 로직을 통해 조인과 필터가 각 SQL 구문별로 정확히 매핑되는지 검증할 수 있습니다.

```xml
<!-- ExampleMapper.xml -->
<select id="getUserOrders" resultType="Order">
  SELECT U.ID, U.NAME, O.ORDER_ID, O.AMOUNT
  FROM USER U 
  JOIN ORDER O ON U.ID = O.USER_ID
  WHERE U.STATUS = 'ACTIVE'
</select>

<select id="getAvailableProducts" resultType="Product">
  SELECT P.ID, P.NAME, P.PRICE
  FROM PRODUCT P
  WHERE P.DEL_YN = 'N'
</select>
```

해당 예제와 함께 간단한 DAO 클래스(`ExampleDao.java`)를 제공하여 XML과 자바 소스 간의 연계를 시험할 수 있습니다.

### 예제 3 – 증분 분석 및 신뢰도 테스트

증분 분석 기능과 신뢰도 점수 활용을 확인하기 위한 프로젝트입니다. 처음에는 정상적인 코드를 제공하고, 이후 파일을 수정하여 복잡도와 동적 SQL 사용을 증가시킵니다. `--incremental` 옵션을 사용해 변경된 파일만 재분석되는지, 신뢰도 점수가 낮아진 파일이 필터링되는지를 실험할 수 있습니다.

초기 버전:

```java
// Sample.java (initial)
public class Sample {
    public void queryData() {
        String sql = "SELECT * FROM USERS";
        // ... (정상적인 쿼리 수행)
    }
}
```

수정 후 버전:

```java
// Sample.java (modified)
public class Sample {
    public void queryData() {
        String table = "USERS";
        String sql = "SELECT * FROM " + table;  // 동적 SQL 생성
        try {
            Class<?> clazz = Class.forName("com.example.Unknown");  // 리플렉션 사용
        } catch (Exception e) {
            // ...
        }
    }
}
```

이를 통해 증분 분석 로직과 신뢰도 활용 로직이 올바르게 동작하는지 확인할 수 있습니다.

## 마무리

이 문서에서 제안한 개선 사항들은 시스템의 성능과 정확도를 높이고 유지보수성을 향상하는 데 목적이 있습니다. 병렬 처리 일원화, 신뢰도 점수 활용, 의존성 그래프 보완, 증분 분석 모드 구현, 로깅·예외 처리 강화, 코드 구조 개선을 순차적으로 적용한다면 다음 단계의 소스 분석기 발전에 큰 도움이 될 것입니다.
