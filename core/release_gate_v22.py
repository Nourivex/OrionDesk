from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GateScenario:
    name: str
    command: str


class ReleaseGateV22:
    def run_reliability_matrix(self, execute_command, scenarios: list[GateScenario]) -> dict:
        reports = []
        passed = 0
        for item in scenarios:
            result = execute_command(item.command)
            ok = result.get("ok", False)
            reports.append({"scenario": item.name, "ok": ok, "message": result.get("message", "")})
            if ok:
                passed += 1
        total = len(reports)
        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": round((passed / total) * 100, 2) if total else 0.0,
            "reports": reports,
        }

    def compare_baseline(self, v21: dict, v22: dict) -> dict:
        keys = ["startup_ms", "command_latency_ms", "storage_io_ms"]
        comparison = {}
        for key in keys:
            old_value = float(v21.get(key, 0.0))
            new_value = float(v22.get(key, 0.0))
            delta = round(new_value - old_value, 2)
            improvement = 0.0 if old_value == 0 else round(((old_value - new_value) / old_value) * 100, 2)
            comparison[key] = {
                "v21": old_value,
                "v22": new_value,
                "delta_ms": delta,
                "improvement_percent": improvement,
            }
        return comparison

    def release_checklist(self, reliability: dict, comparison: dict) -> dict:
        checks = {
            "reliability_gate": reliability.get("pass_rate", 0.0) >= 80.0,
            "startup_gate": comparison["startup_ms"]["improvement_percent"] >= -15.0,
            "command_latency_gate": comparison["command_latency_ms"]["improvement_percent"] >= -15.0,
            "storage_gate": comparison["storage_io_ms"]["improvement_percent"] >= -15.0,
        }
        passed = sum(1 for item in checks.values() if item)
        total = len(checks)
        return {
            "checks": checks,
            "passed": passed,
            "total": total,
            "ready": passed == total,
            "rollback_notes": [
                "Fallback ke runtime v2.1 jika reliability gate gagal.",
                "Reset chat model ke default gemma3:4b dan disable advanced tuning.",
                "Disable async enhanced response path jika UI freeze terdeteksi.",
            ],
        }
