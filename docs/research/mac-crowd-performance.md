# Crowded rendering work, MAC-PERF-011

Measured 2026-10-23 on Apple M5, macOS 27.0.1 build 26A434, the free Wine runtime built from CrossOver 26.3 sources
(`wine --version`: `wine-11.0`), Apple OpenGL 2.1 Metal - 91.7. This is an offline rendering investigation. No game session, credentials,
server or protection module was used. The player's prefix and installed DLL were not changed.

## Changes

**Buffer lookup.** `shadow_of` linearly searched up to 8,192 shadow records; `buf_info` searched up to 4,096
metadata records. These searches occur on uploads and array-pointer conversion. `id_index.h` now indexes each
GLuint name to its existing row with bounded open addressing at at most half occupancy. Rows and shadow storage
do not move. Deletion still resets the row's contents and name reuse finds the same row, as before. No buffer
capacity, allocation policy or GL result is intentionally changed.

**Visibility scans.** When the first vertex was outside the view, the culler scanned every vertex to build its
bounding box. Batches of at least 128 vertices now test the middle and last vertex before that scan. An inside
sample keeps the batch. This can skip work but cannot introduce a new rejection. The prior clip planes, relative
margin, NaN fallback, matrix epochs and selection/feedback exclusions remain. The GL proxy and diagnostic share
`cull_geometry.h`; `probes=0` retains the old predicate for comparisons.

## Method

`glcrowd.c` uses authored textured triangle meshes, deterministic animation, changing textures and blended draws.
It can update many named buffers each frame. It contains no game assets, recovered binary bytes or account code.
A batch is a draw-sized synthetic mesh, not a player or monster. It does not simulate AI, client game logic,
complete pose/skill processing, network traffic or real combat.

Each comparison below ran old/new/new/old, 60 measured frames per process after eight warm-up frames, at 1280x800.
Times include copying the mesh, culling, GL submission, GPU completion and swap, with no 25 FPS sleep. Final-frame
readback is excluded from timing. Median columns average the two run medians; p95 uses the slower of the two runs.
The benchmark requests a zero swap interval and records the returned driver information. A compositor wait still
appears near 8.3 ms in small cases. Fast x87 is not injected into these SSE2-only diagnostic executables.

The culling-only cases call the shared kernel over builtin Wine GL. Buffer and combined cases load separate old
and new **synthetic** proxy builds with `full+vbo`; proxy load and active VBO emulation were confirmed in logs.
The baseline proxy is built from repository commit `53fa172`. The runner records executable/proxy hashes, Wine
version, load averages and each raw result locally. All variants use one fresh, self-owned disposable prefix per
comparison set. Every individual process has a 120-second timeout; the prefix is stopped by its exact path and
removed afterwards.

## Results

| Synthetic case | Old median | New median | Old / new worst p95 | New frames over 40 ms |
|---|---:|---:|---:|---:|
| 8,000 edge-crossing batches, 690 vertices, client arrays | 30.48 ms | 27.55 ms | 32.51 / 29.88 ms | 0 / 120 |
| 12,000 mixed visible/offscreen batches, 690 vertices, client arrays | 29.11 ms | 26.35 ms | 30.80 / 28.56 ms | 0 / 120 |
| 8,000 draws, 96 vertices, 2,048 updated buffers | 27.18 ms | 21.96 ms | 29.63 / 23.33 ms | 0 / 120 |
| 12,000 draws, 96 vertices, 2,048 updated buffers | 40.01 ms | 31.85 ms | 41.76 / 34.68 ms | 0 / 120 |
| 8,000 edge-crossing batches, 690 vertices, 2,048 updated buffers | 52.07 ms | 44.05 ms | 53.18 / 45.39 ms | 120 / 120 |
| 12,000 edge-crossing batches, 690 vertices, client arrays | 43.76 ms | 39.80 ms | 46.08 / 43.41 ms | 76 / 120 |

The 12,000-small-mesh buffer workload crossed from 64/120 frames over budget to 0/120. The much larger combined
workload remains above budget. Already-inside and entirely-offscreen controls showed no consistent material gain
or regression. These are two trials per path, not a confidence interval or a guarantee on another machine.

Every old/new framebuffer hash, draw count and cull count matched in all 48 timed runs across the comparison sets.
The runner correctly exits 3 for sets whose optimized p95 still exceeds 40 ms. Lower frame times in this harness
cannot establish 25 FPS in the actual client; its other CPU and rendering work is absent.

A further four ABBA runs used the actual private candidate and a private baseline, both linked with the existing
native JPEG implementation. At 12,000 draws of 96 vertices and 2,048 updated buffers, old/new median work was
39.89 / 32.98 ms, worst p95 was 41.40 / 36.89 ms, and frames over 40 ms were 54/120 / 1/120. Output hashes,
draw/cull counts and buffer lifecycle checks matched. This confirms the improvement in that DLL build, still
outside the game. It also shows why a passing p95 does not mean every frame meets the cap.

