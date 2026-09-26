#!/bin/bash
# Open a URL in a brand-new, throwaway Chrome profile -- guaranteed empty
# storage (IndexedDB, cache, everything), every single time. Simpler and
# more reliable than clearing site data by hand or hoping an "incognito"
# window is actually fresh (Chrome shares one incognito session across all
# incognito windows open at once, so a "new" one isn't always empty).
#
# Usage: tools/fresh_browser.sh [url]
# Defaults to the Part 1.2 notebook on the usual dev server port if no URL given.

set -euo pipefail

URL="${1:-http://localhost:8234/notebooks/index.html?path=Part_1.2_Intro_to_ASE.ipynb}"
PROFILE_DIR="$(mktemp -d -t jupyterlite-fresh-profile)"

open -na "Google Chrome" --args --user-data-dir="$PROFILE_DIR" --no-first-run "$URL"

echo "Opened in a fresh Chrome profile: $PROFILE_DIR"
echo "(safe to delete that folder later; it's just a throwaway profile)"
