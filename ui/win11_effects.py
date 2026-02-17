from __future__ import annotations

import ctypes


def apply_mica_or_acrylic(win_id: int) -> bool:
    if win_id <= 0:
        return False

    try:
        dwmapi = ctypes.windll.dwmapi
    except AttributeError:
        return False

    hwnd = ctypes.c_void_p(win_id)
    value = ctypes.c_int(2)
    attribute_mica = 38
    result = dwmapi.DwmSetWindowAttribute(
        hwnd,
        ctypes.c_uint(attribute_mica),
        ctypes.byref(value),
        ctypes.sizeof(value),
    )
    if result == 0:
        return True

    accent_state_acrylic = ctypes.c_int(3)
    attribute_acrylic = 19
    fallback = dwmapi.DwmSetWindowAttribute(
        hwnd,
        ctypes.c_uint(attribute_acrylic),
        ctypes.byref(accent_state_acrylic),
        ctypes.sizeof(accent_state_acrylic),
    )
    return fallback == 0
