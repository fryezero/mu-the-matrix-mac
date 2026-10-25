# Current status (Wine track)

## Launcher news emoji restored, 2026-10-25

MAC-APP-008 replaces the missing-glyph boxes in news titles with the original colored emoji. The tested fix installs
Mozilla's verified COLR/CPAL vector font in the Wine prefix; raster emoji fonts did not work in this browser.
Setup, Verify, the selected MTM app and the local launcher repair kit now include the fix and attribution.
See [font provenance and live evidence](research/mac-launcher-emoji.md).
The final fresh launch showed colored news symbols and enabled START in 12.7 seconds. The prefix reports
35 PASS, 2 optional-tool WARN and 0 FAIL. Local CI passed 136 Python tests, 369 installer checks, 268 app checks,
Mac/MinGW builds and the publication audit. Owned launcher tests are closed; the owner can reopen normally.

## Launcher artwork/news restored after reinstall, 2026-10-25

MAC-APP-007 fixes the Windows MU launcher's blank artwork/news panel. The fresh prefix lacked full Wine mshtml
registration despite having the v3 proxy and official skin. Registration restored the live page; setup now repairs
it after .NET and verification checks it. The selected MTM Mac app's embedded installer was updated.
Launcher patches, repair commands and local rollback files are gathered in `Launcher Patches/`.
See [the finding](research/mac-launcher-browser.md).
Verified artwork/news and enabled START after a cold launch. Local CI passed 132 Python tests, 354 installer checks,
268 app checks, Mac/MinGW builds and the publication audit. The fixed prefix reports 33 PASS, 2 optional-tool WARN,
0 FAIL. No account login or combat test was needed.

## Local consolidation, 2026-10-25

The single Wine checkout is now `~/Documents/MTM/Mac Optimizations`. Current patch source, earlier local builds,
private tables, profiling tools, fast-x87 dependencies and the packaged Wine runtime are together there.
See [`../CONTENTS.md`](../CONTENTS.md). Files were moved, with old paths retained as symlinks; no checkout was copied.
The native port and installed games retain their locations. Full visual quality remains required.
Verification: moved files retained their hashes and metadata, compatibility links resolve, eight relocated helpers
pass shell syntax/path checks, and `make test` passed from the folder with spaces, including all 128 Python tests
and the installer/app suites. The repository audit reported zero rejections. No live game test was run.

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

## Repository split, 2026-10-21

