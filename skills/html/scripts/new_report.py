#!/usr/bin/env python3
"""Generate a starter HTML report built on html_lib.

Usage:
    python3 new_report.py --title "My Report" -o my_report.html
    python3 new_report.py --title "My Report" -o my_report.html --theme light --mode cdn

Emits a single self-contained file (inline mode): Bootstrap 5 + Chart.js are
inlined, so the report opens fully styled anywhere, offline. Mermaid renders
from CDN with a fullscreen zoom viewer. Edit the generated sections in place.
"""

import argparse
import math
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from html_lib import (
    build_head, build_foot, stat_cards_row, callout, table_html,
    section_heading, verdict, fnum, pct_str, fmt_ms, med,
    chartjs_canvas, chartjs_script, chartjs_defaults,
    chartjs_line, chartjs_bar, chartjs_doughnut,
    mermaid_block, mermaid_init,
)


def build_report(title, theme, mode):
    # --- sample data: computed, never hardcoded (keep this rule when editing)
    labels = [f"W{i+1}" for i in range(12)]
    current = [round(120 + 40 * math.sin(i / 2.5) + 6 * i, 1) for i in range(12)]
    baseline = [round(90 + 35 * math.sin(i / 2.1 + 1) + 5 * i, 1) for i in range(12)]
    regions = ["us-east", "us-west", "eu-west", "ap-south"]
    share = [round(100 * v / sum([38, 24, 21, 17])) for v in [38, 24, 21, 17]]

    html = [build_head(title, theme=theme, mode=mode)]

    html.append(f"""
<h1 class="mb-1">{title}</h1>
<p class="subtitle">One-line context: what, where, when. Update me.</p>

<p class="lead">Replace this paragraph with a two-sentence summary of what the
report measures and the headline conclusion. Numbers below are computed
sample data — swap in real ones.</p>
""")

    # 1 — Outcomes ---------------------------------------------------------
    gain = pct_str(baseline[-1], current[-1])
    html.append(section_heading(1, "Outcomes"))
    html.append(stat_cards_row([
        ("Throughput", fnum(current[-1], 1), f"vs baseline {fnum(baseline[-1], 1)}", "#58a6ff"),
        ("Change", gain, "last period vs baseline", "#3fb950"),
        ("Median latency", fmt_ms(med(current) * 3), "upper-middle median", "#d29922"),
        ("Error rate", "0.00%", "12 weeks, computed", "#f85149"),
    ]))

    # 2 — Charts ------------------------------------------------------------
    html.append(section_heading(2, "Trends"))
    html.append(chartjs_defaults(theme=theme))
    html.append(chartjs_canvas("chart-line"))
    html.append(chartjs_script("chart-line", chartjs_line(
        labels,
        [("current", "#58a6ff", current), ("baseline", "#8b949e", baseline)],
        y_title="requests/s")))
    html.append(chartjs_canvas("chart-bar"))
    html.append(chartjs_script("chart-bar", chartjs_bar(
        labels[:6],
        [("current", "#3fb950", current[:6]), ("baseline", "#8b949e", baseline[:6])],
        y_title="requests/s")))
    html.append(chartjs_canvas("chart-share", height=240))
    html.append(chartjs_script("chart-share", chartjs_doughnut(regions, share)))

    # 3 — Architecture (mermaid, fullscreen zoom by default) ----------------
    html.append(section_heading(3, "Architecture"))
    html.append('<p class="text-secondary small">Click the diagram (or ⛶) for '
                'fullscreen: wheel to zoom, drag to pan, Esc to close.</p>')
    html.append(mermaid_block(
        "flowchart LR\n"
        "    A[Data sources] --> B[Python computes\nthe numbers]\n"
        "    B --> C[html_lib renders\nsingle-file HTML]\n"
        "    C --> D((Browser))\n"
        "    D --> E[Fullscreen zoom\nfor large graphs]",
        caption="Replace with the system or pipeline this report describes."))

    # 4 — Data table ---------------------------------------------------------
    rows = []
    for i, lbl in enumerate(labels):
        rows.append([
            lbl,
            fnum(current[i], 1),
            fnum(baseline[i], 1),
            pct_str(baseline[i], current[i]),
            fmt_ms(current[i] * 3),
        ])
    html.append(section_heading(4, "Per-Period Detail"))
    html.append(table_html(
        ["Period", "Current", "Baseline", "Change", "Latency (p50)"],
        rows,
        caption="First column left-aligned, numerics right-aligned with tabular-nums."))

    # 5 — Findings & caveats --------------------------------------------------
    html.append(section_heading(5, "Findings & Caveats"))
    html.append(callout("info",
                        "<strong>Finding.</strong> State the strongest computed result here, "
                        "with the numbers inline."))
    html.append(callout("warning",
                        "<strong>Caveat.</strong> Always state confounds: different time windows, "
                        "coverage bias, missing metrics, environment differences."))
    html.append(verdict(
        "<p>One short paragraph: what wins, by how much, and under which conditions. "
        "If the comparison is not apples-to-apples, say so here.</p>"))

    # mermaid init exactly once, after all diagrams, before the document close
    html.append(mermaid_init())

    assets = "inlined" if mode == "inline" else "via CDN"
    html.append(build_foot(
        f"Generated by new_report.py · {date.today().isoformat()} · "
        f"Bootstrap 5 + Chart.js {assets}, Mermaid via CDN"))

    return "".join(html)


def main():
    ap = argparse.ArgumentParser(description="Generate a starter HTML report scaffold.")
    ap.add_argument("--title", default="Demo Report", help="report title")
    ap.add_argument("-o", "--output", default="report.html", help="output HTML path")
    ap.add_argument("--theme", default="dark", choices=["dark", "light"])
    ap.add_argument("--mode", default="inline", choices=["inline", "cdn"],
                    help="inline = single self-contained file (default)")
    args = ap.parse_args()

    out = Path(args.output)
    html = build_report(args.title, args.theme, args.mode)
    out.write_text(html)
    print(f"Report generated: {out.resolve()} ({len(html):,} bytes)")
    print("Next: edit sections in place — numbers must be computed, not typed.")


if __name__ == "__main__":
    main()
