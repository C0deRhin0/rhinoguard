from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rhinoguard.config import Settings
from rhinoguard.errors import RhinoGuardError
from rhinoguard.factory import create_adapter
from rhinoguard.models import PolicyMode, RunResult
from rhinoguard.reports.writer import write_reports
from rhinoguard.runner.engine import Runner
from rhinoguard.runner.loader import discover_scenarios, load_scenario


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rhinoguard", description="Purple-team security testing for tool-using AI agents"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    list_parser = subparsers.add_parser("list", help="List available scenarios")
    list_parser.add_argument("--scenario-dir", type=Path)

    run_parser = subparsers.add_parser("run", help="Run one scenario")
    run_parser.add_argument("scenario", type=Path)
    run_parser.add_argument(
        "--mode",
        choices=["vulnerable", "defended", "off", "monitor", "enforce"],
        default="vulnerable",
    )
    run_parser.add_argument("--provider", choices=["scripted", "ollama", "openai-compatible"])
    run_parser.add_argument("--output-dir", type=Path)
    run_parser.add_argument("--json", action="store_true", help="Print the redacted JSON result")

    compare_parser = subparsers.add_parser("compare", help="Compare vulnerable and defended runs")
    compare_parser.add_argument("scenario", type=Path)
    compare_parser.add_argument("--provider", choices=["scripted", "ollama", "openai-compatible"])
    compare_parser.add_argument("--output-dir", type=Path)

    all_parser = subparsers.add_parser("run-all", help="Run every scenario")
    all_parser.add_argument("--scenario-dir", type=Path)
    all_parser.add_argument("--mode", choices=["vulnerable", "defended"], default="vulnerable")
    all_parser.add_argument("--provider", choices=["scripted", "ollama", "openai-compatible"])
    all_parser.add_argument("--output-dir", type=Path)

    validate_parser = subparsers.add_parser("validate", help="Validate all scenario documents")
    validate_parser.add_argument("--scenario-dir", type=Path)

    serve_parser = subparsers.add_parser("serve", help="Start the local API")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8080)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    settings = Settings.from_env()
    try:
        exit_code = dispatch(args, settings)
    except (RhinoGuardError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    raise SystemExit(exit_code)


def dispatch(args: argparse.Namespace, settings: Settings) -> int:
    if args.command == "list":
        paths = discover_scenarios(args.scenario_dir or settings.scenario_dir)
        for path in paths:
            scenario = load_scenario(path)
            print(f"{scenario.id:<28} {scenario.severity.value:<8} {scenario.name}")
        return 0
    if args.command == "validate":
        paths = discover_scenarios(args.scenario_dir or settings.scenario_dir)
        scenarios = [load_scenario(path) for path in paths]
        identifiers = [scenario.id for scenario in scenarios]
        duplicates = sorted({item for item in identifiers if identifiers.count(item) > 1})
        if duplicates:
            raise ValueError(f"Duplicate scenario IDs: {', '.join(duplicates)}")
        print(f"Validated {len(scenarios)} scenario(s).")
        return 0
    if args.command == "serve":
        import uvicorn

        uvicorn.run("rhinoguard.api.app:app", host=args.host, port=args.port)
        return 0

    provider = args.provider or settings.provider
    runner = Runner(create_adapter(provider, settings), settings.policy_file)
    output_dir = args.output_dir or settings.report_dir
    if args.command == "run":
        result = runner.run(load_scenario(args.scenario), _parse_mode(args.mode))
        paths = write_reports(result, output_dir)
        _print_summary(result)
        if args.json:
            print(paths["json"].read_text(encoding="utf-8"))
        else:
            print(f"Reports: {paths['html']}")
        return 0
    if args.command == "compare":
        scenario = load_scenario(args.scenario)
        vulnerable = runner.run(scenario, PolicyMode.MONITOR)
        defended = runner.run(scenario, PolicyMode.ENFORCE)
        write_reports(vulnerable, output_dir)
        write_reports(defended, output_dir)
        print("MODE        SCORE  ATTACK     FINDINGS")
        for label, result in (("vulnerable", vulnerable), ("defended", defended)):
            status = "succeeded" if result.attack_succeeded else "blocked"
            print(f"{label:<12}{result.score:<7}{status:<11}{len(result.findings)}")
        print(f"Score improvement: {defended.score - vulnerable.score:+d}")
        return 0
    if args.command == "run-all":
        mode = _parse_mode(args.mode)
        results = [
            runner.run(load_scenario(path), mode)
            for path in discover_scenarios(args.scenario_dir or settings.scenario_dir)
        ]
        for result in results:
            write_reports(result, output_dir)
            _print_summary(result)
        failures = sum(result.attack_succeeded for result in results)
        print(f"Completed {len(results)} scenario(s); successful attacks: {failures}.")
        return 0
    raise ValueError(f"Unsupported command: {args.command}")


def _parse_mode(value: str) -> PolicyMode:
    aliases = {"vulnerable": PolicyMode.MONITOR, "defended": PolicyMode.ENFORCE}
    if value in aliases:
        return aliases[value]
    return PolicyMode(value)


def _print_summary(result: RunResult) -> None:
    status = "SUCCEEDED" if result.attack_succeeded else "BLOCKED"
    finding_ids = ", ".join(finding.id for finding in result.findings) or "none"
    print(f"[{status}] {result.scenario.id} · score {result.score}/100 · {finding_ids}")


if __name__ == "__main__":
    main()
# Capture a cleanup item for cli module
