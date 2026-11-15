"""Retiene un archivo XLSX con uso exclusivo hasta recibir Enter (QA R5)."""
from __future__ import annotations

import ctypes
from ctypes import wintypes
from pathlib import Path
import sys

path = Path(sys.argv[1]).resolve(strict=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
create_file = kernel32.CreateFileW
create_file.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
                        ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
create_file.restype = wintypes.HANDLE
close_handle = kernel32.CloseHandle
close_handle.argtypes = [wintypes.HANDLE]
close_handle.restype = wintypes.BOOL

handle = create_file(str(path), 0x80000000, 0, None, 3, 0x80, None)
if handle == ctypes.c_void_p(-1).value:
    raise OSError(ctypes.get_last_error(), f"No se pudo bloquear {path}")

try:
    print(f"LOCKED {path}", flush=True)
    input("Enter para liberar... ")
finally:
    close_handle(handle)
    print("RELEASED", flush=True)
