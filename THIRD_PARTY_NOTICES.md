# Third-party notices

This repository contains authored code (MIT, see [LICENSE](LICENSE)) that installs, configures and speeds up the
original Mu The Matrix Windows client on macOS. It does not vendor Wine, CrossOver, Microsoft software, Apple
software, game binaries, game assets or DLLs built from the client. The player app built from it can bundle the
separately built components below; anyone distributing such a build must carry their notices.

## Bundled Wine runtime (player builds)

`make player-app EMBED_RUNTIME=…` embeds `winecx-26.3.0-mu1.tar.xz`, CodeWeavers' open-source Wine from the
CrossOver 26.3.0 sources, built unmodified by `mac-play/installer/packaging/build-wine.sh`. Wine is licensed under
the GNU LGPL 2.1 or later; the app carries `COPYING.LIB` and
[`mac-play/bundle/licenses/wine-runtime-SOURCES.txt`](mac-play/bundle/licenses/wine-runtime-SOURCES.txt), which lists
the corresponding sources: the CrossOver 26.3.0 source tarball (pinned SHA-256), wine-gecko 2.47.4 (MPL 2.0) and the
x86_64 support libraries from Sikarugir's wrapper template (freetype, gnutls, nettle, gmp, libpng, zlib and others,
each under its own license). Without an embedded runtime the installer falls back to Sikarugir's public build of
CrossOver 24.0.7's Wine. CrossOver itself is commercial software from CodeWeavers and remains optional.

## Microsoft .NET Framework and winetricks

The installer runs winetricks, which downloads Microsoft's .NET Framework 4.8 installer from Microsoft under
Microsoft's terms. Only the installer's SHA-256 is recorded here; no Microsoft binary is included.

## libjpeg-turbo (optional, hotpatch JPEG path)

`mac-play/hotpatch/build-libjpeg-turbo.sh` builds libjpeg-turbo (IJG License, Modified BSD License, zlib License)
outside the repository, and the hotpatch DLL can link it statically (`LJT_DIR=…`). Distributing such a DLL requires
libjpeg-turbo's notices, including "This software is based in part on the work of the Independent JPEG Group".

## Optional fast x87 runtime

`mac-play/install-fast-x87.sh` fetches and builds external
[aprilmaccydee/rosetta-timewalker](https://github.com/aprilmaccydee/rosetta-timewalker)
at `ab1a6a032e488c0d6eade54ce70a02d653277810` in the user's cache. No upstream
source or binary is vendored here. Its top-level license is MIT, copyright
2026 aprilmaccydee. Its bundled modified
[Lifeisawful/rosettax87_jit](https://github.com/Lifeisawful/rosettax87_jit)
snapshot derives from `a44f1eff28591a90f4a8c7297134294811da06b5`, MIT,
copyright 2025 Lifeisawful. The embedded openlibm/fdlibm/FreeBSD msun routines
retain their per-file notices, including the David Schultz two-clause BSD
notice reproduced in upstream `THIRD_PARTY_NOTICES.md`. Keep the fetched
`LICENSE`, `THIRD_PARTY_NOTICES.md`, and embedded source notices with any
redistribution. CrossOver and Apple Rosetta remain separately supplied software.

The `fpbench.c` and `glbench.c` diagnostics were authored for this investigation
and copied from the local mu-mac-tools project, with GL error checks added here.
They contain no game code or assets.

## Immediate-mode batching and profiling

`mac-play/mugl/`, `diagnostics/eipprof.c`, `diagnostics/glcheck.c` and
`diagnostics/pe_nearest_export.py` are authored for this investigation and covered
by the repository MIT license. `mugl/exports.txt` is an API-name manifest extracted
from the separately installed CrossOver 26.3 i386 OpenGL DLL. No Wine/CrossOver
implementation or binary is included. The generated proxy loads the user's
installed Wine builtin OpenGL implementation at runtime.

## Claude v7.0 performance tools

`mac-play/hotpatch`, `mac-play/mumodes`, `mac-play/machprof` and
`mac-play/automation` publish authored code from the owner's local mu-mac-tools
work under this repository's MIT license. Source identities and packaging
adaptations are recorded with the performance finding. The mscoree declarations,
DEF and jump stubs contain forwarding API names/ordinals only. No Microsoft, Wine,
CrossOver or game implementation is included. Original game instruction bytes,
including the xform entry prologue, are generated only into ignored local build
directories from owner-supplied private inputs. Generated DLLs containing original
bytes are outside the publication boundary and must not be redistributed here.

## Claude v7.1 mesh-draw tools

`mac-play/hotpatch/meshdraw.c`, the v7.1 `mugl.c` and `mac-play/diagnostics/glstride.c`
are authored code from the owner's local mu-mac-tools work, published under this
repository's MIT license with the same boundary as the v7.0 tools. The three
original patch-site byte sequences used by `meshdraw.c` are generated only into the
ignored build directory from owner-supplied private input; `targets.json` records
their addresses, lengths and SHA-256 only. No Microsoft, Wine, CrossOver or game
implementation is included.

## Claude v7.2 precise waits

The v7.2 `mac-play/hotpatch/mugl.c` is authored code from the owner's local mu-mac-tools
work, published under this repository's MIT license with the same boundary as v7.0
and v7.1. It adds no original game bytes and no Microsoft, Wine, CrossOver or game
implementation; it calls the documented Win32 waitable-timer API.

## Mac setup kit

`mac-play/installer/` is authored shell code from the owner's local mu-mac-tools work, published
under this repository's MIT license. It contains no Microsoft, CrossOver, Wine, winetricks or game
code or binaries. It invokes CrossOver, winetricks (which downloads Microsoft's .NET Framework
installer under Microsoft's terms) and MinGW-w64 from the user's machine, and records SHA-256 values
of Microsoft's installer, a CrossOver builtin and user-supplied proxy DLLs only. Prebuilt mugl DLLs
contain client-derived bytes and are not part of the repository.

## Game and launcher

The Mu The Matrix client, launcher, game data and server belong to their owners and are not covered by this
repository's license. Nothing in this repository grants rights to them. Players install the game from the official
installer or their own copy.
