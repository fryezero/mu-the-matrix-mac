#!/bin/bash
# Shared by the installer, diagnostics and the copied bottle launcher.
FAST_X87_COMMIT=ab1a6a032e488c0d6eade54ce70a02d653277810
FAST_X87_HOME=${MU_FAST_X87_HOME:-$HOME/Library/Caches/MuTheMatrix/fast-x87/$FAST_X87_COMMIT}

fast_x87_identity() {
    local loader="$CX_ROOT/lib/wine/x86_64-unix/wine" server="$CX_ROOT/bin/wineserver-x86"
    if [ -x "$CX_ROOT/lib/wine/x86_64-unix/wine.app/Contents/MacOS/wine" ]; then
        loader="$CX_ROOT/lib/wine/x86_64-unix/wine.app/Contents/MacOS/wine"
    fi
    [ -x "$server" ] || server="$CX_ROOT/bin/wineserver"
    sw_vers -buildVersion &&
        cksum "$CX_ROOT/bin/wine" "$loader" "$server" \
            "$CX_ROOT/lib/wine/x86_64-unix/ntdll.so" /Library/Apple/usr/libexec/oah/libRosettaRuntime \
            "$FAST_X87_HOME/source/build/libtimewalker.dylib" \
            "$FAST_X87_HOME/x87-main-only-wrapper.c" \
            "$FAST_X87_HOME/x87-main-only-wrapper" \
            "$FAST_X87_HOME/source/build/x87/bin/runtime_loader" \
            "$FAST_X87_HOME/source/build/x87/bin/libRuntimeRosettax87"
}

fast_x87_ready() {
    local identity
    identity=$(fast_x87_identity) || return 1
    [ -f "$FAST_X87_HOME/validated" ] &&
        [ "$(cat "$FAST_X87_HOME/validated")" = "$identity" ] &&
        [ "$(git -C "$FAST_X87_HOME/source" rev-parse HEAD)" = "$FAST_X87_COMMIT" ] &&
        git -C "$FAST_X87_HOME/source" diff --quiet HEAD -- &&
        [ -x "$FAST_X87_HOME/source/scripts/run-crossover.sh" ] &&
        [ -f "$FAST_X87_HOME/source/build/libtimewalker.dylib" ] &&
        [ -f "$FAST_X87_HOME/x87-main-only-wrapper.c" ] &&
        [ -x "$FAST_X87_HOME/x87-main-only-wrapper" ] &&
        [ -x "$FAST_X87_HOME/source/build/x87/bin/runtime_loader" ] &&
        [ -x "$FAST_X87_HOME/source/build/x87/bin/libRuntimeRosettax87" ]
}

# Why fast_x87_ready failed, as one line naming the fix. A validated file that no longer matches means macOS,
# Rosetta or CrossOver changed since install-fast-x87.sh ran (a macOS update replaces libRosettaRuntime).
fast_x87_stale_reason() {
    if [ -f "$FAST_X87_HOME/validated" ]; then
        printf 'Fast x87 needs revalidation after a macOS update (macOS %s, or Rosetta/CrossOver changed): run mac-play/install-fast-x87.sh --bottle SETUP_OWNED_IDLE_BOTTLE.' \
            "$(sw_vers -buildVersion 2>/dev/null || echo unknown)"
    else
        printf 'Fast x87 is not installed or not validated (%s): run mac-play/install-fast-x87.sh --bottle SETUP_OWNED_IDLE_BOTTLE.' "$FAST_X87_HOME"
    fi
}

# ---- free runtime: self-check after macOS/Rosetta/translator changes (WINE-FASTX87-002) ----
# The free runtime keeps the translator in $MUKIT_FREE_HOME/fast-x87. mu-launch.sh records the identity below in
# its "validated" file after the authored x86_64 probe (mac-play/x87-smoke.c) passed through runtime_loader, and
# reruns the probe whenever the identity changes. MU_ROSETTA_FILES (colon-separated) replaces the system Rosetta
# paths in tests.
fast_x87_free_identity() { # FX INNER PROBE
    local fx=$1 inner=$2 probe=$3 rosetta=() IFS_SAVE=$IFS
    IFS=:; rosetta=(${MU_ROSETTA_FILES:-/Library/Apple/usr/libexec/oah/libRosettaRuntime:/usr/libexec/rosetta/runtime}); IFS=$IFS_SAVE
    sw_vers -buildVersion &&
        cksum "${rosetta[@]}" "$fx/runtime_loader" "$fx/libRuntimeRosettax87" "$fx/libtimewalker.dylib" \
            "$fx/x87-main-only-wrapper" "$inner" "$probe"
}

# fast_x87_free_selfcheck FX PROBE LOG: 0 when the translator reports itself built and the probe prints PASS.
# Two tries (one translator start in ~17 crashed in a fresh prefix under heavy load), 20 s each.
fast_x87_free_selfcheck() {
    local fx=$1 probe=$2 log=$3 try out pid t rc
    for try in 1 2; do
        out="$log.out"
        "$fx/runtime_loader" "$probe" > "$out" 2>&1 &
        pid=$!; t=0
        while kill -0 "$pid" 2>/dev/null && [ "$t" -lt 100 ]; do sleep 0.2; t=$((t + 1)); done
        kill -0 "$pid" 2>/dev/null && { kill -9 "$pid" 2>/dev/null; echo 'x87 self-check: timed out after 20 s' >> "$out"; }
        wait "$pid" 2>/dev/null; rc=$?
        { echo "== $(date '+%Y-%m-%d %H:%M:%S') try $try exit $rc"; cat "$out"; } >> "$log"
        if [ "$rc" = 0 ] && grep -q 'RosettaRuntimex87 built' "$out" && grep -q '^x87 smoke: PASS' "$out"; then
            rm -f "$out"; return 0
        fi
    done
    rm -f "$out"; return 1
}

fast_x87_select() {
    MU_WINE=("$CX_ROOT/bin/wine")
    case "${MU_FAST_X87:-auto}" in
        0) printf 'Using plain CrossOver (MU_FAST_X87=0).\n' ;;
        auto|1)
            if fast_x87_ready 2>/dev/null; then
                export TIMEWALKER_CROSSOVER_ROOT="$CX_ROOT"
                export TIMEWALKER_X87_LOADER_WRAPPER="$FAST_X87_HOME/x87-main-only-wrapper"
                export TIMEWALKER_X87_ONLY="${TIMEWALKER_X87_ONLY-main.exe}"
                MU_WINE=("$FAST_X87_HOME/source/scripts/run-crossover.sh")
                printf 'Using opt-in fast x87 (%s).\n' "$FAST_X87_COMMIT"
            elif [ "${MU_FAST_X87:-auto}" = 1 ]; then
                printf '%s\n' "$(fast_x87_stale_reason)" >&2
                return 1
            else
                printf '%s Using plain CrossOver.\n' "$(fast_x87_stale_reason)"
            fi
            ;;
        *) printf 'MU_FAST_X87 must be auto, 0 or 1.\n' >&2; return 1 ;;
    esac
}
