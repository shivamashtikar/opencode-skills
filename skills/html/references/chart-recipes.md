# Chart recipes — Chart.js, Mermaid, and inline SVG

Three chart tiers, pick per context:

| Tier | Use when | Library |
|---|---|---|
| Chart.js | Interactive on-screen reports (default) | inlined, offline OK |
| Mermaid | Diagrams: flowcharts, sequence, gantt, ... | CDN only |
| Inline SVG | Print/no-JS contexts, PDF-bound output | none (stdlib) |

## Chart.js

Python computes, JS renders — `chartjs_*` builders return plain config dicts.

```python
from html_lib import (chartjs_canvas, chartjs_script, chartjs_defaults,
                      chartjs_line, chartjs_bar, chartjs_doughnut)

html.append(chartjs_defaults(theme="dark"))   # ONCE per page, after build_head
html.append(chartjs_canvas("rps"))           # <div><canvas id="rps"></div>
html.append(chartjs_script("rps", chartjs_line(
    ["W1", "W2", "W3"],
    [("current", "#58a6ff", [120, 135, 161]), ("baseline", "#8b949e", [90, 101, 110])],
    y_title="requests/s")))
```

- Dark theme config: `chartjs_defaults(theme="dark")` sets tick/grid/legend
  colors and turns **animations off** (keeps print/PDF export faithful).
  Light values: color `#495057`, border `rgba(0,0,0,.08)`.
- **Theme toggle:** charts created via `chartjs_script()` register themselves
  in `window.__charts`, so the page's 🌓 light/dark toggle re-themes them
  (ticks, grid, legend) automatically. Hand-written `new Chart(...)` calls
  are not registered and will NOT re-theme — always use `chartjs_script()`.
  `chartjs_defaults()` sets the colors matching the page's INITIAL theme.
- Palette: `CHART_PALETTE = ["#58a6ff", "#3fb950", "#d29922", "#bc8cff",
  "#f85149", "#39c5cf"]` — cycle for >6 series.
- Always wrap each chart in `chartjs_canvas(id, height=...)` — Chart.js needs
  a fixed-height container with `maintainAspectRatio: False`.
- Charts require `build_head(include_js=True)` (default) — Chart.js is
  inlined into the file, so charts work offline.

### Bar / doughnut

```python
chartjs_script("b1", chartjs_bar(["A", "B"], [("v1", "#3fb950", [1, 2]), ("v2", "#8b949e", [2, 1])], y_title="ms"))
chartjs_script("d1", chartjs_doughnut(["us-east", "eu-west"], [62, 38]))
```

## Mermaid — MANDATORY fullscreen zoom pattern

Large diagrams are unreadable at fixed page width. **Every mermaid diagram in
every report ships with fullscreen zoom by default**: click the diagram (or
its ⛶ button) opens a fullscreen overlay with wheel-to-zoom, drag-to-pan,
double-click reset, and Esc/✕/backdrop-click to close.

```python
from html_lib import mermaid_block, mermaid_init

html.append(mermaid_block("""
flowchart LR
    A[Client] --> B[Router]
    B --> C[Worker 1]
    B --> D[Worker 2]
""", caption="Serving topology"))

# ... later, after ALL diagrams, exactly once:
html.append(mermaid_init())
```

- `mermaid_block()` wraps the `<pre class="mermaid">` in a `diagram-frame`
  with the ⛶ affordance; `mermaid_init()` loads mermaid AND embeds the
  vanilla-JS zoom viewer (event delegation, so it works no matter when or
  whether mermaid finishes rendering).
- **Never hand-roll a bare `<pre class="mermaid">`.** If you must write the
  markup yourself, keep the `diagram-frame` wrapper + one `mermaid_init()`
  per page, or the zoom viewer has nothing to attach to.
- Mermaid is loaded from CDN (`mermaid_init(cdn=True)`, default) — diagrams
  need network. To run fully offline, vendor mermaid's dist folder next to
  the report and pass `mermaid_init(local_path="./assets/mermaid.esm.min.mjs")`.
- Diagrams render via `window.__renderMermaid()` using the theme that
  matches the CURRENT `data-bs-theme` — so the light/dark toggle re-themes
  them automatically. No theme parameter exists (or is needed).

### Diagram types

```
flowchart LR\n  A --> B                    # topology, pipelines (LR/TD)
sequenceDiagram\n  A->>B: req              # request flows
gantt\n  title Plan\n  task :a1, 2026-01-01, 30d   # timelines
pie\n  "hit": 57\n  "miss": 43             # simple shares
stateDiagram-v2\n  [*] --> Active          # state machines
erDiagram\n  CUSTOMER ||--o{ ORDER : places # schemas
```

## Inline SVG (print / no-JS fallback)

`svg_*` functions have zero dependencies and render as plain SVG — use them
when the report will be printed or when JS may be unavailable:

```python
from html_lib import svg_bar_chart_grouped, svg_line_chart, svg_line_chart_time

svg_bar_chart_grouped([("fixed-80", [("tp2", "#3fb950", 288.7), ("g3", "#58a6ff", 135.5)])],
                      y_label="req/s", title="Fixed 80")
svg_line_chart([("tp2", "#3fb950", [(0, 1), (60, 2)]), ("g3", "#58a6ff", [(0, 2), (60, 3)])],
              y_label="req/s", x_fmt=lambda v: f"{v:.0f}s")
svg_line_chart_time([(epoch0, 1.0), (epoch60, 2.0)], [(epoch0, epoch60, "test")], "#3fb950")
```

- Theme-aware: backgrounds/borders/ticks use Bootstrap CSS variables with
  hardcoded fallbacks, so they render correctly in both dark and light pages.
- Missing data returns a muted `no data` paragraph — never raises.
- `x_fmt` defaults to seconds; pass a custom formatter for non-time axes.
