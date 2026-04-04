from __future__ import annotations

from dataclasses import dataclass

from rhinoguard.sandbox.email import SyntheticMailbox
from rhinoguard.sandbox.filesystem import VirtualFilesystem
from rhinoguard.sandbox.http import SyntheticHTTP
from rhinoguard.sandbox.memory import SyntheticMemory
from rhinoguard.sandbox.shell import SyntheticShell


@dataclass(slots=True)
class Sandbox:
    filesystem: VirtualFilesystem
    mailbox: SyntheticMailbox
    http: SyntheticHTTP
    memory: SyntheticMemory
    shell: SyntheticShell
    secrets: dict[str, str]

    @classmethod
    def from_config(cls, config: dict[str, object]) -> Sandbox:
        files = dict(config.get("files", {}) or {})
        secrets = {
            str(key): str(value) for key, value in dict(config.get("secrets", {}) or {}).items()
        }
        filesystem = VirtualFilesystem(files)
        return cls(
            filesystem=filesystem,
            mailbox=SyntheticMailbox(),
            http=SyntheticHTTP(dict(config.get("http_endpoints", {}) or {})),
            memory=SyntheticMemory(dict(config.get("memory", {}) or {})),
            shell=SyntheticShell(filesystem),
            secrets=secrets,
        )
