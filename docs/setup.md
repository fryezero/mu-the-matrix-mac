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
