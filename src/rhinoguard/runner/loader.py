from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from rhinoguard.errors import ScenarioValidationError
from rhinoguard.models import Scenario, Severity

REQUIRED_FIELDS = {
    "id",
    "name",
    "description",
    "category",
    "severity",
    "objective",
    "system_prompt",
    "user_prompt",
    "attack_prompt",
    "tools",
    "framework",
    "sandbox",
    "model_script",
    "expected_findings",
}


def discover_scenarios(directory: str | Path) -> list[Path]:
    root = Path(directory)
    if not root.exists():
        raise ScenarioValidationError(f"Scenario directory does not exist: {root}")
    return sorted([*root.rglob("*.yaml"), *root.rglob("*.yml")])


def load_scenario(path: str | Path) -> Scenario:
    scenario_path = Path(path)
    try:
        document = yaml.safe_load(scenario_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ScenarioValidationError(f"Cannot read {scenario_path}: {exc}") from exc
    if not isinstance(document, dict):
        raise ScenarioValidationError(f"Scenario must be a mapping: {scenario_path}")
    missing = sorted(REQUIRED_FIELDS - document.keys())
    if missing:
        raise ScenarioValidationError(f"{scenario_path} is missing: {', '.join(missing)}")
    try:
        severity = Severity(str(document["severity"]).lower())
    except ValueError as exc:
        raise ScenarioValidationError(f"Invalid severity in {scenario_path}") from exc
    for field_name in ("tools", "expected_findings"):
        if not isinstance(document[field_name], list):
            raise ScenarioValidationError(f"{field_name} must be a list in {scenario_path}")
    sandbox = _expand_fixtures(dict(document["sandbox"]), scenario_path)
    framework = dict(document["framework"])
    return Scenario(
        id=str(document["id"]),
        name=str(document["name"]),
        description=str(document["description"]),
        category=str(document["category"]),
        severity=severity,
        objective=str(document["objective"]),
        system_prompt=str(document["system_prompt"]),
        user_prompt=str(document["user_prompt"]),
        attack_prompt=str(document["attack_prompt"]),
        tools=[str(item) for item in document["tools"]],
        framework={str(key): [str(item) for item in value] for key, value in framework.items()},
        sandbox=sandbox,
        model_script=dict(document["model_script"]),
        expected_findings=[str(item) for item in document["expected_findings"]],
        source_path=str(scenario_path),
    )


def _expand_fixtures(config: dict[str, Any], scenario_path: Path) -> dict[str, Any]:
    files = dict(config.get("files", {}) or {})
    expanded: dict[str, str] = {}
    for target, value in files.items():
        if isinstance(value, dict) and "fixture" in value:
            fixture_path = _project_root(scenario_path) / str(value["fixture"])
            try:
                expanded[str(target)] = fixture_path.read_text(encoding="utf-8")
            except OSError as exc:
                raise ScenarioValidationError(f"Cannot read fixture {fixture_path}: {exc}") from exc
        else:
            expanded[str(target)] = str(value)
    config["files"] = expanded
    return config


def _project_root(path: Path) -> Path:
    for parent in [path.parent, *path.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return Path.cwd()
# Review follow-up details for loader module
