# Further crowd profiling, MAC-PERF-012

Measured 2026-10-24 on the same Apple M5 and macOS 27.0.1 build 26A434 as
[MAC-PERF-011](mac-crowd-performance.md), using the free CrossOver 26.3-source Wine runtime reporting
`wine-11.0` and Apple OpenGL 2.1 Metal - 91.7. This round found no additional renderer change with a consistent
benefit over the published zero-copy path. All experimental renderer changes were removed. Full visual quality
and the 25 FPS cap are unchanged.

## Offline investigation

The 8,000-draw, 690-vertex, 2,048-buffer edge-crossing workload still exceeded 40 ms. With the published proxy
and the current visibility probes, the two initial medians were 43.58 and 43.51 ms. A sampled phase probe put
roughly 25 ms inside draw submission, 8.6 ms in buffer updates and 5.2 ms in GPU completion. Sampling adds overhead
and estimates different calls; those figures are not an additive, exact frame budget.

Comparisons used authored meshes and separate disposable prefixes. Old/new/new/old runs used 60 measured frames
following eight warm-up frames at 1280x800, unless noted below. Completed rendering comparisons checked output
hashes and draw/cull counts. These meshes do not model a complete player, AI, skill logic or combat traffic.

| Alternative | Observed result | Decision |
|---|---|---|
| Unrolled SSE copies | At 33,120 bytes, warmed CRT copy took 8.29 ms versus 8.14 to 8.17 ms for SSE per 8,000-copy microbenchmark frame. Actual live upload volume was much smaller. | Too little benefit to justify another copy implementation. |
| Sequential indexed draws | 44.06 ms median with array draws versus 45.42 ms with sequential indices; output hashes matched. | Slower. |
| Apple threaded GL engine | Successfully enabled, 44.20 ms versus 45.47 ms; output hashes matched. | Slower on this host and workload. |
| Apple shared vertex-array range | Extension not advertised; required entry points unavailable. | Could not run on this driver. |
| Unsynchronized mapped-range buffer | Required entry point unavailable in this legacy context. | No timing comparison. |
| Direct 36-byte records, without a packing pass | A layout-only probe improved 40.32 to 38.40 ms at 12,000 client-array draws, and 45.10 to 41.58 ms at 8,000 buffered draws. | Investigated in the actual mesh emitter before accepting it. |

