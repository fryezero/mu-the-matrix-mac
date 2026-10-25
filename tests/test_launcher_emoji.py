"""Detect the missing/tampered emoji-font states that leave news titles with boxes."""
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / 'mac-play/installer/lib/mukit.sh'
FONT = b'authored synthetic font identity, not a real TTF'
REG = r'''WINE REGISTRY Version 2
[Software\\Microsoft\\Windows NT\\CurrentVersion\\Fonts]
"Twemoji Mozilla (TrueType)"="TwemojiMozilla.ttf"
'''


class LauncherEmojiFont(unittest.TestCase):
    def check(self, font=FONT, registry=REG):
        with tempfile.TemporaryDirectory() as temp:
            prefix = Path(temp)
            (prefix / 'system.reg').write_text(registry)
            folder = prefix / 'drive_c/windows/Fonts'
            folder.mkdir(parents=True)
            if font is not None:
                (folder / 'TwemojiMozilla.ttf').write_bytes(font)
            before = sorted(str(p.relative_to(prefix)) for p in prefix.rglob('*'))
            result = subprocess.run(
                ['bash', '-c', 'source "$1"; declare -F mukit_emoji_font_installed >/dev/null || exit 99; '
                 'mukit_emoji_font_installed "$2"', '_', str(LIB), str(prefix)],
                env={**os.environ, 'MUKIT_EMOJI_FONT_SHA256': hashlib.sha256(FONT).hexdigest()},
                capture_output=True, text=True)
            self.assertEqual(before, sorted(str(p.relative_to(prefix)) for p in prefix.rglob('*')))
        self.assertNotEqual(result.returncode, 99, 'emoji font check is missing')
        return result.returncode == 0

    def test_registered_matching_font(self):
        self.assertTrue(self.check())

    def test_registration_without_font_is_not_enough(self):
        self.assertFalse(self.check(font=None))

    def test_font_without_registration_is_not_enough(self):
        self.assertFalse(self.check(registry='WINE REGISTRY Version 2\n'))

    def test_wrong_font_bytes_are_not_accepted(self):
        self.assertFalse(self.check(font=b'different font'))


if __name__ == '__main__':
    unittest.main()
