from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Settings:
    provider: str = "scripted"
    policy_mode: str = "monitor"
    policy_file: Path = Path("policies/default.yaml")
    scenario_dir: Path = Path("scenarios")
    report_dir: Path = Path("reports")
    ollama_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "llama3.2:3b"
    openai_base_url: str = "http://127.0.0.1:8001/v1"
    openai_model: str = "local-model"
    openai_api_key: str = ""
    request_timeout: float = 60.0

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            provider=os.getenv("RHINOGUARD_PROVIDER", "scripted"),
            policy_mode=os.getenv("RHINOGUARD_POLICY_MODE", "monitor"),
            policy_file=Path(os.getenv("RHINOGUARD_POLICY_FILE", "policies/default.yaml")),
            scenario_dir=Path(os.getenv("RHINOGUARD_SCENARIO_DIR", "scenarios")),
            report_dir=Path(os.getenv("RHINOGUARD_REPORT_DIR", "reports")),
            ollama_url=os.getenv("RHINOGUARD_OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/"),
            ollama_model=os.getenv("RHINOGUARD_OLLAMA_MODEL", "llama3.2:3b"),
            openai_base_url=os.getenv(
                "RHINOGUARD_OPENAI_BASE_URL", "http://127.0.0.1:8001/v1"
            ).rstrip("/"),
            openai_model=os.getenv("RHINOGUARD_OPENAI_MODEL", "local-model"),
            openai_api_key=os.getenv("RHINOGUARD_OPENAI_API_KEY", ""),
            request_timeout=float(os.getenv("RHINOGUARD_REQUEST_TIMEOUT", "60")),
        )
