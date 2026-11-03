"""The authored fast x87 self-check probe: builds for x86_64 and passes on plain Rosetta (WINE-FASTX87-002)."""
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'mac-play/x87-smoke.c'


@unittest.skipUnless(platform.system() == 'Darwin' and shutil.which('xcrun'), 'needs macOS with Xcode tools')
class X87SmokeTests(unittest.TestCase):
    def test_probe_builds_for_x86_64_and_passes_under_rosetta(self):
        with tempfile.TemporaryDirectory(prefix='mu x87 smoke ') as tmp:
            probe = Path(tmp) / 'x87-smoke'
            subprocess.run(['xcrun', 'clang', '-arch', 'x86_64', '-std=c11', '-O2', '-Wall', '-Wextra', '-Werror',
                            str(SOURCE), '-o', str(probe)], check=True)
            # The probe must contain real x87 instructions, or it would not exercise the translator.
            text = subprocess.run(['otool', '-tv', str(probe)], capture_output=True, text=True, check=True).stdout
            for mnemonic in ('flds', 'fsqrt', 'fistpl', 'faddp'):
                self.assertIn(mnemonic, text)
            if subprocess.run(['arch', '-x86_64', '/usr/bin/true'], capture_output=True).returncode != 0:
                self.skipTest('Rosetta is not installed')
            result = subprocess.run(['arch', '-x86_64', str(probe)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertRegex(result.stdout, r'^x87 smoke: PASS \(fld 1\.5, fsqrt\+fadd 3\.25, fistp 4, loop 249750\)')

    def test_launcher_bundle_and_setup_ship_the_probe(self):
        self.assertIn('../x87-smoke.c', (ROOT / 'mac-play/bundle/Makefile').read_text())
        setup = (ROOT / 'mac-play/installer/setup-mu-mac.sh').read_text()
        self.assertIn('x87-main-only-wrapper x87-smoke LICENSE', setup)
        self.assertIn('"$MAC_PLAY/x87-smoke.c"', setup)


if __name__ == '__main__':
    unittest.main()
