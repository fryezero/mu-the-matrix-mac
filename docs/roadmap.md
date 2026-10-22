# Roadmap (Wine track)

## Goal

Players with an Apple-silicon Mac download one file, install Mu The Matrix without CrossOver or Terminal, and play
at the game's 25 fps cap, with the official launcher, until the native port
([mu-the-matrix-native](https://github.com/fryezero/mu-the-matrix-native)) can replace it.

## Next

| ID | Work | Completion evidence |
|---|---|---|
| MAC-DMG-002 | Full install rehearsal from `Mu The Matrix.dmg` on a clean account: download, .NET, game, launcher, in world | Timed log, screenshots, no manual step |
| MAC-SIGN-001 | Developer ID signing and notarization (`SIGN_IDENTITY`, `NOTARY_PROFILE`) | `spctl -a` accepts the app and DMG; no "Open Anyway" step |
| MAC-HOST-001 | Host the DMG on the official site | Download page link; SHA-256 published |
| MAC-SECOND-MAC | Test on a second Mac (other chip / macOS 13-15) | Install and 25 fps check recorded |
| MAC-PERF-011 | Zoomed-out boss fight at 25 fps (needs 5-9 ms less work per frame) | Same-session A/B runs |
| MAC-APP-005 | Launcher "Hash Protection" 0xA4 dialog (paused by the owner) | Reproduced cause and fix |

## Done (historical rows, IDs from the combined repository)

| ID | Work | Completion evidence | Dependencies |
|---|---|---|---|
| MAC-CROSSOVER-001 | Implemented: original-launcher setup in a new win10/win32 bottle | Authored isolated setup, builtin WIC/GDI+, cloned-skin workaround, 8/8 synthetic image steps, 65.8-second launcher survival, test bottle deleted | Issue #39; GAME START and gameplay require owner validation; native acceptance gates unchanged |
| MAC-BUNDLE-001 | Published for review: "Mu The Matrix.app" (`mac-play/bundle`, `make mac-bundle`), an ad-hoc signed double-click launcher with settings (bottle, fast x87, resolution), preflight error dialogs and logs in `~/Library/Logs/MuTheMatrix` | Built from source; 112-check suite (stub CrossOver on macOS/Linux, bundle/plist/signature/icon and CLI dry run on macOS); one live start in MuMatrixKit to server select | Not notarized, host architecture only, no login tested; native acceptance gates unchanged |
| MAC-DMG-001 | Implemented: one-file player download `Mu The Matrix.dmg` (`make player-dmg`): the app bundles the pinned CX26 Wine runtime (`EMBED_RUNTIME`, LGPL notice), offers to move itself to Applications, shows one Install window with plain progress and starts the launcher when done; optional Developer ID signing and notarization | 268-check bundle suite (runtime embed, first-run wiring and jargon check, move hooks, a real hardened ad-hoc disk image); live checks of the real disk image (window, Gatekeeper message, move to Applications with eject, first-run window) | End-to-end install from the DMG not rehearsed yet (owner request); not notarized (no Apple Developer account; signed path tested ad hoc only); hosting the DMG is the owner's; native acceptance gates unchanged |
| MAC-KIT-001 | Published for review: reproducible Mac setup kit `mac-play/installer` (setup, verify, launcher script) for the MuMatrix32 layout | Pinned SHA-256 only (no DLLs), build from repository sources or user-supplied DLLs, no account/Keychain/path constants, 190-check synthetic suite on macOS and Linux CI, dry run against a real CrossOver tree, live run of the repository version in a throwaway bottle to server select (all three DLL paths, fast x87; five bugs fixed) | Issue #63; the owner's local copy was live-validated (reported) and the repository version was run live only to the server-select screen (not logged in), so login and in-world play of a repository-built kit bottle are still unrepeated; fast-x87 and anti-cheat variants are TODO hooks; native acceptance gates unchanged |
| MAC-PERF-006 | Published for review: Claude v7.2 precise frame-pacing waits (waitable timer for bit 1024), with the background-Sleep-coalescing cause of 17-22 fps | No new patch site or original byte, source-only CI compile, 4 new portable tests; reported 25.00 fps over 140 s in the background and 24.95 frontmost | Issue #61; runtime figures are supplied single-host reports; other hosts, longer runs, Windows equivalence and anti-cheat unverified |
| MAC-PERF-005 | Published for review: Claude v7.1 mesh-draw native loop, light precompute, frame pacing and zero-copy batches, with the 44.8% attribution corrected to about 3% | Three patch-site digests pinned, private regeneration and instruction-identical private rebuild, source-only CI compile, 5 new portable tests; reported zero mismatches over about 9.5M call-stream/8.2M direct/2.5M light verification meshes | Issue #59; runtime figures are supplied single-host reports; 0x20/0x200000 and 0x8000 paths, other inputs, Windows equivalence and anti-cheat unverified; no single hotspot left under the 25 fps logic cap |
| MAC-PERF-004 | Published for review: existing Claude v7.0 CPU hotpatch sources and local regeneration | Nine helper patches, 18,583 inline/50,977 peephole sites reproduce exact private tables; source-only CI compile and portable tests | Issue #57; stacked on OPEN PR #52; reported runtime observations only; mesh C replacement, Windows equivalence and dual anti-cheat builds remain future work |
| MAC-PERF-003 | Implemented: default-on mugl immediate-mode OpenGL batching | 361 exports, host conversion tests, setup-owned bottle deployment, matching hashes at 1/4/16 quads per block and GL state regressions | Issue #51; owner in-world performance/stability, general GL behavior and native rendering remain open |
| MAC-PERF-001 | Implemented: opt-in fast x87 cache build and launcher path | Pinned external commit, matching synthetic checksum, activation log, authored FP/GL probes, preserved idle/display guards and tested fallback | Issue #45; actual patched launcher-to-main forwarding, in-world FPS, precision and anti-cheat compatibility remain unverified |

Later milestones (MAC-PERF-007 to 010, MAC-APP-001 to 006, MAC-FREE-001) are recorded in
[status](status.md), [handoff](handoff.md) and the research notes.
