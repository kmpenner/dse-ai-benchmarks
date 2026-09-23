#!/usr/bin/env bash
# Stage repo content into pages/ and build the MkDocs site.
set -euo pipefail
cd "$(dirname "$0")/.."
rm -rf pages/resac2026 pages/docs
mkdir -p pages/resac2026 pages/docs
cp resac2026/*.md resac2026/*.png resac2026/*.jpg resac2026/*.csv resac2026/*.html resac2026/*.pdf pages/resac2026/
cp docs/*.md pages/docs/
mkdocs "${1:-build}"
