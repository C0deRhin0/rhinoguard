from __future__ import annotations

from rhinoguard.models import TraceEvent


class TraceRecorder:
    def __init__(self) -> None:
        self.events: list[TraceEvent] = []

    def record(self, kind: str, message: str, **data: object) -> None:
        self.events.append(TraceEvent(kind=kind, message=message, data=dict(data)))
