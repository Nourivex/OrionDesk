from __future__ import annotations

import getpass
import os
import time
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable
from uuid import uuid4

from core.capability_guardrail import CapabilityGuardrail
from core.capability_layer import SystemCapabilityLayer
from core.deployment_manager import ConfigMigrationManager, ProfileBackupManager, ReleaseChannelManager
from core.argument_extractor import ArgumentExtractor
from core.embedding_provider import EmbeddingConfig, EmbeddingProvider, OllamaEmbeddingProvider
from core.generation_provider import GenerationConfig, GenerationProvider, OllamaGenerationProvider
from core.latency_budget import LatencyBudget, MainThreadResponsivenessGuard
from core.execution_profile import ExecutionProfilePolicy
from core.executor import ExecutionContext, UnifiedCommandExecutor, build_execution_timestamp
from core.intent_engine import LocalIntentEngine
from core.intent_graph import IntentGraphPlanner
from core.memory_engine import MemoryEngine
from core.multi_command_executor import MultiCommandExecutor
from core.observability import DiagnosticReporter, HealthMonitor, RecoveryManager, StructuredLogger
from core.plugin_registry import PluginRegistry
from core.performance_profiler import PerformanceProfiler
from core.reasoning_engine import ComplexReasoningEngine
from core.retrieval_optimizer import RetrievalOptimizer
from core.release_hardening import ReleaseHardeningPlan
from core.safe_mode_policy import SafeModePolicy
from core.security_guard import SecurityGuard
from core.session import SessionLayer
from core.smart_assist import SmartAssistEngine
from core.system_intent_mapper import SystemIntentMapper
from modules.clipboard_manager import ClipboardManager
from modules.file_manager import FileManager
from modules.focus_mode import FocusModeManager
from modules.launcher import Launcher
from modules.network_diagnostics import NetworkDiagnostics
from modules.project_manager import ProjectManager
from modules.system_actions import SystemActions
from modules.system_tools import SystemTools


@dataclass(frozen=True)
class ParsedCommand:
    keyword: str
    args: list[str]
    raw: str


@dataclass(frozen=True)
class CommandResult:
    message: str
    requires_confirmation: bool = False
    pending_command: str | None = None


@dataclass(frozen=True)
class CommandContract:
    keyword: str
    usage: str
    min_args: int = 0
    max_args: int | None = None
    first_arg_equals: str | None = None


