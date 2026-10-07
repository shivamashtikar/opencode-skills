# Layout conventions — PDF reports (ReportLab + matplotlib)

Adapted from the chat-analyzer PDF generators (`generate_tp2_vs_g3_pdf.py`,
`generate_pdf_report.py`), which produced the reference reports
(`tp2_vs_tp2g3_comparison.pdf` etc.). Follow these so every PDF from this
skill looks like the same family.

## Pipeline

```
data -> matplotlib (Agg) charts as PNG @ dpi=200
     -> ReportLab platypus story (Paragraph / Table / Image / KeepTogether)
     -> SimpleDocTemplate.build(story, onFirstPage=decor, onLaterPages=decor)
```

There is **no HTML→PDF conversion** anywhere in this pipeline — PDFs are
composed natively. (For HTML deliverables use the `html` skill.)

## Page geometry

- Landscape A4
- Margins: left/right 1.5 cm, top 1.8 cm, bottom 1.5 cm
- `new_doc(path, title, author)` from `pdf_lib` encodes all of this

## Page decorations (every page)

- Dark header bar `#1B1F24`, 1.2 cm tall, full width: bold title left, date right
- Footer: left text (data source / generator), `Page N` right, hairline above
- Built by `add_page_decorations(header_title, date_str, footer_left)` — a
  factory, because doc.build needs an `(canvas, doc)` callback

## Document structure (in order)

1. **Cover** — `cover_page()`: title, subtitle, config table, verdict box, PageBreak
2. **Executive summary** — stat-card table (values color-tinted per side)
3. **Charts** — `chart_pair()`: 2 images per page in `KeepTogether`
4. **Data tables** — `make_table()`: zebra, repeated header rows
5. **Key findings** — `BulletItem` paragraphs
6. **Conclusion + verdict box** — `verdict_box()`

## Charts

- `figsize=(10, 3.2)`, `dpi=200`, white figure background, axes `#FAFBFC`
- `bbox_inches="tight", pad_inches=0.15`
- Placed at `24cm × 7.68cm` — the 10:3.2 aspect ratio is preserved exactly
- Ticks/labels: muted `#57606A`; grid `#D0D7DE`; no top/right spines
- Series colors from `CHART_PALETTE` (green `#3FB950` first, blue `#58A6FF`
  second — keeps side-by-side comparisons consistent with the HTML reports)

## Tables

- Dark header row `#161B22`, white bold text
- Zebra rows: white / `#F6F8FA`; grid `#D0D7DE` 0.5pt
- First column left-aligned, all others right-aligned (numeric columns —
  matches `html_lib.table_html` so HTML and PDF reports read the same)
- `repeatRows=1` — header repeats when a table crosses a page break

## Light print theme — why

The companion `html` skill produces dark reports; PDFs are deliberately
light (white background, dark text). Printing dark backgrounds wastes toner
and renders poorly. Keep the light theme for print deliverables.

## Style names (`build_styles()`)

| Style | Use |
|---|---|
| `ReportTitle` / `ReportSubtitle` | cover page |
| `SectionHeading` (blue `#0969DA`) | numbered top-level sections |
| `SubHeading` | sub-sections, chart titles |
| `BodyTextCustom` / `SmallNote` | prose / muted asides |
| `VerdictText` | inside the verdict box |
| `BulletItem` | findings bullets |

## Engineering rules

- **Compute, don't hardcode** — every number comes from data
- **NaN guard** — filter `v != v` before `max()`/`mean()`; `None` values in
  chart series create gaps, they never poison the axis
- Confounds always stated in the verdict box
- Keep `pdf_lib` dependency-light: reportlab + matplotlib only
