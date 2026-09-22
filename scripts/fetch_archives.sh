#!/usr/bin/env bash
# Phase 05 — fetch the three per-project rerun-log archives named in data/README.md.
# Source: Zenodo record 4450723 (DOI 10.5281/zenodo.4450723), CC-BY-4.0.
#
# 589 MB total. Deliberately NOT the full 6.5 GB: the other 14 archives are not needed,
# and spring-projects-spring-boot.tgz alone is 2.6 GB.
#
# Zenodo publishes no per-file md5 for these, so integrity is checked structurally:
# the file must be a readable gzip tar. Recorded as a weaker guarantee than the CSVs.

set -euo pipefail

DEST="data/raw/archives"
BASE="https://zenodo.org/records/4450723/files"

mkdir -p "$DEST"

ARCHIVES=(
  "kevinsawicki-http-request.tgz"
  "tootallnate-java-websocket.tgz"
  "square-okhttp.tgz"
)

for name in "${ARCHIVES[@]}"; do
  path="$DEST/$name"
  if [[ -f "$path" ]] && tar -tzf "$path" >/dev/null 2>&1; then
    echo "ok (cached)  $name  $(du -h "$path" | cut -f1)"
    continue
  fi
  echo "fetching $name ..."
  curl -fsSL -o "$path" "$BASE/$name?download=1"
  if ! tar -tzf "$path" >/dev/null 2>&1; then
    echo "NOT A READABLE GZIP TAR: $name — deleting" >&2
    rm -f "$path"; exit 1
  fi
  echo "ok  $name  $(du -h "$path" | cut -f1)"
done

echo "archives ready in $DEST/"
