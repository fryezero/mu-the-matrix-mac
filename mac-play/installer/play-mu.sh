#!/bin/zsh
# Launch Mu The Matrix from a prefix created by setup-mu-mac.sh. The Desktop .command file written by the
# setup runs this script; Mu The Matrix.app does the same through its own mu-launch.sh.
#
#   MU_RUNTIME         free (default: the free Wine runtime) | crossover (legacy CrossOver bottle; the default
#                      when only MU_BOTTLE is set, as in launchers written by earlier kit versions)
#   MU_PREFIX          free runtime: the prefix (default ~/Library/Application Support/MuTheMatrix/prefix)
#   MUKIT_FREE_HOME    free runtime folder (default ~/Library/Application Support/MuTheMatrix)
#   MU_BOTTLE          crossover: bottle to start (default MuMatrixKit)
#   MU_FAST_X87        free: 1 (default) uses the fast x87 translator when the setup installed it; 0 = off.
#                      crossover: 1 routes main.exe through an existing rosetta-timewalker build (default 0)
#   MU_TIMEWALKER_DIR  that checkout/build (only with MU_FAST_X87=1)
#   CX_ROOT            CrossOver runtime directory
#   MU_DEBUGMSG        crossover: passed to wine --debugmsg; free: WINEDEBUG
#
# It refuses a second instance (one client at a time, across all prefixes) and restarts the prefix's idle
# wineserver first, because stale display state after sleep breaks the launcher. It starts the original
# launcher MuTheMatrix.exe in C:\MuTheMatrix; log: ~/Library/Logs/MuTheMatrix-<name>.log (per prefix, so
# starting one never truncates another one's running log). The free runtime delegates to mu-launch.sh, uses
# MU_LOG_DIR/wine-<prefix>.log and accepts --fast-x87-check, --check and --dry-run.
for _v in ${(k)parameters[(I)CLAUDE*]}; do unset $_v; done; unset _v
RUNTIME=${MU_RUNTIME:-}
# Launchers written by earlier kit versions set only MU_BOTTLE: keep them on CrossOver.
[ -n "$RUNTIME" ] || { [ -n "${MU_BOTTLE:-}" ] && RUNTIME=crossover || RUNTIME=free; }
if pgrep -f 'C:\\MuTheMatrix\\main.exe' >/dev/null || pgrep -f 'C:\\MuTheMatrix\\MuTheMatrix.exe' >/dev/null; then
  osascript -e 'display dialog "Mu The Matrix is already running. Close the game and launcher first, then launch again." buttons {"OK"} with title "Mu The Matrix"' >/dev/null 2>&1
  exit 1
fi
if [ "$RUNTIME" = free ]; then
  # Use the app's preflight, identity cache and fallback instead of a second fast-x87 policy.
  HERE=${0:A:h}
  LAUNCH="$HERE/../mu-launch.sh"                  # app Resources/installer
  [ -f "$LAUNCH" ] || LAUNCH="$HERE/../bundle/mu-launch.sh"  # source checkout
  [ -f "$LAUNCH" ] || { echo "Missing mu-launch.sh; update the installer kit." >&2; exit 1; }
  export MU_RUNTIME=free MU_FAST_X87=${MU_FAST_X87:-1}
  exec /bin/bash "$LAUNCH" "$@"
fi

CX=${CX_ROOT:-/Applications/CrossOver.app/Contents/SharedSupport/CrossOver}
BOTTLE=${MU_BOTTLE:-MuMatrixKit}
# stale display state after sleep breaks the launcher; restart this (idle) bottle's wineserver
WINEPREFIX="$HOME/Library/Application Support/CrossOver/Bottles/$BOTTLE" "$CX/bin/wineserver" -k 2>/dev/null
sleep 1
LOG=$HOME/Library/Logs/MuTheMatrix-$BOTTLE.log
DBG=(); [ -n "$MU_DEBUGMSG" ] && DBG=(--debugmsg "$MU_DEBUGMSG")
if [ "${MU_FAST_X87:-0}" = 1 ]; then
  [ -x "${MU_TIMEWALKER_DIR:-}/scripts/run-crossover.sh" ] || { echo "MU_FAST_X87=1 needs MU_TIMEWALKER_DIR with scripts/run-crossover.sh" >&2; exit 1; }
  export TIMEWALKER_X87_ONLY=main.exe
  exec "$MU_TIMEWALKER_DIR/scripts/run-crossover.sh" --bottle "$BOTTLE" "${DBG[@]}" --workdir 'C:\MuTheMatrix' 'C:\MuTheMatrix\MuTheMatrix.exe' >"$LOG" 2>&1
fi
exec "$CX/bin/wine" --bottle "$BOTTLE" "${DBG[@]}" --workdir 'C:\MuTheMatrix' 'C:\MuTheMatrix\MuTheMatrix.exe' >"$LOG" 2>&1
