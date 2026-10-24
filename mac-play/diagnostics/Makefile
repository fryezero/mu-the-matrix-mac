MINGW_CC ?= i686-w64-mingw32-gcc
# Mandatory SSE math on Rosetta; no x87 in either diagnostic.
CFLAGS := -O2 -msse2 -mfpmath=sse
all: build/glbench.exe build/eipprof.exe build/glcheck.exe build/glstride.exe build/glcstate.exe build/glvbench.exe build/glcaps.exe build/glcrowd.exe
build:
	mkdir -p $@
build/glbench.exe: glbench.c | build
	$(MINGW_CC) $(CFLAGS) $< -o $@ -lopengl32 -lgdi32
build/glcheck.exe: glcheck.c | build
	$(MINGW_CC) $(CFLAGS) $< -o $@ -lopengl32 -lgdi32
build/glstride.exe: glstride.c | build
	$(MINGW_CC) $(CFLAGS) $< -o $@ -lopengl32 -lgdi32
build/glcstate.exe: glcstate.c | build
	$(MINGW_CC) $(CFLAGS) $< -o $@ -lopengl32 -lgdi32
build/glcaps.exe: glcaps.c | build
	$(MINGW_CC) $(CFLAGS) $< -o $@ -lopengl32 -lgdi32
build/glvbench.exe: glvbench.c | build
	$(MINGW_CC) $(CFLAGS) $< -o $@ -lopengl32 -lgdi32
build/glcrowd.exe: glcrowd.c ../hotpatch/cull_geometry.h ../hotpatch/cull_probe.h | build
	$(MINGW_CC) $(CFLAGS) -ffp-contract=off -Wall -Wextra -Werror $< -o $@ -lopengl32 -lgdi32
build/eipprof.exe: eipprof.c | build
	$(MINGW_CC) $(CFLAGS) $< -o $@
# The read-only live-state readers (objread, memread, lightread, langread) used to validate the
# native reconstruction moved to the native repository (fryezero/mu-the-matrix-native, live-readers/).
.PHONY: all
