from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IntentPlan:
    title: str
    steps: list[str]
    commands: list[str]
    requires_confirmation: bool = False


class SystemIntentMapper:
    def map_request(self, raw: str) -> IntentPlan | None:
        clean = raw.strip().lower()
        if not clean:
            return None

        if "koneksi" in clean or "network" in clean or "internet" in clean:
            return IntentPlan(
                title="Network Health Check",
                steps=["Ping host target", "Check interface status", "Summarize findings"],
                commands=[
                    "capability network ping google.com",
                    "capability network interface_summary",
                ],
            )

        if "download" in clean and ("bersih" in clean or "cleanup" in clean or "rapihin" in clean):
            return IntentPlan(
                title="Download Cleanup Preview",
                steps=[
                    "List files di folder download",
                    "Detect file besar dan duplikat",
                    "Prepare archive plan dengan konfirmasi",
                ],
                commands=["capability file preview_cleanup ~/Downloads"],
                requires_confirmation=True,
            )

        if "proses" in clean or "process" in clean:
            return IntentPlan(
                title="Process Overview",
                steps=["List process aktif", "Tampilkan process penting"],
                commands=["capability process list"],
            )

        return None
