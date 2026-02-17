from core.safe_mode_policy import SafeModePolicy
from core.security_guard import SecurityGuard


def test_security_guard_command_whitelist() -> None:
    guard = SecurityGuard(command_whitelist={"open", "sys"})
    assert guard.is_command_allowed("open") is True
    assert guard.is_command_allowed("delete") is False


def test_security_guard_path_restriction(tmp_path) -> None:
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    inside = allowed / "data.txt"
    outside = tmp_path / "outside.txt"

    guard = SecurityGuard(command_whitelist={"delete"}, allowed_delete_roots=[allowed])
    assert guard.is_path_allowed(str(inside)) is True
    assert guard.is_path_allowed(str(outside)) is False


def test_security_guard_default_allows_current_working_directory() -> None:
    guard = SecurityGuard(command_whitelist={"delete"})
    assert guard.is_path_allowed(".") is True


def test_security_guard_process_guard() -> None:
    guard = SecurityGuard(command_whitelist={"kill"})
    assert guard.is_process_target_allowed("1234") is True
    assert guard.is_process_target_allowed("4") is False
    assert guard.is_process_target_allowed("lsass.exe") is False


def test_safe_mode_policy_behaviour() -> None:
    policy = SafeModePolicy(
        require_confirmation_for=("delete",),
        blocked_actions=("shutdown",),
    )
    assert policy.requires_confirmation("delete") is True
    assert policy.requires_confirmation("kill") is False
    assert policy.is_blocked("shutdown") is True