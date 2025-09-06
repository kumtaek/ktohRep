#!/usr/bin/env python3
import sys, re, csv
from pathlib import Path

repo = Path(sys.argv[1] if len(sys.argv)>1 else ".")
out_dir = (Path(__file__).resolve().parent / ".." / "docs").resolve()
out_dir.mkdir(parents=True, exist_ok=True)
out_csv = out_dir / "error_registry.csv"

code_regex = re.compile(r'(SYS-\d{4}|BUS-\d{4})')
adv_regex = re.compile(r'@ControllerAdvice|@ExceptionHandler')
msg_regex = re.compile(r'^[A-Za-z0-9_.-]+\s*=\s*(.+)$')

rows = []
# Scan Java & JSP for codes
for f in list(repo.rglob("*.java")) + list(repo.rglob("*.jsp")) + list(repo.rglob("*.properties")):
    try:
        text = f.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue
    if f.suffix == ".properties":
        # treat as message bundle
        for i, line in enumerate(text.splitlines(), 1):
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=",1)
                rows.append({"file": str(f), "line": i, "code": k.strip(), "level":"", "user_message": v.strip(), "internal_message":"", "location": ""})
        continue
    for i, line in enumerate(text.splitlines(), 1):
        for m in code_regex.finditer(line):
            rows.append({"file": str(f), "line": i, "code": m.group(1), "level":"", "user_message":"", "internal_message":"", "location": f"{f}:{i}"})

# Deduplicate by (code,location)
seen = set()
deduped = []
for r in rows:
    key = (r["code"], r.get("location",""), r["file"], r.get("line",""))
    if key in seen:
        continue
    seen.add(key)
    deduped.append(r)

with out_csv.open("w", newline="", encoding="utf-8") as fp:
    w = csv.DictWriter(fp, fieldnames=["code","level","user_message","internal_message","file","line","location"])
    w.writeheader()
    for r in deduped:
        w.writerow(r)

print(f"Generated {out_csv}")
