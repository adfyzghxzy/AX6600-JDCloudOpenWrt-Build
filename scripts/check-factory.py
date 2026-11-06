#!/usr/bin/env python3
"""Check the RE-CS-02 combined factory layout against its sysupgrade payload."""
import hashlib
import json
from pathlib import Path
import struct
import sys
import tarfile

sysupgrade, factory = map(Path, sys.argv[1:])
with tarfile.open(sysupgrade) as archive:
    kernel = archive.extractfile('sysupgrade-jdcloud_re-cs-02/kernel').read()
    root = archive.extractfile('sysupgrade-jdcloud_re-cs-02/root').read()
image = factory.read_bytes()
kernel_limit = 6 * 1024 * 1024
assert len(kernel) <= kernel_limit, 'Kernel exceeds 6 MiB'
assert root[:4] == b'hsqs', 'Missing SquashFS magic'
used = struct.unpack_from('<Q', root, 40)[0]
assert 96 <= used <= len(root), 'Invalid SquashFS bytes_used'
assert image[:len(kernel)] == kernel, 'Factory kernel differs'
assert image[len(kernel):kernel_limit] == b'\x00' * (kernel_limit - len(kernel)), 'Invalid kernel padding'
assert image[kernel_limit:kernel_limit + used] == root[:used], 'Factory rootfs differs'
print(json.dumps({
    'passed': True,
    'layout': 'kernel FIT padded to 6 MiB, SquashFS rootfs, fwtool metadata',
    'kernel_bytes': len(kernel),
    'rootfs_offset': kernel_limit,
    'squashfs_bytes_used': used,
    'factory_sha256': hashlib.sha256(image).hexdigest(),
    'hardware_tested_factory': False,
}, indent=2))
