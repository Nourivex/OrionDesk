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