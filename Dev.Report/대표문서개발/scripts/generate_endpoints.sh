#!/usr/bin/env bash
set -euo pipefail
REPO="${1:-.}"
OUT_DIR="$(cd "$(dirname "$0")"/.. && pwd)/docs"
mkdir -p "$OUT_DIR"

command -v rg >/dev/null 2>&1 || { echo "ERROR: ripgrep (rg) is required." >&2; exit 1; }

TMP=$(mktemp)
trap 'rm -f "$TMP"' EXIT

# Find Spring MVC mappings in Java files
rg -n --no-heading -g "*.java" '@(RequestMapping|GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping)\s*\(' "$REPO" > "$TMP" || true

# Output CSV header
OUT="$OUT_DIR/endpoints.csv"
echo "file,line,annotation,method,path,controller#method" > "$OUT"

# Parse rudimentary info (best-effort, static scan)
# Extract annotation type and path, then find following method signature line.
# This is simplistic and may not catch complex formatting.
while IFS= read -r line; do
  FILE="${line%%:*}"
  REST="${line#*:}"
  LINENO="${REST%%:*}"
  ANNLINE="${REST#*:}"

  ANN=$(echo "$ANNLINE" | sed -E 's/.*@(RequestMapping|GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping).*/\1/')
  PATHS=$(echo "$ANNLINE" | sed -nE "s/.*\((.*)\).*/\1/p" | tr -d ' ' | sed -E 's/.*value=\\"?([^\\",)]+)\\"?.*/\1/; t; s/^\\"?([^\\",)]+)\\"?.*/\1/')
  [ -z "$PATHS" ] && PATHS="/"

  # try to read next few lines to get method signature
  METHOD_SIG=$(awk -v start=$LINENO 'NR>=start && NR<start+10{print} ' "$FILE" | tr '\n' ' ' | sed -E 's/^\s+//;s/\s+/ /g')
  CTRL_METHOD=$(echo "$METHOD_SIG" | sed -nE 's/.*(public|protected|private)\s+[A-Za-z0-9_<>,\[\] ?]+\s+([A-Za-z0-9_]+)\s*\(.*/\2/p')

  echo "$FILE,$LINENO,$ANN,HTTP?,$PATHS,?$CTRL_METHOD" >> "$OUT"
done < "$TMP"

echo "Generated $OUT"
