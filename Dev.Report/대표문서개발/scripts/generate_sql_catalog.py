#!/usr/bin/env python3
import sys, re, csv
from pathlib import Path
import xml.etree.ElementTree as ET

repo = Path(sys.argv[1] if len(sys.argv)>1 else ".")
out_dir = (Path(__file__).resolve().parent / ".." / "docs").resolve()
out_dir.mkdir(parents=True, exist_ok=True)
out = out_dir / "sql_catalog.csv"

mapper_files = list(repo.rglob("*.xml"))
rows = []
for f in mapper_files:
    try:
        text = f.read_text(encoding="utf-8", errors="ignore")
        if "<mapper" not in text:
            continue
        root = ET.fromstring(text)
    except Exception:
        continue
    ns = {}
    for tag in ["select","insert","update","delete"]:
        for el in root.findall(tag, ns):
            id_ = el.attrib.get("id","")
            param = el.attrib.get("parameterType","")
            result = el.attrib.get("resultMap","") or el.attrib.get("resultType","")
            sql_text = "".join(el.itertext())
            # naive table detection: first token after FROM or JOIN
            tbls = set()
            for kw in [" from ", " FROM ", " join ", " JOIN "]:
                for m in re.finditer(re.escape(kw), sql_text):
                    tail = sql_text[m.end():]
                    mt = re.match(r'([A-Za-z0-9_\."]+)', tail.strip())
                    if mt:
                        tbls.add(mt.group(1).strip('"'))
            rows.append({
                "file": str(f),
                "mapper_id": id_,
                "type": tag,
                "parameter": param,
                "result": result,
                "tables": ";".join(sorted(tbls)),
            })

with out.open("w", newline="", encoding="utf-8") as fp:
    w = csv.DictWriter(fp, fieldnames=["file","mapper_id","type","parameter","result","tables"])
    w.writeheader()
    for r in rows:
        w.writerow(r)

print(f"Generated {out}")
