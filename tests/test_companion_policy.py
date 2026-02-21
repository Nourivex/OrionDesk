import time

from core.companion_policy import CompanionPolicy


def test_companion_policy_uses_calm_threshold_by_default() -> None:
    policy = CompanionPolicy()
    now = time.monotonic()
    stamps = [now - 10 for _ in range(6)]

    fatigue = policy.evaluate_fatigue(stamps, profile_name="calm", active_tab="Memory", now=now)

    assert fatigue.threshold_used == 6
    assert fatigue.count_in_window == 6
    assert fatigue.force_confirmation is True
    assert fatigue.fatigue_penalty == 0.0


def test_companion_policy_applies_progressive_penalty() -> None:
    policy = CompanionPolicy()
    now = time.monotonic()
    stamps = [now - 5 for _ in range(8)]

    fatigue = policy.evaluate_fatigue(stamps, profile_name="calm", active_tab="Memory", now=now)

    assert fatigue.threshold_used == 6
    assert fatigue.count_in_window == 8
    assert fatigue.fatigue_penalty == 0.16
    assert fatigue.force_confirmation is True


def test_companion_policy_uses_hacker_threshold() -> None:
    policy = CompanionPolicy()
    now = time.monotonic()
    stamps = [now - 5 for _ in range(8)]

    fatigue = policy.evaluate_fatigue(stamps, profile_name="hacker", active_tab="Memory", now=now)

    assert fatigue.threshold_used == 12
    assert fatigue.force_confirmation is False
    assert fatigue.fatigue_penalty == 0.0


def test_companion_policy_command_tab_overrides_threshold() -> None:
    policy = CompanionPolicy()
    now = time.monotonic()
    stamps = [now - 5 for _ in range(8)]

    fatigue = policy.evaluate_fatigue(stamps, profile_name="calm", active_tab="Command", now=now)

    assert fatigue.threshold_used == 12
    assert fatigue.force_confirmation is False