Apple documents both the worker-thread setup cost and the need to measure its benefit in
[Concurrency and OpenGL](https://developer.apple.com/library/archive/documentation/GraphicsImaging/Conceptual/OpenGL-MacProgGuide/opengl_threading/opengl_threading.html).
The proposed shared-array path would have required explicit memory-lifetime and synchronization management under
[APPLE_vertex_array_range](https://registry.khronos.org/OpenGL/extensions/APPLE/APPLE_vertex_array_range.txt).
Neither option is enabled by this change.

The compact-emitter prototype generated texture coordinates, colors and positions directly as 36-byte records,
with one current normal for the whole mesh. Its synthetic fixture exercised the actual authored mesh loop with
owned records, without loading a game binary. It passed 144 attribute-calculation comparisons and eight paired
rendering checks covering lighting, normalization, color material, flat shading, a shader reading normals/colors,
array restoration and expansion back to the canonical layout. Another 100,000 record-store tests passed in the
i686 Wine/SSE build, and both record strides passed 100,000 host culling comparisons.

The first emitter timing comparison accidentally disabled the existing zero-copy flags on the baseline. Its apparent
large improvement was invalid as a comparison with the production settings. With both zero-copy and strided arrays
restored, the emitter results were:

| Mesh draws of 690 vertices | Existing median | Compact median | Existing / compact worst p95 |
|---|---:|---:|---:|
| 4,000 | 24.04 ms | 24.43 ms | 26.69 / 27.08 ms |
| 6,000 | 35.56 ms | 35.28 ms | 38.04 / 37.43 ms |
| 8,000 | 46.39 ms | 46.18 ms | 50.20 / 48.99 ms |

Each median averages two runs; p95 uses the slower run. Output hashes matched. The small differences did not
justify a new mesh-storage and submission path, especially with a regression at 4,000 draws. The compact path,
its mode token and fixture exports are absent from the production diff. Its source and measurements remain only
in the ignored experiment directory.

A macOS sampling attempt captured Wine's startup helper rather than the renderer. It was discarded. A separate
live 32-bit sample identified builtin GL calls, but thread suspension and the optional `+finish` diagnostic distort
frame timing. Samples from those intervals are not evidence of ordinary gameplay FPS.

## Isolated live check of MAC-PERF-011

A private copy of the installed prefix was created with APFS clones. The original executable and proxy hashes were
recorded and verified unchanged afterwards. All process shutdowns used the disposable prefix's explicit wineserver;
the shared game lock was released between completed sessions. The disposable copy has been deleted.

The comparison used the old installed proxy and the published MAC-PERF-011 candidate, both with native JPEG support.
The old proxy's code and read-only-data sections matched the prior `53fa172` baseline build. Runtime, mask 380460463,
`full+vbo+time`, and the installed main-only fast-x87 wrapper configuration were held fixed. The candidate was placed
only in the disposable copy. No player installation was updated.

Nighty remained at Tormenta Island 128,120. This was a light portal-area scene with character and ambient effects,
not a crowded boss fight. Window captures confirmed that the news modal was closed and that the F6 camera was
active for the zoomed view. Captured window size was 1968x1280, including the title bar. Animated captures are
visual smoke checks, not pixel-equivalence comparisons.

The qualifying old and candidate sessions lasted 138 and 136 seconds, including launcher and login. Earlier attempts
were excluded: one lacked the automation helpers, one ended after an incorrect host-process-name lookup, and one
kept the news modal open while using `+finish`. The corrected check identified the game by its command line and
verified open files under the owned prefix before profiling it.

Both qualifying builds settled at a reported 25.0 FPS. In the last six two-second periods after profiling ended,
the zoomed-view work ranges were 36.76 to 37.63 ms for the old build and 36.47 to 37.27 ms for the candidate. Their medians
were 37.18 and 36.85 ms. One old/new session with changing effects does not establish a significant speedup.
Camera transitions and first-sight loading still produced long frames; an immediate post-zoom capture showed a lower
counter before the scene settled. This is not a claim that every frame met 40 ms.

## Benchmark fixes retained

- `--cull-probes 0|1` can select the same visibility algorithm for both DLL variants. Result records now distinguish
  the DLL variant from the visibility-probe setting, and the budget verdict uses only candidate-variant results.
- Cleanup accepts wineserver's no-running-server exit code, then still requires its scoped wait to finish. An early
  compiler/version failure no longer leaves an owned prefix behind or hides the original error with a cleanup error.
- Nine focused runner tests passed, including same-culler comparisons, a slow baseline with a passing candidate,
  cleanup after early failure, output mismatch rejection and existing-directory refusal. Three regressions fail on
  the prior runner. `bash scripts/local-macos-ci.sh` passed all 128 Python tests, 340 installer checks, 268 app/bundle
  checks, the Mac and MinGW builds, and the publication audit: 178 staged files, zero rejections. No hosted CI ran.

For a DLL-only comparison using the current visibility algorithm on both sides, add `--cull-probes 1`:

```sh
python3 scripts/run-crowd-bench.py --wine /path/to/wine/bin/wine \
  --out runtime/next-crowd-comparison --frames 60 --batches 8000 --vertices 690 --scenes edge \
  --buffers 2048 --cull-probes 1 --proxies /baseline/opengl32.dll /candidate/opengl32.dll --require-budget
```

Local evidence is ignored under `runtime/crowd2/`. Private binaries, captures, game files and raw logs are not
published. The only code changes retained this round are the benchmark fixes.

Next: the universal full-quality 25 FPS target remains open. The high-load synthetic cases still exceed 40 ms;
the live portal-area check does not establish performance in a crowded fight.
