from __future__ import annotations

from pathlib import Path

from rhinoguard.models import RunResult
from rhinoguard.reports.html_report import render_html
from rhinoguard.reports.json_report import render_json
from rhinoguard.reports.markdown_report import render_markdown


def write_reports(result: RunResult, directory: str | Path) -> dict[str, Path]:
    output = Path(directory)
    output.mkdir(parents=True, exist_ok=True)
    stem = f"{result.scenario.id}-{result.mode.value}-{result.run_id[:8]}"
    paths = {
        "json": output / f"{stem}.json",
        "markdown": output / f"{stem}.md",
        "html": output / f"{stem}.html",
    }
    paths["json"].write_text(render_json(result) + "\n", encoding="utf-8")
    paths["markdown"].write_text(render_markdown(result), encoding="utf-8")
    paths["html"].write_text(render_html(result), encoding="utf-8")
    return paths
