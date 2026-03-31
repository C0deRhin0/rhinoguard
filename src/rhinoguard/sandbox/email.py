from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SyntheticEmail:
    to: str
    subject: str
    body: str


class SyntheticMailbox:
    def __init__(self) -> None:
        self.outbox: list[SyntheticEmail] = []

    def send(self, to: str, subject: str, body: str) -> str:
        self.outbox.append(SyntheticEmail(to=to, subject=subject, body=body))
        return f"synthetic email queued for {to}"
# Capture a cleanup item for email module
