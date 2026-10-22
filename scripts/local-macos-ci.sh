#!/bin/sh
# Run the full CI locally on a Mac; this is the merge gate (the hosted workflow is
# manual-only). Usage: scripts/local-macos-ci.sh [PYTHON]
set -eu
cd "$(dirname "$0")/.."
PY="${1:-${PYTHON:-python3}}"
[ "$(uname)" = Darwin ] || { echo "local-macos-ci: run this on macOS" >&2; exit 2; }
make test PYTHON="$PY"
make mac-bundle
make machprof
if command -v i686-w64-mingw32-gcc >/dev/null 2>&1; then
    # mugl out of tree: the installer tests require that the checkout's own
    # mac-play/mugl/build does not exist (setup builds from a copy).
    out=$(mktemp -d "${TMPDIR:-/tmp}/mu-mac-ci.XXXXXX")
    make -C mac-play/mugl BUILD="$out/mugl"
    make -C mac-play/hotpatch
    make -C mac-play/diagnostics
    rm -rf "$out"
else
    echo "local-macos-ci: i686-w64-mingw32-gcc not found, skipping the Windows cross-builds (brew install mingw-w64)"
fi
"$PY" scripts/audit_repository.py
echo "local-macos-ci: all macOS checks passed"
