# Development

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

## Required checks

```bash
ruff check src tests
python -m unittest discover -s tests -v
python -m rhinoguard validate
python -m rhinoguard run-all --mode vulnerable
python -m rhinoguard run-all --mode defended
```

Core tests use `unittest`, allowing the engine to be verified in a minimal
environment. The development extras also install pytest for coverage and editor
integration.

## Design rules

- Keep synthetic side effects visibly separate from real provider networking.
- Make enforcement deterministic and pre-execution.
- Redact before writing or returning serialized run data.
- Prefer stable scenario IDs and small, reviewable fixtures.
- Add tests for every policy condition and output format.

<!-- Capture a cleanup item for development documentation -->
<!-- Align local documentation for development documentation -->
