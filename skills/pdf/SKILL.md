---
name: pdf
description: Generate polished, print-ready PDF reports using ReportLab and matplotlib with a reusable Python library that provides page decorations, zebra tables, chart rendering, verdict boxes, and cover pages. Use this skill when asked to create PDF documents or reports, generate PDF summaries of data or analysis, produce benchmark/load-test/performance comparison PDFs, export findings as a printable document, or convert computed results into a formatted PDF. Triggers on requests like "create a pdf", "generate a pdf report", "make a pdf document", "export this analysis as pdf", "build a pdf summary", "write the findings to a pdf".
license: MIT
compatibility: opencode
metadata:
  audience: developers, analysts
  workflow: documentation, reporting
  stack: reportlab-5, matplotlib-3, python
---

## What I do

- **Native PDF composition** — matplotlib renders charts to PNG @ dpi=200,
  ReportLab platypus builds the document: landscape A4, dark header bar with
  title/date on every page, footer with page numbers
- **Consistent report family** — zebra tables with repeated header rows,
  2-up chart pages, stat-card tables, verdict boxes, cover pages — all from
  the proven chat-analyzer PDF generators
- **Light print theme** — deliberate contrast with the dark `html` skill
  reports: print-friendly white background
- **Zero web dependencies** — no HTML→PDF conversion, no headless browser

## When to use me

**Perfect for:**

- Benchmark / load-test / performance comparison reports
- Data analysis summaries that must be printable and shareable as files
- Any deliverable that must be a fixed-layout document

**Use the `html` skill instead when** the deliverable should be an
interactive page (charts with hover, fullscreen-zoom diagrams) or a single
self-contained HTML file.

## Quick start

1. **Scaffold first, edit second:**

   ```bash
   python3 skills/pdf/scripts/new_pdf_report.py --title "My Report" -o my_report.pdf
   ```

   (path relative to this skill's directory). Produces a multi-page
   landscape-A4 PDF from computed sample data — swap in real data and edit
   the sections in place.

2. **Read the references before writing layout code by hand:**
   - `references/layout-conventions.md` — page geometry, structure order,
     chart/table conventions, style names

3. **Import the library** in your generator script:

   ```python
   import sys; sys.path.insert(0, "<skill-dir>/scripts")
   from pdf_lib import (new_doc, add_page_decorations, build_styles,
                        make_table, chart_pair, verdict_box, cover_page,
                        mpl_line_chart, mpl_bar_chart, CHART_PALETTE)
   from reportlab.platypus import Paragraph, Spacer, PageBreak
   ```

## Dependencies

`reportlab>=5` and `matplotlib>=3.9` — installed on this machine's system
python3 (`reportlab 5.0.1`, `matplotlib 3.9.4`). Nothing else; do not add
dependencies to `pdf_lib.py`.

## Canonical document structure

1. **Cover** — title + subtitle + config table + verdict box
2. **Executive summary** — stat cards (values tinted per side)
3. **Charts** — 2 per page, KeepTogether
4. **Data tables** — zebra, header repeats across page breaks
5. **Key findings** — bullets with numbers inline
6. **Conclusion + verdict box** — always state confounds

## Helper map (`pdf_lib.py`)

| Helper | Does |
|---|---|
| `new_doc(path, title, author)` | landscape-A4 SimpleDocTemplate, standard margins |
| `add_page_decorations(title, date_str, footer_left)` | factory for the every-page header bar + footer |
| `build_styles()` | the named ParagraphStyles (see layout-conventions.md) |
| `make_table(data, col_widths, ...)` | zebra table, dark header, repeatRows=1 |
| `mpl_line_chart(labels, series, title, y_label, out_path)` | PNG @ dpi=200; None values gap |
| `mpl_bar_chart(categories, series, ...)` | grouped bars |
| `chart_pair(story, charts, styles)` | 2-up images in KeepTogether (24cm × 7.68cm) |
| `verdict_box(story, styles, text)` | accent-bordered verdict |
| `cover_page(story, styles, ...)` | cover + optional config table + verdict |

## Engineering rules

- **Compute, don't hardcode** — every number in the PDF comes from data
- **NaN guard** — filter `v != v` before any aggregation; `None` in chart
  series renders a gap, never a poisoned axis
- Charts land in a `<output_stem>_charts/` dir next to the PDF
- Color per side: first series green `#3FB950`, second blue `#58A6FF`
  (consistent with the html skill reports)

## Verification checklist

Before delivering a PDF:

1. Open it — header bar and page numbers render on every page
2. Tables that cross pages repeat their header row
3. Charts not clipped, aspect correct, legends readable
4. Spot-check at least three numbers against source data
5. Confounds stated in the verdict box if any comparison has them

Run the library's tests after any change to `pdf_lib.py`:

```bash
python3 skills/pdf/scripts/test_pdf_lib.py
```
