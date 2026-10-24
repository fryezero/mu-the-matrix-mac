#!/usr/bin/env python3
"""Build and run authored GL crowd workloads in a new disposable Wine prefix.

No client inputs, account, existing prefix, registry edits or game deployment.
All runs have a 120-second limit. Results are rendering measurements, not gameplay.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SCENES = {'mixed': 0, 'edge': 1, 'offscreen': 2, 'inside': 3}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wine', type=Path, required=True, help='Wine binary; adjacent wineserver required')
    parser.add_argument('--out', type=Path, required=True, help='New output directory, preferably under runtime/')
    parser.add_argument('--batches', type=int, nargs='+', default=[2000, 8000, 12000])
    parser.add_argument('--scenes', choices=SCENES, nargs='+', default=list(SCENES))
    parser.add_argument('--frames', type=int, default=60)
    parser.add_argument('--vertices', type=int, default=690)
    parser.add_argument('--size', type=int, nargs=2, default=[1280, 800], metavar=('WIDTH', 'HEIGHT'))
    parser.add_argument('--buffers', type=int, default=0, help='Named buffers updated per mesh, 0..4096')
    parser.add_argument('--cull-probes', type=int, choices=[0, 1],
                        help='Use this visibility algorithm on both variants; default compares old/new')
    parser.add_argument('--proxies', type=Path, nargs=2, metavar=('BASELINE_DLL', 'OPTIMIZED_DLL'),
                        help='Optional authored synthetic proxy builds; enables full+vbo in the disposable prefix')
    parser.add_argument('--require-budget', action='store_true', help='Exit 3 if any optimized p95 exceeds 40 ms')
    args = parser.parse_args()
    if (not 5 <= args.frames <= 300 or not 3 <= args.vertices <= 6000 or args.vertices % 3 or
            any(not 1 <= n <= 50000 for n in args.batches) or any(not 64 <= n <= 2048 for n in args.size) or not 0 <= args.buffers <= 4096):
        parser.error('frames 5..300, vertices 3..6000 divisible by 3, batches 1..50000, size 64..2048, buffers 0..4096')
    wine = args.wine.expanduser().resolve()
    server = wine.with_name('wineserver')
    if not wine.is_file() or not server.is_file():
        parser.error('Expected Wine and adjacent wineserver executables')
    proxies = [p.expanduser().resolve() for p in args.proxies] if args.proxies else None
    if proxies and not all(p.is_file() for p in proxies):
        parser.error('Both proxy DLLs must exist')
    out = args.out.expanduser().resolve()
    out.mkdir(parents=True, exist_ok=False)  # never reuse an existing or player prefix
    prefix = out / 'prefix'
    prefix.mkdir()
    marker = prefix / '.mu-crowd-owner'
    marker.write_text('mu-crowd-synthetic-v1\n')
    env = dict(os.environ, WINEPREFIX=str(prefix), WINEDEBUG='-all', WINEDLLOVERRIDES='opengl32=b;mscoree,mshtml=')
    env.pop('WINEARCH', None)
    # A benchmark must not inherit the game's translator injection or prefix selection.
    for key in list(env):
        if key.startswith(('TIMEWALKER_', 'CX_', 'MUGL_')) or key in ('DYLD_INSERT_LIBRARIES', 'WINELOADER', 'WINESERVER'):
            del env[key]

    def run(command, name, command_env=env, timeout=120, accepted=(0,)):
        with (out / (name + '.out')).open('w') as stdout, (out / (name + '.err')).open('w') as stderr:
            result = subprocess.run(command, env=command_env, stdout=stdout, stderr=stderr, timeout=timeout)
            if result.returncode not in accepted:
                raise subprocess.CalledProcessError(result.returncode, command)

    results = []
    summary = {'completed': False, 'source': 'synthetic-renderer-only', 'started_utc': datetime.now(timezone.utc).isoformat(),
               'wine_sha256': hashlib.sha256(wine.read_bytes()).hexdigest(),
               'size': args.size, 'results': results, 'equivalent': True, 'gameplay_verified': False}
    try:
        summary['wine_version'] = subprocess.check_output([str(wine), '--version'], env=env, text=True, timeout=20).strip()
        binary = out / 'glcrowd.exe'
        compiler = os.environ.get('MINGW_CC', 'i686-w64-mingw32-gcc')
        run([compiler, '-O2', '-msse2', '-mfpmath=sse', '-ffp-contract=off', '-Wall', '-Wextra', '-Werror',
             str(ROOT / 'mac-play/diagnostics/glcrowd.c'), '-o', str(binary), '-lopengl32', '-lgdi32'], 'build')
        summary['benchmark_sha256'] = hashlib.sha256(binary.read_bytes()).hexdigest()
        binaries = [binary, binary]
        if proxies:
            binaries = []
            summary['proxy_sha256'] = [hashlib.sha256(p.read_bytes()).hexdigest() for p in proxies]
            for index, proxy in enumerate(proxies):
                variant = out / str(index)
                variant.mkdir()
                shutil.copy2(binary, variant / binary.name)
                shutil.copy2(proxy, variant / 'opengl32.dll')
                binaries.append(variant / binary.name)
        run([str(server), '-p', '5'], 'prefix-start', dict(env, WINEARCH='win32'), 20)
        run([str(wine), 'wineboot', '-i'], 'prefix-boot', timeout=60)
        run([str(server), '-k'], 'prefix-flush', timeout=20)
        run([str(server), '-w'], 'prefix-wait', timeout=20)
        if '#arch=win32' not in (prefix / 'system.reg').read_text(errors='replace'):
            raise RuntimeError('Expected a 32-bit prefix; no player prefixes will be used')
        if proxies:
            tools = prefix / 'drive_c/mutools'
            tools.mkdir(parents=True, exist_ok=True)
            (tools / 'mugl-mode.txt').write_text('full+vbo\n')
        for scene in args.scenes:
            for batches in args.batches:
                case = []
                for round_index, variant in enumerate([0, 1, 1, 0]):  # ABBA limits order bias
                    probes = variant if args.cull_probes is None else args.cull_probes
                    name = f'{scene}-{batches}-{round_index}-{variant}'
                    load = os.getloadavg() if hasattr(os, 'getloadavg') else None
                    command_env = dict(env)
                    if proxies:
                        command_env['WINEDLLOVERRIDES'] = 'opengl32=n,b;mscoree,mshtml='
                        command_env['MUGL_STATS'] = 'C:\\mutools\\' + name + '.log'
                    run([str(wine), str(binaries[variant]), str(args.frames), str(batches), str(args.vertices),
                         str(SCENES[scene]), str(probes), *map(str, args.size), str(args.buffers)], name, command_env)
                    if proxies:
                        stats = prefix / 'drive_c/mutools' / (name + '.log')
                        if not stats.exists() or 'mugl loaded' not in stats.read_text(errors='replace'):
                            raise RuntimeError(f'{name}: proxy load not verified')
                        shutil.copy2(stats, out / (name + '.proxy.log'))
                    result = json.loads((out / (name + '.out')).read_text())
                    result.update(scene_name=scene, load_average=load, round=round_index, variant=variant)
                    if result['gl_error'] or result['frames'] != args.frames or (args.buffers and not result.get('buffer_lifecycle_ok')):
                        raise RuntimeError(f'{name}: invalid GL run')
                    case.append(result)
                    results.append(result)
                    print(f'{name}: median={result["median_ms"]:.2f}ms p95={result["p95_ms"]:.2f}ms '
                          f'over40={result["over_40ms"]}/{args.frames}', flush=True)
                for key in ['framebuffer_hash', 'drawn', 'culled']:
                    if len({r[key] for r in case}) != 1:
                        summary['equivalent'] = False
                        raise RuntimeError(f'{scene}/{batches}: {key} differs across paths')
        summary['completed'] = True
        summary['optimized_p95_within_40ms'] = all(r['p95_ms'] <= 40 for r in results if r['variant'] == 1)
    finally:
        summary['ended_utc'] = datetime.now(timezone.utc).isoformat()
        (out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
        if marker.is_file() and marker.read_text() == 'mu-crowd-synthetic-v1\n':
            # Only this newly created prefix. Never use global process-name shutdown.
            # Exit 1 also occurs with no server, e.g. compilation failed before startup.
            run([str(server), '-k'], 'cleanup-stop', timeout=20, accepted=(0, 1))
            run([str(server), '-w'], 'cleanup-wait', timeout=20)
            shutil.rmtree(prefix)
    return 3 if args.require_budget and not summary.get('optimized_p95_within_40ms') else 0


if __name__ == '__main__':
    sys.exit(main())
