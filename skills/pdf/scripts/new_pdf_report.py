#!/usr/bin/env python3
"""Generate a starter PDF report built on pdf_lib.

Usage:
    python3 new_pdf_report.py --title "My Report" -o my_report.pdf

Produces a 3–4 page landscape-A4 PDF (cover -> executive summary stat cards ->
chart pages -> detail table -> findings -> conclusion) from computed sample
data. Swap in real data and edit the sections in place.

Dependencies: reportlab + matplotlib (system python3 on this machine has them).
"""

import argparse
import math
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pdf_lib import (
    new_doc, add_page_decorations, build_styles, make_table, chart_pair,
    verdict_box, cover_page, mpl_line_chart, mpl_bar_chart, CHART_PALETTE,
)

from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, TableStyle


def build_report(title, output):
    styles = build_styles()
    story = []

    # --- sample data: computed, never hardcoded (keep this rule when editing)
    labels = [f"W{i+1}" for i in range(12)]
    current = [round(120 + 40 * math.sin(i / 2.5) + 6 * i, 1) for i in range(12)]
    baseline = [round(90 + 35 * math.sin(i / 2.1 + 1) + 5 * i, 1) for i in range(12)]
    green, blue = CHART_PALETTE[0], CHART_PALETTE[1]
    charts_dir = output.parent / f"{output.stem}_charts"

    # charts (matplotlib -> PNG @ dpi 200)
    line_png = mpl_line_chart(labels, [("current", green, current),
                                       ("baseline", "#8B949E", baseline)],
                              title="Throughput per period",
                              y_label="requests/s", out_path=charts_dir / "throughput.png")
    bar_png = mpl_bar_chart(labels[:6], [("current", green, current[:6]),
                                         ("baseline", "#8B949E", baseline[:6])],
                             title="Throughput (first 6 periods)",
                             y_label="requests/s", out_path=charts_dir / "throughput_bar.png")

    # 1 — cover ------------------------------------------------------------
    cover_page(story, styles, title, "PDF Report Scaffold",
               config_rows=[
                   ["", "Current", "Baseline"],
                   ["Periods", "12", "12"],
                   ["Source", "computed sample data", "computed sample data"],
                   ["Generated (UTC)", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"), ""],
               ],
               verdict_text=(
                   "One short paragraph: what wins, by how much, and under which conditions. "
                   "If the comparison is not apples-to-apples, say so here."))

    # 2 — executive summary stat cards -------------------------------------
    story.append(Paragraph("1. Executive Summary", styles["SectionHeading"]))
    data = [["Metric", "Current", "Baseline", "Result"]]
    for name, c, b, note in [
        ("Throughput (last period)", f"{current[-1]:.1f}", f"{baseline[-1]:.1f}", "replace with computed verdict"),
        ("Throughput (median)", f"{sorted(current)[len(current)//2]:.1f}", f"{sorted(baseline)[len(baseline)//2]:.1f}", "replace"),
        ("Periods", "12", "12", "tie"),
    ]:
        data.append([name, c, b, note])
    t = make_table(data, col_widths=[8 * cm, 5 * cm, 5 * cm, 6 * cm])
    t.setStyle(TableStyle([
        ("TEXTCOLOR", (1, 1), (1, -1), colors.HexColor(green)),
        ("TEXTCOLOR", (2, 1), (2, -1), colors.HexColor(blue)),
        ("FONTNAME", (1, 1), (2, -1), "Helvetica-Bold"),
    ]))
    story.append(t)

    # 3 — charts --------------------------------------------------------------
    story.append(Paragraph("2. Charts", styles["SectionHeading"]))
    chart_pair(story, [("Throughput per period (line)", line_png),
                       ("Throughput first 6 periods (bar)", bar_png)], styles)

    # 4 — per-period table ------------------------------------------------------
    story.append(Paragraph("3. Per-Period Detail", styles["SectionHeading"]))
    rows = [["Period", "Current", "Baseline", "Change", "Latency p50 (ms)"]]
    for i, lbl in enumerate(labels):
        chg = f"{(current[i] / baseline[i] - 1) * 100:+.0f}%"
        rows.append([lbl, f"{current[i]:.1f}", f"{baseline[i]:.1f}", chg,
                     f"{current[i] * 3:.0f}"])
    story.append(make_table(rows, col_widths=[5 * cm, 5 * cm, 5 * cm, 5 * cm, 4 * cm]))

    # 5 — findings -------------------------------------------------------------
    story.append(Paragraph("4. Key Findings", styles["SectionHeading"]))
    for item in [
        "Finding one — strongest computed result, with the numbers inline.",
        "Finding two — second result.",
        "Finding three — reliability/correctness note (errors, coverage).",
    ]:
        story.append(Paragraph(f"•  {item}", styles["BulletItem"]))

    # 6 — conclusion + verdict box ----------------------------------------------
    story.append(Paragraph("5. Conclusion", styles["SectionHeading"]))
    verdict_box(story, styles,
                "State the verdict: which side wins, by how much, and the "
                "conditions. Always list confounds here (different days, "
                "coverage bias, missing metrics).")

    doc = new_doc(output, title=title, author="pdf skill scaffold")
    decorate = add_page_decorations(
        title, date_str=date.today().strftime("%B %Y"),
        footer_left=f"Generated by new_pdf_report.py · {date.today().isoformat()}")
    doc.build(story, onFirstPage=decorate, onLaterPages=decorate)


def main():
    ap = argparse.ArgumentParser(description="Generate a starter PDF report scaffold.")
    ap.add_argument("--title", default="Demo Report", help="report title")
    ap.add_argument("-o", "--output", default="report.pdf", help="output PDF path")
    args = ap.parse_args()

    output = Path(args.output).resolve()
    build_report(args.title, output)
    print(f"PDF report generated: {output} ({output.stat().st_size:,} bytes)")
    print(f"Charts saved under: {output.parent / (output.stem + '_charts')}")
    print("Next: edit sections in place — numbers must be computed, not typed.")


if __name__ == "__main__":
    main()
