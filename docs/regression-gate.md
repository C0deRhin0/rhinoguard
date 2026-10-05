# Regression gate

Pull requests targeting `main` run the **Release readiness** check. It evaluates
the exact PR head against the target commit and uploads Markdown/JSON evidence
and coverage in the `regression-gate-reports` artifact, including on failure.

All four groups are required even for documentation-only changes:

- Full pytest suite with Cobertura coverage (minimum 80%).
- Explicit policy, sandbox, corpus execution, and report-redaction regressions.
- Validation of the scenario corpus.
- Ruff checks of application code and tests.

The gate uses deterministic analysis with no LLM calls or API credentials.
RhinoGuard's provider is explicitly scripted in CI. Workflow permissions are
read-only; no deployment, publishing, or real-target attacks occur.
The gate dependency is pinned to commit
`c49f48a7d646c7f6ae2b4e934fac95034df1e100` of
`C0deRhin0/ai-regression-gate`.

## Local verification

From the repository root, with Python 3.12 or newer:

```bash
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m pip install 'ai-regression-gate @ git+https://github.com/C0deRhin0/ai-regression-gate.git@c49f48a7d646c7f6ae2b4e934fac95034df1e100'
argate config validate
git fetch origin main
RHINOGUARD_PROVIDER=scripted argate evaluate --base origin/main --head HEAD --no-ai --report-dir reports/argate
```

Commit tracked edits before evaluation: the gate requires the worktree to match
the selected head. After a merge, use `--base HEAD~1` to check the latest commit.
Reports and generated coverage are ignored; `src/rhinoguard/reports/` is tracked.
Exit status 0 means READY; 1 means BLOCKED. A failed required group or coverage
below 80% blocks readiness. The gate does not replace code review, and enforcing
its result on merges requires GitHub branch protection with Release readiness
configured as a required check.
