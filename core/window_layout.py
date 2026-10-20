"""Helpers for arranging concurrent Camoufox windows on Windows."""

from __future__ import annotations

import ctypes
import os
import time
from ctypes import wintypes


class _Rect(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]


class _ProcessEntry32W(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.c_size_t),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", wintypes.LONG),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", wintypes.WCHAR * 260),
    ]


def get_tiled_window_layout(
    window_size: tuple[int, int],
    window_index: int,
    window_count: int,
) -> tuple[tuple[int, int], tuple[int, int]]:
    """Arrange windows in a grid while preserving their requested height."""
    if os.name != "nt":
        raise OSError("El mosaico de ventanas solo está disponible en Windows.")
    if window_count < 2 or not 0 <= window_index < window_count:
        raise ValueError("El índice y la cantidad de ventanas no son válidos.")
    if window_size[0] < 1 or window_size[1] < 1:
        raise ValueError("El tamaño de ventana debe ser positivo.")

    work_area = _Rect()
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.SystemParametersInfoW.argtypes = [
        wintypes.UINT,
        wintypes.UINT,
        ctypes.POINTER(_Rect),
        wintypes.UINT,
    ]
    user32.SystemParametersInfoW.restype = wintypes.BOOL
    if not user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(work_area), 0):
        raise ctypes.WinError(ctypes.get_last_error())

    work_width = work_area.right - work_area.left
    work_height = work_area.bottom - work_area.top
    if work_width < 1 or work_height < 1:
        raise OSError("El área disponible de pantalla no permite acomodar las ventanas.")

    columns = 1
    while columns * columns < window_count:
        columns += 1
    max_rows = max(1, work_height // window_size[1])
    columns = max(columns, (window_count + max_rows - 1) // max_rows)
    rows = (window_count + columns - 1) // columns
    cell_width = work_width // columns
    cell_height = work_height // rows
    width = min(window_size[0], cell_width)
    height = window_size[1]
    column = window_index % columns
    row = window_index // columns
    return (
        (
            work_area.left + column * cell_width + (cell_width - width) // 2,
            work_area.top + row * cell_height + max(0, (cell_height - height) // 2),
        ),
        (width, height),
    )


def _get_process_tree_ids(root_pid: int) -> set[int]:
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
    kernel32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    kernel32.Process32FirstW.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(_ProcessEntry32W),
    ]
    kernel32.Process32FirstW.restype = wintypes.BOOL
    kernel32.Process32NextW.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(_ProcessEntry32W),
    ]
    kernel32.Process32NextW.restype = wintypes.BOOL
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL

    snapshot = kernel32.CreateToolhelp32Snapshot(0x00000002, 0)
    if snapshot == ctypes.c_void_p(-1).value:
        raise ctypes.WinError(ctypes.get_last_error())

    parents: dict[int, int] = {}
    try:
        entry = _ProcessEntry32W()
        entry.dwSize = ctypes.sizeof(entry)
        if kernel32.Process32FirstW(snapshot, ctypes.byref(entry)):
            while True:
                parents[entry.th32ProcessID] = entry.th32ParentProcessID
                if not kernel32.Process32NextW(snapshot, ctypes.byref(entry)):
                    break
    finally:
        kernel32.CloseHandle(snapshot)

    process_ids = {root_pid}
    while True:
        children = {
            process_id
            for process_id, parent_id in parents.items()
            if parent_id in process_ids and process_id not in process_ids
        }
        if not children:
            return process_ids
        process_ids.update(children)


def position_current_process_window(
    position: tuple[int, int],
    size: tuple[int, int],
    timeout_seconds: float = 10,
) -> bool:
    """Move the visible Firefox window owned by this worker's process tree."""
    if os.name != "nt":
        return False

    user32 = ctypes.WinDLL("user32", use_last_error=True)
    enum_windows_proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows.argtypes = [enum_windows_proc, wintypes.LPARAM]
    user32.EnumWindows.restype = wintypes.BOOL
    user32.GetWindowThreadProcessId.argtypes = [
        wintypes.HWND,
        ctypes.POINTER(wintypes.DWORD),
    ]
    user32.GetWindowThreadProcessId.restype = wintypes.DWORD
    user32.IsWindowVisible.argtypes = [wintypes.HWND]
    user32.IsWindowVisible.restype = wintypes.BOOL
    user32.IsIconic.argtypes = [wintypes.HWND]
    user32.IsIconic.restype = wintypes.BOOL
    user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(_Rect)]
    user32.GetWindowRect.restype = wintypes.BOOL
    user32.GetClassNameW.argtypes = [
        wintypes.HWND,
        wintypes.LPWSTR,
        ctypes.c_int,
    ]
    user32.GetClassNameW.restype = ctypes.c_int
    user32.SetWindowPos.argtypes = [
        wintypes.HWND,
        wintypes.HWND,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        wintypes.UINT,
    ]
    user32.SetWindowPos.restype = wintypes.BOOL

    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        process_ids = _get_process_tree_ids(os.getpid())
        candidates: list[tuple[bool, int, wintypes.HWND]] = []

        @enum_windows_proc
        def collect_window(hwnd: int, _lparam: int) -> bool:
            if not user32.IsWindowVisible(hwnd) or user32.IsIconic(hwnd):
                return True

            process_id = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
            if process_id.value not in process_ids:
                return True

            rect = _Rect()
            if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                return True
            area = (rect.right - rect.left) * (rect.bottom - rect.top)
            if area <= 0:
                return True

            class_name = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, class_name, len(class_name))
            is_firefox_window = class_name.value == "MozillaWindowClass"
            candidates.append((is_firefox_window, area, hwnd))
            return True

        if not user32.EnumWindows(collect_window, 0):
            raise ctypes.WinError(ctypes.get_last_error())

        firefox_candidates = [candidate for candidate in candidates if candidate[0]]
        matching_windows = firefox_candidates or candidates
        if matching_windows:
            hwnd = max(matching_windows, key=lambda candidate: candidate[1])[2]
            if user32.SetWindowPos(
                hwnd,
                None,
                position[0],
                position[1],
                size[0],
                size[1],
                0x0004 | 0x0010,
            ):
                return True
            raise ctypes.WinError(ctypes.get_last_error())

        time.sleep(0.2)

    return False
