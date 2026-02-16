from pathlib import Path

from persona.persona_engine import PersonaEngine


def test_format_output_with_existing_profile() -> None:
    profile_dir = Path(__file__).resolve().parents[1] / "persona" / "profiles"
    engine = PersonaEngine(profile_dir=profile_dir, persona_name="calm")
    formatted = engine.format_output("Halo")
    assert formatted.startswith("[Calm]")
    assert "Halo" in formatted


def test_format_output_with_missing_profile() -> None:
    profile_dir = Path(__file__).resolve().parents[1] / "persona" / "profiles"
    engine = PersonaEngine(profile_dir=profile_dir, persona_name="not-found")
    formatted = engine.format_output("Halo")
    assert formatted == "Halo"


def test_format_warning_respects_verbosity() -> None:
    profile_dir = Path(__file__).resolve().parents[1] / "persona" / "profiles"
    calm = PersonaEngine(profile_dir=profile_dir, persona_name="calm")
    hacker = PersonaEngine(profile_dir=profile_dir, persona_name="hacker")

    calm_warning = calm.format_warning("Aksi berisiko", detail="Menyentuh file sistem")
    hacker_warning = hacker.format_warning("Aksi berisiko", detail="Menyentuh file sistem")

    assert "Detail:" in calm_warning
    assert "Detail:" not in hacker_warning


def test_accepts_risk_uses_profile_tolerance() -> None:
    profile_dir = Path(__file__).resolve().parents[1] / "persona" / "profiles"
    calm = PersonaEngine(profile_dir=profile_dir, persona_name="calm")
    hacker = PersonaEngine(profile_dir=profile_dir, persona_name="hacker")

    assert calm.accepts_risk("low") is True
    assert calm.accepts_risk("high") is False
    assert hacker.accepts_risk("high") is True


def test_set_persona_changes_output_style() -> None:
    profile_dir = Path(__file__).resolve().parents[1] / "persona" / "profiles"
    engine = PersonaEngine(profile_dir=profile_dir, persona_name="calm")
    first = engine.format_output("Halo")
    engine.set_persona("hacker")
    second = engine.format_output("Halo")

    assert first.startswith("[Calm]")
    assert second.startswith("[Hacker]")