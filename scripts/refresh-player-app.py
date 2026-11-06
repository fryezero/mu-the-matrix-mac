#!/usr/bin/env python3
"""Owner-run app swap/rollback. Never launches Wine or edits its prefix."""
import argparse
from contextlib import contextmanager
from pathlib import Path
import os
import subprocess
import tempfile


def run(*args):
    subprocess.run([str(a) for a in args], check=True)


def verify(app, player=False):
    if app.is_symlink() or not app.is_dir():
        raise RuntimeError(f'Expected an app directory: {app}')
    run('/usr/bin/codesign', '--verify', '--strict', app)
    if player:
        run(app / 'Contents/MacOS/MuTheMatrix', '--check-bundle')


@contextmanager
def idle_lock(root):
    locks = [root / 'mu-mac-tools/.game-lock',
             root / 'Mac Optimizations/Local Files/mu-mac-tools/.game-lock']
    if any(p.exists() for p in locks):
        raise RuntimeError('Game lock held. Close the game and wait for testing to finish.')
    owned = []
    try:
        for lock in dict.fromkeys(p.resolve() for p in locks):
            lock.mkdir()  # exclusive; release only directories this invocation acquired
            owned.append(lock)
            (lock / 'owner').write_text(f'Owner app refresh pid {os.getpid()}\n')
        result = subprocess.run(['/usr/bin/pgrep', '-fl', 'main.exe|MuTheMatrix|Mu The Matrix'],
                                capture_output=True, text=True)
        if result.returncode != 1:
            raise RuntimeError('A client/launcher may be running, or process check failed. Close it first.')
        yield
    finally:
        for lock in reversed(owned):
            (lock / 'owner').unlink(missing_ok=True)
            lock.rmdir()


def replace_app(candidate, target, temp):
    previous = temp / 'previous.app'
    target.rename(previous)
    try:
        candidate.rename(target)
    except BaseException:
        previous.rename(target)
        raise
    # The enclosing TemporaryDirectory removes the old copy only after the replacement succeeds.


def refresh(mode, root, stage):
    target = root / 'MTM/Mu The Matrix.app'
    backup = stage / 'owner-app-before-refresh.zip'
    with idle_lock(root):
        if mode == 'swap':
            verify(target)
        elif target.is_symlink() or not target.is_dir():
            raise RuntimeError(f'Expected an app directory: {target}')
        with tempfile.TemporaryDirectory(prefix='.mu-app-refresh-', dir=target.parent) as tmp:
            temp = Path(tmp)
            candidate = temp / 'Mu The Matrix.app'
            if mode == 'swap':
                if backup.exists():
                    raise RuntimeError(f'Backup already exists; keep it safe before another swap: {backup}')
                source = stage / 'Mu The Matrix.app'
                verify(source, player=True)
                run('/usr/bin/ditto', source, candidate)
                verify(candidate, player=True)
                # Create and test a complete zip before moving even one byte of the installed app.
                partial = stage / 'owner-app-before-refresh.partial.zip'
                if partial.exists():
                    raise RuntimeError(f'Inspect the interrupted backup before retrying: {partial}')
                run('/usr/bin/ditto', '-c', '-k', '--sequesterRsrc', '--keepParent', target, partial)
                run('/usr/bin/unzip', '-tq', partial)
                partial.rename(backup)
            else:
                if not backup.is_file():
                    raise RuntimeError(f'No rollback zip: {backup}')
                run('/usr/bin/unzip', '-tq', backup)
                run('/usr/bin/ditto', '-x', '-k', backup, temp)
                verify(candidate)  # older apps need not implement --check-bundle
            replace_app(candidate, target, temp)
    print(f'{mode} complete: {target}\nRollback zip retained: {backup}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['swap', 'rollback'])
    args = parser.parse_args()
    root = Path.home() / 'Documents/MTM'
    stage = root / 'mu-mac-tools/wine/staged/wine-app-refresh-001'
    try:
        refresh(args.mode, root, stage)
    except (RuntimeError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Stopped: {error}\n')


if __name__ == '__main__':
    main()
