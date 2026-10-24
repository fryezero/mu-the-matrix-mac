# Continue from here (Wine track)

## Follow-up profiling, MAC-PERF-012 (2026-10-24)

Further full-quality rendering alternatives did not show a consistent gain over the existing zero-copy path and
were removed. An isolated live old/new check at Tormenta Island 128,120 settled at 25 FPS, including the zoomed
view, but this was a light scene. The extreme synthetic workload remains over 40 ms. The disposable game copy was
removed and the player installation is unchanged. Retained code fixes improve benchmark comparisons and cleanup.
See [the follow-up evidence](research/mac-crowd-followup.md).

## Crowded rendering, MAC-PERF-011 (2026-10-23)

GL-only changes index named buffers and avoid some full visibility scans. The authored Wine stress test uses
fresh disposable prefixes, ABBA runs and output hashes. In a 2,048-buffer, 12,000-small-draw workload, median
work fell 40.01 -> 31.85 ms and frames above 40 ms fell 64/120 -> 0/120. Larger combined cases still exceed
40 ms. This is synthetic rendering evidence, not live combat FPS; no player install was changed.
The private candidate also built with native JPEG support and passed a separate Wine rendering comparison.
The local macOS merge gate passed. See [measurements and reproduction](research/mac-crowd-performance.md).
Next: controlled crowded-gameplay validation before player distribution.

## Repository split (REPO-SPLIT-001, 2026-10-21)

This repository was split out of `fryezero/mu-the-matrix-recovery` (renamed to `mu-the-matrix-native`) with
`git filter-repo` over `mac-play/`, `docs/research/mac-*.md` (except `mac-runtime.md`, the QEMU code-capture note,
which stayed native), the Wine-track tests and the shared repository files, so `git log --follow` works. Local
checkout: `~/Documents/mu-the-matrix-mac`. Differences from the old layout: `make test` here runs only this track's
checks; `scripts/local-macos-ci.sh` also builds the development app, machprof and (with MinGW) mugl out of tree, the
hotpatch DLL and the diagnostics; the live-state readers (`objread`, `memread`, `lightread`, `langread`) moved to the
native repository's `live-readers/`; the app icon script is duplicated there for the Native Preview app. README
screenshots live in `docs/images/` and are hash-pinned in `scripts/audit_repository.py` (update the pin when you
replace one). Issue/PR numbers in older notes refer to the native repository.

## Player disk image and first run (MAC-DMG-001)

Read [`research/mac-dmg-installer.md`](research/mac-dmg-installer.md) and `mac-play/bundle/README.md`. Player builds:
`make player-dmg EMBED_MUGL=… EMBED_MSCOREE=… EMBED_FAST_X87=… EMBED_RUNTIME=…` (the runtime pin is `RuntimeFile` in
`Sources/Core.swift`); `dmg/make-dmg.sh` (Finder layout from `dmg/dmg-tool.swift`, signing/notarization with
`SIGN_IDENTITY`/`NOTARY_PROFILE`). The first-run window is `InstallWindowController` (`Sources/main.swift`), its step
names and overall progress and "Move to Applications" are in `Sources/FirstRun.swift`. Rehearse without touching a real
install with `open --env MUKIT_FREE_HOME=… --env MU_SETTINGS_FILE=… --env MU_LOG_DIR=… --env MU_APPLICATIONS_DIR=…`
(the move passes these on). Keep player-facing strings free of technical words (the suite checks them). Next: a full
install rehearsal from the DMG (not done yet, owner request), the owner's Developer ID notarization run, hosting the DMG.

## Free runtime without CrossOver (MAC-FREE-001)

