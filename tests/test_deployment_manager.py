from core.deployment_manager import ConfigMigrationManager, ProfileBackupManager, ReleaseChannelManager


def test_release_channel_manager_roundtrip(tmp_path) -> None:
    manager = ReleaseChannelManager(config_dir=tmp_path / "deploy")
    assert manager.get_channel() == "stable"
    manager.set_channel("beta")
    assert manager.get_channel() == "beta"


def test_config_migration_manager() -> None:
    manager = ConfigMigrationManager()
    payload = {"theme": "dark"}
    migrated = manager.migrate(payload, "1.2", "1.3")

    assert migrated["config_version"] == "1.3"
    assert migrated["previous_version"] == "1.2"


def test_profile_backup_restore(tmp_path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "config.json").write_text('{"a":1}', encoding="utf-8")

    manager = ProfileBackupManager(backup_dir=tmp_path / "backup")
    archive = manager.backup(source, "profile")

    target = tmp_path / "restore"
    manager.restore(archive, target)
    restored = target / "config.json"
    assert restored.exists() is True