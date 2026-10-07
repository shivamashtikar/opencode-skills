#!/usr/bin/env python3
"""pdf_lib — shared library for building PDF reports with ReportLab + matplotlib.

Adapted from chat-analyzer's generate_tp2_vs_g3_pdf.py and generate_pdf_report.py
(Sep 2026) and generalised for the `pdf` OpenCode skill:

  - matplotlib (Agg backend) renders charts to PNG at dpi=200
  - ReportLab platypus composes the document: landscape A4, dark header bar
    with title/date on every page, footer with page numbers, zebra tables
    with repeated header rows, 2-up chart pages in KeepTogether groups
  - light print theme (white background) — a deliberate print decision,
    unlike the dark reports from the companion `html` skill

Dependencies: reportlab + matplotlib (nothing else).
"""

from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # must run before pyplot import
import matplotlib.pyplot as plt  # noqa: E402

from reportlab.lib.pagesizes import landscape, A4  # noqa: E402
from reportlab.lib.units import cm  # noqa: E402
from reportlab.lib import colors  # noqa: E402
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # noqa: E402
from reportlab.platypus import (  # noqa: E402
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether,
)

TEXT_DARK = "#1F2328"
TEXT_MUTED = "#57606A"
GRID_COLOR = "#D0D7DE"
HEADER_BG = "#161B22"
ZEBRA = "#F6F8FA"
CHART_PALETTE = ["#3FB950", "#58A6FF", "#D29922", "#BC8CFF", "#F85149", "#39C5CF"]


# ---------------------------------------------------------------- document

def new_doc(path, title="", author=""):
    """Landscape-A4 SimpleDocTemplate with the standard report margins."""
    return SimpleDocTemplate(
        str(path), pagesize=landscape(A4),
        leftMargin=1.5 * cm, rightMargin=1.5 * cm,
        topMargin=1.8 * cm, bottomMargin=1.5 * cm,
        title=title, author=author,
    )


def add_page_decorations(header_title, date_str=None, footer_left=""):
    """Factory for the doc.build(onFirstPage=..., onLaterPages=...) callbacks.

    Draws the dark header bar (title + date), footer line (left text + page
    number) on every page. Returns an (canvas, doc) function."""
    date_str = date_str or datetime.now(timezone.utc).strftime("%B %Y")

    def _decorate(canvas, doc):
        canvas.saveState()
        width, height = landscape(A4)

        canvas.setFillColor(colors.HexColor("#1B1F24"))
        canvas.rect(0, height - 1.2 * cm, width, 1.2 * cm, fill=1, stroke=0)
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.drawString(1.5 * cm, height - 0.8 * cm, header_title)
        canvas.setFont("Helvetica", 7)
        canvas.drawRightString(width - 1.5 * cm, height - 0.8 * cm, date_str)

        canvas.setFillColor(colors.HexColor(TEXT_MUTED))
        canvas.setFont("Helvetica", 7)
        canvas.drawString(1.5 * cm, 0.7 * cm, footer_left or header_title)
        canvas.drawRightString(width - 1.5 * cm, 0.7 * cm, f"Page {doc.page}")

        canvas.setStrokeColor(colors.HexColor("#E0E0E0"))
        canvas.setLineWidth(0.5)
        canvas.line(1.5 * cm, 1.0 * cm, width - 1.5 * cm, 1.0 * cm)

        canvas.restoreState()

    return _decorate


def build_styles():
    """Named ParagraphStyles for the whole report family."""
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReportTitle", fontName="Helvetica-Bold", fontSize=28,
                              leading=34, textColor=colors.HexColor(TEXT_DARK), spaceAfter=6))
    styles.add(ParagraphStyle(name="ReportSubtitle", fontName="Helvetica", fontSize=14,
                              leading=20, textColor=colors.HexColor(TEXT_MUTED), spaceAfter=4))
    styles.add(ParagraphStyle(name="SectionHeading", fontName="Helvetica-Bold", fontSize=16,
                              leading=20, textColor=colors.HexColor("#0969DA"), spaceBefore=18,
                              spaceAfter=8))
    styles.add(ParagraphStyle(name="SubHeading", fontName="Helvetica-Bold", fontSize=12,
                              leading=16, textColor=colors.HexColor(TEXT_DARK), spaceBefore=12,
                              spaceAfter=6))
    styles.add(ParagraphStyle(name="BodyTextCustom", fontName="Helvetica", fontSize=9.5,
                              leading=14, textColor=colors.HexColor(TEXT_DARK), spaceAfter=8))
    styles.add(ParagraphStyle(name="SmallNote", fontName="Helvetica-Oblique", fontSize=8,
                              leading=11, textColor=colors.HexColor(TEXT_MUTED), spaceAfter=6))
    styles.add(ParagraphStyle(name="VerdictText", fontName="Helvetica", fontSize=10.5,
                              leading=15, textColor=colors.HexColor(TEXT_DARK), spaceAfter=6))
    styles.add(ParagraphStyle(name="BulletItem", fontName="Helvetica", fontSize=9.5,
                              leading=14, textColor=colors.HexColor(TEXT_DARK), leftIndent=14,
                              spaceAfter=4))
    return styles