Read [`research/mac-free-runtime.md`](research/mac-free-runtime.md). `mac-play/installer/setup-mu-mac.sh` defaults to
`--runtime free` (prefix in `~/Library/Application Support/MuTheMatrix`); `--runtime crossover`/`--bottle` keeps the
CrossOver path. Mu The Matrix.app bundles the installer (Install window). Owner decisions open: host the
CrossOver 26.3 Wine archive from `installer/packaging/build-wine.sh` (then set `MUKIT_RT_ARCHIVE_URL`/`_SHA256`;
until then players get the slower CX24 engine), distribute the app with bundled mugl/fast-x87 (`EMBED_*`), and
Apple Developer ID signing/notarization. Next: publish, then a rehearsal on a second Mac.

## Launcher windows on macOS (MAC-APP-004)

Read [`research/mac-launcher-windows.md`](research/mac-launcher-windows.md). The fix lives in
`mac-play/mumodes/winfix.c` (since mscoree proxy v2 `0405b330…`; the current proxy is v3 `0cf77991…`, see MAC-APP-006 below; v1 `6f2d2ace…` and v2 are recognised and replaced).
`C:\mutools\winfix.log` shows whether it and the tray-icon hook are on; `MU_LAUNCHER_WINFIX=0` disables it.
A new Wine build with a different `shell32!Shell_NotifyIconW` prologue leaves the tray hook off (the log says so):
the Dock click then restores the window but not the launcher's faded content; add the prologue to `wf_hotpatch`.

## Official launcher skin (MAC-APP-006)

Read [`research/mac-launcher-skin.md`](research/mac-launcher-skin.md). The server's `Template.design` works again with
mscoree proxy v3 (`mac-play/mumodes/wicfix.c`, pinned `0cf77991…`; v2 `0405b330…` and v1 are recognised and replaced).
The old "custom GIF skin aborts the launcher constructor" was a Wine 11 JPEG decoder bug (NULL `pcbRead`, upstream
fix `111e5197`). Setup's launcher skin step runs after the DLLs and renames the newest `Template.design.disabled[.N]`
back when the installed proxy has the fix; without it the skin stays disabled. `winfix.log` shows `WIC stream fix used`;
`MU_LAUNCHER_WICFIX=0` disables it.

## Launcher "Hash Protection" 0xA4 dialog (MAC-APP-005, paused)

Read [`research/mac-launcher-hash-dialog.md`](research/mac-launcher-hash-dialog.md). The launcher's `File.ReadAllBytes`
gets a short read (EndOfStream) in about 1-2 % of starts. Forced kills leave no broken file, so a clean-up step
would not help. The protection is a black box: do not analyse or bypass it. Next step: about 300 automated starts
each with and without `gcConcurrent` disabled for the launcher, to test the Wine/XNU EFAULT-offset hypothesis.

## Original launcher in CrossOver

Read [`research/mac-crossover-32bit.md`](research/mac-crossover-32bit.md) and
[`../mac-play/README.md`](../mac-play/README.md). The owner now reports GAME START,
login and gameplay in MuMatrix32. Claude owns frame-rate work there; do not edit
that bottle or stop its processes. This is compatibility gameplay, not a native
source build.

MAC-CROSSOVER-002 is issue #42, branch `codex/mac-launcher-settings`, isolated
worktree `~/Documents/mu-worktrees/mac-settings`. A fresh win32 and fresh win10_64
bottle both use winemac.drv and a valid APPA061 monitor. Injecting a stale runtime
MonitorID0 link to missing Default_Monitor reproduces the exact launcher Settings
MonitorFromWindow/Win32Exception Success stack and Wine find_monitor_from_path
error. A direct link repair works; a prefix-scoped server restart independently
rebuilds the source link. The exact natural sleep/display-change trigger remains
unverified because this task did not change the host display or sleep state.

