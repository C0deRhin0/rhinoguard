from __future__ import annotations

from html import escape

from rhinoguard.models import RunResult
from rhinoguard.reports.redaction import redacted_payload


def render_html(result: RunResult) -> str:
    payload = redacted_payload(result)
    blocked = sum(item["blocked"] for item in payload["tool_results"])
    outcome = (
        "Attack succeeded" if payload["attack_succeeded"] else
        "Attack blocked" if blocked else "Attack not observed"
    )
    outcome_class = "danger" if payload["attack_succeeded"] else "safe"
    provider_note = (
        "Scripted adapter. Deterministic local demonstration; no live model was evaluated."
        if payload["provider"] == "scripted"
        else "Results apply to the provider, scenario, and configuration recorded in this run."
    )
    findings = "".join(
        f"""<article class="finding">
          <header class="finding-heading"><h3>{escape(finding["title"])}</h3>
            <span class="severity {escape(str(finding["severity"]))}">{escape(str(finding["severity"]).upper())}</span></header>
          <p>{escape(finding["description"])}</p>
          <dl class="evidence"><dt>Evidence</dt><dd>{escape(finding["evidence"])}</dd>
            <dt>Remediation</dt><dd>{escape(finding["remediation"])}</dd></dl>
          <p class="mapping"><span>OWASP</span> {escape(", ".join(finding["owasp"]) or "—")} <span>MITRE ATLAS</span> {escape(", ".join(finding["mitre_atlas"]) or "—")}</p>
        </article>"""
        for finding in payload["findings"]
    ) or '<p class="empty">No findings were generated.</p>'
    tool_rows = "".join(
        f"""<tr><td><code>{escape(item['call_id'])}</code></td><td><code>{escape(item['tool'])}</code></td>
          <td><span class="decision {'denied' if item['blocked'] else 'allowed' if item['success'] else 'error'}">{'Blocked' if item['blocked'] else 'Allowed' if item['success'] else 'Error'}</span></td>
          <td><code>{escape(str(item.get('policy_rule') or '—'))}</code></td></tr>"""
        for item in payload["tool_results"]
    ) or '<tr><td colspan="4">No tool calls were recorded.</td></tr>'
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>RhinoGuard · {escape(payload["scenario"]["name"])}</title>
  <style>
    :root{{color-scheme:light;--ink:#202731;--muted:#5d6875;--line:#d5dbe1;--blue:#214f8e;--paper:#fff;--canvas:#edf0f3}}
    *{{box-sizing:border-box}}html{{scroll-padding-top:24px}}body{{margin:0;background:var(--canvas);color:var(--ink);font:14px/1.55 Arial,Helvetica,sans-serif}}a{{color:var(--blue)}}
    .appbar{{height:64px;display:flex;align-items:center;justify-content:space-between;gap:20px;padding:0 30px;background:#202b39;color:#fff;border-bottom:1px solid #111b27}}
    .brand{{display:flex;align-items:center;gap:12px;font-size:18px;font-weight:700}}.brand-mark{{display:grid;place-items:center;width:30px;height:30px;border:1px solid #8c9aaa;font:700 12px ui-monospace,monospace}}.appbar p{{margin:0;color:#d1d9e2;font-size:13px}}
    .shell{{display:grid;grid-template-columns:205px minmax(0,1fr);max-width:1360px;min-height:calc(100vh - 64px);margin:auto;background:var(--paper);border-right:1px solid var(--line);border-left:1px solid var(--line)}}
    aside{{padding:28px 20px;background:#f4f6f8;border-right:1px solid var(--line)}}.nav-title{{margin:0 0 12px;font-size:12px;font-weight:700;color:var(--muted)}}nav{{display:grid;gap:4px}}nav a{{padding:9px 10px;text-decoration:none;border-left:2px solid transparent;color:#3e4c5e}}nav a:first-child{{border-color:var(--blue);background:#e4ebf4;color:#163e73;font-weight:700}}nav a:hover{{background:#e4ebf4}}a:focus-visible{{outline:2px solid #214f8e;outline-offset:3px}}
    .run-details{{border-top:1px solid var(--line);margin:28px 0 0;padding-top:20px;font-size:12px}}dt{{color:var(--muted)}}.run-details dd{{margin:3px 0 15px;overflow-wrap:anywhere}}code,pre{{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}}.run-details code{{font-size:11px}}
    main{{padding:30px 38px 34px;min-width:0}}.breadcrumb{{margin:0 0 14px;color:var(--muted);font-size:12px}}.report-heading{{display:flex;align-items:flex-start;justify-content:space-between;gap:24px}}h1{{font-size:28px;line-height:1.2;letter-spacing:-.5px;margin:0 0 14px;max-width:760px}}.description{{color:#4b5765;font-size:14px;max-width:800px;margin:0 0 22px}}
    .outcome{{border:1px solid;padding:5px 9px;white-space:nowrap;font-size:12px;font-weight:700}}.safe{{background:#edf6ef;border-color:#9dbba4;color:#245b35}}.danger{{background:#fff0ed;border-color:#d6a49b;color:#9a3022}}
    .summary{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));border-top:2px solid #36465a;border-bottom:1px solid var(--line);margin:0 0 18px;padding:17px 0}}.summary>div{{padding:0 20px;border-right:1px solid var(--line)}}.summary>div:first-child{{padding-left:0}}.summary>div:last-child{{border:0}}.summary dt{{font-size:12px}}.summary dd{{margin:4px 0 0;font-size:23px;line-height:1.2;font-weight:700}}.summary dd small{{font-size:13px;color:var(--muted);font-weight:400}}.summary dd.policy{{font-size:20px;text-transform:capitalize}}
    .provenance{{background:#f4f6f8;border-left:3px solid #8d9caf;color:#566270;padding:10px 13px;font-size:12px;margin:0 0 26px}}
    section{{scroll-margin-top:24px;margin-top:28px}}.section-heading{{display:flex;align-items:baseline;justify-content:space-between;gap:16px;border-bottom:1px solid #9da9b6;padding-bottom:10px}}h2{{font-size:18px;margin:0}}.section-heading span{{color:var(--muted);font-size:12px}}
    .finding{{padding:20px 0;border-bottom:1px solid var(--line)}}.finding-heading{{display:flex;align-items:baseline;justify-content:space-between;gap:20px}}h3{{font-size:15px;margin:0}}.finding>p{{margin:9px 0 12px;max-width:900px}}.severity{{font-size:10px;font-weight:700;letter-spacing:.3px;padding:3px 7px;border:1px solid #a6b0ba;color:#4e5d6b;background:#f2f4f6}}.severity.medium{{color:#805600;border-color:#c8b88f;background:#fff9e9}}.severity.high,.severity.critical{{color:#9c3028;border-color:#d2a19b;background:#fff1ee}}.evidence{{display:grid;grid-template-columns:95px minmax(0,1fr);gap:7px 12px;margin:0;font-size:13px}}.evidence dt{{font-weight:700}}.evidence dd{{margin:0;overflow-wrap:anywhere}}.finding .mapping{{font-size:11px;color:#4f6072;margin:14px 0 0}}.mapping span{{font-weight:700;margin-right:5px}}.mapping span:not(:first-child){{margin-left:18px}}
    .table-wrap{{overflow-x:auto}}table{{width:100%;border-collapse:collapse;font-size:12px}}th,td{{padding:12px 10px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}}th{{color:#4c5b6b;font-size:11px;background:#f4f6f8}}td code{{font-size:11px}}.decision{{font-weight:700}}.denied{{color:#9a3022}}.allowed{{color:#245b35}}.error{{color:#805600}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px;background:#f5f7f9;border:1px solid var(--line);padding:17px;line-height:1.7;margin:16px 0 0}}footer{{border-top:1px solid var(--line);margin-top:32px;padding-top:15px;color:var(--muted);font-size:11px}}.empty{{padding:20px 0;color:var(--muted)}}
    @media(max-width:900px){{.shell{{grid-template-columns:170px minmax(0,1fr)}}aside{{padding:24px 14px}}main{{padding:26px 24px}}.report-heading{{display:block}}.outcome{{display:inline-block;margin-bottom:15px}}h1{{font-size:26px}}}}
    @media(max-width:600px){{.appbar{{height:58px;padding:0 16px}}.appbar p{{font-size:11px;max-width:120px;text-align:right}}.shell{{display:block;border:0}}aside{{padding:12px 16px;border-right:0;border-bottom:1px solid var(--line)}}.nav-title,.run-details{{display:none}}nav{{display:flex;gap:6px;overflow-x:auto}}nav a{{white-space:nowrap;font-size:12px;padding:5px 8px}}main{{padding:24px 18px}}h1{{font-size:25px}}.summary{{grid-template-columns:repeat(2,minmax(0,1fr));row-gap:18px}}.summary>div{{padding:0 14px}}.summary>div:nth-child(odd){{padding-left:0}}.summary>div:nth-child(even){{border:0}}.summary dd{{font-size:22px}}.finding-heading{{align-items:flex-start;gap:12px}}h3{{font-size:14px}}.evidence{{grid-template-columns:1fr;gap:3px}}.evidence dd{{margin-bottom:8px}}.mapping span:not(:first-child){{display:block;margin:8px 0 0}}.section-heading span{{font-size:11px}}th,td{{padding:10px 8px}}}}
    @media print{{body{{background:white}}.appbar{{background:white;color:#202731}}.appbar p{{color:#5d6875}}.shell{{display:block;border:0}}aside{{display:none}}main{{padding:20px}}.finding{{break-inside:avoid}}}}
  </style>
</head>
<body>
  <header class="appbar"><div class="brand"><span class="brand-mark" aria-hidden="true">RG</span>RhinoGuard</div><p>Security evaluation report</p></header>
  <div class="shell">
    <aside aria-label="Report navigation"><p class="nav-title">Report contents</p><nav><a href="#overview">Overview</a><a href="#findings">Findings</a><a href="#tool-trace">Tool trace</a><a href="#final-answer">Final answer</a></nav>
      <dl class="run-details"><dt>Scenario</dt><dd><code>{escape(payload["scenario"]["id"])}</code></dd><dt>Provider</dt><dd>{escape(payload["provider"])}</dd><dt>Completed</dt><dd><time>{escape(payload["completed_at"])}</time></dd><dt>Run ID</dt><dd><code>{escape(payload["run_id"])}</code></dd></dl>
    </aside>
    <main>
      <div id="overview"><p class="breadcrumb">Evaluation / {escape(payload["scenario"]["id"])}</p><div class="report-heading"><h1>{escape(payload["scenario"]["name"])}</h1><span class="outcome {outcome_class}">{outcome}</span></div><p class="description">{escape(payload["scenario"]["description"])}</p>
        <dl class="summary" aria-label="Run summary"><div><dt>Evaluation score</dt><dd>{payload["score"]}<small> / 100</small></dd></div><div><dt>Policy mode</dt><dd class="policy">{escape(payload["mode"])}</dd></div><div><dt>Findings</dt><dd>{len(payload["findings"])}</dd></div><div><dt>Blocked calls</dt><dd>{blocked}<small> / {len(payload["tool_results"])}</small></dd></div></dl>
        <p class="provenance">{provider_note}</p>
      </div>
      <section id="findings" aria-labelledby="findings-title"><header class="section-heading"><h2 id="findings-title">Findings</h2><span>Detection evidence &amp; remediation</span></header>{findings}</section>
      <section id="tool-trace" aria-labelledby="trace-title"><header class="section-heading"><h2 id="trace-title">Tool trace</h2><span>{len(payload["tool_results"])} calls recorded</span></header><div class="table-wrap"><table><thead><tr><th scope="col">Call</th><th scope="col">Tool</th><th scope="col">Decision</th><th scope="col">Policy rule</th></tr></thead><tbody>{tool_rows}</tbody></table></div></section>
      <section id="final-answer" aria-labelledby="answer-title"><header class="section-heading"><h2 id="answer-title">Redacted final answer</h2></header><pre>{escape(str(payload["final_answer"]))}</pre></section>
      <footer>RhinoGuard · {escape(payload["scenario"]["id"])} · Secret values are redacted before export.</footer>
    </main>
  </div>
</body>
</html>"""
