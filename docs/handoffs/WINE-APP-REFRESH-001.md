# WINE-APP-REFRESH-001: owner app refresh

Prepared from Wine `origin/main` e6c06b6, with a pinned font build input and a shared self-check for the setup's
play-mu.sh. The owner's `~/Documents/MTM/MTM/Mu The Matrix.app` was read only and remains byte-identical.
The staged app is `~/Documents/MTM/mu-mac-tools/wine/staged/wine-app-refresh-001/Mu The Matrix.app`.
No hosted CI, no merge, no Desktop changes, no account login.

## What changes

A complete SHA-256 comparison found 7 changed, 4 added, 18 identical files, none removed. The full manifests are
beside the staged app. The comparison covers all files, including the signature.

Changed files relative to `Contents/`:

- `MacOS/MuTheMatrix`: rebuilt current Swift app. The old October 18 binary predates MAC-DMG-001, retains
  “Use Windows Layer File” and checks only three embedded components. The new first-run flow offers moving to
  Applications, one install window, and a bundled-runtime check. These UI changes come from current main.
- `Resources/mu-launch.sh` and `Resources/fast-x87.sh`: macOS/Rosetta/translator identity, automatic probe,
  validated/failed cache, plain-Rosetta fallback and explicit `--fast-x87-check` from WINE-FASTX87-002.
- `Resources/installer/setup-mu-mac.sh`: installs or compiles x87-smoke during setup/Repair.
- `Resources/installer/play-mu.sh`: delegates free-runtime starts to the same mu-launch.sh. Legacy CrossOver is
  unchanged. The setup source and bundle layouts both resolve the helper.
- `Resources/fast-x87/x87-main-only-wrapper`: rebuilt from current authored source. The old translator payloads
  are retained. No new rendering or frame-time improvement is claimed.
- `_CodeSignature/CodeResources`: new ad-hoc signature for the rebuilt bundle.

Added files: `Resources/fast-x87/x87-smoke`, `Resources/runtime/winecx-26.3.0-mu1.tar.xz`,
`Resources/runtime/COPYING.LIB`, `Resources/runtime/SOURCES.txt`.

Identical files: Info.plist, PkgInfo, AppIcon.icns; both DLLs; libtimewalker.dylib, runtime_loader,
libRuntimeRosettax87 and their four notices/source files; TwemojiMozilla.ttf and attribution; both copies of
mukit.sh; installer registry and verify script. The browser registration and colored-news-emoji fixes from
MAC-APP-007/008 were already installed and are preserved. No new crowd-performance DLL is included.

## Build inputs

The old bundle did not record build flags. Its exact bytes and the historical local symlinks establish these
reproducible inputs. Private payloads stay outside Git:

- `EMBED_MUGL="$OWNER/Contents/Resources/dlls/opengl32.dll"`, identical to
  `~/Documents/MTM/Mac Optimizations/Local Files/mu-mac-tools/mugl/builds/mugl-v77.dll`.
  SHA-256 `6efe0b602356b64d47516a418e5609576a778b46329ad637e871810394771daf`.
- `EMBED_MSCOREE="$OWNER/Contents/Resources/dlls/mscoree.dll"`, identical to the sibling local
  `mscoree-builds/mscoree-v3.dll`, SHA-256 `0cf77991cdc8a26aec90349fd3641747fa9d66564abc86a002c980041ec997b4`.
- `EMBED_FAST_X87="$OWNER/Contents/Resources/fast-x87"`. SOURCE.txt identifies rosetta-timewalker
  `ab1a6a032e488c0d6eade54ce70a02d653277810`. The three translator payloads are also byte-identical to the
  active prefix's copies. The wrapper is compiled again and x87-smoke is new.
- `EMBED_RUNTIME="$HOME/Documents/MTM/Mac Optimizations/Local Files/winecx-26.3.0-mu1.tar.xz"`.
  This is an addition to the old bundle, which had no embedded runtime. SHA-256
  `c50cb614576764fa0c08595d6901402353c1954f20b3b7ad997286727f116599`, matching the runtime already installed as
  `archive-c50cb6145767`. Future installs/repairs use this pinned CX26 archive instead of downloading CX24.
- `EMBED_EMOJI_FONT="$OWNER/Contents/Resources/installer/fonts/TwemojiMozilla.ttf"`, SHA-256
  `6d90152ee0d29e82fe2a87793af5aa4b7ad13e6538360889e141e81ed299ee8e`. The new optional input preserves the
  locally embedded MAC-APP-008 font. Ordinary builds without it retain the installer's pinned download fallback.

`OWNER="$HOME/Documents/MTM/MTM/Mu The Matrix.app"`. Build with `nice -n 10 make -j4 player-app`, those five
inputs, and `B="$HOME/Documents/MTM/mu-mac-tools/wine/staged/wine-app-refresh-001"`. Default plist fields are
identical to the owner's app. The Makefile signs ad hoc and runs `codesign --verify --strict` and `--check-bundle`.

## Live proof and restoration

