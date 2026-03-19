from __future__ import annotations

import json
import urllib.error
import urllib.request

from rhinoguard.adapters.base import ModelAdapter, ModelRequest
from rhinoguard.adapters.json_contract import parse_decision, response_contract_prompt
from rhinoguard.errors import AdapterError
from rhinoguard.models import AgentDecision


class OpenAICompatibleAdapter(ModelAdapter):
    name = "openai-compatible"

    def __init__(self, base_url: str, model: str, api_key: str = "", timeout: float = 60.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.timeout = timeout

    def decide(self, request: ModelRequest) -> AgentDecision:
        messages = [
            *request.messages,
            {"role": "system", "content": response_contract_prompt(request.tool_names)},
        ]
        body = json.dumps({"model": self.model, "messages": messages, "temperature": 0}).encode()
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        http_request = urllib.request.Request(
            f"{self.base_url}/chat/completions", data=body, headers=headers, method="POST"
        )
        try:
            with urllib.request.urlopen(http_request, timeout=self.timeout) as response:
                payload = json.loads(response.read())
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise AdapterError(f"OpenAI-compatible request failed: {exc}") from exc
        try:
            return parse_decision(payload["choices"][0]["message"]["content"])
        except (KeyError, IndexError, TypeError) as exc:
            raise AdapterError("Response did not contain choices[0].message.content") from exc
