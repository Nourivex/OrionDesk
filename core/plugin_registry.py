from __future__ import annotations

from dataclasses import dataclass
import importlib
import pkgutil


@dataclass(frozen=True)
class PluginCommandDefinition:
    keyword: str
    usage: str
    min_args: int
    max_args: int | None
    first_arg_equals: str | None
    handler_name: str
    dangerous: bool


class PluginRegistry:
    def __init__(self, package_name: str = "plugins") -> None:
        self.package_name = package_name

    def discover(self) -> list[PluginCommandDefinition]:
        package = importlib.import_module(self.package_name)
        definitions: list[PluginCommandDefinition] = []
        seen_keywords: set[str] = set()

        for module_info in pkgutil.iter_modules(package.__path__, f"{self.package_name}."):
            module_name = module_info.name
            if not module_name.endswith("_plugin"):
                continue
            module = importlib.import_module(module_name)
            raw_items = getattr(module, "COMMAND_DEFINITIONS", [])
            for item in raw_items:
                definition = PluginCommandDefinition(
                    keyword=item["keyword"],
                    usage=item["usage"],
                    min_args=item.get("min_args", 0),
                    max_args=item.get("max_args"),
                    first_arg_equals=item.get("first_arg_equals"),
                    handler_name=item["handler_name"],
                    dangerous=item.get("dangerous", False),
                )
                if definition.keyword in seen_keywords:
                    raise ValueError(f"Keyword plugin duplikat: {definition.keyword}")
                seen_keywords.add(definition.keyword)
                definitions.append(definition)

        return definitions
