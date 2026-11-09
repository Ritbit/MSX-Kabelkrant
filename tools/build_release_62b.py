#!/usr/bin/env python3
"""Rebuild 6.2b MSX FAT12 disk/ZIP from original 6.2 plus src/ BASIC files.

No external FAT tools or network required. Preserves boot code, graphics, RAMdisk,
unchanged files and original archive; verifies disk and ZIP before writing.
"""
from pathlib import Path
from io import BytesIO
from zipfile import ZipFile
from hashlib import sha1, sha256
import argparse

FILES = ('AUTOEXEC.BAS', 'KBLINIT.SYS', 'LOOP.SYS')
ORIGINAL_DSK = '2fcd117bc57aedb5e3851224e5ca6ab3a1d18d95'
ORIGINAL_ZIP = 'ccd1273aae064abea58a94292c2d1ce0129319ab'


def git_blob(data):
    return sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def dos_text(raw):
    if not raw.endswith(b'\n') or b'\r' in raw:
        raise ValueError('BASIC source must be LF text ending in newline')
    return raw.replace(b'\n', b'\r\n')


class Disk:
    def __init__(self, data):
        self.data = bytearray(data)
        b = self.data
        self.bps = int.from_bytes(b[11:13], 'little')
        self.spc = b[13]
        self.reserved = int.from_bytes(b[14:16], 'little')
        self.fats = b[16]
        self.nroot = int.from_bytes(b[17:19], 'little')
        self.spf = int.from_bytes(b[22:24], 'little')
        if (len(b), self.bps, self.spc, self.fats, self.spf) != (737280, 512, 2, 2, 3):
            raise ValueError('Incorrect original MSX FAT12 geometry')
        self.root = (self.reserved + self.fats * self.spf) * self.bps
        self.start = self.root + ((self.nroot * 32 + self.bps - 1) // self.bps) * self.bps
        self.fat = self.reserved * self.bps

    def entries(self):
        for i in range(self.nroot):
            pos = self.root + i * 32
            e = self.data[pos:pos + 32]
            if e[0] == 0:
                break
            if e[0] == 0xe5:
                continue
            name = e[:8].decode('ascii').strip() + '.' + e[8:11].decode('ascii').strip()
            yield name, pos

    def chain(self, pos):
        c = int.from_bytes(self.data[pos + 26:pos + 28], 'little')
        seen = set()
        while 2 <= c < 0xff8:
            if c in seen:
                raise ValueError('Cyclic FAT12 chain')
            seen.add(c)
            yield c
            off = self.fat + c * 3 // 2
            val = int.from_bytes(self.data[off:off + 2], 'little')
            c = val >> 4 if c & 1 else val & 0xfff

    def read(self, name):
        p = dict(self.entries())[name]
        size = int.from_bytes(self.data[p + 28:p + 32], 'little')
        raw = b''.join(self.data[self.start + (c - 2) * 1024:self.start + (c - 1) * 1024] for c in self.chain(p))
        if len(raw) < size:
            raise ValueError('Broken FAT chain in ' + name)
        return bytes(raw[:size])

    def replace(self, name, value):
        p = dict(self.entries())[name]
        clusters = list(self.chain(p))
        if len(value) > len(clusters) * 1024:
            raise ValueError(name + ' exceeds original cluster allocation')
        padded = value.ljust(len(clusters) * 1024, b'\0')
        for i, cluster in enumerate(clusters):
            off = self.start + (cluster - 2) * 1024
            self.data[off:off + 1024] = padded[i * 1024:(i + 1) * 1024]
        self.data[p + 28:p + 32] = len(value).to_bytes(4, 'little')
        assert self.read(name) == value


def build(root):
    assets = root / 'assets'
    disk = (assets / 'kabelkrant-6.2.dsk').read_bytes()
    archive = (assets / 'kabelkrant-6.2.zip').read_bytes()
    if git_blob(disk) != ORIGINAL_DSK or git_blob(archive) != ORIGINAL_ZIP:
        raise ValueError('Historical 6.2 release does not match original Git objects')
    changes = {name: dos_text((root / 'src' / name).read_bytes()) for name in FILES}
    for name, data in changes.items():
        if b'V6.2b' not in data:
            raise ValueError('Version not updated in ' + name)
    old = Disk(disk)
    new = Disk(disk)
    for name, value in changes.items():
        new.replace(name, value)
    old_names = [name for name, _ in old.entries()]
    assert old_names == [name for name, _ in new.entries()]
    assert len(old_names) == 30
    for name in old_names:
        if name not in FILES:
            assert old.read(name) == new.read(name), name
    dest = BytesIO()
    with ZipFile(BytesIO(archive)) as previous, ZipFile(dest, 'w') as zipped:
        assert sorted(previous.namelist()) == sorted(old_names)
        for info in previous.infolist():
            name = info.filename
            original = previous.read(name)
            assert original == old.read(name), name
            zipped.writestr(info, changes.get(name, original))
    zip_data = dest.getvalue()
    with ZipFile(BytesIO(zip_data)) as verify:
        assert sorted(verify.namelist()) == sorted(old_names)
        for name in old_names:
            assert verify.read(name) == new.read(name), name

    (assets / 'kabelkrant-6.2b.dsk').write_bytes(new.data)
    (assets / 'kabelkrant-6.2b.zip').write_bytes(zip_data)
    print('Version 6.2b: updated 3 BASIC files, preserved 27 other files')
    print('Disk size:', len(new.data), 'SHA256:', sha256(new.data).hexdigest())
    print('ZIP size:', len(zip_data), 'SHA256:', sha256(zip_data).hexdigest())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path('.'))
    build(parser.parse_args().root)
