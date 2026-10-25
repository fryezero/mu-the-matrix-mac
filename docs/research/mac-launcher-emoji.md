# News-title emoji under Wine, MAC-APP-008

Measured on 2026-10-25, Apple M5, macOS 27.0.1, free CX26.3-source Wine `archive-c50cb6145767`.

## Failure

The restored launcher news page displayed small hexadecimal missing-glyph boxes within its titles.
The live [launcher page](https://webx.muthematrix.com/launcher/launcher_news.php) supplies Unicode emoji, including
egg, package, gem and sparkle characters. They are text, rather than image or GIF downloads.

An authored Wine/i686 GDI/Uniscribe probe shaped the egg, package and gem characters. Tahoma, Arial and Wine's
Apple Color Emoji face returned three glyph-zero results. The prefix had no installed Windows emoji font.

## Measured alternatives

- Noto Color Emoji supplied nonzero glyph IDs when explicitly selected, but the launcher still displayed boxes.
- Its Windows-compatible variant also left boxes. Wine enumerated both variants as raster fonts, type 1.
- The unchanged Mozilla Twemoji COLR/CPAL vector font enumerated as TrueType, type 4. It supplied nonzero glyphs
  and the actual launcher displayed colored dragon, egg, package, sparkle and gem symbols in the titles.

The failed Noto font files and registration were removed. Only the working font remains installed. Font coverage
alone did not establish that Wine Gecko would render a candidate; every retained result includes a window capture.

## Fix and provenance

Setup registers and installs the verified `TwemojiMozilla.ttf` in the selected prefix's `C:\windows\Fonts`.
The font fills missing characters while the page retains its existing Tahoma/Arial text styling.
No game executable, launcher executable, skin or server page was changed.

- Source: [Mozilla's font](https://github.com/mozilla/gecko-dev/blob/bcb0701db5c25bec5cf82b12586f6ff6660ff535/browser/fonts/TwemojiMozilla.ttf).
- SHA-256: `6d90152ee0d29e82fe2a87793af5aa4b7ad13e6538360889e141e81ed299ee8e`, 1,474,284 bytes.
- Format: COLR version 0 with vector glyphs. The [Mozilla project](https://github.com/mozilla/twemoji-colr)
  documents this format for Gecko-based applications.
- Attribution and license links are installed as `C:\mutools\licenses\Twemoji-Mozilla.md`.
  The artwork is CC BY 4.0; Mozilla's font-building code is Apache 2.0. The font file is unchanged.

A bundled `installer/fonts/TwemojiMozilla.ttf` is used when available. An explicit `MUKIT_EMOJI_FONT_FILE` is
verified against the same pin. Otherwise setup downloads the pinned file into a user cache outside the signed
Mac app, then installs it. A wrong source hash stops setup. Existing unrelated files are preserved by the installer's
backup policy. Verify reports missing, changed or unregistered news-font files.

The selected MTM Mac app carries the updated installer, verified font and attribution, and its ad-hoc signature
is checked after updating those resources. The local `Launcher Patches/Fonts` folder holds the canonical font,
provenance and original notices. `Fix MU Launcher.command` now checks/repairs both browser registration and news icons.
Font binaries, captures and rollback files remain outside Git; this repository publishes the recipe and notices.

## Verification

All 13 emoji/symbol codepoints used by the measured page are covered by the selected font. The vertical text
separator U+2502 remains in the original text font. The actual launcher news was visually inspected with the
colored symbols and no hexadecimal placeholders. The three owned candidate runs lasted 47.0, 48.4 and 86.9 seconds;
each stayed below the three-minute limit and the shared game lock was released. No account login or gameplay occurred.

Four identity/registration regressions failed before the helper existed and pass after it. The installer suite
passed 369 checks, including font installation, attribution, tampering, wrong-source rejection, repair, idempotence,
and a dry-run that keeps the download cache outside app resources. The font tests use authored synthetic bytes and
injected test pins; they do not prove glyph appearance. Actual glyph and color evidence comes from the Wine probe
and launcher captures described above.

A final fresh launch through the selected Mac app completed in 12.7 seconds. The browser probe passed,
the START button was enabled and the window capture again showed the colored news symbols without boxes.
The installed font and app-bundled font match the pinned hash. The game and Windows launcher hashes are unchanged.
The read-only prefix check reports 35 PASS, 2 optional autologin-tool WARN and 0 FAIL. Owned launcher sessions
are closed and the shared game lock is released.

`bash scripts/local-macos-ci.sh` passed 136 Python tests, 369 installer checks, 268 app checks, the Mac/MinGW
builds and the publication audit, which reported 184 staged files and zero rejections.
Next: the owner can reopen the MU launcher normally; no additional repair command is needed for this installation.
