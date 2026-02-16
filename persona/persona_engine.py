import json
from pathlib import Path


class PersonaEngine:
    def __init__(self, profile_dir: Path | None = None, persona_name: str = "calm") -> None:
        base_dir = Path(__file__).resolve().parent / "profiles"
        self.profile_dir = profile_dir or base_dir
        self.persona_name = persona_name

    def format_output(self, message: str) -> str:
        profile = self._load_profile(self.persona_name)
        prefix = profile.get("prefix", "")
        suffix = profile.get("suffix", "")
        return f"{prefix}{message}{suffix}".strip()

    def _load_profile(self, persona_name: str) -> dict:
        profile_file = self.profile_dir / f"{persona_name}.json"
        if not profile_file.exists():
            return {"prefix": "", "suffix": ""}

        with profile_file.open("r", encoding="utf-8") as file:
            return json.load(file)