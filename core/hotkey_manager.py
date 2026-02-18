from __future__ import annotations

from dataclasses import dataclass, field

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008


@dataclass
class GlobalHotkeyManager:
    active_hotkey: str = "Win+Shift+O"
    reserved_hotkeys: set[str] = field(
        default_factory=lambda: {
            "Alt+Space",
            "Ctrl+Shift+Esc",
            "Win+L",
        }
    )

    def normalize(self, hotkey: str) -> str:
        chunks = [item.strip().title() for item in hotkey.split("+") if item.strip()]
        modifiers = [item for item in chunks if item in {"Win", "Ctrl", "Alt", "Shift"}]
        keys = [item for item in chunks if item not in {"Win", "Ctrl", "Alt", "Shift"}]
        ordered_mods = [item for item in ["Win", "Ctrl", "Alt", "Shift"] if item in modifiers]
        return "+".join(ordered_mods + keys[:1])

    def is_conflicted(self, hotkey: str, local_shortcuts: set[str] | None = None) -> tuple[bool, str]:
        normalized = self.normalize(hotkey)
        if normalized in {self.normalize(item) for item in self.reserved_hotkeys}:
            return True, f"Hotkey konflik dengan OS/global binding: {normalized}"

        local = local_shortcuts or set()
        if normalized in {self.normalize(item) for item in local}:
            return True, f"Hotkey konflik dengan shortcut internal: {normalized}"
        return False, ""

    def set_hotkey(self, hotkey: str) -> None:
        self.active_hotkey = self.normalize(hotkey)

    def to_windows_binding(self, hotkey: str) -> tuple[int, int] | None:
        normalized = self.normalize(hotkey)
        parts = normalized.split("+")
        if len(parts) < 2:
            return None

        modifiers = 0
        for part in parts[:-1]:
            if part == "Alt":
                modifiers |= MOD_ALT
            if part == "Ctrl":
                modifiers |= MOD_CONTROL
            if part == "Shift":
                modifiers |= MOD_SHIFT
            if part == "Win":
                modifiers |= MOD_WIN

        key_text = parts[-1]
        if len(key_text) == 1 and key_text.isalpha():
            return modifiers, ord(key_text.upper())
        if key_text == "Space":
            return modifiers, 0x20
        return None