Setup now installs a synthetic MonitorCheck.exe using the bottle's .NET compiler
and rewrites Play.command to use the shipped start helper. On an idle start it
runs a prefix-scoped wineserver -k/-w, verifies a hidden window's monitor and the
primary mode, then starts the launcher. A tasklist guard refuses a running game
or launcher, failed/invalid queries, and failed reset/display checks. A live
synthetic main.exe sentinel survived a refused start with the same Wine PID.
Settings was clicked and captured after reset, with no new launcher log after
archiving/decoding the injected failure. Settings value persistence and gameplay
in the test bottle were not exercised. Logs/captures are local and ignored at
`runtime/mac-settings/` in that worktree. Both test bottles and the setup lock
are deleted. After integrating the bone-track changes, portable checks pass
148/162 with fourteen private-input skips, plus four Bash syntax checks. See the
finding for the registry snapshots and capture details. Next, observe a natural
post-sleep idle start using Play.command;
do not trigger a host display change while another bottle is in use.

Keep builtin windowscodecs/gdiplus, .NET 4.8, software rendering and the built-in
IGCN skin from MAC-CROSSOVER-001, issue #39 / PR #41. Native WIC was a failed
hypothesis; recreate experimental bottles that installed it. Setup refuses
protected/unowned bottles, clones to a bottle-specific path and disables only
the cloned Template.design on every rerun (that legacy script installs no mscoree
proxy; the installer kit restores the skin, MAC-APP-006). Original installations stay intact.
The previous MuMatrix32-ci-test validation passed all eight image steps and
65.8-second launcher survival before deletion. Source-recovery and native game
acceptance gates remain open. Two static selector-0x33 far-return sequences
support the Heaven's Gate hypothesis without proving the original Rosetta fault.

## Immediate-mode GL batching

MAC-PERF-003 is issue #51, branch `codex/mac-gl-batching`, worktree
`~/Documents/mu-worktrees/mac-mugl`. Read
[`research/mac-performance.md`](research/mac-performance.md) and
[`../mac-play/mugl/README.md`](../mac-play/mugl/README.md). The authored MIT proxy
and 361-export generator build with `make mugl`; generated sources/DLL stay
ignored. Portable tests compile the primitive conversion with host clang.
Setup is default-on, rechecks the Wine system32 builtin marker, installs beside
the cloned main.exe and records SHA-256. `MU_GL_BATCHING=0` removes the managed
proxy and override. It refuses an active game/launcher and unmanaged DLLs.

Validation uses the new setup-created MuMugl-test bottle, never MuMatrix32.
Three 240-frame pairs at 20,000 quads/frame have matching framebuffer hashes:
38.7/118.7 FPS at one quad/block, 65.2/118.9 at four and 76.8/119.6 at sixteen.
All thirty-six glcheck hashes match with no state failures or GL errors. Real setup
off/on/rerun checks pass. GAME START launched main.exe PID 888, with active fan
buffering and 25.0 FPS. Its last saved interval has 999,569 blocks and 8,966 draws,
with zero in-block fallbacks. No login/in-world test was performed. The bottle
was stopped with its explicit prefix, deleted by name and absence checked. The
final proxy digest is in the performance finding.
Raw logs/binaries are ignored in `runtime/mac-mugl/`. CrossOver's wrapper replaces
WINEDLLOVERRIDES; the diagnostic helper must use `--dll opengl32=b` or `n,b`.
Initial environment-only A/B runs were rejected because the proxy never loaded.
Native-only cannot load the real Wine builtin. Do not reuse those failed runs.

Both review axes found the wireframe triangulation issue; non-fill polygon modes
now permanently fall back, and the synthetic GL probe covers a wireframe quad.
Display lists compile without array conversion; in-block multitexture calls use
immediate replay.
Server/client texture selection and other-unit arrays are preserved; modern
buffer variants select a conservative process fallback. VAO binding is preserved
by submitting through saved/restored default-VAO state. The extension table has
4,096 slots because the client exceeds the prototype's 512 slots at startup.
Ordinary VBO bindings are preserved around
CPU array submission; GL2.1 compatibility shaders remain active. First-vertex
flat fans/strips keep their original primitive mode. Shared globals assume one
rendering thread
and one current context at a time. Float32 fixed-function inputs are the measured
domain. General GL equivalence, in-world FPS/stability and anti-cheat behavior
remain open. Claude's reported 73% in-world OpenGL sample share supersedes the
x87 bottleneck hypothesis. Native game recovery gates remain unchanged.