The isolated lookup microbenchmark, 24,000 lookups per synthetic frame, gave 8.38 -> 0.06 ms at 2,048 records and
33.69 -> 0.06 ms at 8,192. The culling microbenchmark with 12,000 batches of 690 vertices gave 4.11 -> 0.13 ms for
edge-crossing batches and 4.54 -> 2.45 ms for a half-offscreen mix; entirely offscreen was 4.68 -> 4.78 ms. These
microbenchmarks isolate helper cost and must not be presented as game-frame improvements.

Rejected alternatives: disabling the normal array made no measurable improvement at 12,000 draws; packing a
36-byte vertex format instead of the existing 48-byte format increased the probe's work from 44.48 to 54.68 ms.
Neither change was kept.

## Correctness and remaining limits

- 100,000 seeded perspective/nonfinite/mixed-size geometry comparisons equal an independent scalar form of the
  old predicate on the host, and another 100,000 passed in the actual Wine/i686 SSE build. Explicit cases cover
  small batches, clip margins, inside samples and boxes whose vertices are all outside but still cross the view.
- Index tests cover collisions, wraparound, a full table, row zero, 32-bit names, actual capacities and reuse.
- A Wine lifecycle check deletes and reuses buffer names, updates part of their contents and reads back size and
  bytes on builtin GL and both proxy builds. The checks and framebuffer comparisons pass.
- `glcstate` ran 150 frames on builtin GL and both private proxies, at mask 0 and at mask 1841152, which enables
  deferred client arrays, zero-copy/strided arrays, culling and its sample-query verification. The original
  diagnostic and a local variant with 192-vertex perspective batches each matched all five output hashes with
  zero GL errors. No private stats log was enabled. Sample-query counts were not captured.
- `glstride` and `glcaps` framebuffer hashes match builtin GL, baseline and candidate. `glcaps` query checksum
  also matches. All 17 `glcheck` framebuffer hashes match between baseline and candidate. Five differ from builtin
  GL on both proxies: incomplete primitives, display-list/attribute restore, first-provoking flat strips and fans,
  and wireframe quads.
- `glcheck` reports **two existing state failures** on both baseline and candidate, with no GL errors. The builtin
  passes. The failures are a current-color check and VAO buffer-pointer/binding state, outside this optimization.
  This is an unresolved baseline limitation, not a passed general-OpenGL-equivalence test.
- No new game hook, instruction patch, game-state simulation, protection change, credential access or network
  packet handling was introduced.
- The private candidate was built locally with `LJT_DIR` from the existing pinned libjpeg-turbo recipe. Cached
  inline/peephole tables matched their canonical record digests and their original bytes matched the cached text.
  All nine helper replacements matched the current authored assembly with its required padding. Eleven original
  patch sites and the xform prologue matched the existing hash pins. Only the ignored copy of the patch-site
  header was regenerated. The owner's cache remained unchanged. This reused verified cached text, not a fresh
  full-dump regeneration. The compiled game-patch harness was not executed; game hooks were not tested live.
- `bash scripts/local-macos-ci.sh` passed: 125 Python tests, 340 installer checks, 268 app/bundle checks, Mac
  builds, MinGW cross-builds and the publication audit, 177 staged files and zero rejections. No hosted CI ran.

Next: profile controlled crowded gameplay with the same view, gear, effects and runtime using the private candidate.
Verify frame tails and visual output
before updating a player build. The heavier simulated cases still exceed 40 ms, so the universal 25 FPS target
remains unachieved.

## Reproduce

Build the normal synthetic proxies from this branch and the baseline checkout. Never put a synthetic DLL in a
player installation; it has no game patch tables. Supply the path to a free Wine binary with adjacent wineserver.
All output directories below must be new.

```sh
python3 scripts/run-crowd-bench.py --wine /path/to/wine/bin/wine \
  --out runtime/crowd-arrays --frames 60 --batches 8000 12000 --scenes mixed edge offscreen inside

python3 scripts/run-crowd-bench.py --wine /path/to/wine/bin/wine \
  --out runtime/crowd-buffers --frames 60 --batches 8000 12000 --vertices 96 --scenes inside \
  --buffers 2048 --proxies /baseline/build/synthetic/opengl32.dll mac-play/hotpatch/build/synthetic/opengl32.dll \
  --require-budget
```

Local evidence is ignored under `runtime/crowd/`, `runtime/crowd-abba/`, `runtime/buffer-abba/`,
`runtime/buffer-extreme-abba/`, `runtime/combined-abba/` and `runtime/private-buffer-abba/` in the task worktree.
The private culling integration checks are under `runtime/private-cull-regression/`.
The private candidate remains at ignored `mac-play/hotpatch/build/private/opengl32.dll` and was not installed.
No DLL, raw log or prefix is committed.

## Follow-up

The [2026-10-24 investigation](mac-crowd-followup.md) includes an isolated live check of this candidate and further
rendering experiments. Its light portal-area scene settled at the cap; crowded combat remains unverified.
