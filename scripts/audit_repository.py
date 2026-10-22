#!/usr/bin/env python3
"""Review the staged source tree for accidentally published local artifacts."""
import hashlib
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
PRIVATE_DIRS = {'input','evidence','runtime','vendor','publish','dist','node_modules','__pycache__'}
GENERATED = {'.exe','.dll','.bin','.obj','.bmd','.smd','.png','.jpg','.zip','.dmg','.xz','.dmp','.mdmp','.dylib','.so','.o','.pyc','.orig','.new'}


# Owner-requested README screenshots (reviewed 2026-10-21: window-only, no account
# names, passwords or private paths). Only these exact bytes are documentation media;
# all other binary/generated inputs remain rejected.
REVIEWED_MEDIA = {
    'docs/images/01-hero-in-game-lorencia-fps.jpg':
        'af769235cd19c69dfa76c82916f562318bbfbaca7671c37041df2b4a13d8dff4',
    'docs/images/02-dmg-window.png':
        '912e7188791bf14129e5bae31ceea815867c4d3dd3657195e6fed04372dc184c',
    'docs/images/03-gatekeeper-not-opened.png':
        'e4490859ea5be08e8c8c3496b0418330ebab01287c765fc3a25295e8d7b59fec',
    'docs/images/04-move-to-applications.png':
        'a89ed274b0ae24a85902d68b5c8e766af59a15c4bdb40348c887cd12933199cf',
    'docs/images/05-welcome-install.png':
        '6ef4e3e3685a82b2ba8e700c45eb61850b48c662944630596cc1cb9965391c02',
    'docs/images/06-install-progress.png':
        'aa8665348c1d04528ea230f1e748204ddc1a18fb7088c3332f5db50190b98b42',
    'docs/images/07-official-launcher.png':
        '18502b90dee65358736d124bc31cc0ddeef1b0e3eaf4e59d17e2c35af987c051',
    'docs/images/08-character-select.jpg':
        '610ab86a01ab82da87addc2ac71c985d51c292c51e91f1368f0a690b71081c5b',
    'docs/images/09-in-game-twisted-karutan.jpg':
        '9d793f7515c4d047cf47ca13f8193c2b4769152454c5742484336fa92576c8c7',
    'docs/images/10-in-game-tormenta-hunting.jpg':
        'f1d78046da999d61acab2890dafaf2eca29824bbc93d203c4f92507fac70ae37',
    'docs/images/11-app-settings.png':
        'c820da9857052664881ad3c12f458af2f618740c6653250545a260fae0fd5f8f',
}


def violations(name, content):
    path = pathlib.PurePosixPath(name)
    if name in REVIEWED_MEDIA and hashlib.sha256(content).hexdigest() == REVIEWED_MEDIA[name]:
        return []
    errors = []
    if any(part in PRIVATE_DIRS or part.startswith('verified') for part in path.parts):
        errors.append('local/generated directory')
    if name.startswith('mac-play/hotpatch/') and path.name in {'hotpatches.h','inlinesites.h','peepsites.h','orig.h','xform-prologue.h','meshdraw-orig.h'}:
        errors.append('private generated game-byte table')
    if path.suffix.lower() in GENERATED:
        errors.append('binary or generated asset type')
    if len(content) > 512*1024:
        errors.append('file exceeds reviewed source size limit')
    if b'\0' in content:
        errors.append('binary content')
    text = content.decode('utf-8',errors='replace')
    if re.search(r'/Users/[A-Za-z0-9_.-]+/',text):
        errors.append('machine-specific home path')
    if re.search(r'(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})',text):
        errors.append('GitHub credential pattern')
    if re.search(r'-----BEGIN [A-Z ]*PRIVATE KEY-----',text):
        errors.append('private key marker')
    return errors


def main():
    names = subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    names = [name for name in names if name]
    if not names:
        raise SystemExit('No staged/tracked source files to audit')
    failures = []
    for name in names:
        content = subprocess.check_output(['git','show',':'+name],cwd=ROOT)
        errors = violations(name,content)
        if errors:
            failures.append((name,errors))
    for name,errors in failures:
        print(name+': '+', '.join(errors))
    print(f'Audited {len(names)} staged files; {len(failures)} rejected.')
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(main())
