#!/usr/bin/env python3
"""Fingerprint toolchain inputs and stabilize checkout mtimes for exact cache reuse."""
import hashlib
import os
from pathlib import Path
import platform
import subprocess
import sys

root = Path(sys.argv[1]).resolve()
os.chdir(root)
epoch = int(subprocess.check_output(['git', 'show', '-s', '--format=%ct', 'HEAD']))
h = hashlib.sha256()

def add(label, value):
    h.update(label.encode() + b'\0' + value + b'\0')

# Include build recipes, target defaults and kernel headers configuration.
for name in ['tools', 'toolchain', 'include', 'scripts', 'config', 'target']:
    for p in sorted(Path(name).rglob('*')):
        if p.is_symlink():
            add(str(p), os.readlink(p).encode())
        elif p.is_file():
            add(str(p), p.read_bytes())
for name in ['rules.mk', 'Makefile', 'Config.in']:
    add(name, Path(name).read_bytes())
# Package/UI selections do not change the compiler. Their toolchain-affecting
# selected symbols remain included (GCC, libc, kernel, target, build flags, etc.).
for line in Path('.config').read_text().splitlines():
    if line.startswith('CONFIG_') and not line.startswith(('CONFIG_PACKAGE_', 'CONFIG_LUCI_', 'CONFIG_DEFAULT_', 'CONFIG_VERSION_')):
        add('config', line.encode())
for var in ['ImageOS', 'ImageVersion']:
    add(var, os.environ.get(var, 'unknown').encode())
add('cache-helper', Path(__file__).read_bytes())
add('host-packages', subprocess.check_output(['dpkg-query', '-W', '-f=${Package}=${Version}\n']))
add('workspace', str(root).encode())
add('machine', platform.machine().encode())
for cmd in [['gcc', '--version'], ['ldd', '--version'], ['python3', '--version']]:
    add(cmd[0], subprocess.check_output(cmd, stderr=subprocess.STDOUT))

# New checkouts have new mtimes. With exact content keys, fixed source mtimes
# allow Make's original dependency checks to reuse cached tools without forcing
# stamp files or bypassing any compilation checks.
skip = {'.git', 'build_dir', 'staging_dir', 'dl', '.ccache', 'tmp', 'bin', 'logs'}
for directory, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in skip and not Path(directory, d).is_symlink()]
    for filename in files:
        p = Path(directory, filename)
        if not p.is_symlink():
            os.utime(p, (epoch, epoch))

with open(os.environ['GITHUB_OUTPUT'], 'a') as out:
    out.write('toolchain=' + h.hexdigest() + '\n')
print('Toolchain fingerprint:', h.hexdigest())
