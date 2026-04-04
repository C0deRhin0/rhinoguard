from __future__ import annotations

import json

from rhinoguard.models import RunResult
from rhinoguard.reports.redaction import redacted_payload


def render_json(result: RunResult) -> str:
    return json.dumps(redacted_payload(result), indent=2, sort_keys=True)