Next, the owner validates login, Karutan and other in-world scenes, comparing
builtin versus mugl with the same game settings and collecting optional stats.
Do not stop or change the owner's MuMatrix32 bottle to obtain those numbers.

## Fast x87 compatibility path

MAC-PERF-001 is issue #45 / merged PR #47. MAC-PERF-002 is issue #48, branch
`codex/mac-x87-main-only`, worktree `~/Documents/mu-worktrees/mac-x87-filter`.
Read [`research/mac-performance.md`](research/mac-performance.md).
The installer still requires clean rosetta-timewalker pin
`ab1a6a032e488c0d6eade54ce70a02d653277810`. Our separate MIT
`mac-play/x87-main-only-wrapper.c` is copied, compiled arm64 and ad-hoc signed
in the cache. Its source/binary join the identity checks. No third-party source
changes are needed. Upstream run-crossover.sh honors our wrapper override.

Selection exports the built wrapper and defaults `TIMEWALKER_X87_ONLY=main.exe`.
A case-insensitive substring in any argument after argv[0] selects fast
translation; nonmatches exec the real Wine loader directly. Caller overrides
are preserved, including empty to apply to everything. This avoids the verified
unfiltered .NET launcher/monitor hang. The installer's matching-filter check uses
`fp_x87`. Existing caches need reinstalling, and existing setup-owned bottles
need a setup rerun to copy the updated helper. Idle guards, prefix-scoped reset,
plain monitor check and explicit `MU_FAST_X87=0` fallback remain intact.

Local logs and the separate cache are ignored in `runtime/mac-x87-filter/` in
this worktree. The disposable bottle is `MuX87Filter-test`, created by setup
from Windows10MU's read-only source. MuMatrix32 and its processes are excluded.
The actual launcher window appeared under required-fast selection with the
default filter. PID-scoped window enumeration and a private capture confirmed
the normal launcher; MonitorCheck passed and no x87 translator activation
appeared during launcher startup. A post-setup matching `fp_x87` check measured
279.1 Mverts/s versus 2.7 plain, both printing 3.904312. The bottle was stopped
with its explicit prefix, deleted by name and absence checked. Six wrapper and
sixteen launcher tests pass; full make test passes 163/177 with fourteen private
skips. Both review axes pass; publication audit rejects no files.
See the finding for methods and limits. Next, the owner
continues in-world FPS/stability validation. Claude's reported GAME START and
profile improvement remain separately attributed; this task does not click
GAME START or use credentials.

## MAC-PERF-004 publication handoff

Issue #57 / `codex/mac-hotpatch`, worktree `~/Documents/mu-worktrees/mac-hotpatch`,
is stacked on OPEN PR #52 (`codex/mac-gl-batching`, base `d1c86a3`). The owned
scope is `mac-play/hotpatch`, `mumodes`, `machprof`, `automation`, generator/policy
tests, CI cross-build and the shared performance/status/roadmap/evidence notes.
This publishes Claude's saved v7.0 work. No main.exe or Wine process was started,
stopped, attached to or patched, and neither MuMatrix32 nor its C:\MuTheMatrix /
C:\mutools directories were modified. Default setup remains PR #52's proxy.

Read `research/mac-performance.md`, MAC-PERF-004, and
`../mac-play/hotpatch/README.md`. `source-provenance.json` pins the pre-packaging
authored sources. v7.0 mugl is `c8397771…b6a1`; xform is `cce0902f…c624`.
The owner-supplied pristine memory dump remains `/tmp/pristine.bin`, SHA-256
`6e7957c9af8685f5a5fb14008131eab50470d40d2e6128397d5795a88160bfd4`.
The source generator derives objdump listings from that dump, verifies identities
and reproduces exactly nine helper patches, 18,583 inline sites and 50,977
peepholes. The old cached `/tmp/calls.txt` differs from the derived call list by
one nonmatching target; both listing identities are pinned and yield identical
final tables. Original templates become length/hash metadata. The xform original
prologue and all original/replacement tables are generated under ignored
`mac-play/hotpatch/build/private`, never committed or uploaded.

