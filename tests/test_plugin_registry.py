from core.plugin_registry import PluginRegistry


def test_plugin_registry_discovers_default_plugins() -> None:
    registry = PluginRegistry(package_name="plugins")
    items = registry.discover()
    keywords = {item.keyword for item in items}

    assert "open" in keywords
    assert "search" in keywords
    assert "sys" in keywords
    assert "delete" in keywords
    assert "kill" in keywords
    assert "shutdown" in keywords


def test_plugin_registry_marks_dangerous_commands() -> None:
    registry = PluginRegistry(package_name="plugins")
    items = registry.discover()
    dangerous = {item.keyword for item in items if item.dangerous}

    assert dangerous == {"delete", "kill", "shutdown"}