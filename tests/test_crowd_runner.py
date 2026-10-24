"""Exercise disposable-prefix ownership, equivalence failures and budget reporting."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CrowdRunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.wine = self.root / 'wine'
        self.server = self.root / 'wineserver'
        self.compiler = self.root / 'compiler'
        self.out = self.root / 'results'
        self.wine.write_text(f'#!{sys.executable}\n' + '''
from pathlib import Path
import os, sys, json
if sys.argv[1] == '--version':
    if os.getenv('FAKE_CROWD_VERSION_FAIL'): sys.exit(2)
    print('synthetic-wine-test'); sys.exit(0)
prefix = Path(os.environ['WINEPREFIX'])
assert (prefix / '.mu-crowd-owner').read_text().strip() == 'mu-crowd-synthetic-v1'
if sys.argv[1] == 'wineboot':
    (prefix / 'system.reg').write_text('#arch=win32\\n'); sys.exit(0)
frames,batches,vertices,scene,probes,width,height,buffers = map(int,sys.argv[2:])
hash_ = 'changed' if probes and os.getenv('FAKE_CROWD_MISMATCH') else 'same'
late = bool(os.getenv('FAKE_CROWD_LATE') or (os.getenv('FAKE_CROWD_BASELINE_LATE') and Path(sys.argv[1]).parent.name == '0'))
if os.getenv('MUGL_STATS'):
    (prefix / 'drive_c/mutools' / os.environ['MUGL_STATS'].split(chr(92))[-1]).write_text('mugl loaded')
print(json.dumps(dict(frames=frames,batches=batches,vertices=vertices,scene=scene,probes=probes,
buffers=buffers,buffer_lifecycle_ok=0 if os.getenv('FAKE_CROWD_LIFECYCLE_FAIL') else 1,
width=width,height=height,median_ms=35 if late else 12,p95_ms=45 if late else 15,
over_40ms=3 if late else 0,framebuffer_hash=hash_,drawn=frames*batches,culled=0,gl_error=0)))
''')
        self.server.write_text(f'#!{sys.executable}\n' + '''
from pathlib import Path
import os
import sys
assert (Path(os.environ['WINEPREFIX']) / '.mu-crowd-owner').exists()
if '-k' in sys.argv and os.getenv('FAKE_CROWD_SERVER_ABSENT'): sys.exit(1)
''')
        self.compiler.write_text(f'#!{sys.executable}\n' + '''
from pathlib import Path
import sys
Path(sys.argv[sys.argv.index('-o')+1]).write_text('synthetic compiler output')
''')
        for path in [self.wine, self.server, self.compiler]:
            path.chmod(0o700)

    def run_case(self, options=(), extra_env=None):
        env = dict(os.environ, MINGW_CC=str(self.compiler))
        env.update(extra_env or {})
        return subprocess.run([sys.executable, str(ROOT / 'scripts/run-crowd-bench.py'),
                               '--wine', str(self.wine), '--out', str(self.out), '--frames', '5',
                               '--batches', '8', '--scenes', 'edge', *options],
                              env=env, text=True, capture_output=True)

    def test_success_compares_four_runs_and_removes_only_owned_prefix(self):
        sentinel = self.root / 'player-prefix'
        sentinel.mkdir()
        (sentinel / 'keep').write_text('untouched')
        result = self.run_case()
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.out / 'summary.json').read_text())
        self.assertTrue(report['completed'] and report['equivalent'])
        self.assertFalse(report['gameplay_verified'])
        self.assertEqual([r['probes'] for r in report['results']], [0, 1, 1, 0])
        self.assertFalse((self.out / 'prefix').exists())
        self.assertEqual((sentinel / 'keep').read_text(), 'untouched')

    def test_framebuffer_mismatch_fails_and_still_cleans_up(self):
        result = self.run_case(extra_env={'FAKE_CROWD_MISMATCH': '1'})
        self.assertNotEqual(result.returncode, 0)
        report = json.loads((self.out / 'summary.json').read_text())
        self.assertFalse(report['completed'] or report['equivalent'])
        self.assertFalse((self.out / 'prefix').exists())

    def test_budget_failure_is_separate_from_correctness(self):
        result = self.run_case(['--require-budget'], {'FAKE_CROWD_LATE': '1'})
        self.assertEqual(result.returncode, 3, result.stderr)
        report = json.loads((self.out / 'summary.json').read_text())
        self.assertTrue(report['completed'] and report['equivalent'])
        self.assertFalse(report['optimized_p95_within_40ms'])

    def test_buffer_lifecycle_failure_rejects_run(self):
        result = self.run_case(['--buffers', '16'], {'FAKE_CROWD_LIFECYCLE_FAIL': '1'})
        self.assertNotEqual(result.returncode, 0)
        report = json.loads((self.out / 'summary.json').read_text())
        self.assertFalse(report['completed'])
        self.assertFalse((self.out / 'prefix').exists())

    def test_same_culling_algorithm_on_both_variants(self):
        result = self.run_case(['--cull-probes', '1'])
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.out / 'summary.json').read_text())
        self.assertEqual([r['probes'] for r in report['results']], [1, 1, 1, 1])
        self.assertEqual([r['variant'] for r in report['results']], [0, 1, 1, 0])

    def test_absent_server_after_early_failure_still_cleans_up(self):
        result = self.run_case(extra_env={'FAKE_CROWD_VERSION_FAIL': '1', 'FAKE_CROWD_SERVER_ABSENT': '1'})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('check_output', result.stderr)
        self.assertNotIn('During handling', result.stderr)
        self.assertFalse((self.out / 'prefix').exists())

    def test_budget_uses_proxy_variant_when_both_enable_culling_probes(self):
        proxies = [self.root / 'old.dll', self.root / 'new.dll']
        for p in proxies:
            p.write_text('authored proxy fixture')
        result = self.run_case(['--cull-probes', '1', '--proxies', *map(str, proxies), '--require-budget'],
                               {'FAKE_CROWD_BASELINE_LATE': '1'})
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads((self.out / 'summary.json').read_text())
        self.assertTrue(report['completed'] and report['optimized_p95_within_40ms'])
        self.assertEqual([r['p95_ms'] for r in report['results']], [45, 15, 15, 45])

    def test_version_failure_still_cleans_up(self):
        result = self.run_case(extra_env={'FAKE_CROWD_VERSION_FAIL': '1'})
        self.assertNotEqual(result.returncode, 0)
        report = json.loads((self.out / 'summary.json').read_text())
        self.assertFalse(report['completed'])
        self.assertFalse((self.out / 'prefix').exists())

    def test_existing_output_and_invalid_limits_are_refused(self):
        result = self.run_case(['--frames', '301'])
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.out.exists())
        self.out.mkdir()
        (self.out / 'player-data').write_text('keep')
        result = self.run_case()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.out / 'player-data').read_text(), 'keep')
        self.assertFalse((self.out / 'prefix').exists())


if __name__ == '__main__':
    unittest.main()
