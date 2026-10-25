# Blank launcher artwork and news after reinstall, MAC-APP-007

Measured on 2026-10-25, Apple M5, macOS 27.0.1, the free CX26.3-source Wine runtime
`archive-c50cb6145767`. The affected program was the Windows `MuTheMatrix.exe` launcher inside Wine.

## Failure and cause

The official skin drew the server clock, controls, progress bars and START button, but the whole artwork/news
rectangle stayed black. The installed v3 mscoree proxy, WIC stream fix, official skin and registry overrides
already matched their pins. The existing verifier reported 32 PASS, 2 WARN, 0 FAIL despite the blank panel.
The skin, launcher executable and codec DLLs matched the older working installation.

The new prefix had Wine's basic HTMLDocument COM class, but lacked the full mshtml DLL registration. In particular,
the `AboutURLs:blank` and HTMLDocument `MiscStatus` entries were missing. An authored Win32 probe found the
900x620 launcher window but no `Internet Explorer_Server` control. Its capture reproduced the owner's blank panel.

Running `regsvr32.exe /s mshtml.dll` with the selected prefix created that control and restored the live artwork,
news and online-player count. No game or launcher executable, skin file or protection code was changed.

The installer deliberately suppresses mshtml during initial wineboot to avoid install prompts before .NET setup.
It did not register mshtml afterwards. Wine's [mshtml registration file](https://github.com/wine-mirror/wine/blob/wine-11.0/dlls/mshtml/mshtml.inf)
defines the missing entries. Its [Gecko integration](https://github.com/wine-mirror/wine/blob/wine-11.0/dlls/mshtml/nsembed.c)
loads the separately packaged browser engine. A bundled engine and a base COM class are insufficient evidence
that the browser registration step completed.

## Fix

- Setup checks full mshtml registration after .NET and Windows-version setup, and runs the registration command
  when missing. A failed command stops setup; an already registered prefix skips it.
- The read-only verifier reports a dedicated `launcher web browser` PASS/FAIL. It never runs Wine or changes the prefix.
- The selected Mac app's embedded setup, verifier and helper library were updated, preserving its other resources.
  This makes Repair and subsequent installs include the new registration step.
- The local `Launcher Patches/` folder gathers links to the existing launcher source, installer, pinned DLLs,
  startup code and research. `Fix MU Launcher.command` provides a focused repair with an idle-process check,
  prefix-scoped Wine operations and registry rollback files. These local files and captures remain excluded from Git.

An older Downloads app also contained v1 patch payloads. It was briefly updated before the owner identified the
MTM app as the selected copy, then restored. All saved file hashes and its original signature matched after restore.
That older app was not the cause of the blank panel in the selected installation.

## Verification

The live failure reproduced with no browser control. After registration, the 900x450 browser control was visible
and the page's graphics and current news were visually inspected. A content check over the middle rectangle
changed from 0.00% colorful pixels to 30.38%. This is a guard for this blank-panel regression, not general rendering
equivalence. Cross-process DOM marshalling returned E_FAIL in the diagnostic, so no DOM-content claim is made.

A cold start through the selected app's actual startup helper also restored the visible browser and animated
page, and reached the enabled green START button. The final capture was taken during a 51.9-second owned run.
Its body contained 19.69% colorful pixels and 89.42% of the sampled button area was green. Captures use a wide-gamut
profile; the readiness check uses relative color channels. The original absolute-RGB check falsely rejected that
green and was corrected against the same retained capture. An earlier probe ran before browser initialization;
that early result is not used as a completed-startup verdict.

The original game and launcher executable hashes were preserved. Only the owned launcher sessions were stopped,
using the explicit prefix; no login or combat was performed. Captures and registry rollback files are local under
`Launcher Patches/`. The v3 DLL and its previously established WIC/window fixes are unchanged.

Four focused regression tests failed before the change and passed after it. They distinguish the base COM class
from full registration, reject partial registration and verify that the read-only check flags the failure.
The installer suite passed 354 checks, including missing-registration detection, dry-run behavior, a failing Wine
command, successful repair in the selected fake bottle and a no-op rerun. The test uses authored synthetic files
and a Wine command stub, with no game assets or real prefix.

`bash scripts/local-macos-ci.sh` passed: 132 Python tests, 354 installer checks, 268 app/bundle checks,
Mac builds, MinGW cross-builds and the publication audit, 181 staged files with zero rejections. No hosted CI ran.

The rare launcher Hash Protection 0xA4 dialog remains outside this fix.
