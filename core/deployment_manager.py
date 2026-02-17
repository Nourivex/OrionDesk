from __future__ import annotations

import json
from pathlib import Path
import shutil


class ReleaseChannelManager:
    def __init__(self, config_dir: Path | None = None) -> None:
        self.config_dir = config_dir or (Path(".oriondesk") / "deployment")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.channel_file = self.config_dir / "channel.json"

    def get_channel(self) -> str:
        if not self.channel_file.exists():
            return "stable"
        payload = json.loads(self.channel_file.read_text(encoding="utf-8"))
        return payload.get("channel", "stable")

    def set_channel(self, channel: str) -> str:
        if channel not in {"stable", "beta"}:
            raise ValueError("Channel hanya boleh stable atau beta")
        self.channel_file.write_text(json.dumps({"channel": channel}), encoding="utf-8")
        return channel


class ConfigMigrationManager:
    def migrate(self, payload: dict, from_version: str, to_version: str) -> dict:
        result = dict(payload)
        result["config_version"] = to_version
        result["previous_version"] = from_version
        return result


class ProfileBackupManager:
    def __init__(self, backup_dir: Path | None = None) -> None:
        self.backup_dir = backup_dir or (Path(".oriondesk") / "backup")
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def backup(self, source_dir: Path, backup_name: str) -> Path:
        target = self.backup_dir / backup_name
        archive_path = shutil.make_archive(str(target), "zip", root_dir=str(source_dir))
        return Path(archive_path)

    def restore(self, archive_path: Path, target_dir: Path) -> Path:
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.unpack_archive(str(archive_path), str(target_dir), "zip")
        return target_dir
