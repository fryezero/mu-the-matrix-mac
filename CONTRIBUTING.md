# Contributing

Read [AGENTS.md](AGENTS.md) and [the roadmap](docs/roadmap.md). Useful contributions: install and play reports
from other Macs (chip, macOS version, fps in a named scene), installer fixes, performance work with measurements,
and clearer player documentation.

## Before changing code

1. Open or pick an issue with an observable problem or goal and how you will check it.
2. Use a branch. Keep changes to one area (app, installer, mugl/hotpatch, launcher proxy) where possible.

## Deliver a reviewable change

Explain what changed for players, how it was tested and what remains uncertain. Run
`bash scripts/local-macos-ci.sh` (it runs `make test`, builds the app, the profiling tools and, with
`brew install mingw-w64`, the Windows cross-builds, then the publication audit). For performance claims give the
scene, the runtime, the mugl mask and same-session before/after numbers.

Never attach logs that contain account names or passwords, game files, or DLLs built from the client.