Actual local checks: `make test PYTHON=tools/.venv/bin/python` discovers 208 tests,
193 pass and fifteen explicitly skip private inputs. `make mac-hotpatch` builds
the compile-only proxy, mscoree mode proxy, mesh/call benchmarks and muinput.
`make -C mac-play/hotpatch private` cross-builds the private proxy and hptest;
neither was executed. `make -C mac-play/machprof` compiles all three x86_64 Mach
tools without signing/attachment. All five automation scripts pass zsh parsing.
The final staged publication audit and diff check pass. Existing compiler warnings
are an unused legacy extra-mode installer and compact hptest indentation.
Fresh private tables match all eighteen original/replacement helper arrays and
both final v7.0 tables byte for byte. Full generation also succeeds using only
`--dump`, with locally derived listings. Verification logs and reference headers
are ignored under `runtime/mac-hotpatch/`.

Claude's prior 900k/helper comparison, >1M live skinning comparison, hunting FPS,
6.4 ms GL timing, 44.8% mesh attribution and Rosetta behavior are supplied reports,
not rerun measurements here. Raw measurement logs were not acquired. The
performance finding keeps those claims separate from actual publication checks.
The pinned v7.0 source does not contain an identifiable frame-cap patch installer;
the 25 FPS/40 ms cap remains a reported condition and the merged frame-loop
analysis is linked. Flags-dead analysis remains heuristic and full EFLAGS/access
identity is unverified. Broad GL equivalence and Windows-native behavior remain
unverified. Anti-cheat variants are a plan only.

Review the PR and its macOS/Linux CI before integration. Do not merge the child
while #52 is open without preserving that dependency. No independent reviewer
approval is supplied by this implementation task. Next performance task, under
separate authorization, is an original-vs-C mesh draw comparison at
`0x012b8d1d..0x012bb35a` before measuring speed. Use EBP walks, retain the old
stack-scan misattribution, and disable AeDebug only in disposable test bottles
before crash-prone probes. The original process-killing restart helper and later
meshdraw experiment remain omitted. Login/movement scripts select an explicit
test bottle and refuse MuMatrix32; login reads the password from Keychain.

After #58 was merged into `codex/mac-gl-batching` and `main` (with #54/#56) was merged in, the combined tree discovers 236 tests: 218 pass and 18 explicitly skip private inputs (`make test PYTHON=tools/.venv/bin/python`). The earlier counts above are per-PR snapshots.

## MAC-PERF-005 publication handoff

