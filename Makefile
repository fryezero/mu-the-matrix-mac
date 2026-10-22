PYTHON ?= python3

# Mu The Matrix on macOS through Wine: the player app, its installer, the OpenGL proxy and the
# performance tools. `make test` needs no game files, no Wine runtime and no MinGW.

all: test

test:
	for script in mac-play/automation/*.sh; do bash -n "$$script" || exit; done
	bash -n mac-play/setup-crossover-32bit.sh
	bash -n mac-play/cxwine
	bash -n mac-play/cxwineserver
	bash -n mac-play/start-launcher.sh
	bash -n mac-play/gl-batching.sh
	bash -n mac-play/diagnostics/run-eipprof.sh
	bash -n mac-play/fast-x87.sh
	bash -n mac-play/install-fast-x87.sh
	bash -n mac-play/diagnostics/bottle.sh
	bash -n mac-play/diagnostics/run-fpbench.sh
	bash -n mac-play/diagnostics/run-glbench.sh
	bash mac-play/installer/tests/test-mukit.sh
	bash mac-play/bundle/tests/test-bundle.sh
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py' -v

# Cross-builds (need i686-w64-mingw32-gcc: brew install mingw-w64).
mugl:
	$(MAKE) -C mac-play/mugl

mac-hotpatch:
	$(MAKE) -C mac-play/hotpatch

mac-diagnostics:
	$(MAKE) -C mac-play/diagnostics

# Host profiling tools for a running client (clang, x86_64).
machprof:
	$(MAKE) -C mac-play/machprof

mac-bundle:
	$(MAKE) -C mac-play/bundle

# Mu The Matrix.app for players: needs EMBED_MUGL=... EMBED_MSCOREE=... EMBED_FAST_X87=... EMBED_RUNTIME=...
# (see mac-play/bundle/README.md); player-dmg packages it as "Mu The Matrix.dmg" (DMG=..., SIGN_IDENTITY=..., NOTARY_PROFILE=...).
player-app:
	$(MAKE) -C mac-play/bundle player-app

player-dmg:
	$(MAKE) -C mac-play/bundle player-dmg

.PHONY: all test mugl mac-hotpatch mac-diagnostics machprof mac-bundle player-app player-dmg