This repository holds the Wine track of the Mu The Matrix Mac project: `Mu The Matrix.app`, the player disk image,
the installer kit, the free Wine runtime packaging, the mugl OpenGL proxy, the CPU hotpatches, the mscoree proxy,
fast x87 and their diagnostics, tests and research notes. It was split out of
[mu-the-matrix-native](https://github.com/fryezero/mu-the-matrix-native) (formerly `mu-the-matrix-recovery`) with
its full history (`git log --follow` works for every file under `mac-play/` and `docs/research/`). Issue and
PR numbers before the split (#39 to #136) refer to that repository. The read-only live-state readers
(`objread`, `memread`, `lightread`, `langread`) serve the native reconstruction and stayed there.

## Summary

- **Playable today.** The original Windows client (launcher, server select, login, gameplay) runs on Apple-silicon
  Macs through free LGPL Wine (CodeWeavers' CrossOver 26.3 sources, built by `installer/packaging/build-wine.sh`).
  No CrossOver licence is needed.
- **One download.** `make player-dmg` builds `Mu The Matrix.dmg` (about 130 MB): the app bundles the runtime, the
  mugl proxy, the mscoree proxy and fast x87, installs .NET 4.8 and the game from one window and opens the official
  launcher.
- **25 fps.** The client caps itself at 25 fps (a 40 ms logic step). With mugl v7.7 and fast x87 the tested towns,
  hunting spots and the default-view Tormenta boss fight hold the cap; the zoomed-out boss fight still runs at about
  20 to 23 fps. Measurements: [mac-performance.md](research/mac-performance.md),
  [mac-free-runtime.md](research/mac-free-runtime.md).
- **Open.** A full install rehearsal from the disk image, Developer ID notarization (removes "Open Anyway"), hosting
  the DMG, testing on a second Mac, the rare launcher "Hash Protection" 0xA4 dialog (paused).

## Details

Without CrossOver (MAC-FREE-001): the original client also runs on free LGPL Wine, CodeWeavers' open-source
Wine running a 32-bit prefix in wow64 mode; upstream WineHQ builds stop during the protected start. A self-built
CrossOver 26.3 Wine matches CrossOver (18.1 vs 18.3 fps in a busy scene) and reaches the 25 fps cap with fast x87.
The installer and "Mu The Matrix.app" now default to this free runtime; a fresh install with the official installer
was rehearsed end to end (44 min 50 s, mostly the 2.2 GB download) and reached the world.
[Finding](research/mac-free-runtime.md), [player guide](../mac-play/PLAYER-GUIDE.md).
Launcher windows on macOS (MAC-APP-004): the mscoree proxy v2 keeps the launcher's TopMost news panel from
floating over the game (Wine's Mac driver puts topmost windows above the Dock even while inactive) and makes the
launcher's minimize-to-tray a Dock minimize that a Dock click restores; verified live in the free runtime and
MuMatrix32. [Finding](research/mac-launcher-windows.md).
Official launcher skin (MAC-APP-006): the server's `Template.design`, disabled since the first Mac setups, works
again. Its crash was a Wine 11 JPEG decoder bug (NULL `pcbRead` to WPF's managed stream), worked around by mscoree
proxy v3 (`wicfix.c`); the installer restores the skin. Verified live in both runtimes (skin, server time, GAME START,
Dock restore). [Finding](research/mac-launcher-skin.md).
One download for players (MAC-DMG-001): `make player-dmg` builds `Mu The Matrix.dmg` (about 130 MB) with the app,
an Applications link and a generated drag-to-Applications window. The app bundles the pinned CX26 runtime (no runtime
download, no hosting, 25 fps), offers to move itself to Applications, installs from one window with plain progress and
opens the official launcher when done. The full install from the disk image has not been rehearsed yet.
[Finding](research/mac-dmg-installer.md).
Launcher "Hash Protection" code 0xA4 dialog (MAC-APP-005, paused by the owner): rare (2 in about 135 test starts),
not caused by a file left half-written by a forced kill (snapshots show none; it also follows clean closes). The
leading, unconfirmed hypothesis is a macOS-specific short read in Wine's `NtReadFile` retry path. No fix yet.
[Finding](research/mac-launcher-hash-dialog.md).

The original client works on Windows. Earlier isolated CrossOver `win10_64`
starts fail with a Rosetta selector error. A new `win10`/win32 compatibility path
uses .NET 4.8, builtin WIC/GDI+, WPF software rendering and the default IGCN skin
in a cloned installation (the installer kit shows the server's official skin again
with the mscoree proxy v3, [finding](research/mac-launcher-skin.md)). The authored setup and local validation are recorded
in [the CrossOver finding](research/mac-crossover-32bit.md), issue #39.
The fresh test bottle passed all eight synthetic image-pipeline steps, kept
the launcher alive for 65.8 seconds, and was deleted after validation.
The owner now reports GAME START, login and gameplay in MuMatrix32. This is
original-client compatibility gameplay, not a recovered native build. Issue #42
adds an idle-bottle startup reset and monitor validation. An injected stale
source-to-monitor link reproduces the exact Settings exception; the guarded
reset rebuilds the link and Settings opens again in MuSettings-test. Both fresh
win32 and win10_64 bottles have valid monitor registrations. Natural sleep/display
change recovery during an active game remains unverified. MuMatrix32 is reserved
for Claude's frame-rate work and was not modified by this task. No Windows PC is currently available. The separate Mac-only Linux
guest still has outbound networking blocked and reaches an unresolved localhost
connection. Native Windows capture/equivalence
remains unverified, although the optional Windows helper builds and its own
memory/hash smoke checks pass under Wine.

MAC-PERF-001, issue #45 / PR #47, adds an opt-in pinned Rosetta Timewalker
cache build, matching-checksum x87 self-check, authored PE32 transform/GL probes
and launcher selection with plain CrossOver fallback. MAC-PERF-002, issue #48,
adds an authored MIT wrapper that defaults fast translation to arguments
containing `main.exe`. MuTheMatrix.exe and .NET dependencies use the real loader;
the unfiltered fast runtime hangs on .NET. The installer builds/signs and
fingerprints our wrapper in the cache without editing pinned upstream source.
Caller substring overrides and an empty apply-to-all override are supported.
The idle-process guard, prefix-scoped reset and plain monitor check remain.
The real launcher produced its normal window in setup-owned MuX87Filter-test
under required-fast selection with the default filter. The matching-filter
benchmark measured 279.1 Mverts/s fast versus 2.7 plain with matching checksum
3.904312. The test bottle was removed. All 163 portable tests pass, with fourteen
private-input skips; both review axes and the publication audit pass.

MAC-PERF-003, issue #51, adds the authored MIT mugl OpenGL batching proxy,
361-name export generation, host-tested primitive conversion and a default-on
setup step with `MU_GL_BATCHING=0` opt-out. Deployment checks Wine's system32
builtin marker and records the proxy SHA-256. The setup-created MuMugl-test
bottle passed three plain/proxy framebuffer comparisons at 20,000 quads/frame:
38.7 to 118.7 FPS for one quad/block, 65.2 to 118.9 for four, and 76.8 to 119.6
for sixteen. All thirty-six GL regression hashes match, with zero state failures or
GL errors. Setup off/on/rerun checks pass. The launcher started main.exe with
active batching and a 25.0 FPS log; one interval reduced 999,569 blocks to 8,966
draws. The test bottle was removed. Owner in-world testing remains open.
The x87 hypothesis is superseded by Claude's reported in-world EIP profile,
which places 73% of main-thread samples in OpenGL; fast x87 did not improve
in-world FPS. These figures are compatibility evidence, not native recovery.

See [measurements and limits](research/mac-performance.md) for local checks and
Claude's separately supplied launcher-to-main/profile observations. Post-patch
in-world FPS remains owner testing. MuMatrix32 was not touched. This improves
original-client compatibility; native source recovery acceptance gates are
unchanged.

MAC-PERF-004, issue #57, publishes Claude's opt-in v7.0 CPU hotpatch source
stacked on open PR #52. Local pinned-input generation reproduces nine helper
patches, 18,583 inline sites and 50,977 peepholes. Original byte tables and the
xform prologue stay private; CI uses empty tables with game hooks disabled.
Claude reports 20.5 FPS at mask 0, 24.1 at mask 7 and 24.7 at mask 15 in the
same approximate hunting area, and zero skinning comparison mismatches over
more than one million in-game calls. These are prior single-host reports,
not rerun measurements; the 44.8% mesh-draw attribution it cites was later
corrected (below). Default setup still uses #52. No running game, bottle or registry
was changed. [Evidence and limits](research/mac-performance.md#mac-perf-004-claude-v70-in-process-cpu-hotpatches).

MAC-PERF-005, issue #59, publishes Claude's opt-in v7.1 source: a native
replacement of the per-corner loop of mesh draw routine `0x012b8d1d`, a native
light-table precompute, a frame-pacing fix, direct batch append and zero-copy or
strided batch arrays, plus the `glstride` framebuffer-hash test. The three small
original patch-site byte sequences stay private (SHA-256 in `targets.json`,
generated into an ignored header); CI builds with zero tables and no game hooks.
Local checks: private regeneration matches the pinned digests and a private rebuild
has an instruction stream identical to Claude's DLL; neither was run. Claude reports
zero mismatches over about 9.5M call-stream, 8.2M direct-append and 2.5M light-table
verification meshes, equal framebuffer hashes at five masks, and, in the default
7599 mask, 24.1 fps at the hunting spot (22.6 at mask 15) with 33.8 ms of work. These
are supplied single-host reports, not rerun. The correction: the v7.0 finding that
the routine took 44.8% of main-thread self time came from a profile of a build
without frame pointers and charged mugl's own code to the caller; the routine's true
self time is about 3%. 25 fps remains the fixed 40 ms logic-step cap, with no single
dominant hotspot left. Default setup still uses #52. No running game or bottle was
changed. [Evidence and limits](research/mac-performance.md#mac-perf-005-claude-v71-mesh-draw-loop-frame-pacing-and-zero-copy-batches).

MAC-PERF-006, issue #61, publishes Claude's v7.2 `mugl.c`: the frame-pacing bit now
waits on a waitable timer instead of Wine's `Sleep`. Claude's diagnostic builds traced
the 17-22 fps seen with pacing on (28 ms of work) to macOS stretching Wine `Sleep`
calls (7-14 ms took 17-45 ms) whenever the game is not the frontmost Mac app, not to
the client's inactive throttle or a double sleep. Claude reports 25.00 fps in the
background over 140 s with 99.6% of frames at 38-42 ms, versus about 24.5 fps with half
the frames late for v7.1, and 24.95 fps frontmost; the logic still runs at 25 Hz. No new
patch site or original byte is added. A later 6-minute background soak at a hunting spot (MU Helper on) kept a 25.00 fps median with no growth in memory and no deaths or disconnects; one 2-second interval dipped to 6.3 fps and recovered, and an hour-long session is still open. These are supplied single-host reports, not rerun;
the new code was only compiled here. Default setup still uses #52. No running game or
bottle was changed. [Evidence and limits](research/mac-performance.md#mac-perf-006-claude-v72-precise-frame-pacing-waits).

MAC-KIT-001, issue #63, publishes the owner's reproducible Mac setup kit as
`mac-play/installer/`: an idempotent setup, a read-only verify, a launcher script and a
synthetic test suite that reproduce the hand-built MuMatrix32 layout in a new win32
bottle. The owner reports that the local copy built a fresh bottle in 3 min 44 s with
.NET 4.8 and ran in world at parity or better than MuMatrix32, after six live-found bugs
were fixed. This publication replaced machine-specific siblings with repository sources and
parameters, ships no DLL (pinned SHA-256 only; prebuilt v7.x DLLs are user supplied), keeps
account and Keychain names out of the tree, and runs its 180-check suite on macOS and Linux
in CI. A follow-up live run of the repository version in a throwaway bottle (`claude/kit-live-fixes`)
covered the public build, the private hotpatch build, a prebuilt `--dll-dir` and `--fast-x87` up to the
server-select screen (25.0 fps with the hotpatch builds, 19-20 fps with the public proxy; not logged in
because the account was in use elsewhere), found five bugs (non-reproducible PE timestamps, a
`--dll-dir` that demanded `mscoree.dll`, a test that depended on the checkout, a log shared by all
bottles, and verify ignoring the launcher's fast-x87 setting) and fixed them; the suite is now 190 checks.
It sits beside the older `setup-crossover-32bit.sh`. The throwaway bottle was the only bottle created;
MuMatrix32 was not touched.
[Evidence and limits](research/mac-crossover-32bit.md#reproducible-setup-kit-mac-kit-001).
