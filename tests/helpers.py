from pathlib import Path

from rhinoguard.adapters.scripted import ScriptedAdapter
from rhinoguard.runner.engine import Runner

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCENARIO_DIR = PROJECT_ROOT / "scenarios"
POLICY_FILE = PROJECT_ROOT / "policies" / "default.yaml"


def scripted_runner() -> Runner:
    return Runner(ScriptedAdapter(), POLICY_FILE)
