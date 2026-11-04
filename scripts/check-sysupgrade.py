#!/usr/bin/env python3
"""Read-only image preflight for JDCloud RE-CS-02 sysupgrade tar images.

This does not prove a device will boot. It never writes to a router/device.
"""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile

BOARD = 'jdcloud_re-cs-02'
LIMIT = 6 * 1024 * 1024
ROOT_LIMIT = 2 * 1024 * 1024 * 1024
OVERLAY_ALIGN = 64 * 1024
OVERLAY_RESET = 4096
KERNEL_MAGIC = bytes.fromhex('d00dfeed')
ROOT_MAGIC = b'hsqs'


def check(path):
    report = {'file': path.name, 'board': BOARD, 'sha256': hashlib.file_digest(path.open('rb'), 'sha256').hexdigest(), 'checks': {}}
    checks = report['checks']
    def test(key, outcome):
        checks[key] = bool(outcome)
    try:
        with tarfile.open(path, 'r:*') as archive:
            members = archive.getmembers()
            base = f'sysupgrade-{BOARD}'
            directories = [i.name.rstrip('/') for i in members
                           if i.isdir() and i.name.startswith('sysupgrade-')]
            test('upgrade_directory', directories == [base])
            names = {i.name: i for i in members if i.isfile()}
            names_required = [f'{base}/{part}' for part in ('CONTROL','kernel','root')]
            test('expected_members', all(s in names and sum(i.name == s for i in members) == 1
                                         for s in names_required))
            if not checks['expected_members']:
                report['passed'] = False
                return report
            control = archive.extractfile(names_required[0]).read(4096).decode('ascii',errors='replace')
            test('correct_board', any(line.strip() == f'BOARD={BOARD}' for line in control.splitlines()))
            kernel_size = names[names_required[1]].size
            root_size = names[names_required[2]].size
            report.update({'kernel_size':kernel_size, 'root_size':root_size})
            test('kernel_fits_6_mib', 0 < kernel_size <= LIMIT)
            test('rootfs_nonempty', root_size > 65536)
            overlay_start = (root_size + OVERLAY_ALIGN - 1) // OVERLAY_ALIGN * OVERLAY_ALIGN
            test('rootfs_and_overlay_reset_fit_2_gib', overlay_start + OVERLAY_RESET <= ROOT_LIMIT)
            k = archive.extractfile(names_required[1]).read(8)
            r = archive.extractfile(names_required[2]).read(4)
            test('kernel_fit_fdt_header', len(k) == 8 and k.startswith(KERNEL_MAGIC)
                 and 40 <= int.from_bytes(k[4:8], 'big') <= kernel_size)
            test('root_squashfs_header', r == ROOT_MAGIC)
    except (tarfile.TarError, OSError) as exc:
        report['error'] = str(exc)
        report['passed'] = False
        return report
    report['passed'] = all(checks.values())
    report['warning'] = 'Static header preflight only; does NOT certify DTB, eMMC upgrade, boot or stability.'
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', type=Path)
    args = parser.parse_args()
    result = check(args.image)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if result['passed'] else 1)

