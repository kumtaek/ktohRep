# Test Cases – Visual Dataflow Overlays & Data Flow

본 테스트는 샘플 소스(PROJECT/sampleSrc)와 DB 스키마를 사용하여 1) 메타정보 생성(Phase1) → 2) 시각화(visualize)까지 엔드투엔드로 검증합니다.

## 준비
- Python 패키지 설치: `pip install -r requirements.txt`
- 환경: SQLite 사용(기본). DB 파일: `./data/metadata.db`
- 참고: `PROJECT/` 폴더는 테스트용 샘플 소스입니다.

## 1) DB 스키마 준비(샘플)
- 샘플 프로젝트 경로: `PROJECT/sampleSrc`
- DB 스키마 CSV: `PROJECT/sampleSrc/DB_SCHEMA/` 에 최소 테이블(USERS, CUSTOMERS, ORDERS, ORDER_ITEMS, PRODUCTS) 포함됨
  - 파일: `ALL_TABLES.csv`, `ALL_TAB_COLUMNS.csv`, `PK_INFO.csv`

검증(선택): CSV 구조 검증 유틸 사용
```bash
python - << 'PY'
from phase1.src.utils.csv_loader import CsvLoader
import yaml
cfg=yaml.safe_load(open('config/config.yaml','r',encoding='utf-8'))
loader=CsvLoader(cfg)
for n in ['ALL_TABLES.csv','ALL_TAB_COLUMNS.csv','PK_INFO.csv']:
    print(n, loader.validate_csv_structure(f'PROJECT/sampleSrc/DB_SCHEMA/{n}'))
PY
```

## 2) 메타정보 생성(Phase1)
프로젝트 분석 실행(샘플 소스 + 샘플 DB 스키마 로드)
```bash
python phase1/src/main.py PROJECT/sampleSrc --project-name sample
```
성공 시 콘솔에 `project_id`와 파일/SQL 수 요약이 출력됩니다. 기본 SQLite 경로는 `config/config.yaml`에서 조정 가능합니다.

## 3) 시각화 – 그래프(데이터 흐름 강조)
아래 명령으로 HTML + Mermaid Markdown을 생성합니다.
```bash
python -m visualize.cli graph \
  --project-id 1 \
  --kinds use_table,include,call \
  --min-confidence 0.5 \
  --out out/graph.html \
  --export-mermaid out/graph.md \
  --export-strategy balanced \
  --keep-edge-kinds include,call,use_table
```
확인 사항:
- 그룹 색상: JSP/Controller/Service/Mapper/DB 적용
- Hotspot: 라벨에 `<br/>(LOC=.., Cx=..)` 표기, 클래스 `hotspot_*` 존재
- 취약점: 기본값 없음. 아래 5) 참고 후 `vuln_*` 클래스 확인
- 미해결 호출: `-.->` 점선 화살표 확인

## 4) 시각화 – ERD/시퀀스(선택)
ERD(요약):
```bash
python -m visualize.cli erd \
  --project-id 1 \
  --out out/erd.html \
  --export-mermaid out/erd.md
```
시퀀스(유스케이스):
```bash
python -m visualize.cli sequence \
  --project-id 1 \
  --out out/seq.html \
  --export-mermaid out/seq.md
```

## 5) 취약점 오버레이 테스트(선택)
분석 후, 특정 SQL 유닛에 취약점 레코드를 추가하여 오버레이를 확인할 수 있습니다.
```bash
python - << 'PY'
import sqlite3, json
from pathlib import Path
DB=str(Path('data/metadata.db').absolute())
con=sqlite3.connect(DB)
cur=con.cursor()
# 대상 SQL 유닛(예: UserMapper.selectUserById) 검색
cur.execute("""
SELECT su.sql_id FROM sql_units su 
WHERE su.mapper_ns LIKE '%UserMapper%' AND su.stmt_id='selectUserById' LIMIT 1
""")
row=cur.fetchone()
if row:
    sql_id=row[0]
    cur.execute("""
    INSERT INTO vulnerability_fixes(
      target_type,target_id,vulnerability_type,severity,owasp_category,cwe_id,description,confidence
    ) VALUES(?,?,?,?,?,?,?,?)
    """,(
      'sql_unit',sql_id,'sql_injection','high','A03','CWE-89','Test seed',0.9
    ))
    con.commit()
    print('Seeded vulnerability for sql_unit', sql_id)
else:
    print('No target sql_unit found; check sample analysis results')
con.close()
PY
```
이후 그래프를 다시 내보내 `out/graph.md`에서 `class ... vuln_high` 등의 클래스가 적용되었는지 확인합니다.

## 6) 결과 검증
- `out/graph.html` 열기 → 그룹 색/레이아웃/검색 동작
- `out/graph.md` 열기 → Mermaid 코드에 `classDef hotspot_*`, `classDef vuln_*` 및 `class nX*` 적용 확인
- ERD/시퀀스 산출물(선택) 확인

## 비고/제약
- Mermaid 대규모 그래프는 렌더링 실패 가능 → `--export-strategy minimal`, `--max-nodes`, `--depth`, `--focus` 사용 권장
- Hotspot 복잡도는 근사치(아웃바운드 호출 수 기반)
- `PROJECT/sampleSrc`는 테스트 샘플이며, 실제 프로젝트 분석 시 프로젝트 루트에 `DB_SCHEMA/`가 있어야 스키마가 로드됩니다.
