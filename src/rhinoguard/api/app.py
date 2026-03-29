from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from rhinoguard import __version__
from rhinoguard.config import Settings
from rhinoguard.factory import create_adapter
from rhinoguard.models import PolicyMode
from rhinoguard.reports.redaction import redacted_payload
from rhinoguard.runner.engine import Runner
from rhinoguard.runner.loader import discover_scenarios, load_scenario


class RunRequest(BaseModel):
    scenario_id: str = Field(min_length=1, max_length=120)
    mode: str = Field(default="defended", pattern="^(vulnerable|defended|monitor|enforce|off)$")
    provider: str = Field(default="scripted", pattern="^(scripted|ollama|openai-compatible)$")


def create_app(settings: Settings | None = None) -> FastAPI:
    active = settings or Settings.from_env()
    app = FastAPI(
        title="RhinoGuard API",
        version=__version__,
        description="Local-first security evaluations for tool-using AI agents.",
    )

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    @app.get("/v1/scenarios")
    def scenarios() -> list[dict[str, str]]:
        return [
            {
                "id": scenario.id,
                "name": scenario.name,
                "category": scenario.category,
                "severity": scenario.severity.value,
            }
            for scenario in (
                load_scenario(path) for path in discover_scenarios(active.scenario_dir)
            )
        ]

    @app.post("/v1/runs")
    def run_scenario(request: RunRequest) -> dict[str, object]:
        matches = [
            scenario
            for scenario in (
                load_scenario(path) for path in discover_scenarios(active.scenario_dir)
            )
            if scenario.id == request.scenario_id
        ]
        if not matches:
            raise HTTPException(status_code=404, detail="Scenario not found")
        aliases = {
            "vulnerable": PolicyMode.MONITOR,
            "defended": PolicyMode.ENFORCE,
        }
        mode = aliases[request.mode] if request.mode in aliases else PolicyMode(request.mode)
        runner = Runner(create_adapter(request.provider, active), active.policy_file)
        return redacted_payload(runner.run(matches[0], mode))

    return app


app = create_app()
# Align local documentation for app module
