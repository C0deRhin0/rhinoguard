from __future__ import annotations

from rhinoguard.adapters.base import ModelAdapter
from rhinoguard.adapters.ollama import OllamaAdapter
from rhinoguard.adapters.openai_compatible import OpenAICompatibleAdapter
from rhinoguard.adapters.scripted import ScriptedAdapter
from rhinoguard.config import Settings


def create_adapter(name: str, settings: Settings) -> ModelAdapter:
    normalized = name.lower()
    if normalized == "scripted":
        return ScriptedAdapter()
    if normalized == "ollama":
        return OllamaAdapter(settings.ollama_url, settings.ollama_model, settings.request_timeout)
    if normalized in {"openai", "openai-compatible"}:
        return OpenAICompatibleAdapter(
            settings.openai_base_url,
            settings.openai_model,
            settings.openai_api_key,
            settings.request_timeout,
        )
    raise ValueError(f"Unknown provider: {name}")