Issue #59 / `claude/mac-meshdraw`, worktree `~/Documents/mu-worktrees/mac-meshdraw`,
based on main `f629ef9` (PR #52/#58 merged). The owned scope is `mac-play/hotpatch`
(`meshdraw.c`, v7.1 `mugl.c`, `meshdraw-notes.md`, generator/targets/provenance),
`mac-play/diagnostics/glstride.c`, the audit and tests, and the shared
performance/status/roadmap/evidence/notices notes. This publishes Claude's saved v7.1
work. No main.exe or Wine process was started, stopped, attached to or patched, and
neither MuMatrix32 nor its C:\MuTheMatrix / C:\mutools directories were modified. Default
setup remains PR #52's proxy. `~/Documents/mu-mac-tools` was read only.

Read `research/mac-performance.md`, MAC-PERF-005, and `../mac-play/hotpatch/README.md`
and `meshdraw-notes.md`. `source-provenance.json` pins `mugl_v71.c` (`62798456...`),
`meshdraw_v71.c` (`ac3f115b...`) and `glstride.c` (`f8393505...`); `xform.c` is
unchanged from v7.0. The three patch-site original byte sequences that `meshdraw_v71.c`
embedded (7/6/10 bytes at `0x012ba899`, `0x012b968c`, `0x012b8d1d`) are now length plus
SHA-256 in `targets.json` (`meshdraw_sites`); `generate.py` verifies the owner-supplied
dump `/tmp/pristine.bin` (SHA-256 `6e7957c9...160bfd4`) against them and writes an
ignored `build/private/meshdraw-orig.h`, and the synthetic header is zeros. The audit
and tests reject that header name as a source file.

Actual local checks: `make test PYTHON=tools/.venv/bin/python` discovers 241 tests,
223 pass and eighteen skip private inputs (five tests are new). `make mac-hotpatch
mac-diagnostics` cross-builds the compile-only proxy and `glstride.exe`. Full private
generation from the dump reproduces nine helpers, 18,583 inline sites, 50,977
peepholes and the three new digests, and `make -C mac-play/hotpatch private` builds.
That private DLL, rebuilt at image base `0x69680000`, has the same size as Claude's
`mugl-v71.dll` and an identical disassembly modulo data addresses. Nothing was
executed or installed. `local_integration_passed` in the evidence index is the earlier
value; private integration was not rerun for this change.

Everything about runtime behavior (zero verification mismatches, framebuffer-hash
equality, fps and work-time tables, the frame-pointer profile, the Winsock 10049
reconnect during a known outage) is Claude's supplied report. Notable record points:
the spawn "full v7.1" row is mask 4015 (not the 7599 default), the 8111 mask (adds
strided arrays) measured lower fps than 4015, and the spawn rows include the bit-512
timer. The v7.0 44.8% attribution is withdrawn: mugl had no frame pointers. Not
established: the `0x20`/`0x200000` vertex paths, mode `0x8000`, inputs outside the
reported sessions, EFLAGS or access-trace equivalence, Windows-native behavior,
anti-cheat and server compatibility.

Next work: no single dominant hotspot is reported. The remaining main.exe self time is
spread over indirect/vtable calls (mostly from `0x00ea27ac`), `0x012bc07a`,
`0x016d197d`, terrain decals `0x016cdd5f` and `0x016cc9e2`. Frame rate is bounded by
the 40 ms logic step, so any further gain needs the logic step itself (see the
frame-loop finding) rather than more render-path work. Dual anti-cheat builds remain a
plan only. Use disposable bottles for any crash-prone probe.

## MAC-PERF-006 publication handoff

Issue #61 / `claude/mac-pacing-v72`, worktree `~/Documents/mu-worktrees/mac-pacing`, based on
main `5b96c26` (PR #60 merged). The owned scope is `mac-play/hotpatch/mugl.c` (v7.1 to v7.2
diff only), the v7.2 section of `mac-play/hotpatch/meshdraw-notes.md` and the README,
`source-provenance.json`, the new `PrecisePacingTests` and the performance/status/roadmap/
evidence/notices notes. A separate PR (reproducible Mac setup kit under `mac-play/`) does not
touch these files. No main.exe or Wine process was started, stopped, attached to or patched,
and neither MuMatrix32 nor MuMatrixKit was modified. `~/Documents/mu-mac-tools` was read only.

Read `research/mac-performance.md`, MAC-PERF-006, and `meshdraw-notes.md` (v7.2). Cause as
reported from Claude's diagnostic builds: with the game not frontmost, macOS coalesces the
timers behind Wine's `Sleep` (7-14 ms took 17-45 ms), which made bit-1024 pacing jitter and
fall to 17-22 fps. The inactive-window throttle (`[0x01cf0fc0]` stayed 1; the inactive branch
at `0x0120ee34` has no Sleep) and double sleeping (only the driver's Sleep, return `0x01852680`)
were ruled out. The fix waits on a waitable timer to the exact 40 ms deadline, with a `Sleep`
fallback, and routes any other render-thread `Sleep(ms>0)` through it. `Sleep(0)` and other
threads are unchanged, and there are no GL changes or new patch sites. `source-provenance.json`
pins `mugl_v72.c` (`9eeed0c5...138dbdfd`) and marks `mugl_v71.c` superseded.

Actual local checks: `make test PYTHON=tools/.venv/bin/python` discovers 245 tests, 227
pass and eighteen skip private inputs (four are new); `make mugl mac-diagnostics mac-hotpatch`
cross-builds; the audit passes. The new code was compiled, not executed, because it only
runs inside a private build in the game. All fps, histogram and overshoot figures are Claude's
supplied report (spawn, about 28-29 ms of work: background 19.3-21.1 fps with pacing off,
about 24.5 with v7.1 and half the frames late, 25.00 over 140 s with v7.2; frontmost 25.0,
25.0 and 24.95).

Not established: other hosts, macOS versions or power states, runs beyond the reported 140 s,
login and character-select numbers, Windows-native behavior, anti-cheat and server
compatibility. Next work: no new performance lever is reported; 25 fps remains the fixed
40 ms logic step. A 6-minute background hunting-spot soak is now reported (see
`research/mac-performance.md`); an hour-long, heavier-load run would still extend the evidence.

## MAC-KIT-001 publication handoff

Issue #63 / `claude/mac-setup-kit`, worktree `~/Documents/mu-worktrees/mac-setup-kit`, stacked after
PR #62 (MAC-PERF-006), based on main `6f4344d`. The owned scope is the new `mac-play/installer/`
(`setup-mu-mac.sh`, `verify-mu-mac.sh`, `play-mu.sh`, `lib/mukit.sh`, `registry/mu-mac.reg`, `README.md`,
`tests/`), `tests/test_mac_installer.py`, the `make test` hook, `.gitignore`/`.gitattributes` entries and
the shared notes. `~/Documents/mu-mac-tools` was read only. No main.exe, Wine process or game was
started and neither MuMatrix32 nor MuMatrixKit was touched; the only bottle name used for the
real-CrossOver dry run (`MuRepoDryRun`) does not exist and was not created.

Read `research/mac-crossover-32bit.md` (MAC-KIT-001) and `../mac-play/installer/README.md`. Differences
from the owner's live-validated local copy: paths now come from the repository (`mac-play/cxwine`,
`cxwineserver`, `mumodes`, `mugl`, `hotpatch`) or parameters (`--dll-dir`, `--dotnet-installer`,
`--helpers-dir`, `--timewalker-dir`, `--mugl-build`); `--dll-source build` is the default and builds the
public batching-only mugl (DevModeIndex capped at 2); `--dll-source current` and `--mugl-repo` are gone;
`play-mu.sh` is part of the kit and defaults to plain Rosetta; the pins stay in `lib/mukit.sh` with
`MUKIT_*_SHA256` environment overrides that exist only for the synthetic tests. Account ID and Keychain
item names appear nowhere in the tree; autologin uses the existing `MU_ACCOUNT`/`MU_KEYCHAIN_SERVICE`.
Prebuilt DLL hashes (v7.2 `e37cf5d5...`, v7.1 `85a8e3b6...`, v7.0 `c06534df...`, mscoree `6f2d2ace...`)
were checked against the owner's files read-only.

Actual local checks: `make test PYTHON=tools/.venv/bin/python` discovers 254 tests (236 pass, 18 explicit
private skips; the 9 new tests are `tests/test_mac_installer.py`) and runs the 180-check shell suite;
the same suite passed 180/180 in an Ubuntu 24.04 container with MinGW, python3 and zsh, and 166/166
without them (those checks skipped); `python3 scripts/audit_repository.py`; `--dry-run` of the setup
against the real CrossOver tree and a synthetic client folder. Not run: a live bottle build, the
repository shims under winetricks, the new default build path's DLL in the game, any game start.

Next work: on a throwaway bottle (never MuMatrix32 or MuMatrixKit, game not running), run the kit once
with `--dll-source build` and once with `--dll-source prebuilt --dll-dir ...`, record timings and the
verify output, and delete the bottle; then decide whether to retire the older setup or merge the two.
The `MonitorCheck.exe` pre-launch display probe in `start-launcher.sh` is not in the kit. Fast-x87
and the anti-cheat variants stay TODO hooks. Use disposable bottles for any crash-prone probe.


## MAC-KIT-001 live-validation follow-up

Branch `claude/kit-live-fixes`, worktree `~/Documents/mu-worktrees/kit-live`, based on main `0c1b5c8` (PR #64).
The repository version of the kit was run live in a throwaway bottle (all three DLL paths and `--fast-x87`, to
the server-select screen; not logged in because the account was in use elsewhere; MuMatrix32 and its processes
untouched). It found five bugs, fixed here: PE timestamps made builds non-reproducible
(`--no-insert-timestamp` in the kit's mscoree command and `mac-play/mugl/Makefile`), `--dll-dir` demanded
`mscoree.dll` (the public proxy is now built when missing, and a failed DLL copy aborts), a test depended on
a real private build in the checkout (`MUKIT_PRIVATE_BUILD_DIR`), `play-mu.sh` shared one log between bottles
(`MuTheMatrix-<bottle>.log`), and verify ignored the launcher's fast-x87 setting. Results and timings are in
the kit README ("Live validation of the repository version") and `research/mac-crossover-32bit.md`; the shell
suite is 190 checks. The pre-existing README-wording test was updated to the new status text. Also recorded
in `research/mac-performance.md` (MAC-PERF-006): a reported 6-minute background soak with v7.2.

Next: log in with a kit-built bottle and measure in-world fps against MuMatrix32 once the account is free;
run a long (an hour or more) session, with heavier monster load, to settle stability; decide whether to
retire `setup-crossover-32bit.sh`. The private hotpatch build output stays in the ignored
`mac-play/hotpatch/build/private/` and must never be committed.

## Mu The Matrix.app (MAC-BUNDLE-001)

Branch `claude/mac-bundle`. Read `../mac-play/bundle/README.md`. `make mac-bundle` builds
`mac-play/bundle/build/Mu The Matrix.app`. One live start in MuMatrixKit reached server select;
MuMatrix32 was untouched.

Next: the owner selects MuMatrix32 in the first-run settings window and can optionally run
`make -C mac-play/bundle install`. Notarization and a universal build are still open.


## MAC-PERF-007 (v7.3)

Branch `claude/mac-perf-v73`, worktree `~/Documents/mu-worktrees/mac-perf`. The soak "hitch" was a ~2.9 s
frame, likely a synchronous asset load. CPU contention causes frequent 100-300 ms frames, and v7.3 fixes them
with a HIGHEST render-thread priority. Terrain face sorting (bit 16384) cuts terrain draws about 20x and was
verified pixel-exact offscreen. Read the MAC-PERF-007 section of `research/mac-performance.md`. Next: busy-town
measurement, sorting the additive sprites, and the kit's `--hotpatch-mask` default (still 7599).

## MAC-PERF-008 (v7.4)

Branch `claude/mac-perf-v74`, worktree `~/Documents/mu-worktrees/mac-perf2` (local commit, not pushed). Sprite and
grass quads are batched by commutation (bit 65536), effect client-array enables are deferred (262144) and batches
entirely off screen are not drawn (524288); default mask 875951, verification bits 131072 and 1048576 (0 differences,
0 samples). Zoomed out now reaches 25 fps at load ~4 (v7.3: 24.4-24.8; 20-21 under load 8). The GPU is not the limit
(at most 10 ms queued per 40 ms frame, see the MAC-PERF-008 section of `research/mac-performance.md`). The setup kit
writes 875951 and `mu-autologin.sh` defaults to MTM-1. Next: the crowded MTM-1 boss scene (18-19 fps, CPU-bound),
culling meshes before the mesh loop runs, and a busy town.

