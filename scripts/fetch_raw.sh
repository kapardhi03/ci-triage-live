#!/usr/bin/env bash
# Phase 04 — fetch the three FlakeFlagger CSVs into data/raw/ and verify integrity.
# Source: Zenodo record 4450723 (DOI 10.5281/zenodo.4450723), licensed CC-BY-4.0.
# Deliberately does NOT fetch the ~6.5 GB per-project .tgz rerun logs (phase 08's job).
#
# Usage:  bash scripts/fetch_raw.sh
# Idempotent: re-running re-verifies existing files against the recorded checksums.

set -euo pipefail

DEST="data/raw"
BASE="https://zenodo.org/records/4450723/files"

mkdir -p "$DEST"

# filename  expected_md5
FILES=(
  "Project_Info.csv 5b3392a4f7367b2a566b919a98989a97"
  "test_features.csv 63306c05fafcc6446911ab7000f85ae0"
  "test_results.csv fcd2674ab42068de627ec6afce4f6d1a"
)

md5_of() {
  if command -v md5sum >/dev/null 2>&1; then md5sum "$1" | awk '{print $1}';
  else md5 -q "$1"; fi   # macOS fallback
}

for entry in "${FILES[@]}"; do
  name="${entry%% *}"
  want="${entry##* }"
  path="$DEST/$name"

  if [[ ! -f "$path" ]]; then
    echo "fetching $name"
    curl -fsSL -o "$path" "$BASE/$name?download=1"
  fi

  got="$(md5_of "$path")"
  if [[ "$got" != "$want" ]]; then
    echo "CHECKSUM MISMATCH for $name: got $got, expected $want" >&2
    echo "Refusing to proceed. Delete $path and re-run." >&2
    exit 1
  fi
  echo "ok  $name  ($got)"
done

echo "All three CSVs present and verified in $DEST/"
