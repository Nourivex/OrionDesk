import psutil


class SystemTools:
    def system_info(self) -> str:
        cpu_usage = psutil.cpu_percent(interval=0.0)
        memory = psutil.virtual_memory()
        process_lines = self._running_processes(limit=10)

        lines = [
            "Informasi Sistem:",
            f"- CPU Usage: {cpu_usage:.1f}%",
            f"- RAM Usage: {memory.percent:.1f}% ({self._bytes_to_gb(memory.used):.2f} GB / {self._bytes_to_gb(memory.total):.2f} GB)",
            "- Running Processes:",
        ]
        lines.extend(process_lines)
        return "\n".join(lines)

    def _running_processes(self, limit: int) -> list[str]:
        process_names: list[str] = []

        for process in psutil.process_iter(["name"]):
            name = process.info.get("name")
            if name:
                process_names.append(name)

        process_names.sort()
        selected = process_names[:limit]
        if not selected:
            return ["  - Tidak ada data proses."]
        return [f"  - {name}" for name in selected]

    def _bytes_to_gb(self, value: int) -> float:
        return value / (1024 ** 3)