2026-11-05 21:30–21:31 Central, macOS 27.2 build 26B123. Both lock paths and pgrep were clear; both distinct lock
directories were acquired for about 53 seconds. Launcher only, no client/login, no travel or game actions.
The staged Mac executable launched with MU_SKIP_MOVE=1 and a private copy of Launcher.plist with start-immediately
on, fast x87 on and resolution keep. No install/Repair was run. It used the existing free prefix and bundled
probe. The prefix's translator matches the staged translator; its existing wrapper was left alone.

The probe emitted `RosettaRuntimex87 built` and `x87 smoke: PASS` on its first attempt and wrote
`~/Library/Application Support/MuTheMatrix/fast-x87/validated`. The launch returned success after 6.66 s.
Two visually inspected 900×620 window-only PNGs show artwork, news with colored emoji and the green START
button. The elapsed time to the first screenshot was not separately timed. The explicit staged
`Resources/mu-launch.sh --fast-x87-check` passed in 0.34 s after the launcher was closed.

The owned launcher was stopped, then only its prefix's wineserver was stopped. Registry files, LauncherOption.if
and Launcher.plist were restored byte-identically from `rollback-settings/`. DisplayDeviceModeIndex remains 2.
Both locks were released and no owned process remained. The new validated record remains as requested; its identity
includes the staged probe path and will revalidate if the app moves. Owner-app before/after manifests match.

## Owner commands

Close the client and launcher. The script refuses a held lock or a matching process. The prepared local copy
is the same as the reviewed `scripts/refresh-player-app.py`. The agent did not run either command against the
owner app. Only disposable fake-app tests exercised swap and rollback.

```sh
python3 "$HOME/Documents/MTM/mu-mac-tools/wine/staged/wine-app-refresh-001/refresh-player-app.py" swap
python3 "$HOME/Documents/MTM/mu-mac-tools/wine/staged/wine-app-refresh-001/refresh-player-app.py" rollback
```

Swap verifies the candidate and its copy, creates and integrity-tests `owner-app-before-refresh.zip` beside the
stage, then replaces the app. If the final rename fails, it restores the previous directory. An existing zip
blocks another swap, preserving the first rollback. Rollback verifies and restores the archived app; the zip stays.
Neither command edits the prefix, settings or Desktop. The complete zip is created only when the owner runs swap.
After swapping, open the owner's app normally. If offered a move to Applications, choose Not Now to keep this
owner-selected path. Repair is unnecessary for the self-check because the bundled probe is used directly.

## Desktop report, read only

- `~/Desktop/Play Mu The Matrix.command` calls missing `~/Documents/mu-mac-tools/play-mu.sh`. Its comment describes
  the deleted CrossOver setup.
- `~/Desktop/Play Mu The Matrix (MuMatrixKit).command` calls the same missing path and forces the obsolete
  `MU_BOTTLE=MuMatrixKit` CrossOver branch.

Both should launch the owner's chosen app after the swap:
`open "$HOME/Documents/MTM/MTM/Mu The Matrix.app"`. Remove the old bottle exports if the owner updates them.
No Desktop file was edited or removed. The legacy local mu-autologin.sh is documented as deprecated for this
free-runtime app; no Keychain access or login automation migration was performed.

## Checks and limits

- Initial staged `make -j4 player-app`: 5.54 s, complete payload and strict ad-hoc signature checks passed.
- `make -j4 test` first run: 141.86 s, two test-fixture failures. The new synthetic font was still present when
  later installer tests expected the ordinary no-font fixture; its embed tests now run after those checks.
- Final `nice -n 10 bash scripts/local-macos-ci.sh`, with MAKEFLAGS=-j4: 140.24 s, passed. Its `make test`
  passed 369 installer checks, 305 bundle checks and 147 Python tests, zero failures/skips in the bundle suite.
  Python tests took 13.600 s; the make-test phase was not timed separately from the gate.
- The same gate built the Mac app, machprof, MinGW mugl, synthetic hotpatch and diagnostics; publication audit:
  189 staged files, zero rejections. No hosted CI was dispatched.
- Eight disposable-app swap/rollback tests are included in the 147: round trip with a real ditto zip, repeat-swap
  refusal, both locks, running-process refusal, invalid candidate, rename recovery, missing backup and restoring
  over an app whose current signature need not pass. No owner swap/rollback was performed.
- Final staged reassembly after a comment-only helper update: 1.90 s; strict signature and complete
  bundle checks passed again. The live run preceded only this comment change; executable behavior was unchanged.
- Live launcher start: 6.66 s; explicit self-check: 0.34 s. Both passed. Two small window-only PNGs retained.
- `git diff --check` passed. Final staged-index publication audit repeated after these documentation updates.

No fresh installation, notarization, second-Mac check, logged-in START click or frame-time A/B was run. The earlier
16.5 vs 37.4 ms Lorencia result belongs to WINE-FASTX87-002 and was not re-measured here. The staged app preserves
existing DLLs; it does not distribute the newer crowd-performance candidates. Protection modules and protocols
were not inspected. Remaining owner work: run swap, open the app, optionally play and use rollback if needed.
Remaining steward work: review and merge the PR. No native validator applies.
