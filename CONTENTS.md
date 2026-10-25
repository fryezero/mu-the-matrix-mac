# Mac Optimizations

This is the single Wine-patch repository, formerly `mu-the-matrix-mac`. It was moved here on 2026-10-25.
The existing Git history and remote are preserved. The source includes both merged crowd-performance passes.

Launcher-specific fixes and the blank-panel repair command are gathered in `Launcher Patches/`.
Read `Launcher Patches/README.md` for the individual fixes and rollback instructions.

## Current patch source

| Folder or file | What it contains |
|---|---|
| `mac-play/hotpatch/` | CPU helper, inline and peephole patches; skinning and mesh drawing; frame pacing; terrain, effects, shadows and decals; visibility culling; JPEG and CRC acceleration; buffer lookup indexes. Start with its `README.md`. |
| `mac-play/mugl/` | Public OpenGL batching proxy, triangle handling and FPS display. |
| `mac-play/mumodes/` | Launcher/display proxy, window behavior and WIC stream compatibility fixes. |
| `mac-play/fast-x87.sh`, `mac-play/install-fast-x87.sh`, `mac-play/x87-main-only-wrapper.c` | Fast x87 runtime selection, installation and main.exe-only routing. |
| `mac-play/installer/` | Applies the DLLs, overrides and configuration to an installed game. Includes verification and runtime packaging. |
| `mac-play/bundle/` | Mac app and disk-image packaging that carry the installer and patch components. |
| `mac-play/diagnostics/`, `mac-play/machprof/`, `mac-play/automation/` | Graphics/CPU benchmarks, profiling and controlled test helpers. |
| `scripts/`, `tests/` | Build checks, publication audit and patch regression tests. |
| `docs/research/mac-performance.md`, `docs/research/mac-crowd-*.md` | Optimization history, measured results and remaining limits. |

## Local builds and supporting files

`Local Files/` is excluded from Git and contains the files moved from the shared tools folder:

- `mu-mac-tools/private/hotpatch-tables/`: generated patch tables and their private inputs.
- `mu-mac-tools/mugl/`, `hotpatch/`, `inliner/`, `peep/`, `perf9/`, `perf10/`: earlier implementations,
  compiled DLL versions and performance experiments.
- `mu-mac-tools/mscoree-builds/`, `mumodes/`, `installer/`: earlier launcher fixes and setup builds.
- `mu-mac-tools/fast-x87-package/`, `third_party/rosetta-timewalker/`, `third_party/rosettax87_jit/`:
  packaged fast x87 and its upstream source.
- `mu-mac-tools/downloads/`: existing decoder/graphics dependencies and .NET installer.
- `mu-mac-tools/backups-mac-app-004/`, `backups-mac-app-006/`: rollback files from earlier launcher fixes.
- `mu-mac-tools/GAME-LOCK.md`: shared rules and lock location for live tests.
- `winecx-26.3.0-mu1.tar.xz`: the existing packaged Wine runtime.
- `Earlier Wine Evidence/mac32/`: earlier Wine compatibility and FPS logs/captures from `main-exe-study/runtime/mac32`.
- `MOVE-MANIFEST.json`: file hashes and metadata used to verify this move.

Earlier compiled DLLs remain versioned historical builds. Build the current source with the verified private inputs
when preparing a new game patch. The synthetic DLL from `make mac-hotpatch` is for compilation checks only.
The private build recipe is in `mac-play/hotpatch/README.md`.

## Working here

```sh
cd "$HOME/Documents/MTM/Mac Optimizations"
make test
```

Keep optimization work here and preserve full visual quality. The old `../mu-the-matrix-mac` name and selected
paths in `../mu-mac-tools` are symlinks to these files. Opening a symlink shows the same file and uses no second copy.
The native port, character-stat tool and installed game folders retain their existing locations.
