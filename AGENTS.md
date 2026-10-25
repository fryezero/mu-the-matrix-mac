# Agent entry point (Wine track)

## Local workspace

The owner's checkout is `~/Documents/MTM/Mac Optimizations`. Read `../AGENTS.md` for the single-checkout rule
and `CONTENTS.md` when locating current patch code, private inputs or earlier builds.
`Local Files/` contains preserved owner files and is excluded from Git through `.git/info/exclude`.

## Mission

Keep the original Mu The Matrix Windows client easy to install and smooth to play on Apple-silicon Macs: the
player app and disk image, the installer kit, the free Wine runtime, the mugl OpenGL proxy and CPU hotpatches,
the mscoree launcher fixes and fast x87. The native arm64 reconstruction of the client is a separate repository,
[fryezero/mu-the-matrix-native](https://github.com/fryezero/mu-the-matrix-native); put native work there.

Start with `docs/status.md` and `docs/handoff.md`, then the README of the area you change (`mac-play/bundle`,
`mac-play/installer`, `mac-play/mugl`, `mac-play/hotpatch`) and its research note in `docs/research/`.

The owner authorizes merging changes into `main` once `bash scripts/local-macos-ci.sh` passes on the rebased
branch. There is no hosted CI (the workflow is manual-only; never dispatch it). Use PRs to keep the review record.

## Rules

- Never commit game files, the Wine runtime archive, DMGs, app builds, or DLLs built from the client (the private
  hotpatch tables and prebuilt mugl DLLs contain client-derived bytes). `scripts/audit_repository.py` checks the
  tracked tree; README screenshots under `docs/images/` are allowed only with their SHA-256 pinned there.
- Player-facing text (app strings, PLAYER-GUIDE.md) stays plain: no technical words; the bundle tests check them.
- Live game tests follow the shared game lock (`Local Files/mu-mac-tools/GAME-LOCK.md`): at most 3 minutes per run,
  window-only screenshots, never print or store the account password, never touch a client you did not start.
- Out of scope: the client's protection/licensing modules and the network encryption/login packets.
- Measurements: say which scene, runtime, mugl mask and load; label reported vs re-measured numbers.

At handoff, update `docs/status.md`, the relevant research note and `docs/handoff.md` (a short section) with the
change, the checks actually run and the next step.
