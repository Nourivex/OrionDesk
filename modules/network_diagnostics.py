from __future__ import annotations

import socket
import subprocess
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class NetworkDiagnostics:
    dns_resolver: Callable[[str], tuple[str, list[str], list[str]]] = field(default=socket.gethostbyname_ex)
    ping_runner: Callable[[list[str]], subprocess.CompletedProcess] = field(
        default=lambda cmd: subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    )

    def public_ip(self) -> str:
        return "Public IP check tersedia via command `net dns` / `net ping` pada mode lokal-first."

    def ping_profile(self, host: str, count: int = 2) -> str:
        target = host.strip()
        if not target:
            return "Format salah. Contoh: net ping <host>"

        command = ["ping", "-n", str(count), target]
        result = self.ping_runner(command)
        status = "ok" if result.returncode == 0 else "failed"
        first_line = result.stdout.splitlines()[0] if result.stdout else ""
        return f"Ping {target}: {status}. {first_line}".strip()

    def dns_lookup(self, host: str) -> str:
        target = host.strip()
        if not target:
            return "Format salah. Contoh: net dns <host>"

        try:
            _, _, addresses = self.dns_resolver(target)
        except OSError as error:
            return f"DNS lookup gagal: {error}"

        if not addresses:
            return f"DNS lookup {target}: tidak ada alamat."
        rendered = ", ".join(addresses)
        return f"DNS lookup {target}: {rendered}"
