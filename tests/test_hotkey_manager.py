from core.hotkey_manager import GlobalHotkeyManager


def test_hotkey_normalization() -> None:
    manager = GlobalHotkeyManager()
    assert manager.normalize("shift+win+o") == "Win+Shift+O"


def test_hotkey_conflict_detection_with_reserved() -> None:
    manager = GlobalHotkeyManager()
    conflict, reason = manager.is_conflicted("Alt+Space")

    assert conflict is True
    assert "konflik" in reason.lower()


def test_hotkey_conflict_detection_with_local_shortcuts() -> None:
    manager = GlobalHotkeyManager()
    conflict, reason = manager.is_conflicted("Ctrl+K", local_shortcuts={"Ctrl+K"})

    assert conflict is True
    assert "shortcut internal" in reason.lower()


def test_windows_binding_generation() -> None:
    manager = GlobalHotkeyManager()
    binding = manager.to_windows_binding("Ctrl+Shift+O")

    assert binding is not None
    modifiers, keycode = binding
    assert modifiers > 0
    assert keycode == ord("O")
