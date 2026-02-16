import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PersonaProfile:
    name: str
    prefix: str
    suffix: str
    warning_prefix: str
    warning_verbosity: str
    risk_tolerance: str


class PersonaEngine:
    def __init__(self, profile_dir: Path | None = None, persona_name: str = "calm") -> None:
        base_dir = Path(__file__).resolve().parent / "profiles"
        self.profile_dir = profile_dir or base_dir
        self.persona_name = persona_name

    def format_output(self, message: str) -> str:
        profile = self._load_profile(self.persona_name)
        return f"{profile.prefix}{message}{profile.suffix}".strip()

    def format_warning(self, message: str, detail: str | None = None) -> str:
        profile = self._load_profile(self.persona_name)
        lines = [f"{profile.warning_prefix} {message}".strip()]
        if detail and profile.warning_verbosity == "high":
            lines.append(f"Detail: {detail}")
        return "\n".join(lines)

    def accepts_risk(self, level: str) -> bool:
        profile = self._load_profile(self.persona_name)
        level_rank = {"low": 1, "medium": 2, "high": 3}
        tolerance = level_rank.get(profile.risk_tolerance, 1)
        risk = level_rank.get(level, 3)
        return risk <= tolerance

    def set_persona(self, persona_name: str) -> None:
        self.persona_name = persona_name

    def _load_profile(self, persona_name: str) -> PersonaProfile:
        profile_file = self.profile_dir / f"{persona_name}.json"
        if not profile_file.exists():
            return PersonaProfile(
                name="default",
                prefix="",
                suffix="",
                warning_prefix="Warning:",
                warning_verbosity="low",
                risk_tolerance="low",
            )

        with profile_file.open("r", encoding="utf-8") as file:
            payload = json.load(file)

        return PersonaProfile(
            name=payload.get("name", "default"),
            prefix=payload.get("prefix", ""),
            suffix=payload.get("suffix", ""),
            warning_prefix=payload.get("warning_prefix", "Warning:"),
            warning_verbosity=payload.get("warning_verbosity", "low"),
            risk_tolerance=payload.get("risk_tolerance", "low"),
        )