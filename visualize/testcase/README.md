# Visualize 테스트 케이스

## 목적
- 그래프/ERD/컴포넌트/클래스 다이어그램 데이터 생성과 내보내기(HTML/JSON/CSV/Markdown) 동작을 점검합니다.

## 준비
- DB에 분석 결과가 존재해야 합니다(예: `tests/run_tests.py`로 샘플 파싱 후 생성).

## 실행 예시
- 의존 그래프 (project_id=1), Mermaid 내보내기:
```
python -m visualize.cli graph --project-id 1 \
  --kinds use_table,include,extends,implements \
  --export-mermaid ./outputs/graph.md \
  --export-json ./outputs/graph.json \
  --export-csv-dir ./outputs/graph_csv
```

- ERD (project_id=1):
```
python -m visualize.cli erd --project-id 1 \
  --export-mermaid ./outputs/erd.md
```

- 컴포넌트/클래스 다이어그램도 동일한 방식으로 실행 가능합니다.

## 확인 항목
- 출력 파일 생성 여부와 내용(노드/엣지 수, 기본 필드)
- 라벨 길이 제한/노드 수 제한 옵션 동작
- CSV 헤더/행 수 무결성