def make_table(data, col_widths=None, header_bg=HEADER_BG, font_size=8.5):
    """Zebra-striped table, dark header row, grid, first column left-aligned
    and the rest right-aligned, header row repeated across page breaks."""
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_bg)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor(GRID_COLOR)),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor(ZEBRA)]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


# ---------------------------------------------------------------- charts
# matplotlib Agg -> PNG at dpi=200, white print background, tight bbox.

def _style_axis(ax, title, y_label):
    ax.set_title(title, fontsize=11, fontweight="bold", color=TEXT_DARK, pad=8)
    ax.set_ylabel(y_label, fontsize=9, color=TEXT_MUTED)
    ax.tick_params(axis="both", labelsize=8, colors=TEXT_MUTED)
    ax.grid(True, color=GRID_COLOR, linewidth=0.5, alpha=0.7)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GRID_COLOR)
    ax.spines["bottom"].set_color(GRID_COLOR)
    ax.set_facecolor("#FAFBFC")


def _save(fig, out_path):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.patch.set_facecolor("white")
    plt.tight_layout()
    fig.savefig(str(out_path), facecolor="white", bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    return out_path


def mpl_line_chart(labels, series, title, y_label, out_path, x_label="", legend=True):
    """Line chart. labels: x tick labels; series: [(label, color, [values])].
    None/NaN values create gaps (the point is skipped)."""
    fig, ax = plt.subplots(figsize=(10, 3.2), dpi=200)
    for label, color, values in series:
        xs = [i for i, v in enumerate(values) if v is not None and v == v]
        ys = [v for v in values if v is not None and v == v]
        if xs:
            ax.plot(xs, ys, color=color, linewidth=1.2, label=label, alpha=0.85)
    if x_label:
        ax.set_xlabel(x_label, fontsize=9, color=TEXT_MUTED)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels([str(x) for x in labels], fontsize=8)
    _style_axis(ax, title, y_label)
    if legend and len(series) > 1:
        ax.legend(loc="upper left", fontsize=8, framealpha=0.9, edgecolor=GRID_COLOR)
    return _save(fig, out_path)


def mpl_bar_chart(categories, series, title, y_label, out_path, x_label="", legend=True):
    """Grouped bar chart. series: [(label, color, [values])] aligned to categories."""
    fig, ax = plt.subplots(figsize=(10, 3.2), dpi=200)
    n = len(series)
    width = 0.8 / max(n, 1)
    for i, (label, color, values) in enumerate(series):
        xs = [x + (i - (n - 1) / 2) * width for x in range(len(categories))]
        ys = [float("nan") if v is None else v for v in values]  # nan bars are skipped
        ax.bar(xs, ys, width=width * 0.92, color=color, label=label, alpha=0.9)
    if x_label:
        ax.set_xlabel(x_label, fontsize=9, color=TEXT_MUTED)
    ax.set_xticks(range(len(categories)))
    ax.set_xticklabels([str(c) for c in categories], fontsize=8)
    _style_axis(ax, title, y_label)
    if legend and n > 1:
        ax.legend(loc="upper left", fontsize=8, framealpha=0.9, edgecolor=GRID_COLOR)
    return _save(fig, out_path)


def chart_pair(story, charts, styles, img_w=24 * cm, img_h=7.68 * cm):
    """Append chart images 2-up inside KeepTogether groups (10:3.2 aspect
    preserved by the default img_w/img_h). charts: [(title, path)]."""
    for i in range(0, len(charts), 2):
        group = []
        for title, path in charts[i:i + 2]:
            group.append(Paragraph(title, styles["SubHeading"]))
            group.append(Image(str(path), width=img_w, height=img_h))
            group.append(Spacer(1, 0.3 * cm))
        story.append(KeepTogether(group))


# ---------------------------------------------------------------- blocks

def verdict_box(story, styles, text, title="Verdict"):
    """Accent-bordered verdict box (chat-analyzer report convention)."""
    story.append(Paragraph(title, styles["SubHeading"]))
    box = Table([[Paragraph(text, styles["VerdictText"])]], colWidths=[24 * cm])
    box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F0F6FF")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#0969DA")),
        ("LINEBEFORE", (0, 0), (0, -1), 4, colors.HexColor("#0969DA")),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
    ]))
    story.append(box)


def cover_page(story, styles, title, subtitle, config_rows=None,
               col_widths=None, verdict_text=None):
    """Cover page: title, subtitle, optional config table, optional verdict
    box, then a page break."""
    story.append(Spacer(1, 3 * cm))
    story.append(Paragraph(title, styles["ReportTitle"]))
    story.append(Paragraph(subtitle, styles["ReportSubtitle"]))
    story.append(Spacer(1, 1 * cm))
    if config_rows:
        if col_widths is None:
            n = len(config_rows[0])
            col_widths = [24 * cm / n] * n
        story.append(make_table(config_rows, col_widths=col_widths))
        story.append(Spacer(1, 1 * cm))
    if verdict_text:
        verdict_box(story, styles, verdict_text)
    story.append(PageBreak())
