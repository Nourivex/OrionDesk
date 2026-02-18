from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class TriggerActionRule:
    rule_id: str
    name: str
    trigger_type: str
    trigger_config: dict
    action_command: str
    risk_level: str = "low"
    enabled: bool = True


@dataclass(frozen=True)
class AutomationExecution:
    rule_id: str
    rule_name: str
    action_command: str
    status: str
    message: str
    executed_at: str


@dataclass
class TriggerActionRegistry:
    rules: dict[str, TriggerActionRule] = field(default_factory=dict)

    def register(self, rule: TriggerActionRule) -> None:
        self.rules[rule.rule_id] = rule

    def enabled_rules(self) -> list[TriggerActionRule]:
        return [rule for rule in self.rules.values() if rule.enabled]

    def load_from_file(self, path: Path) -> int:
        payload = self._read_payload(path)
        raw_rules = payload.get("rules", [])
        for item in raw_rules:
            self.register(self._to_rule(item))
        return len(raw_rules)

    def _read_payload(self, path: Path) -> dict:
        if path.suffix.lower() in {".yaml", ".yml"}:
            return self._read_yaml(path)
        return json.loads(path.read_text(encoding="utf-8"))

    def _read_yaml(self, path: Path) -> dict:
        try:
            import yaml  # type: ignore
        except ImportError as error:
            raise RuntimeError("YAML rules membutuhkan dependency PyYAML.") from error
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return data or {}

    def _to_rule(self, payload: dict) -> TriggerActionRule:
        return TriggerActionRule(
            rule_id=str(payload["rule_id"]),
            name=str(payload["name"]),
            trigger_type=str(payload["trigger_type"]),
            trigger_config=dict(payload.get("trigger_config", {})),
            action_command=str(payload["action_command"]),
            risk_level=str(payload.get("risk_level", "low")),
            enabled=bool(payload.get("enabled", True)),
        )


@dataclass
class FileWatcherEngine:
    snapshots: dict[str, dict[str, int]] = field(default_factory=dict)

    def triggered_rules(self, rules: list[TriggerActionRule]) -> list[str]:
        fired: list[str] = []
        for rule in rules:
            if rule.trigger_type != "file_watch":
                continue
            path = Path(str(rule.trigger_config.get("path", "")))
            pattern = str(rule.trigger_config.get("pattern", "*"))
            current = self._snapshot(path, pattern)
            previous = self.snapshots.get(rule.rule_id)
            self.snapshots[rule.rule_id] = current
            if previous is None:
                continue
            if self._has_changes(previous, current):
                fired.append(rule.rule_id)
        return fired

    def _snapshot(self, root: Path, pattern: str) -> dict[str, int]:
        if not root.exists() or not root.is_dir():
            return {}
        files = root.rglob(pattern)
        snapshot: dict[str, int] = {}
        for item in files:
            if not item.is_file():
                continue
            snapshot[str(item)] = item.stat().st_mtime_ns
        return snapshot

    def _has_changes(self, previous: dict[str, int], current: dict[str, int]) -> bool:
        if set(previous.keys()) != set(current.keys()):
            return True
        for key, old_mtime in previous.items():
            if current.get(key) != old_mtime:
                return True
        return False


@dataclass
class SchedulerEngine:
    last_run: dict[str, datetime] = field(default_factory=dict)

    def triggered_rules(self, rules: list[TriggerActionRule], now: datetime) -> list[str]:
        fired: list[str] = []
        for rule in rules:
            if rule.trigger_type != "schedule":
                continue
            interval = self._interval_seconds(rule)
            if interval <= 0:
                continue
            previous = self.last_run.get(rule.rule_id)
            if previous is None or (now - previous) >= timedelta(seconds=interval):
                self.last_run[rule.rule_id] = now
                fired.append(rule.rule_id)
        return fired

    def _interval_seconds(self, rule: TriggerActionRule) -> int:
        raw = rule.trigger_config.get("interval_seconds", 0)
        try:
            return int(raw)
        except (TypeError, ValueError):
            return 0


@dataclass
class TriggerActionAutomationEngine:
    registry: TriggerActionRegistry
    execute_command: Callable[[str], object]
    approval_hook: Callable[[TriggerActionRule], bool] | None = None
    file_watcher: FileWatcherEngine = field(default_factory=FileWatcherEngine)
    scheduler: SchedulerEngine = field(default_factory=SchedulerEngine)

    def run_cycle(self, now: datetime | None = None) -> list[AutomationExecution]:
        current = now or datetime.now(UTC)
        active_rules = self.registry.enabled_rules()

        triggered = self.file_watcher.triggered_rules(active_rules)
        triggered.extend(self.scheduler.triggered_rules(active_rules, current))

        executions: list[AutomationExecution] = []
        for rule_id in list(dict.fromkeys(triggered)):
            rule = self.registry.rules.get(rule_id)
            if rule is None:
                continue
            executions.append(self._run_rule(rule, current))
        return executions

    def _run_rule(self, rule: TriggerActionRule, now: datetime) -> AutomationExecution:
        approve = self.approval_hook or (lambda _rule: True)
        if self._is_high_risk(rule) and not approve(rule):
            return AutomationExecution(
                rule_id=rule.rule_id,
                rule_name=rule.name,
                action_command=rule.action_command,
                status="blocked",
                message="Rule blocked by approval hook.",
                executed_at=self._to_iso(now),
            )

        result = self.execute_command(rule.action_command)
        status, message = self._normalize_result(result)
        return AutomationExecution(
            rule_id=rule.rule_id,
            rule_name=rule.name,
            action_command=rule.action_command,
            status=status,
            message=message,
            executed_at=self._to_iso(now),
        )

    def _normalize_result(self, result: object) -> tuple[str, str]:
        message = str(getattr(result, "message", result))
        requires_confirmation = bool(getattr(result, "requires_confirmation", False))
        if requires_confirmation:
            return "pending_confirmation", message
        lowered = message.lower()
        if "ditolak" in lowered or "blocked" in lowered or "error" in lowered:
            return "failed", message
        return "success", message

    def _is_high_risk(self, rule: TriggerActionRule) -> bool:
        return rule.risk_level.lower() in {"high", "critical"}

    def _to_iso(self, value: datetime) -> str:
        return value.astimezone(UTC).isoformat(timespec="seconds")