@dataclass
class CommandRouter:
    launcher: Launcher | None = None
    file_manager: FileManager | None = None
    system_tools: SystemTools | None = None
    handlers: dict[str, Callable[[ParsedCommand], str]] | None = None
    contracts: dict[str, CommandContract] | None = None
    dangerous_keywords: set[str] | None = None
    safe_mode: bool = True
    pending_confirmation: ParsedCommand | None = None
    pending_autocorrect: str | None = None
    session_layer: SessionLayer | None = None
    safe_mode_policy: SafeModePolicy | None = None
    security_guard: SecurityGuard | None = None
    intent_engine: LocalIntentEngine | None = None
    memory_engine: MemoryEngine | None = None
    logger: StructuredLogger | None = None
    recovery_manager: RecoveryManager | None = None
    health_monitor: HealthMonitor | None = None
    diagnostic_reporter: DiagnosticReporter | None = None
    release_channel_manager: ReleaseChannelManager | None = None
    migration_manager: ConfigMigrationManager | None = None
    backup_manager: ProfileBackupManager | None = None
    executor: UnifiedCommandExecutor | None = None
    session_id: str | None = None
    capability_layer: SystemCapabilityLayer | None = None
    capability_guardrail: CapabilityGuardrail | None = None
    system_intent_mapper: SystemIntentMapper | None = None
    smart_assist: SmartAssistEngine | None = None
    system_actions: SystemActions | None = None
    execution_profile_policy: ExecutionProfilePolicy | None = None
    project_manager: ProjectManager | None = None
    clipboard_manager: ClipboardManager | None = None
    focus_mode_manager: FocusModeManager | None = None
    network_diagnostics: NetworkDiagnostics | None = None
    performance_profiler: PerformanceProfiler | None = None
    release_hardening_plan: ReleaseHardeningPlan | None = None
    embedding_provider: EmbeddingProvider | None = None
    generation_provider: GenerationProvider | None = None
    chat_model_enabled: bool = True
    response_quality: str = "balanced"
    intent_graph_planner: IntentGraphPlanner | None = None
    reasoning_engine: ComplexReasoningEngine | None = None
    argument_extractor: ArgumentExtractor | None = None
    multi_command_executor: MultiCommandExecutor | None = None
    retrieval_optimizer: RetrievalOptimizer | None = None

    def __post_init__(self) -> None:
        self.launcher = self.launcher or Launcher()
        self.file_manager = self.file_manager or FileManager()
        self.system_tools = self.system_tools or SystemTools()
        self.handlers = {}
        self.contracts = {}
        self.dangerous_keywords = set()
        self.session_layer = self.session_layer or SessionLayer(session_name="router-session")
        self.safe_mode_policy = self.safe_mode_policy or SafeModePolicy()
        self.intent_engine = self.intent_engine or LocalIntentEngine()
        self.memory_engine = self.memory_engine or MemoryEngine()
        self.logger = self.logger or StructuredLogger()
        self.recovery_manager = self.recovery_manager or RecoveryManager()
        self.health_monitor = self.health_monitor or HealthMonitor()
        self.diagnostic_reporter = self.diagnostic_reporter or DiagnosticReporter()
        self.release_channel_manager = self.release_channel_manager or ReleaseChannelManager()
        self.migration_manager = self.migration_manager or ConfigMigrationManager()
        self.backup_manager = self.backup_manager or ProfileBackupManager()
        self.executor = self.executor or UnifiedCommandExecutor()
        self.capability_layer = self.capability_layer or SystemCapabilityLayer()
        self.capability_guardrail = self.capability_guardrail or CapabilityGuardrail(permission_tier="basic")
        self.system_intent_mapper = self.system_intent_mapper or SystemIntentMapper()
        self.smart_assist = self.smart_assist or SmartAssistEngine()
        self.system_actions = self.system_actions or SystemActions()
        self.execution_profile_policy = self.execution_profile_policy or ExecutionProfilePolicy(profile="power")
        self.project_manager = self.project_manager or ProjectManager()
        self.clipboard_manager = self.clipboard_manager or ClipboardManager()
        self.focus_mode_manager = self.focus_mode_manager or FocusModeManager()
        self.network_diagnostics = self.network_diagnostics or NetworkDiagnostics()
        self.performance_profiler = self.performance_profiler or PerformanceProfiler()
        self.release_hardening_plan = self.release_hardening_plan or ReleaseHardeningPlan()
        self.embedding_provider = self.embedding_provider or OllamaEmbeddingProvider(
            config=self._build_embedding_config_from_env()
        )
        self.generation_provider = self.generation_provider or OllamaGenerationProvider(
            config=self._build_generation_config_from_env()
        )
        env_chat_model = os.getenv("ORIONDESK_CHAT_MODEL_ENABLED")
        if env_chat_model is not None:
            self.chat_model_enabled = env_chat_model.strip() not in {"0", "false", "False"}
        elif os.getenv("PYTEST_CURRENT_TEST"):
            self.chat_model_enabled = False
        self.intent_graph_planner = self.intent_graph_planner or IntentGraphPlanner()
        self.reasoning_engine = self.reasoning_engine or ComplexReasoningEngine()
        self.argument_extractor = self.argument_extractor or ArgumentExtractor()
        self.multi_command_executor = self.multi_command_executor or MultiCommandExecutor()
        self.retrieval_optimizer = self.retrieval_optimizer or RetrievalOptimizer()
        self.session_id = self.session_id or uuid4().hex
        self._runtime_pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="oriondesk-runtime")
        self._main_thread_guard = MainThreadResponsivenessGuard()
        self._model_catalog_cache: list[dict] = []
        self._health_cache: dict[str, tuple[float, dict]] = {}
        self._health_cache_ttl_seconds = 20.0
        self._register_plugins()
        self.security_guard = self.security_guard or SecurityGuard(command_whitelist=set(self.contracts.keys()))

    def _build_embedding_config_from_env(self) -> EmbeddingConfig:
        host = os.getenv("ORIONDESK_OLLAMA_HOST", "http://localhost:11434")
        model = os.getenv("ORIONDESK_EMBED_MODEL", "nomic-embed-text:latest")
        timeout_text = os.getenv("ORIONDESK_OLLAMA_TIMEOUT", "3.0")
        try:
            timeout_seconds = float(timeout_text)
        except ValueError:
            timeout_seconds = 3.0
        return EmbeddingConfig(host=host, model=model, timeout_seconds=timeout_seconds)

    def _build_generation_config_from_env(self) -> GenerationConfig:
        host = os.getenv("ORIONDESK_OLLAMA_HOST", "http://localhost:11434")
        model = os.getenv("ORIONDESK_GEN_MODEL", "gemma3:4b")
        timeout_text = os.getenv("ORIONDESK_GEN_TIMEOUT", "8.0")
        token_budget_text = os.getenv("ORIONDESK_GEN_TOKEN_BUDGET", "256")
        temperature_text = os.getenv("ORIONDESK_GEN_TEMPERATURE", "0.2")

        try:
            timeout_seconds = float(timeout_text)
        except ValueError:
            timeout_seconds = 8.0
        try:
            token_budget = int(token_budget_text)
        except ValueError:
            token_budget = 256
        try:
            temperature = float(temperature_text)
        except ValueError:
            temperature = 0.2

        return GenerationConfig(
            host=host,
            model=model,
            timeout_seconds=timeout_seconds,
            token_budget=max(32, token_budget),
            temperature=max(0.0, min(1.0, temperature)),
        )

    def route(self, command: str) -> str:
        return self.execute(command).message

    def execute(self, command: str, dry_run: bool = False, allow_autocorrect: bool = True) -> CommandResult:
        if self._contains_multi_step(command):
            return self._execute_multi_step(command, dry_run=dry_run)

        if command.strip().lower().startswith("explain "):
            explain_target = command.strip()[8:]
            message = self.smart_assist.explain(explain_target)
            context = self._build_execution_context(command, dry_run=True)
            self._record_session(command, message, "success", context)
            return CommandResult(message)

        normalized = self._resolve_intent(command)
        normalized = self._normalize_shortcuts(normalized)
        correction = self._resolve_autocorrect(normalized, allow_autocorrect)
        if correction is not None:
            if correction.requires_confirmation:
                self.pending_autocorrect = correction.corrected
                message = f"Smart Assist correction suggested (confidence={correction.confidence:.2f}): {correction.corrected}"
                context = self._build_execution_context(command, dry_run=True)
                self._record_session(command, message, "pending_confirmation", context)
                return CommandResult(message, requires_confirmation=True, pending_command=correction.corrected)
            normalized = correction.corrected

        profile_block = self._apply_profile_policy(normalized)
        if profile_block is not None:
            return profile_block

        context = self._build_execution_context(normalized, dry_run=dry_run)
        envelope = self.executor.run(self, normalized, context)
        self._record_session(normalized or command, envelope.message, envelope.status, envelope.context)
        return self._to_command_result(envelope)

    def execute_with_enhanced_response(self, command: str, dry_run: bool = False) -> CommandResult:
        parsed = self.parse(command)
        if parsed is not None and parsed.keyword in self.contracts:
            return self.execute(command, dry_run=dry_run)
        clean = command.strip()
        if not clean:
            return self.execute(command, dry_run=dry_run)

        response = self.generate_reasoned_answer(clean)
        result = self.execute(command, dry_run=dry_run)
        if result.requires_confirmation:
            return CommandResult(response.get("message", result.message), True, result.pending_command)
        final_message = response.get("message", "")
        if result.message and result.message not in final_message:
            final_message = f"{final_message}\n\nAction Result:\n{result.message}"
        return CommandResult(final_message or result.message)

    def _contains_multi_step(self, raw_command: str) -> bool:
        lowered = raw_command.lower()
        return any(marker in lowered for marker in [" lalu ", " kemudian ", ";", " and then "])

    def _execute_multi_step(self, raw_command: str, dry_run: bool = False) -> CommandResult:
        payload = self.reason_plan(raw_command)
        decisions = payload["reasoning"]["decisions"]
        lines = ["[Multi-step Execution]"]

        for decision in decisions:
            command = decision["command"].strip()
            mode = decision["mode"]
            step_id = decision["step_id"]

            if mode == "pruned":
                lines.append(f"{step_id} PRUNED: {decision['reason']}")
                continue

            if mode == "fallback" and command.startswith("explain "):
                explain_target = command[8:].strip()
                message = self.smart_assist.explain(explain_target)
                lines.append(f"{step_id} FALLBACK: {message}")
                continue

            envelope = self.execute_enveloped(command, dry_run=dry_run)
            status = "guarded_pending" if envelope.requires_confirmation else envelope.status
            lines.append(f"{step_id} {status.upper()}: {command} -> {envelope.message}")

        final_message = "\n".join(lines)
        context = self._build_execution_context(raw_command, dry_run=dry_run)
        self._record_session(raw_command, final_message, "success", context)
        return CommandResult(final_message)

    def confirm_pending(self, approved: bool) -> CommandResult:
        if self.pending_autocorrect is not None:
            corrected = self.pending_autocorrect
            self.pending_autocorrect = None
            if not approved:
                cancelled = "Aksi dibatalkan oleh pengguna."
                context = self._build_execution_context("<confirm-autocorrect>", dry_run=True)
                self._record_session("<confirm-autocorrect>", cancelled, "cancelled", context)
                return CommandResult(cancelled)
            return self.execute(corrected, allow_autocorrect=False)

        context = self._build_execution_context("<confirm>", dry_run=False)
        envelope = self.executor.confirm(self, approved, context)
        self._record_session("<confirm>", envelope.message, envelope.status, envelope.context)
        return self._to_command_result(envelope)

    def execute_enveloped(self, command: str, dry_run: bool = False):
        normalized = self._resolve_intent(command)
        context = self._build_execution_context(normalized, dry_run=dry_run)
        envelope = self.executor.run(self, normalized, context)
        self._record_session(normalized or command, envelope.message, envelope.status, envelope.context)
        return envelope

    def parse(self, command: str) -> ParsedCommand | None:
        clean = command.strip()
        if not clean:
            return None
        tokens = clean.split()
        return ParsedCommand(tokens[0].lower(), tokens[1:], clean)

    def _handle_open(self, command: ParsedCommand) -> str:
        return self.launcher.open_app(" ".join(command.args))

    def _handle_search(self, command: ParsedCommand) -> str:
        query = " ".join(command.args[1:]).strip()
        return self.file_manager.search_file(query)

    def _handle_sys(self, command: ParsedCommand) -> str:
        return self.system_tools.system_info()

    def _handle_capability(self, command: ParsedCommand) -> str:
        if len(command.args) < 2:
            return "Format salah. Contoh: capability <domain> <action> [args]"
        domain, action = command.args[0], command.args[1]
        args = [self._expand_path(item) for item in command.args[2:]]
        decision = self.capability_guardrail.evaluate(domain, action, args)
        if not decision.allowed:
            return f"Guardrail blocked: {decision.reason}"
        preview = self.capability_layer.execute(domain, action, args)
        if decision.requires_confirmation:
            return f"Guardrail confirmation required. {decision.reason}\n{preview}"
        return preview

    def _handle_smart(self, command: ParsedCommand) -> str:
        request = " ".join(command.args).strip()
        if not request:
            return "Format salah. Contoh: smart <permintaan_user>"
        plan = self.system_intent_mapper.map_request(request)
        if plan is None:
            return "Belum ada mapping intent untuk request ini."
        lines = [f"Plan: {plan.title}", *[f"- {step}" for step in plan.steps]]
        for raw in plan.commands:
            parsed = self.parse(raw)
            if parsed is None:
                continue
            lines.append(f"> {raw}")
            lines.append(self._handle_capability(parsed))
        if plan.requires_confirmation:
            lines.append("Note: Plan ini perlu approval manual sebelum aksi destruktif.")
        return "\n".join(lines)

    def _handle_profile(self, command: ParsedCommand) -> str:
        target = command.args[0].lower()
        applied = self.execution_profile_policy.set_profile(target)
        return f"Execution profile aktif: {applied}"

    def _handle_proj(self, command: ParsedCommand) -> str:
        if len(command.args) < 2 or command.args[0].lower() != "open":
            return "Format salah. Contoh: proj open <name>"
        name = " ".join(command.args[1:])
        return self.project_manager.open_project(name)

    def _handle_clip(self, command: ParsedCommand) -> str:
        if not command.args:
            return "Format salah. Contoh: clip <add|show|clear> [text]"
        action = command.args[0].lower()
        if action == "add":
            payload = " ".join(command.args[1:]).strip()
            if not payload:
                return "Format salah. Contoh: clip add <text>"
            self.clipboard_manager.push(payload)
            return "Clipboard history diperbarui."
        if action == "show":
            entries = self.clipboard_manager.recent(limit=5)
            if not entries:
                return "Clipboard history kosong."
            return "Clipboard history:\n" + "\n".join(f"- {item}" for item in entries)
        if action == "clear":
            self.clipboard_manager.clear()
            return "Clipboard history dibersihkan."
        return "Aksi clip tidak dikenali. Gunakan: add, show, clear."

    def _handle_mode(self, command: ParsedCommand) -> str:
        if not command.args:
            return self.focus_mode_manager.status()
        first = command.args[0].lower()
        if first == "off":
            return self.focus_mode_manager.disable()
        if len(command.args) >= 2 and command.args[1].lower() == "on":
            return self.focus_mode_manager.enable(first)
        if first in {"focus", "game"} and len(command.args) == 1:
            return self.focus_mode_manager.enable(first)
        return "Format salah. Contoh: mode focus on | mode game on | mode off"

    def _handle_net(self, command: ParsedCommand) -> str:
        if not command.args:
            return "Format salah. Contoh: net <ping|dns|ip> [host]"
        action = command.args[0].lower()
        if action == "ping":
            host = " ".join(command.args[1:])
            return self.network_diagnostics.ping_profile(host)
        if action == "dns":
            host = " ".join(command.args[1:])
            return self.network_diagnostics.dns_lookup(host)
        if action == "ip":
            return self.network_diagnostics.public_ip()
        return "Aksi net tidak dikenali. Gunakan: ping, dns, ip."

    def _execute_dangerous(self, command: ParsedCommand) -> CommandResult:
        if self.safe_mode_policy.is_blocked(command.keyword):
            return CommandResult("Aksi ditolak oleh safe mode policy.")
        if command.keyword == "shutdown":
            return CommandResult(self.system_actions.shutdown_now())
        if command.keyword == "kill":
            target = " ".join(command.args)
            if not self.security_guard.is_process_target_allowed(target):
                return CommandResult("Kill process ditolak oleh process permission guard.")
            return CommandResult(self.system_actions.terminate_process(target))
        if command.keyword == "delete":
            target = " ".join(command.args)
            if not self.security_guard.is_path_allowed(target):
                return CommandResult("Delete ditolak oleh path restriction policy.")
            return CommandResult(self.system_actions.delete_path(target))
        return CommandResult("Aksi berbahaya tidak dikenali.")

    def _record_session(self, command: str, message: str, status: str, context: ExecutionContext | None = None) -> None:
        self.session_layer.record(command=command, message=message, status=status)
        self.memory_engine.record_command(command=command, status=status)
        level = "error" if status in {"invalid", "blocked", "failed"} else "info"
        metadata = {"command": command, "status": status}
        if context is not None:
            metadata["execution_context"] = asdict(context)
        self.logger.log(level=level, event="command", message=message, metadata=metadata)

    def _to_command_result(self, envelope) -> CommandResult:
        return CommandResult(envelope.message, envelope.requires_confirmation, envelope.pending_command)

    def _build_execution_context(self, command: str, dry_run: bool) -> ExecutionContext:
        parsed = self.parse(command)
        keyword = parsed.keyword if parsed is not None else ""
        risk_level = self.execution_profile_policy.risk_level(keyword)
        profile_policy = self.execution_profile_policy.profile
        return ExecutionContext(
            user=getpass.getuser(),
            profile_policy=profile_policy,
            session_id=self.session_id,
            timestamp=build_execution_timestamp(),
            risk_level=risk_level,
            dry_run=dry_run,
        )

    def _apply_profile_policy(self, normalized: str) -> CommandResult | None:
        parsed = self.parse(normalized)
        if parsed is None:
            return None

        decision = self.execution_profile_policy.evaluate(parsed.keyword)
        if decision.mode == "blocked":
            message = f"Execution profile blocked: {decision.reason}"
            self._record_session(normalized, message, "blocked", self._build_execution_context(normalized, dry_run=True))
            return CommandResult(message)

        if decision.mode == "explain":
            message = f"Execution profile explain-only: {parsed.raw}"
            self._record_session(normalized, message, "success", self._build_execution_context(normalized, dry_run=True))
            return CommandResult(message)

        if decision.requires_confirmation and not self.safe_mode and parsed.keyword in self.dangerous_keywords:
            self.pending_confirmation = parsed
            message = "Execution profile membutuhkan konfirmasi manual."
            self._record_session(normalized, message, "pending_confirmation", self._build_execution_context(normalized, dry_run=True))
            return CommandResult(message, requires_confirmation=True, pending_command=parsed.raw)

        return None

    def _resolve_autocorrect(self, normalized: str, allow_autocorrect: bool):
        if not allow_autocorrect:
            return None
        correction = self.smart_assist.autocorrect(normalized, list(self.contracts.keys()))
        if correction is None:
            return None
        if not correction.requires_confirmation:
            message = f"Smart Assist auto-applied -> {correction.corrected} (confidence={correction.confidence:.2f})"
            self._record_session(normalized, message, "intent_resolved")
        return correction

    def _expand_path(self, value: str) -> str:
        if value.startswith("~/"):
            return str(Path.home() / value[2:])
        return os.path.expandvars(value)

    def _normalize_shortcuts(self, normalized: str) -> str:
        parsed = self.parse(normalized)
        if parsed is None:
            return normalized
        if parsed.keyword == "search" and parsed.args and parsed.args[0].lower() != "file":
            query = " ".join(parsed.args).strip()
            return f"search file {query}"
        return normalized

    def memory_summary(self) -> dict:
        return {
            "top_commands": self.memory_engine.top_commands(limit=5),
            "persona": self.memory_engine.get_preference("persona", None),
        }

    def list_command_keywords(self) -> list[str]:
        return sorted(self.contracts.keys())

    def suggest_commands(self, raw_input: str, limit: int = 5) -> list[str]:
        typed = raw_input.strip().lower()
        usages = sorted(contract.usage for contract in self.contracts.values())
        if not typed:
            return usages[:limit]
        matched = [usage for usage in usages if usage.startswith(typed) or usage.split(" ")[0].startswith(typed)]
        return list(dict.fromkeys(matched))[:limit]

    def usage_hint(self, raw_input: str) -> str | None:
        command = raw_input.strip().split(" ")[0].lower() if raw_input.strip() else ""
        contract = self.contracts.get(command)
        return contract.usage if contract is not None else None

    def argument_hint(self, raw_input: str) -> str:
        return " | ".join(self.smart_assist.argument_hints(raw_input))

    def explain_intent(self, raw_input: str) -> str:
        text = raw_input.strip()
        if not text:
            return ""
        resolution = self.intent_engine.resolve(text, allowed_keywords=set(self.contracts.keys()))
        if resolution.resolved == text:
            return ""
        return f"Did you mean: {resolution.resolved}"

    def save_recovery_snapshot(self):
        entries = [item.__dict__ for item in self.session_layer.entries]
        return self.recovery_manager.save_snapshot("router-session", entries)

    def create_diagnostic_report(self):
        checks = self.health_monitor.run(self)
        recent_logs = self.logger.tail(limit=30)
        return self.diagnostic_reporter.generate(checks, recent_logs)

    def build_performance_baseline(self) -> dict:
        startup = self.performance_profiler.measure_startup(lambda: CommandRouter())
        command_latency = self.performance_profiler.measure_command_latency(self.route, "sys info", iterations=3)
        storage_io = self.performance_profiler.measure_storage_io(iterations=10)
        self.release_hardening_plan.mark_completed("profiling")
        return {
            "startup_ms": startup.average_ms,
            "command_latency_ms": command_latency.average_ms,
            "storage_io_ms": storage_io.average_ms,
        }

    def release_hardening_summary(self) -> dict:
        return self.release_hardening_plan.summary()

    def get_release_channel(self) -> str:
        return self.release_channel_manager.get_channel()

    def set_release_channel(self, channel: str) -> str:
        return self.release_channel_manager.set_channel(channel)

    def embedding_config(self) -> dict:
        config = self.embedding_provider.config()
        return {
            "host": config.host,
            "model": config.model,
            "timeout_seconds": config.timeout_seconds,
        }

    def embedding_health(self) -> dict:
        cached = self._health_cache.get("embedding")
        now = time.monotonic()
        if cached is not None and now - cached[0] <= self._health_cache_ttl_seconds:
            return dict(cached[1])
        health = self.embedding_provider.health()
        payload = {"ok": health.ok, "message": health.message}
        self._health_cache["embedding"] = (now, payload)
        return payload

    def embed_text(self, text: str) -> list[float]:
        return self.embedding_provider.embed(text)

    def generation_config(self) -> dict:
        config = self.generation_provider.config()
        return {
            "host": config.host,
            "model": config.model,
            "timeout_seconds": config.timeout_seconds,
            "token_budget": config.token_budget,
            "temperature": config.temperature,
        }

    def generation_health(self) -> dict:
        cached = self._health_cache.get("generation")
        now = time.monotonic()
        if cached is not None and now - cached[0] <= self._health_cache_ttl_seconds:
            return dict(cached[1])
        health = self.generation_provider.health()
        payload = {"ok": health.ok, "message": health.message}
        self._health_cache["generation"] = (now, payload)
        return payload

    def available_generation_models(self, force_reload: bool = False) -> list[dict]:
        if self._model_catalog_cache and not force_reload:
            return list(self._model_catalog_cache)
        try:
            models = self.generation_provider.list_models()
        except (OSError, ValueError):
            return list(self._model_catalog_cache)
        self._model_catalog_cache = [
            {
                "name": item.name,
                "parameter_size": item.parameter_size,
                "role": item.role,
                "gpu_badge": item.gpu_badge,
            }
            for item in models
        ]
        return list(self._model_catalog_cache)

    def set_generation_runtime(
        self,
        model: str,
        timeout_seconds: float,
        token_budget: int,
        temperature: float,
    ) -> dict:
        current = self.generation_provider.config()
        config = GenerationConfig(
            host=current.host,
            model=model.strip() or current.model,
            timeout_seconds=max(1.0, float(timeout_seconds)),
            token_budget=max(32, int(token_budget)),
            temperature=max(0.0, min(1.0, float(temperature))),
        )
        self.generation_provider = OllamaGenerationProvider(config=config)
        return self.generation_config()

    def set_response_quality(self, quality: str) -> str:
        allowed = {"concise", "balanced", "deep"}
        selected = quality.strip().lower()
        if selected not in allowed:
            selected = "balanced"
        self.response_quality = selected
        return self.response_quality

    def set_chat_model_enabled(self, enabled: bool) -> bool:
        self.chat_model_enabled = bool(enabled)
        return self.chat_model_enabled

    def generate_reasoned_answer(self, raw_input: str) -> dict:
        optimized_query = self.retrieval_optimizer.optimize_query(raw_input)
        cache_key = f"reasoned:{self.response_quality}:{optimized_query}"
        cached = self.retrieval_optimizer.get_cache(cache_key)
        if isinstance(cached, dict):
            return {**cached, "mode": "cache"}

        plan = self.reason_plan(optimized_query)
        if not self.chat_model_enabled:
            payload = {
                "mode": "disabled",
                "message": self._reasoning_fallback_message(plan),
                "health": {"ok": False, "message": "chat model disabled"},
            }
            self.retrieval_optimizer.set_cache(cache_key, payload)
            return payload
        health = self.generation_provider.health()
        if not health.ok:
            fallback = self._reasoning_fallback_message(plan)
            payload = {"mode": "fallback", "message": fallback, "health": {"ok": health.ok, "message": health.message}}
            self.retrieval_optimizer.set_cache(cache_key, payload)
            return payload

        prompt = self._build_reasoning_prompt(optimized_query, plan)
        text = self.generation_provider.generate(prompt=prompt, system_prompt="You are OrionDesk local assistant.")
        if text:
            payload = {"mode": "gemma", "message": text, "health": {"ok": health.ok, "message": health.message}}
            self.retrieval_optimizer.set_cache(cache_key, payload)
            return payload
        fallback = self._reasoning_fallback_message(plan)
        payload = {"mode": "fallback", "message": fallback, "health": {"ok": health.ok, "message": "empty generation"}}
        self.retrieval_optimizer.set_cache(cache_key, payload)
        return payload

    def intent_graph(self, raw_input: str) -> dict:
        allowed = set(self.contracts.keys())
        graph = self.intent_graph_planner.build(
            raw_input=raw_input,
            resolve_intent=lambda text: self.intent_engine.resolve(text, allowed_keywords=allowed),
        )
        return graph.to_dict()

    def reason_plan(self, raw_input: str) -> dict:
        optimized_query = self.retrieval_optimizer.optimize_query(raw_input)
        cache_key = f"reason-plan:{optimized_query}"
        cached = self.retrieval_optimizer.get_cache(cache_key)
        if isinstance(cached, dict):
            return cached

        graph_payload = self.intent_graph(optimized_query)
        plan = self.reasoning_engine.build_plan(
            graph_payload=graph_payload,
            embed_text=self.embed_text,
            risk_level=self.execution_profile_policy.risk_level,
        )
        payload = {
            "graph": graph_payload,
            "reasoning": plan.to_dict(),
        }
        self.retrieval_optimizer.set_cache(cache_key, payload)
        return payload

    def execute_with_latency_budget(self, command: str, dry_run: bool = False) -> dict:
        latency = LatencyBudget()
        normalized = latency.timed("intent", lambda: self._normalize_shortcuts(self._resolve_intent(command)))
        policy_block = latency.timed("policy", lambda: self._apply_profile_policy(normalized))
        if policy_block is not None:
            result = policy_block
        else:
            result = latency.timed("execution", lambda: self.execute(normalized, dry_run=dry_run, allow_autocorrect=False))
        summary = latency.summary()
        responsiveness = self._main_thread_guard.evaluate(summary["stages"])
        return {
            "result": {"message": result.message, "requires_confirmation": result.requires_confirmation},
            "latency": summary,
            "responsiveness": responsiveness,
        }

    def execute_reasoning_async(self, raw_input: str) -> Future:
        return self._runtime_pool.submit(self.generate_reasoned_answer, raw_input)

    def multi_command_bundle(self, raw_input: str) -> dict:
        graph_payload = self.intent_graph(raw_input)
        commands = [step["resolved_command"] for step in graph_payload.get("steps", [])]
        commands = self.retrieval_optimizer.reduce_redundant_patterns(commands)
        return {
            "commands": self.multi_command_executor.bundle(commands, self.execution_profile_policy.risk_level),
            "arguments": self.argument_extractor.extract_many(commands),
        }

    def execute_multi(self, raw_input: str, dry_run: bool = True) -> dict:
        payload = self.multi_command_bundle(raw_input)
        bundles = payload["commands"]

        def _run(command: str) -> tuple[str, str]:
            envelope = self.execute_enveloped(command, dry_run=dry_run)
            status = "guarded_pending" if envelope.requires_confirmation else envelope.status
            return status, envelope.message

        reports = self.multi_command_executor.execute(bundles, _run)
        return {
            "dry_run": dry_run,
            "commands": bundles,
            "arguments": payload["arguments"],
            "reports": reports,
        }

    def _build_reasoning_prompt(self, raw_input: str, plan: dict) -> str:
        decisions = plan["reasoning"].get("decisions", [])
        intent = self.intent_engine.resolve(raw_input, allowed_keywords=set(self.contracts.keys()))
        context_rows = self.retrieval_optimizer.rank_session_context(self.session_layer.recent(limit=12), raw_input, limit=4)
        context_lines = [f"- {item.command} -> {item.status}" for item in context_rows]
        quality_instruction = {
            "concise": "Keep answer very short and direct.",
            "balanced": "Keep answer clear and actionable with moderate detail.",
            "deep": "Provide detailed reasoning and practical steps.",
        }.get(self.response_quality, "Keep answer clear and actionable with moderate detail.")
        lines = [
            f"User input: {raw_input}",
            f"Intent resolved: {intent.resolved} ({intent.reason}, confidence={intent.confidence:.2f})",
            f"Response quality: {self.response_quality}",
            "Reasoning decisions:",
        ]
        for item in decisions:
            lines.append(
                f"- {item['step_id']} mode={item['mode']} confidence={item['confidence']}: {item['command']}"
            )
        if context_lines:
            lines.append("Relevant session context:")
            lines.extend(context_lines)
        lines.append(quality_instruction)
        lines.append("Compose one final answer in Indonesian.")
        return "\n".join(lines)

    def _reasoning_fallback_message(self, plan: dict) -> str:
        decisions = plan["reasoning"].get("decisions", [])
        if not decisions:
            return "Tidak ada step yang dapat diproses."
        lines = ["Ringkasan reasoning (fallback):"]
        for item in decisions:
            lines.append(f"{item['step_id']} {item['mode'].upper()}: {item['command']}")
        return "\n".join(lines)

    def _register_plugins(self) -> None:
        registry = PluginRegistry(package_name="plugins")
        for item in registry.discover():
            self.contracts[item.keyword] = CommandContract(
                keyword=item.keyword,
                usage=item.usage,
                min_args=item.min_args,
                max_args=item.max_args,
                first_arg_equals=item.first_arg_equals,
            )
            if item.dangerous:
                self.dangerous_keywords.add(item.keyword)
                continue
            self.handlers[item.keyword] = getattr(self, item.handler_name)

    def _resolve_intent(self, raw_command: str) -> str:
        allowed = set(self.contracts.keys())
        resolution = self.intent_engine.resolve(raw_command, allowed_keywords=allowed)
        if resolution.reason.startswith("semantic"):
            message = f"Intent resolved -> {resolution.resolved} (confidence={resolution.confidence:.2f})"
            self._record_session(raw_command, message, "intent_resolved")
        return resolution.resolved
