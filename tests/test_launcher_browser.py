"""Catch the Wine prefix state that left the launcher's embedded page blank."""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "mac-play/installer/lib/mukit.sh"
VERIFY = ROOT / "mac-play/installer/verify-mu-mac.sh"
BASE = r'''WINE REGISTRY Version 2
#arch=win32
[Software\\Classes\\CLSID\\{25336920-03F9-11CF-8FD0-00AA00686F13}\\InprocServer32]
@="C:\\windows\\system32\\mshtml.dll"
"ThreadingModel"="Apartment"
'''
FULL = BASE + r'''
[Software\\Microsoft\\Internet Explorer\\AboutURLs]
"blank"="res://mshtml.dll/blank.htm"
[Software\\Classes\\CLSID\\{25336920-03F9-11CF-8FD0-00AA00686F13}\\MiscStatus]
@="2228625"
'''


class LauncherBrowserRegistration(unittest.TestCase):
    def check_registration(self, text):
        with tempfile.TemporaryDirectory() as temp:
            reg = Path(temp) / "system.reg"
            reg.write_text(text)
            result = subprocess.run(
                ["bash", "-c", 'source "$1"; declare -F mukit_browser_registered >/dev/null || exit 99; '
                 'mukit_browser_registered "$2"', "_", str(LIB), str(reg)],
                capture_output=True, text=True,
            )
        self.assertNotEqual(result.returncode, 99, "browser registration check is missing")
        return result.returncode == 0

    def test_base_wine_com_class_does_not_mean_browser_was_registered(self):
        self.assertFalse(self.check_registration(BASE))

    def test_complete_mshtml_registration(self):
        self.assertTrue(self.check_registration(FULL))

    def test_partial_registration_is_not_accepted(self):
        self.assertFalse(self.check_registration(FULL.replace('"2228625"', '"0"')))

    def test_read_only_verifier_flags_blank_browser_prefix_state(self):
        with tempfile.TemporaryDirectory() as temp:
            prefix = Path(temp) / "prefix"
            prefix.mkdir()
            (prefix / "system.reg").write_text(BASE)
            (prefix / "user.reg").write_text("WINE REGISTRY Version 2\n#arch=win32\n")
            before = {p.name: p.read_bytes() for p in prefix.iterdir()}
            result = subprocess.run(["bash", str(VERIFY), "--prefix", str(prefix)],
                                    capture_output=True, text=True,
                                    env={**os.environ, "HOME": temp, "MUKIT_FREE_HOME": temp,
                                         "MUKIT_BOTTLES_DIR": str(Path(temp) / "Bottles")})
            self.assertRegex(result.stdout, r"FAIL\s+launcher web browser\s+")
            self.assertEqual(before, {p.name: p.read_bytes() for p in prefix.iterdir()})


if __name__ == "__main__":
    unittest.main()
