#!/usr/bin/env python3
import sys, re, csv
from pathlib import Path

repo = Path(sys.argv[1] if len(sys.argv)>1 else ".")
out_dir = (Path(__file__).resolve().parent / ".." / "docs").resolve()
out_dir.mkdir(parents=True, exist_ok=True)
out_csv = out_dir / "config_inventory.csv"
out_diff = out_dir / "config_diff.txt"

# Collect keys from application*.yml and *.properties (shallow keys only for yml)
yml_keys = {}
prop_keys = {}

def collect_yml_keys(p: Path):
    keys = set()
    for i, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
        m = re.match(r'^([A-Za-z0-9_.-]+)\s*:\s*(.*)$', line)
        if m:
            keys.add(m.group(1))
    return keys

def collect_prop_keys(p: Path):
    keys = set()
    for i, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
        if line.strip().startswith("#") or "=" not in line:
            continue
        k = line.split("=",1)[0].strip()
        if k:
            keys.add(k)
    return keys

files = list(repo.rglob("application*.yml")) + list(repo.rglob("*.properties"))
profiles = set()

for f in files:
    name = f.name
    prof = "default"
    m = re.match(r'application-([A-Za-z0-9_-]+)\.yml', name)
    if m:
        prof = m.group(1)
    elif name.startswith("application.yml"):
        prof = "default"
    elif name.endswith(".properties"):
        prof = name
    profiles.add(prof)
    try:
        if f.suffix == ".yml":
            ks = collect_yml_keys(f)
            yml_keys.setdefault(prof, set()).update(ks)
        else:
            ks = collect_prop_keys(f)
            prop_keys.setdefault(prof, set()).update(ks)
    except Exception:
        pass

all_keys = set()
for d in [yml_keys, prop_keys]:
    for s in d.values():
        all_keys.update(s)

profiles = sorted(list(profiles))
with out_csv.open("w", newline="", encoding="utf-8") as fp:
    w = csv.writer(fp)
    w.writerow(["key"] + profiles)
    for k in sorted(all_keys):
        row = [k]
        for pf in profiles:
            present = ""
            if k in yml_keys.get(pf,set()) or k in prop_keys.get(pf,set()):
                present = "Y"
            row.append(present)
        w.writerow(row)

# Simple diff report between common profiles dev/stage/prod if present
def report_diff(base, other):
    a = (yml_keys.get(base,set()) | prop_keys.get(base,set()))
    b = (yml_keys.get(other,set()) | prop_keys.get(other,set()))
    add = sorted(list(b - a))
    rm = sorted(list(a - b))
    return base, other, add, rm

diffs = []
for base in ["dev","stage","stg","qa","default"]:
    for other in ["prod","production"]:
        if base in profiles and other in profiles:
            diffs.append(report_diff(base, other))

with out_diff.open("w", encoding="utf-8") as fp:
    if not diffs:
        fp.write("No standard profile pairs (dev/prod, stage/prod) found.\n")
    for base, other, adds, rms in diffs:
        fp.write(f"[{base} -> {other}] added keys in {other}:\n")
        for k in adds:
            fp.write(f"  + {k}\n")
        fp.write(f"[{base} -> {other}] removed keys in {other}:\n")
        for k in rms:
            fp.write(f"  - {k}\n")
        fp.write("\n")

print(f"Generated {out_csv} and {out_diff}")
