from __future__ import annotations

import json
import urllib.error
import urllib.request

from rhinoguard.adapters.base import ModelAdapter, ModelRequest
from rhinoguard.adapters.json_contract import parse_decision, response_contract_prompt
from rhinoguard.errors import AdapterError
from rhinoguard.models import AgentDecision


class OllamaAdapter(ModelAdapter):
    name = "ollama"

    def __init__(self, base_url: str, model: str, timeout: float = 60.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def decide(self, request: ModelRequest) -> AgentDecision:
        messages = [
            *request.messages,
            {"role": "system", "content": response_contract_prompt(request.tool_names)},
        ]
        body = json.dumps(
            {"model": self.model, "messages": messages, "stream": False, "format": "json"}
        ).encode()
        http_request = urllib.request.Request(
            f"{self.base_url}/api/chat",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(http_request, timeout=self.timeout) as response:
                payload = json.loads(response.read())
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise AdapterError(f"Ollama request failed: {exc}") from exc
        try:
            return parse_decision(payload["message"]["content"])
        except (KeyError, TypeError) as exc:
            raise AdapterError("Ollama response did not contain message.content") from exc
# Align local documentation for ollama module
