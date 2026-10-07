#!/usr/bin/env python3
"""html_lib — shared library for building self-contained HTML reports.

Adapted from chat-analyzer's report_lib.py (extracted Sep 2026) and
generalised for the `html` OpenCode skill:

  - Bootstrap 5 provides the component system (cards, tables, alerts, ...),
    inlined by default so every report is a single offline-openable file.
  - Chart.js (inlined) or the zero-dependency svg_* chart functions render
    data charts; svg_* output is theme-aware via CSS variables.
  - Mermaid (CDN only, not vendored — ~3MB) renders diagrams. Every diagram
    ships with a fullscreen zoom viewer (wheel-zoom, drag-pan, double-click
    reset, Esc to close) so large graphs stay readable.
  - Python computes, JS only renders: chartjs_* builders return plain config
    dicts you can tweak before chartjs_script() serialises them.

Behavioural invariants (guarded by scripts/test_html_lib.py):
  - med()/pctile() use the upper-middle index (min(int(n*p), n-1)), matching
    the original report family. Do NOT "fix" these to interpolated medians:
    every published number depends on the exact index arithmetic.
  - winner() returns None on tie or invalid input.
  - Missing data renders "no data" and never raises.

Dependencies: Python standard library only.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------- constants

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

GRID = "#30363d"
TEXT = "#8b949e"
UTC = timezone.utc

BOOTSTRAP_VERSION = "5.3.8"
CHARTJS_VERSION = "4.5.1"
MERMAID_VERSION = "12.1.0"

CDN = {
    "bootstrap_css": f"https://cdn.jsdelivr.net/npm/bootstrap@{BOOTSTRAP_VERSION}/dist/css/bootstrap.min.css",
    "bootstrap_js": f"https://cdn.jsdelivr.net/npm/bootstrap@{BOOTSTRAP_VERSION}/dist/js/bootstrap.bundle.min.js",
    "chartjs": f"https://cdn.jsdelivr.net/npm/chart.js@{CHARTJS_VERSION}/dist/chart.umd.min.js",
}
MERMAID_CDN = f"https://cdn.jsdelivr.net/npm/mermaid@{MERMAID_VERSION}/dist/mermaid.esm.min.mjs"

CHART_PALETTE = ["#58a6ff", "#3fb950", "#d29922", "#bc8cff", "#f85149", "#39c5cf"]

CALLOUT_KINDS = ("info", "warning", "success", "danger", "primary",
                 "secondary", "light", "dark")


# ---------------------------------------------------------------- formatting

def fmt_ms(val):
    try:
        x = float(val)
        return f"{x/1000:.1f}s" if x >= 1000 else f"{x:.0f}ms"
    except (ValueError, TypeError):
        return "N/A"


def fnum(val, nd=1):
    try:
        x = float(val)
        return f"{int(x):,}" if x == int(x) else f"{x:.{nd}f}"
    except (ValueError, TypeError):
        return "N/A"


def pct_str(a, b):
    """% change from a to b."""
    try:
        return f"{(float(b) / float(a) - 1) * 100:+.0f}%"
    except (ValueError, TypeError, ZeroDivisionError):
        return "N/A"


def hhmm(ts):
    return datetime.fromtimestamp(ts, UTC).strftime("%H:%M")


def to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------- stats

def med(vals):
    """Upper-middle median (legacy family semantics); None-safe.

    INVARIANT: sorted(n//2) — upper-middle index. Do not change to an
    interpolated median; published numbers depend on this arithmetic."""
    vals = sorted(v for v in vals if v is not None)
    return vals[len(vals) // 2] if vals else None


def pctile(vals, p):
    """Index percentile: sorted[min(int(n*p), n-1)] (legacy family semantics).

    INVARIANT: index arithmetic, not interpolation."""
    if not vals:
        return None
    vals = sorted(vals)
    return vals[min(int(len(vals) * p), len(vals) - 1)]


def winner(values, lower_is_better=True, threshold=0.05):
    """N-way winner from {key: value}; returns the key that beats ALL others
    by >threshold, else None (tie / invalid / missing input)."""
    try:
        vals = {k: float(v) for k, v in values.items()}
    except (TypeError, ValueError):
        return None
    if any(v != v for v in vals.values()):  # NaN guard
        return None
    for k, v in vals.items():
        others = [x for kk, x in vals.items() if kk != k]
        if not others:
            continue
        if lower_is_better and all(v < o * (1 - threshold) for o in others):
            return k
        if not lower_is_better and all(v > o * (1 + threshold) for o in others):
            return k
    return None


# ---------------------------------------------------------------- windowing

def slice_points(pts, lo, hi):
    return [(t, v) for t, v in pts if lo <= t <= hi]


def window_mean(pts, lo, hi):
    vals = [v for t, v in pts if lo <= t <= hi]
    return sum(vals) / len(vals) if vals else None


def window_max(pts, lo, hi):
    vals = [v for t, v in pts if lo <= t <= hi]
    return max(vals) if vals else None


# ---------------------------------------------------------------- SVG charts
# Zero-JS chart fallback — theme-aware via CSS variables with hardcoded
# fallbacks so they still render standalone.

_NO_DATA = "<p style='color:var(--bs-secondary-color, #8b949e)'>no data</p>"
_SVG_FRAME = ("width:100%;height:auto;"
              "background:var(--bs-body-bg, #0d1117);"
              "border:1px solid var(--bs-border-color, #30363d);border-radius:6px;")
_TICK = "fill:var(--bs-secondary-color, #8b949e)"
_TITLE = "fill:var(--bs-body-color, #c9d1d9)"


def svg_bar_chart_grouped(groups, width=880, height=340, y_label="", title="", y_fmt=None):
    """groups: [(group_label, [(side_label, color, value), ...]), ...] — one cluster per group."""
    y_fmt = y_fmt or (lambda v: f"{v:.0f}")
    if not groups:
        return _NO_DATA
    n_bars = max(len(bars) for _, bars in groups)
    # title and legend each get their own header row (legend below title)
    if title and n_bars > 1:
        height += 18
        legend_y = 34
    else:
        legend_y = 18
    pad_l, pad_r, pad_t, pad_b = 56, 12, 30, 46
    if title and n_bars > 1:
        pad_t += 18
    plot_w = width - pad_l - pad_r
    plot_h = height - pad_t - pad_b

    all_vals = [v for _, bars in groups for _, _, v in bars if v is not None]
    if not all_vals:
        return _NO_DATA
    y_max = max(all_vals) * 1.15 or 1

    def sy(y):
        return pad_t + plot_h - y / y_max * plot_h

    parts = [f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
             f'style="{_SVG_FRAME}">']
    for i in range(5):
        yv = y_max * i / 4
        yy = sy(yv)
        parts.append(f'<line x1="{pad_l}" y1="{yy:.1f}" x2="{width-pad_r}" y2="{yy:.1f}" '
                     f'stroke-width="1" stroke-dasharray="3,3" style="stroke:var(--bs-border-color, {GRID})"/>')
        parts.append(f'<text x="{pad_l-6}" y="{yy+4:.1f}" font-size="11" '
                     f'text-anchor="end" style="{_TICK}">{y_fmt(yv)}</text>')
    n_groups = len(groups)
    group_w = plot_w / n_groups
    bar_w = min(group_w * 0.72 / n_bars, 34)
    for gi, (glabel, bars) in enumerate(groups):
        gx = pad_l + gi * group_w
        cx = gx + group_w / 2
        total_bars_w = bar_w * len(bars)
        for bi, (vlabel, color, val) in enumerate(bars):
            if val is None:
                continue
            bx = cx - total_bars_w / 2 + bi * bar_w
            by = sy(val)
            h = pad_t + plot_h - by
            parts.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bar_w-2:.1f}" '
                         f'height="{max(h,1):.1f}" fill="{color}" rx="2"/>')
            parts.append(f'<text x="{bx + bar_w/2 - 1:.1f}" y="{by-4:.1f}" '
                         f'font-size="10" text-anchor="middle" style="{_TICK}">{val:.0f}</text>')
        parts.append(f'<text x="{cx:.1f}" y="{height-28}" font-size="11" '
                     f'text-anchor="middle" style="{_TICK}">{glabel}</text>')
    if n_bars > 1:
        lx = pad_l + 4
        for _, bars in groups[:1]:
            for vlabel, color, _ in bars:
                parts.append(f'<rect x="{lx}" y="{legend_y}" width="12" height="3" fill="{color}"/>')
                parts.append(f'<text x="{lx+16}" y="{legend_y+5}" font-size="11" style="{_TICK}">{vlabel}</text>')
                lx += 16 + 8 * len(vlabel) + 18
    if title:
        parts.append(f'<text x="{pad_l}" y="16" font-size="13" '
                     f'font-weight="600" style="{_TITLE}">{title}</text>')
    parts.append(f'<text x="6" y="{pad_t + plot_h/2:.0f}" font-size="11" '
                 f'text-anchor="middle" transform="rotate(-90 6 {pad_t + plot_h/2:.0f})" '
                 f'style="{_TICK}">{y_label}</text>')
    parts.append("</svg>")
    return "".join(parts)


def svg_line_chart(series, width=860, height=260, y_label="", y_fmt=None,
                   title="", x_test_windows=None, x_max=None, legend=True,
                   x_fmt=None):
    """series: [(label, color, [(x, y), ...]), ...] — None/NaN y values skipped.

    x_fmt formats the x tick labels; it defaults to seconds ("120s"), which is
    what the original report family expects. Pass it when x is not a time axis."""
    y_fmt = y_fmt or (lambda v: f"{v:.0f}")
    x_fmt = x_fmt or (lambda v: f"{v:.0f}s")
    # title and legend each get their own header row (legend below title)
    if title and legend and len(series) > 1:
        height += 18
        legend_y = 34
    else:
        legend_y = 18
    pad_l, pad_r, pad_t, pad_b = 64, 12, 26, 34
    if title and legend and len(series) > 1:
        pad_t += 18
    plot_w = width - pad_l - pad_r
    plot_h = height - pad_t - pad_b

    all_x = [p[0] for _, _, pts in series for p in pts if p[1] is not None and p[1] == p[1]]
    all_y = [p[1] for _, _, pts in series for p in pts if p[1] is not None and p[1] == p[1]]
    if not all_y:
        return _NO_DATA
    x_min, x_max_actual = (min(all_x), (x_max if x_max else max(all_x)))
    y_min, y_max = 0, max(all_y) * 1.08 or 1

    def sx(x):
        return pad_l + (x - x_min) / max(x_max_actual - x_min, 1e-9) * plot_w

    def sy(y):
        return pad_t + plot_h - y / y_max * plot_h

    parts = [f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
             f'style="{_SVG_FRAME}">']

    # y gridlines + labels (5 ticks)
    for i in range(5):
        yv = y_max * i / 4
        yy = sy(yv)
        parts.append(f'<line x1="{pad_l}" y1="{yy:.1f}" x2="{width-pad_r}" y2="{yy:.1f}" '
                     f'stroke-width="1" stroke-dasharray="3,3" '
                     f'style="stroke:var(--bs-border-color, {GRID})"/>')
        parts.append(f'<text x="{pad_l-6}" y="{yy+4:.1f}" font-size="11" '
                     f'text-anchor="end" style="{_TICK}">{y_fmt(yv)}</text>')

    # x labels (5 ticks, seconds)
    for i in range(5):
        xv = x_min + (x_max_actual - x_min) * i / 4
        parts.append(f'<text x="{sx(xv):.1f}" y="{height-12}" font-size="11" '
                     f'text-anchor="middle" style="{_TICK}">{x_fmt(xv)}</text>')

    # test windows (vertical bands)
    if x_test_windows:
        for (ws, we, name) in x_test_windows:
            parts.append(f'<rect x="{sx(ws):.1f}" y="{pad_t}" width="{max(sx(we)-sx(ws),1):.1f}" '
                         f'height="{plot_h}" fill="#58a6ff" opacity="0.05"/>')

    # series polylines
    for label, color, pts in series:
        d = " ".join(f"{sx(x):.1f},{sy(y):.1f}" for x, y in pts if y is not None and y == y)
        if d:
            parts.append(f'<polyline points="{d}" fill="none" stroke="{color}" stroke-width="1.8"/>')

    if title:
        parts.append(f'<text x="{pad_l}" y="16" font-size="13" font-weight="600" '
                     f'style="{_TITLE}">{title}</text>')
    if legend and len(series) > 1:
        lx = pad_l + 4
        for label, color, _ in series:
            parts.append(f'<rect x="{lx}" y="{legend_y}" width="12" height="3" fill="{color}"/>')
            parts.append(f'<text x="{lx+16}" y="{legend_y+5}" font-size="11" style="{_TICK}">{label}</text>')
            lx += 16 + 8 * len(label) + 18
    parts.append(f'<text x="6" y="{pad_t + plot_h/2:.0f}" font-size="11" text-anchor="middle" '
                 f'transform="rotate(-90 6 {pad_t + plot_h/2:.0f})" style="{_TICK}">{y_label}</text>')
    parts.append("</svg>")
    return "".join(parts)


def svg_line_chart_time(pts, test_windows, color, width=880, height=240, y_label="",
                        title="", y_fmt=None, val_fmt=None):
    """One line over epoch time with shaded test bands; test_windows: [(start, end, label)]."""
    y_fmt = y_fmt or (lambda v: f"{v:.0f}")
    val_fmt = val_fmt or (lambda v: f"{v:.0f}")
    pad_l, pad_r, pad_t, pad_b = 56, 12, 26, 42
    plot_w = width - pad_l - pad_r
    plot_h = height - pad_t - pad_b
    if not pts:
        return _NO_DATA
    pts = [(t, v) for t, v in pts if v == v]  # drop any NaN (idle-gap rate() holes)
    if not pts:
        return _NO_DATA
    x_min = min(w[0] for w in test_windows) if test_windows else pts[0][0]
    x_max = max(w[1] for w in test_windows) if test_windows else pts[-1][0]
    y_max = max(v for _, v in pts) * 1.08 or 1

    def sx(x):
        return pad_l + (x - x_min) / max(x_max - x_min, 1e-9) * plot_w

    def sy(y):
        return pad_t + plot_h - y / y_max * plot_h

    parts = [f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
             f'style="{_SVG_FRAME}">']
    for i in range(5):
        yv = y_max * i / 4
        yy = sy(yv)
        parts.append(f'<line x1="{pad_l}" y1="{yy:.1f}" x2="{width-pad_r}" y2="{yy:.1f}" '
                     f'stroke-width="1" stroke-dasharray="3,3" '
                     f'style="stroke:var(--bs-border-color, {GRID})"/>')
        parts.append(f'<text x="{pad_l-6}" y="{yy+4:.1f}" font-size="11" '
                     f'text-anchor="end" style="{_TICK}">{y_fmt(yv)}</text>')
    for i in range(5):
        xv = x_min + (x_max - x_min) * i / 4
        parts.append(f'<text x="{sx(xv):.1f}" y="{height-12}" font-size="11" '
                     f'text-anchor="middle" style="{_TICK}">{hhmm(xv)}</text>')
    # test windows (vertical bands + label)
    for (ws, we, name) in test_windows:
        parts.append(f'<rect x="{sx(ws):.1f}" y="{pad_t}" width="{max(sx(we)-sx(ws),1):.1f}" '
                     f'height="{plot_h}" fill="#58a6ff" opacity="0.07"/>')
        parts.append(f'<text x="{(sx(ws)+sx(we))/2:.1f}" y="{pad_t+11}" fill="#58a6ff" '
                     f'font-size="8" text-anchor="middle">{name}</text>')
    d = " ".join(f"{sx(t):.1f},{sy(v):.1f}" for t, v in pts)
    parts.append(f'<polyline points="{d}" fill="none" stroke="{color}" stroke-width="1.8"/>')
    # last-value annotation
    parts.append(f'<text x="{width-pad_r}" y="{sy(pts[-1][1])-5:.1f}" fill="{color}" '
                 f'font-size="10" text-anchor="end" font-weight="600">{val_fmt(pts[-1][1])}</text>')
    if title:
        parts.append(f'<text x="{pad_l}" y="16" font-size="13" font-weight="600" '
                     f'style="{_TITLE}">{title}</text>')
    parts.append(f'<text x="6" y="{pad_t + plot_h/2:.0f}" font-size="11" text-anchor="middle" '
                 f'transform="rotate(-90 6 {pad_t + plot_h/2:.0f})" style="{_TICK}">{y_label}</text>')
    parts.append("</svg>")
    return "".join(parts)


# ---------------------------------------------------------------- HTML head

def _read_asset(name):
    try:
        return (ASSETS_DIR / name).read_text()
    except OSError:
        return None


_REPORT_CSS = """
/* html_lib report layer on top of Bootstrap */
.subtitle { color: var(--bs-secondary-color); font-size: .95rem; margin-bottom: 1.5rem; }
.stat-value { font-variant-numeric: tabular-nums; }
.num { text-align: right; font-variant-numeric: tabular-nums; }
.chart-wrap { position: relative; }

/* Light/dark theme toggle (on by default) */
.theme-toggle { position: fixed; top: 1rem; right: 1rem; z-index: 1030; opacity: .8; }

/* Mermaid diagrams + fullscreen zoom viewer */
.diagram-frame { position: relative; }
.diagram-frame .mermaid {
  display: flex; justify-content: center; overflow-x: auto; cursor: zoom-in;
  padding: 1.25rem; margin: 0;
  background: var(--bs-tertiary-bg);
  border: 1px solid var(--bs-border-color); border-radius: .5rem;
}
.diagram-expand { position: absolute; top: .5rem; right: .5rem; z-index: 5; opacity: .7; }
.diagram-viewer {
  position: fixed; inset: 0; z-index: 2050;
  background: rgba(0, 0, 0, .88);
  display: flex; align-items: center; justify-content: center;
}
.diagram-viewer .diagram-stage {
  width: 100%; height: 100%; padding: 3rem 2.5rem;
  display: flex; align-items: center; justify-content: center;
  transform-origin: center center; cursor: grab;
}
.diagram-viewer .diagram-stage svg { max-width: 100%; max-height: 100%; }
.diagram-viewer .diagram-close { position: absolute; top: 1rem; right: 1rem; }

@media print {
  .theme-toggle, .diagram-expand, .diagram-viewer { display: none !important; }
}
"""


# Runs first in <head>: restores the stored theme before first paint, so a
# light-mode reader never sees a dark flash (and vice versa).
_THEME_RESTORE = """<script>
(function () {
  try {
    var t = localStorage.getItem("html-lib-theme");
    if (t === "light" || t === "dark") {
      document.documentElement.setAttribute("data-bs-theme", t);
    }
  } catch (e) {}
})();
</script>"""


# Theme toggle handler: flips data-bs-theme, persists the choice, re-themes
# Chart.js charts (registered by chartjs_script) and re-renders mermaid
# diagrams (via window.__renderMermaid from mermaid_init).
# NOTE: chartColors() must stay in sync with chartjs_defaults() above.
_TOGGLE_SCRIPT = """(function () {
  "use strict";
  var STORE_KEY = "html-lib-theme";
  function isDark() {
    return document.documentElement.getAttribute("data-bs-theme") !== "light";
  }
  function chartColors(dark) {
    return dark ? { tick: "#adb5bd", grid: "rgba(173,181,197,.15)" }
                : { tick: "#495057", grid: "rgba(0,0,0,.08)" };
  }
  function rethemeCharts() {
    (window.__charts || []).forEach(function (c) {
      try {
        var col = chartColors(isDark());
        var scales = c.options && c.options.scales;
        if (scales) {
          Object.keys(scales).forEach(function (k) {
            var ax = scales[k];
            if (ax.ticks) ax.ticks.color = col.tick;
            if (ax.grid) ax.grid.color = col.grid;
          });
        }
        var lg = c.options && c.options.plugins && c.options.plugins.legend;
        if (lg && lg.labels) lg.labels.color = col.tick;
        c.update();
      } catch (e) { /* chart configs vary; skip on shape mismatch */ }
    });
  }
  window.__setTheme = function (t) {
    document.documentElement.setAttribute("data-bs-theme", t);
    try { localStorage.setItem(STORE_KEY, t); } catch (e) {}
    rethemeCharts();
    if (window.__renderMermaid) window.__renderMermaid();
  };
  document.addEventListener("click", function (e) {
    if (!e.target.closest) return;
    if (!e.target.closest(".theme-toggle")) return;
    window.__setTheme(isDark() ? "light" : "dark");
    var label = document.getElementById("theme-toggle");
    if (label) label.textContent = isDark() ? "\\u{1F313}" : "\\u2600\\uFE0F";
  });
})();
"""


def build_head(title, theme="dark", mode="inline", include_js=True, extra_css="", width=1120,
               theme_toggle=True):
    """<!DOCTYPE> through the container open — Bootstrap 5 based skeleton.

    theme: "dark" (default) or "light" — sets Bootstrap's data-bs-theme.
    mode: "inline" (default) inlines the vendored Bootstrap CSS + JS from the
          skill's assets/ dir so the report is a single offline-openable file;
          "cdn" links jsDelivr instead.
    include_js: inline/link bootstrap.bundle.min.js + chart.umd.min.js too.
                Set False for pure-static reports (then skip Chart.js usage).
    extra_css: appended verbatim after the report CSS.
    theme_toggle: emit the light/dark toggle button + persistence script
                (default). Charts made via chartjs_script() and mermaid
                diagrams re-theme when it is clicked.
    """
    if theme not in ("dark", "light"):
        theme = "dark"
    if mode == "inline":
        css = _read_asset("bootstrap.min.css")
        if css is None:  # vendored asset missing -> CDN fallback
            css_block = (f'<link rel="stylesheet" href="{CDN["bootstrap_css"]}">\n'
                         f'<!-- html_lib: vendored bootstrap.min.css not found, using CDN -->')
        else:
            css_block = f"<style>\n{css}\n</style>"
        js_block = ""
        if include_js:
            js_parts = []
            for name, url in (("bootstrap.bundle.min.js", CDN["bootstrap_js"]),
                              ("chart.umd.min.js", CDN["chartjs"])):
                content = _read_asset(name)
                js_parts.append(f'<script src="{url}"></script>' if content is None
                                else f"<script>\n{content}\n</script>")
            js_block = "\n".join(js_parts)
    elif mode == "cdn":
        css_block = f'<link rel="stylesheet" href="{CDN["bootstrap_css"]}">'
        js_block = ""
        if include_js:
            js_block = (f'<script src="{CDN["bootstrap_js"]}"></script>\n'
                        f'<script src="{CDN["chartjs"]}"></script>')
    else:
        raise ValueError(f"mode must be 'inline' or 'cdn', got {mode!r}")

    extra = f"{extra_css}\n" if extra_css else ""
    restore = _THEME_RESTORE + "\n" if theme_toggle else ""
    toggle_js = f"<script>\n{_TOGGLE_SCRIPT}</script>\n" if theme_toggle else ""
    toggle_btn = ('<button type="button" id="theme-toggle" '
                  'class="btn btn-sm btn-outline-secondary theme-toggle" '
                  'title="Toggle light/dark theme" aria-label="Toggle light/dark theme">🌓</button>\n'
                  if theme_toggle else "")
    return f"""<!DOCTYPE html>
<html lang="en" data-bs-theme="{theme}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
{restore}{css_block}
<style>
{_REPORT_CSS}
{extra}</style>
{js_block}
{toggle_js}</head>
<body>
{toggle_btn}<div class="container report-container" style="max-width:{width}px">
"""


def build_foot(text=""):
    """Close the container; emits a footer first when text is given."""
    foot = (f'<footer class="mt-5 pt-3 border-top small text-secondary">{text}</footer>'
            if text else "")
    return f"{foot}</div></body></html>"


# ---------------------------------------------------------------- components

def stat_card(label, value, sub="", accent=None):
    """One Bootstrap stat card. Place inside a .col (or use stat_cards_row)."""
    style = f' style="border-left:3px solid {accent}"' if accent else ""
    sub_html = f'<div class="small text-secondary">{sub}</div>' if sub else ""
    return (f'<div class="card h-100"{style}><div class="card-body py-3">'
            f'<div class="text-secondary small text-uppercase">{label}</div>'
            f'<div class="stat-value fs-3 fw-semibold">{value}</div>'
            f'{sub_html}</div></div>')


def stat_cards_row(items, cols=None):
    """items: [(label, value, sub, accent), ...] -> responsive card grid."""
    if not items:
        return ""
    cols = cols or min(len(items), 4)
    out = [f'<div class="row row-cols-1 row-cols-md-{cols} g-3 my-1">']
    for label, value, sub, accent in items:
        out.append(f'<div class="col">{stat_card(label, value, sub, accent)}</div>')
    out.append("</div>")
    return "".join(out)


def callout(kind, html):
    """Bootstrap alert callout. kind: info|warning|success|danger|primary|secondary|light|dark."""
    if kind not in CALLOUT_KINDS:
        kind = "info"
    return f'<div class="alert alert-{kind} mb-3" role="alert">{html}</div>'


def table_html(headers, rows, caption=None, row_classes=None,
               table_class="table table-striped table-hover align-middle"):
    """Striped Bootstrap data table. Convention (matches pdf_lib.make_table):
    first column left-aligned, all others right-aligned with tabular numerals."""
    cap = f'<caption class="text-secondary">{caption}</caption>' if caption else ""
    head = "<tr>" + "".join(f'<th scope="col">{h}</th>' for h in headers) + "</tr>"
    body = []
    num_cls = ' class="num"'
    for i, r in enumerate(rows):
        cls = f' class="{row_classes[i]}"' if row_classes and row_classes[i] else ""
        cells = "".join(f"<td{num_cls if j else ''}>{c}</td>" for j, c in enumerate(r))
        body.append(f"<tr{cls}>{cells}</tr>")
    return (f'<div class="table-responsive"><table class="{table_class}">{cap}'
            f'<thead>{head}</thead><tbody>' + "".join(body) + "</tbody></table></div>")


def section_heading(n, text):
    """Numbered section heading (chat-analyzer report convention)."""
    return (f'<h2 class="mt-4 mb-3"><span class="badge text-bg-primary rounded-pill me-2">{n}</span>'
            f'{text}</h2>')


def verdict(html, title="Verdict"):
    """Accent-bordered verdict box (chat-analyzer report convention)."""
    return (f'<div class="border border-primary border-3 border-start rounded-3 p-3 my-4 bg-body-tertiary">'
            f'<h2 class="h5 mb-2">{title}</h2>{html}</div>')


# ---------------------------------------------------------------- Chart.js

def chartjs_canvas(chart_id, height=280):
    """Canvas wrapper — fixed-height responsive container for one chart."""
    return (f'<div class="chart-wrap mb-4" style="height:{height}px">'
            f'<canvas id="{chart_id}"></canvas></div>')


def chartjs_script(chart_id, config):
    """Render one Chart.js chart from a config dict (see chartjs_line/bar/doughnut).
    The chart instance is registered in window.__charts so the theme toggle
    can re-theme it (hand-written `new Chart(...)` calls are not registered)."""
    cfg = json.dumps(config, ensure_ascii=False)
    return (f'<script>\nwindow.__charts = window.__charts || [];\n'
            f'window.__charts.push(new Chart(document.getElementById({json.dumps(chart_id)}), {cfg}));\n'
            f'</script>')


def chartjs_defaults(theme="dark", animations=False):
    """Global Chart.js theming — emit once, after Chart.js is loaded and before
    any chartjs_script(). animations=False keeps print/PDF export faithful."""
    color = "#adb5bd" if theme == "dark" else "#495057"
    border = "rgba(173,181,197,.15)" if theme == "dark" else "rgba(0,0,0,.08)"
    anim = "true" if animations else "false"
    font = "-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif"
    return (f'<script>\nChart.defaults.color = {json.dumps(color)};\n'
            f'Chart.defaults.borderColor = {json.dumps(border)};\n'
            f'Chart.defaults.animation = {anim};\n'
            f'Chart.defaults.font.family = {json.dumps(font)};\n</script>')


def _datasets(datasets):
    out = []
    for i, (label, color, values) in enumerate(datasets):
        out.append({"label": label, "data": values,
                    "backgroundColor": color or CHART_PALETTE[i % len(CHART_PALETTE)],
                    "borderColor": color or CHART_PALETTE[i % len(CHART_PALETTE)]})
    return out


def chartjs_line(labels, datasets, y_title="", x_title="", stacked=False, fill=False):
    """labels: ["W1", ...]; datasets: [(label, color, [v, ...]), ...] -> config dict."""
    ds = [{"label": d[0], "data": d[2], "borderColor": d[1], "backgroundColor": d[1],
           "tension": 0.25, "pointRadius": 2, "fill": fill} for d in datasets]
    return {"type": "line",
            "data": {"labels": [str(x) for x in labels], "datasets": ds},
            "options": {"responsive": True, "maintainAspectRatio": False,
                        "plugins": {"legend": {"position": "top"}},
                        "scales": {"x": {"stacked": stacked,
                                         "title": {"display": bool(x_title), "text": x_title}},
                                   "y": {"stacked": stacked, "beginAtZero": True,
                                         "title": {"display": bool(y_title), "text": y_title}}}}}


def chartjs_bar(labels, datasets, y_title="", x_title="", stacked=False):
    """labels: ["A", ...]; datasets: [(label, color, [v, ...]), ...] -> config dict."""
    return {"type": "bar",
            "data": {"labels": [str(x) for x in labels], "datasets": _datasets(datasets)},
            "options": {"responsive": True, "maintainAspectRatio": False,
                        "plugins": {"legend": {"position": "top"}},
                        "scales": {"x": {"stacked": stacked,
                                         "title": {"display": bool(x_title), "text": x_title}},
                                   "y": {"stacked": stacked, "beginAtZero": True,
                                         "title": {"display": bool(y_title), "text": y_title}}}}}


def chartjs_doughnut(labels, values, colors=None):
    """Doughnut/pie chart config; values: [v, ...]."""
    colors = colors or [CHART_PALETTE[i % len(CHART_PALETTE)] for i in range(len(values))]
    return {"type": "doughnut",
            "data": {"labels": [str(x) for x in labels],
                     "datasets": [{"data": values, "backgroundColor": colors}]},
            "options": {"responsive": True, "maintainAspectRatio": False,
                        "cutout": "62%",
                        "plugins": {"legend": {"position": "right"}}}}


# ---------------------------------------------------------------- Mermaid

def mermaid_block(definition, caption=""):
    """Diagram wrapped for the fullscreen zoom viewer.

    ALWAYS use this (plus one mermaid_init() per page) — never a bare
    <pre class="mermaid">, which loses fullscreen zoom and readability
    for large graphs."""
    cap = f'<figcaption class="small text-secondary text-center mt-1">{caption}</figcaption>' \
        if caption else ""
    return (f'<figure class="diagram-frame mb-4">'
            f'<button type="button" class="diagram-expand btn btn-sm btn-outline-secondary" '
            f'title="Fullscreen — wheel to zoom, drag to pan, Esc to close">⛶</button>'
            f'<pre class="mermaid">{definition}</pre>{cap}</figure>')


# Vanilla-JS fullscreen zoom viewer. Event delegation on document means it
# works regardless of when (or whether) mermaid finishes rendering its SVGs.
_VIEWER_SCRIPT = """<script>
(function () {
  "use strict";
  var overlay = null, stage = null, scale = 1, tx = 0, ty = 0, drag = null;

  function apply() {
    if (stage) stage.style.transform = "translate(" + tx + "px," + ty + "px) scale(" + scale + ")";
  }
  function reset() { scale = 1; tx = 0; ty = 0; apply(); }
  function close() {
    if (overlay) { overlay.remove(); overlay = null; stage = null; }
    document.body.style.overflow = "";
  }
  function open(svg) {
    close();
    overlay = document.createElement("div");
    overlay.className = "diagram-viewer";
    stage = document.createElement("div");
    stage.className = "diagram-stage";
    var closeBtn = document.createElement("button");
    closeBtn.type = "button";
    closeBtn.className = "diagram-close btn-close btn-close-white";
    closeBtn.setAttribute("aria-label", "Close");
    closeBtn.onclick = close;
    var clone = svg.cloneNode(true);
    clone.removeAttribute("id");
    clone.style.maxWidth = "100%";
    clone.style.maxHeight = "100%";
    stage.appendChild(clone);
    overlay.appendChild(stage);
    overlay.appendChild(closeBtn);
    document.body.appendChild(overlay);
    document.body.style.overflow = "hidden";
    reset();
    overlay.onclick = function (e) { if (e.target === overlay) close(); };
  }

  document.addEventListener("click", function (e) {
    if (!e.target.closest) return;
    var frame = e.target.closest(".diagram-frame");
    if (!frame) return;
    var svg = frame.querySelector("svg");
    if (svg) open(svg);
  });

  document.addEventListener("dblclick", function (e) {
    if (overlay && e.target.closest && e.target.closest(".diagram-viewer")) reset();
  });

  document.addEventListener("wheel", function (e) {
    if (!overlay) return;
    e.preventDefault();
    scale = Math.min(12, Math.max(0.2, scale * (e.deltaY < 0 ? 1.15 : 1 / 1.15)));
    apply();
  }, { passive: false });

  document.addEventListener("mousedown", function (e) {
    if (overlay) drag = { x: e.clientX, y: e.clientY, tx: tx, ty: ty };
  });
  document.addEventListener("mousemove", function (e) {
    if (!drag || !overlay) return;
    tx = drag.tx + (e.clientX - drag.x);
    ty = drag.ty + (e.clientY - drag.y);
    apply();
  });
  document.addEventListener("mouseup", function () { drag = null; });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") close();
  });
})();
</script>"""


# Mermaid module: renders on demand (startOnLoad: false) so the light/dark
# toggle can re-render diagrams with the matching mermaid theme. Original
# sources are captured into data-src BEFORE the first render because mermaid
# replaces the <pre> content with an <svg> and marks it data-processed.
# Module scripts are deferred, so the top-level __renderMermaid() call runs
# after the whole DOM (all diagrams) exists.
_MERMAID_MODULE = """<script type="module">
import mermaid from "__MERMAID_SRC__";
window.__mermaid = mermaid;
window.__captureMermaidSources = function () {
  document.querySelectorAll("pre.mermaid").forEach(function (el) {
    if (!el.dataset.src && !el.querySelector("svg")) el.dataset.src = el.textContent;
  });
};
window.__restoreMermaidSources = function () {
  document.querySelectorAll("pre.mermaid").forEach(function (el) {
    if (el.dataset.src) {
      el.textContent = el.dataset.src;
      el.removeAttribute("data-processed");
    }
  });
};
window.__renderMermaid = function () {
  window.__restoreMermaidSources();
  window.__captureMermaidSources();
  var t = document.documentElement.getAttribute("data-bs-theme") === "light" ? "default" : "dark";
  mermaid.initialize({ startOnLoad: false, theme: t });
  mermaid.run({ querySelector: "pre.mermaid" }).catch(function () {});
};
window.__renderMermaid();
</script>"""


def mermaid_init(cdn=True, local_path=None):
    """Mermaid loader + fullscreen zoom viewer. Emit exactly once per page,
    after all mermaid_block() diagrams.

    Diagrams (re-)render via window.__renderMermaid() using the theme that
    matches the CURRENT data-bs-theme, so the light/dark toggle re-themes
    them automatically (no theme parameter anymore).
    local_path: URL/path to a locally vendored mermaid.esm.min.mjs (the whole
    dist/ folder must be present); overrides cdn."""
    if local_path:
        src = str(local_path)
    elif cdn:
        src = MERMAID_CDN
    else:
        raise ValueError("mermaid_init: pass local_path or cdn=True")
    return _MERMAID_MODULE.replace("__MERMAID_SRC__", src) + "\n" + _VIEWER_SCRIPT
