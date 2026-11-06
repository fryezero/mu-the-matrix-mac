# Setup and checks

## Tools

- macOS on Apple silicon with the Xcode Command Line Tools (clang, swiftc, iconutil, hdiutil).
- Python 3.9+ (standard library only).
- Optional: MinGW-w64 for the Windows cross-builds (`brew install mingw-w64`): mugl, the hotpatch DLL, the mscoree
  proxy and the GL/x87 benchmarks.

## Checks

```sh
make test                        # shell syntax, installer and app test suites, Python tests; no game files needed
bash scripts/local-macos-ci.sh   # the merge gate: make test + app build + machprof + cross-builds + audit
```

The installer suite (`mac-play/installer/tests/test-mukit.sh`) and the app suite
(`mac-play/bundle/tests/test-bundle.sh`) use fake bottles, fake runtimes and dry runs: they never start Wine or the
game. The suite also requires that the checkout's own `mac-play/mugl/build` does not exist (the installer builds
mugl from a copy); `local-macos-ci.sh` therefore cross-builds mugl and the hotpatch DLL out of tree.

## Builds

| Target | Output | Notes |
|---|---|---|
| `make mac-bundle` | `mac-play/bundle/build/Mu The Matrix.app` | Development app, ad-hoc signed, nothing embedded |
| `make player-app EMBED_MUGL=… EMBED_MSCOREE=… EMBED_FAST_X87=… EMBED_RUNTIME=…` | Player app | See [the app README](../mac-play/bundle/README.md) |
| `make player-dmg … DMG=…` | `Mu The Matrix.dmg` | Optional `SIGN_IDENTITY`, `NOTARY_PROFILE` |
| `make mugl` | `mac-play/mugl/build/opengl32.dll` | Public batching proxy (no game tables) |
| `make mac-hotpatch` | `mac-play/hotpatch/build/synthetic/opengl32.dll` | Synthetic build; the private build needs the owner's client dump ([hotpatch README](../mac-play/hotpatch/README.md)) |
| `make mac-diagnostics`, `make machprof` | benchmarks and profilers | For performance investigations |

Private inputs (the client dump for the hotpatch tables, the prebuilt `mugl-v7x.dll`, the mscoree proxy build, the
fast x87 package and the runtime archive) stay outside the repository.

## Refresh an existing owner app

See [WINE-APP-REFRESH-001](handoffs/WINE-APP-REFRESH-001.md) for the staged build, exact owner commands,
comparison and rollback. `scripts/refresh-player-app.py swap` is owner-run only. It checks both shared game locks
and running processes, verifies the candidate, and creates and tests a complete zip of the existing app before
replacing it. `rollback` restores that zip. Neither mode starts Wine or changes the prefix.

The historical `mu-autologin.sh` in the local tools is deprecated for the free runtime. It hardcodes CrossOver and
the removed MuMatrix32 bottle. Do not use it to test this app. This refresh does not migrate login automation and
never accesses the Keychain. Start the staged app manually for any later owner login check.

For the free runtime, `mac-play/installer/play-mu.sh` now delegates to `mu-launch.sh`, including its identity cache,
plain-Rosetta fallback and `--fast-x87-check`. Logs move to `~/Library/Logs/MuTheMatrix/wine-prefix.log` by default.
The legacy CrossOver branch is unchanged. A standalone copy of play-mu.sh must be updated with the complete kit.
