"""Exercise replacement and recovery on disposable fake apps, never the owner's app."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('refresh', Path(__file__).resolve().parents[1] / 'scripts/refresh-player-app.py')
refresh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(refresh)


@unittest.skipUnless(sys.platform == 'darwin', 'uses macOS ditto archives')
class AppRefresh(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.stage = self.root / 'staged'
        self.target = self.root / 'MTM/Mu The Matrix.app'
        self.source = self.stage / 'Mu The Matrix.app'
        for app, value in ((self.target, 'old'), (self.source, 'new')):
            app.mkdir(parents=True)
            (app / 'payload').write_text(value)
        (self.root / 'mu-mac-tools').mkdir()
        (self.root / 'Mac Optimizations/Local Files/mu-mac-tools').mkdir(parents=True)
        self.verifier = patch.object(refresh, 'verify')
        self.verifier.start()
        self.addCleanup(self.verifier.stop)
        original_run = subprocess.run
        def run(args, **kwargs):
            if args[0] == '/usr/bin/pgrep':
                return subprocess.CompletedProcess(args, 1)
            return original_run(args, **kwargs)
        self.processes = patch.object(refresh.subprocess, 'run', side_effect=run)
        self.processes.start()
        self.addCleanup(self.processes.stop)

    def test_round_trip_and_backup_refusal(self):
        refresh.refresh('swap', self.root, self.stage)
        self.assertEqual((self.target / 'payload').read_text(), 'new')
        with self.assertRaisesRegex(RuntimeError, 'Backup already exists'):
            refresh.refresh('swap', self.root, self.stage)
        refresh.refresh('rollback', self.root, self.stage)
        self.assertEqual((self.target / 'payload').read_text(), 'old')
        self.assertTrue((self.stage / 'owner-app-before-refresh.zip').exists())

    def test_locked(self):
        (self.root / 'mu-mac-tools/.game-lock').mkdir()
        with self.assertRaisesRegex(RuntimeError, 'Game lock held'):
            refresh.refresh('swap', self.root, self.stage)
        self.assertEqual((self.target / 'payload').read_text(), 'old')

    def test_running(self):
        with patch.object(refresh.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0)):
            with self.assertRaisesRegex(RuntimeError, 'may be running'):
                refresh.refresh('swap', self.root, self.stage)
        self.assertFalse((self.root / 'mu-mac-tools/.game-lock').exists())

    def test_invalid_candidate(self):
        with patch.object(refresh, 'verify', side_effect=[None, RuntimeError('bad signature')]):
            with self.assertRaisesRegex(RuntimeError, 'bad signature'):
                refresh.refresh('swap', self.root, self.stage)
        self.assertEqual((self.target / 'payload').read_text(), 'old')
        self.assertFalse((self.stage / 'owner-app-before-refresh.zip').exists())

    def test_rename_failure_restores_target(self):
        temp = self.root / 'replace'; temp.mkdir()
        with self.assertRaises(FileNotFoundError):
            refresh.replace_app(temp / 'missing.app', self.target, temp)
        self.assertEqual((self.target / 'payload').read_text(), 'old')

    def test_missing_backup(self):
        with self.assertRaisesRegex(RuntimeError, 'No rollback zip'):
            refresh.refresh('rollback', self.root, self.stage)
        self.assertEqual((self.target / 'payload').read_text(), 'old')

    def test_rollback_does_not_require_current_signature(self):
        refresh.refresh('swap', self.root, self.stage)
        with patch.object(refresh, 'verify') as checked:
            refresh.refresh('rollback', self.root, self.stage)
        self.assertEqual(checked.call_count, 1)
        self.assertNotEqual(checked.call_args.args[0], self.target)

    def test_second_lock_refused(self):
        (self.root / 'Mac Optimizations/Local Files/mu-mac-tools/.game-lock').mkdir()
        with self.assertRaisesRegex(RuntimeError, 'Game lock held'):
            refresh.refresh('swap', self.root, self.stage)
        self.assertFalse((self.root / 'mu-mac-tools/.game-lock').exists())
