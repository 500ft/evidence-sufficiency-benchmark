"""Serialize native CAD jobs on the Windows host with an OS-held lock."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import time


@contextmanager
def host_lock(path=r'C:\CADLoop\solidworks.lock'):
    import msvcrt
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('a+b') as handle:
        if handle.tell() == 0:
            handle.write(b' ')
            handle.flush()
        handle.seek(0)
        try:
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError as exc:
            raise RuntimeError('Another CAD job holds the SOLIDWORKS host lock') from exc
        try:
            owner = target.with_suffix('.owner.json')
            owner.write_text(json.dumps({'pid': os.getpid(), 'started_unix': time.time()}), encoding='utf-8')
            yield
        finally:
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
