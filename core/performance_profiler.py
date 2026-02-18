from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Callable


@dataclass(frozen=True)
class BenchmarkResult:
    metric: str
    average_ms: float
    iterations: int


@dataclass
class PerformanceProfiler:
    def measure_startup(self, builder: Callable[[], object], iterations: int = 3) -> BenchmarkResult:
        runs = max(1, iterations)
        samples: list[float] = []
        for _ in range(runs):
            started = perf_counter()
            _ = builder()
            elapsed = (perf_counter() - started) * 1000.0
            samples.append(elapsed)
        return BenchmarkResult(metric="startup_ms", average_ms=self._avg(samples), iterations=runs)

    def measure_command_latency(
        self,
        executor: Callable[[str], object],
        command: str,
        iterations: int = 5,
    ) -> BenchmarkResult:
        runs = max(1, iterations)
        samples: list[float] = []
        for _ in range(runs):
            started = perf_counter()
            executor(command)
            elapsed = (perf_counter() - started) * 1000.0
            samples.append(elapsed)
        return BenchmarkResult(metric="command_latency_ms", average_ms=self._avg(samples), iterations=runs)

    def measure_storage_io(self, iterations: int = 20) -> BenchmarkResult:
        runs = max(1, iterations)
        samples: list[float] = []
        payload = "oriondesk-phase31"
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "io.txt"
            for _ in range(runs):
                started = perf_counter()
                target.write_text(payload, encoding="utf-8")
                _ = target.read_text(encoding="utf-8")
                elapsed = (perf_counter() - started) * 1000.0
                samples.append(elapsed)
        return BenchmarkResult(metric="storage_io_ms", average_ms=self._avg(samples), iterations=runs)

    def _avg(self, values: list[float]) -> float:
        if not values:
            return 0.0
        return round(sum(values) / len(values), 3)
