from __future__ import annotations

from html import escape

from rhinoguard.models import RunResult
from rhinoguard.reports.redaction import redacted_payload


def render_html(result: RunResult) -> str:
    payload = redacted_payload(result)
    attack_class = "danger" if payload["attack_succeeded"] else "safe"
    cards = (
        "".join(
            f"""
        <article class="finding {escape(str(finding["severity"]))}">
          <div class="finding-head"><h3>{escape(finding["title"])}</h3><span>{escape(str(finding["severity"]).upper())}</span></div>
          <p>{escape(finding["description"])}</p>
          <p><strong>Evidence:</strong> {escape(finding["evidence"])}</p>
          <p><strong>Remediation:</strong> {escape(finding["remediation"])}</p>
          <small>OWASP {escape(", ".join(finding["owasp"]) or "—")} · MITRE ATLAS {escape(", ".join(finding["mitre_atlas"]) or "—")}</small>
        </article>"""
            for finding in payload["findings"]
        )
        or '<p class="empty">No findings were generated.</p>'
    )
    tool_rows = "".join(
        f"<tr><td>{escape(item['call_id'])}</td><td>{escape(item['tool'])}</td>"
        f"<td>{'BLOCKED' if item['blocked'] else 'OK' if item['success'] else 'ERROR'}</td>"
        f"<td>{escape(str(item.get('policy_rule') or '—'))}</td></tr>"
        for item in payload["tool_results"]
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>RhinoGuard · {escape(payload["scenario"]["name"])}</title>
  <style>
    :root{{--bg:#07110d;--panel:#0d1c16;--line:#244b39;--text:#d9fbe7;--muted:#8db79d;--green:#46e689;--red:#ff6577;--amber:#ffc857}}
    *{{box-sizing:border-box}} body{{margin:0;background:radial-gradient(circle at 15% 0,#123526,var(--bg) 38%);color:var(--text);font:15px/1.6 ui-monospace,SFMono-Regular,Menlo,monospace}}
    main{{width:min(1000px,92vw);margin:48px auto}} h1,h2,h3{{line-height:1.2}} .eyebrow{{color:var(--green);letter-spacing:.16em;text-transform:uppercase}}
    .summary{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:24px 0}} .metric,.finding,section{{background:color-mix(in srgb,var(--panel) 94%,transparent);border:1px solid var(--line);border-radius:12px;padding:18px}}
    .metric strong{{display:block;font-size:26px}} .danger{{color:var(--red)}} .safe{{color:var(--green)}} .finding{{margin:12px 0;color:var(--text)}} .finding-head{{display:flex;justify-content:space-between;gap:16px}} .finding-head span{{color:var(--amber)}}
    table{{width:100%;border-collapse:collapse}} th,td{{padding:10px;text-align:left;border-bottom:1px solid var(--line)}} pre{{white-space:pre-wrap;overflow-wrap:anywhere;color:var(--muted)}} small{{color:var(--muted)}}
  </style>
</head>
<body><main>
  <div class="eyebrow">RhinoGuard security evaluation</div>
  <h1>{escape(payload["scenario"]["name"])}</h1>
  <p>{escape(payload["scenario"]["description"])}</p>
  <div class="summary">
    <div class="metric"><span>Score</span><strong>{payload["score"]}/100</strong></div>
    <div class="metric"><span>Attack</span><strong class="{attack_class}">{"SUCCEEDED" if payload["attack_succeeded"] else "BLOCKED"}</strong></div>
    <div class="metric"><span>Mode</span><strong>{escape(payload["mode"])}</strong></div>
    <div class="metric"><span>Findings</span><strong>{len(payload["findings"])}</strong></div>
  </div>
  <h2>Findings</h2>{cards}
  <section><h2>Tool trace</h2><table><thead><tr><th>Call</th><th>Tool</th><th>Status</th><th>Rule</th></tr></thead><tbody>{tool_rows}</tbody></table></section>
  <section><h2>Redacted final answer</h2><pre>{escape(str(payload["final_answer"]))}</pre></section>
  <p><small>Run {escape(payload["run_id"])} · {escape(payload["completed_at"])}</small></p>
</main></body></html>"""
# Document the next adjustment for html report module
