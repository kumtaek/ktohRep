#!/usr/bin/env bash
set -euo pipefail
REPO="${1:-.}"
OUT_DIR="$(cd "$(dirname "$0")"/.. && pwd)/docs"
mkdir -p "$OUT_DIR"

has() { command -v "$1" >/dev/null 2>&1; }

if has mvn; then
  (cd "$REPO" && mvn -q -DskipTests package || true)
elif has gradle; then
  (cd "$REPO" && gradle -q build -x test || true)
else
  echo "WARN: mvn/gradle not found; jdeps may fail to locate jars." >&2
fi

if ! has jdeps; then
  echo "ERROR: jdeps not found (install JDK)." >&2
  exit 1
fi

JARS=$(find "$REPO" -type f -name "*.jar" | tr '\n' ' ')
if [ -z "$JARS" ]; then
  echo "WARN: no jars found under $REPO/; skipping jdeps."
  exit 0
fi

jdeps -summary -recursive $JARS > "$OUT_DIR/deps_summary.txt" || true
jdeps --dot-output "$OUT_DIR" $JARS || true

if command -v dot >/dev/null 2>&1; then
  if [ -f "$OUT_DIR/summary.dot" ]; then
    dot -Tpng "$OUT_DIR/summary.dot" -o "$OUT_DIR/deps.png" || true
  fi
else
  echo "INFO: graphviz 'dot' not found; deps.png not generated." >&2
fi

echo "Generated $OUT_DIR/deps_summary.txt and (optional) deps.png"
