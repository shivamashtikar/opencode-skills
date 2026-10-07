#!/usr/bin/env python3
"""Tests for html_lib. Run: python3 skills/html/scripts/test_html_lib.py

Adapted from chat-analyzer's test_report_lib.py — the stats invariants are
pinned there and must not change behaviour.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import html_lib as H  # noqa: E402

_FAILED = []
_PASSED = 0


def check(cond, name):
    global _PASSED
    if cond:
        _PASSED += 1
    else:
        _FAILED.append(name)
        print(f"  FAIL: {name}")


# ---------------------------------------------------------------- formatting

def test_fmt():
    check(H.fmt_ms(232) == "232ms", "fmt_ms 232 -> 232ms")
    check(H.fmt_ms(4595) == "4.6s", "fmt_ms 4595 -> 4.6s")
    check(H.fmt_ms("x") == "N/A", "fmt_ms invalid -> N/A")
    check(H.fnum(4595) == "4,595", "fnum thousands separator")
    check(H.fnum(3.14159, 2) == "3.14", "fnum nd=2")
    check(H.fnum(None) == "N/A", "fnum invalid -> N/A")
    check(H.pct_str(100, 150) == "+50%", "pct_str +50%")
    check(H.pct_str(150, 100) == "-33%", "pct_str -33%")
    check(H.pct_str(0, 5) == "N/A", "pct_str div-by-zero -> N/A")
    check(H.to_float("1.5") == 1.5, "to_float parses")
    check(H.to_float("x") is None, "to_float invalid -> None")
    check(H.hhmm(0) == "00:00", "hhmm epoch -> 00:00 UTC")


# ---------------------------------------------------------------- stats
# Invariants pinned from the original report family — do NOT "fix" these.

def test_stats_invariants():
    check(H.med([]) is None, "med([]) is None")
    check(H.med([1, 2]) == 2, "med([1,2]) == 2 (upper-middle)")
    check(H.med([3, 1, 2]) == 2, "med sorts first")
    check(H.med([1, None, 2]) == 2, "med drops None")
    check(H.pctile(list(range(1, 11)), 0.5) == 6,
          "pctile(1..10, 0.5) == 6 (index arithmetic, not interpolation)")
    check(H.pctile([], 0.5) is None, "pctile([]) is None")
    check(H.pctile([5], 0.9) == 5, "pctile clamps to last index")
    check(H.winner({"a": 90, "b": 100}) == "a", "winner lower-is-better")
    check(H.winner({"a": 96, "b": 100}) is None, "winner within threshold -> None (tie)")
    check(H.winner({"a": 90, "b": 100}, lower_is_better=False) == "b", "winner higher-is-better")
    check(H.winner({"a": "x", "b": "1"}) is None, "winner invalid -> None")
    check(H.winner({"a": float("nan"), "b": 1}) is None, "winner NaN -> None")
    check(H.winner({"a": 100, "b": 80, "c": 90}) == "b", "winner must beat ALL others")


# ---------------------------------------------------------------- windowing

def test_windowing():
    pts = [(0, 1.0), (1, 2.0), (2, 3.0), (3, 4.0)]
    check(H.slice_points(pts, 1, 2) == [(1, 2.0), (2, 3.0)], "slice_points inclusive")
    check(H.window_mean(pts, 0, 1) == 1.5, "window_mean")
    check(H.window_max(pts, 0, 3) == 4.0, "window_max")
    check(H.window_mean(pts, 10, 20) is None, "window_mean empty -> None")


# ---------------------------------------------------------------- SVG charts

def test_svg_charts():
    nd = "no data"
    check(nd in H.svg_bar_chart_grouped([]), "bar chart empty -> no data")
    check(nd in H.svg_line_chart([]), "line chart empty -> no data")
    check(nd in H.svg_line_chart_time([], [], "#3fb950"), "time chart empty -> no data")

    g = [("g1", [("a", "#58a6ff", 10), ("b", "#3fb950", 20)]), ("g2", [("a", "#58a6ff", 5)])]
    svg = H.svg_bar_chart_grouped(g, title="T")
    check("<svg" in svg and 'viewBox="0 0 880 358"' in svg, "bar chart svg + title grows height")
    check("var(--bs-body-bg" in svg, "bar chart theme-aware background")

    line = H.svg_line_chart([("s1", "#3fb950", [(0, 1), (1, 2), (2, None)])],
                           x_test_windows=[(0, 1, "w1")])
    check("<polyline" in line, "line chart draws polyline")
    check("#58a6ff" in line, "line chart test window band")

    t = H.svg_line_chart_time([(0, 1.0), (60, 2.0)], [(0, 60, "w")], "#58a6ff")
    check("00:0" in t, "time chart HH:MM ticks")


# ---------------------------------------------------------------- build_head

def test_build_head():
    h = H.build_head("T", mode="inline")
    check('data-bs-theme="dark"' in h, "build_head default dark theme")
    check("Bootstrap  v5.3.8" in h, "build_head inline inlines Bootstrap CSS")
    check("Chart.js v4.5.1" in h, "build_head inline inlines Chart.js")
    check("Bootstrap v5.3.8" in h, "build_head inline inlines Bootstrap JS")
    check(".diagram-frame" in h, "build_head includes report CSS")
    check(h.rstrip().endswith('<div class="container report-container" style="max-width:1120px">'),
          "build_head opens the container")

    # theme toggle is on by default
    check('id="theme-toggle"' in h, "build_head emits toggle button")
    check('localStorage.getItem("html-lib-theme")' in h, "build_head emits theme restore script")
    check("window.__setTheme" in h, "build_head emits toggle handler")
    check(".theme-toggle {" in h, "build_head styles the toggle")

    h2 = H.build_head("T", theme="light", mode="cdn", include_js=False, extra_css=".x{color:red}")
    check('data-bs-theme="light"' in h2, "build_head light theme")
    check(f'href="{H.CDN["bootstrap_css"]}"' in h2, "build_head cdn css link")
    check("cdn.jsdelivr" in h2 and "chart.umd" not in h2.split("</style>")[-1],
          "build_head include_js=False skips JS")
    check(".x{color:red}" in h2, "build_head appends extra_css")

    h3 = H.build_head("T", mode="cdn", theme_toggle=False)
    check('id="theme-toggle"' not in h3 and "html-lib-theme" not in h3
          and "window.__setTheme" not in h3, "build_head theme_toggle=False omits toggle")

    try:
        H.build_head("T", mode="bogus")
        check(False, "build_head rejects bad mode")
    except ValueError:
        check(True, "build_head rejects bad mode")

    foot = H.build_foot("by test")
    check(foot == '<footer class="mt-5 pt-3 border-top small text-secondary">by test</footer>'
          "</div></body></html>", "build_foot shape")
    check(H.build_foot() == "</div></body></html>", "build_foot bare close")


# ---------------------------------------------------------------- components

def test_components():
    c = H.stat_card("Label", "42", "sub text", "#58a6ff")
    check("card h-100" in c and 'border-left:3px solid #58a6ff' in c and "42" in c,
          "stat_card markup + accent")

    row = H.stat_cards_row([("a", "1", "", None), ("b", "2", "", None)])
    check('class="row row-cols-1 row-cols-md-2 g-3 my-1"' in row and row.count("<div class=\"col\">") == 2,
          "stat_cards_row grid")
    check(H.stat_cards_row([]) == "", "stat_cards_row empty")

    check(H.callout("warning", "careful") == '<div class="alert alert-warning mb-3" '
          'role="alert">careful</div>', "callout alert markup")
    check("alert-info" in H.callout("bogus", "x"), "callout unknown kind -> info")

    t = H.table_html(["A", "B"], [["k", "1"], ["j", "2"]], caption="cap",
                     row_classes=["", "table-success"])
    check("table table-striped table-hover align-middle" in t, "table_html striped")
    check(t.count('class="num"') == 2, "table_html numeric cells right-aligned")
    check('<td>k</td>' in t, "table_html first column not num-classed")
    check("table-success" in t and "<caption" in t, "table_html row_classes + caption")

    check('badge text-bg-primary rounded-pill me-2">3</span>Detail' in H.section_heading(3, "Detail"),
          "section_heading numbered badge")

    v = H.verdict("WIN", title="Outcome")
    check("border-primary" in v and "Outcome" in v and "WIN" in v, "verdict box")


# ---------------------------------------------------------------- Chart.js

def test_chartjs():
    check('id="c1"' in H.chartjs_canvas("c1") and 'style="height:280px"' in H.chartjs_canvas("c1"),
          "chartjs_canvas")
    check('style="height:120px"' in H.chartjs_canvas("c2", height=120), "chartjs_canvas height")

    cfg = H.chartjs_line(["a", "b"], [("s", "#fff", [1, 2])], y_title="rps", x_title="wk")
    check(cfg["type"] == "line", "chartjs_line type")
    check(cfg["data"]["labels"] == ["a", "b"], "chartjs_line labels coerced to str")
    check(cfg["data"]["datasets"][0]["borderColor"] == "#fff", "chartjs_line dataset color")
    check(cfg["options"]["scales"]["y"]["title"]["text"] == "rps", "chartjs_line y title")

    cfgb = H.chartjs_bar(["a"], [("s", "#0f0", [3])], stacked=True)
    check(cfgb["type"] == "bar" and cfgb["options"]["scales"]["x"]["stacked"] is True,
          "chartjs_bar type + stacked")

    cfgd = H.chartjs_doughnut(["x", "y"], [1, 2])
    check(cfgd["type"] == "doughnut" and len(cfgd["data"]["datasets"][0]["backgroundColor"]) == 2,
          "chartjs_doughnut palette cycle")

    # emitted script round-trips the config through JSON, and registers the
    # instance so the theme toggle can re-theme it
    s = H.chartjs_script("c1", cfg)
    check("window.__charts = window.__charts || [];" in s
          and "window.__charts.push(new Chart(" in s, "chartjs_script registers instance")
    m = re.search(r'window\.__charts\.push\(new Chart\(document\.getElementById\("c1"\), '
                  r'(\{.*\})\)\);\s*</script>', s, re.S)
    check(m is not None, "chartjs_script shape")
    if m:
        check(json.loads(m.group(1)) == cfg, "chartjs_script JSON round-trip")

    d = H.chartjs_defaults(theme="light")
    check("#495057" in d and "false" in d, "chartjs_defaults light + animations off")


# ---------------------------------------------------------------- Mermaid

def test_mermaid():
    b = H.mermaid_block("flowchart LR\n  A --> B")
    check('class="diagram-frame' in b, "mermaid_block diagram-frame wrapper")
    check('class="mermaid"' in b and "flowchart LR" in b, "mermaid_block pre content")
    check("diagram-expand" in b and "⛶" in b, "mermaid_block expand affordance")
    check("caption" in H.mermaid_block("g", caption="cap note"), "mermaid_block caption")

    init = H.mermaid_init()
    check("mermaid.esm.min.mjs" in init, "mermaid_init CDN import")
    check("startOnLoad: false" in init, "mermaid_init renders on demand (not startOnLoad)")
    check("__renderMermaid" in init and "__captureMermaidSources" in init,
          "mermaid_init exposes render + source capture")
    check('=== "light" ? "default" : "dark"' in init,
          "mermaid_init theme follows current data-bs-theme")
    check("data-processed" in init, "mermaid_init resets processed state for re-render")
    check("diagram-viewer" in init and "wheel" in init and "Escape" in init,
          "mermaid_init embeds fullscreen zoom viewer")
    check("./vendored/mermaid.esm.min.mjs" in H.mermaid_init(local_path="./vendored/mermaid.esm.min.mjs"),
          "mermaid_init local_path wins")
    try:
        H.mermaid_init(cdn=False)
        check(False, "mermaid_init cdn=False without local_path raises")
    except ValueError:
        check(True, "mermaid_init cdn=False without local_path raises")

    # hand-written diagrams must still be able to get the wrapper: the viewer
    # script targets .diagram-frame, so the pattern is composable.
    check(".diagram-frame" in H.mermaid_init(), "viewer targets .diagram-frame via delegation")


def main():
    tests = [(k, v) for k, v in sorted(globals().items()) if k.startswith("test_")]
    for name, fn in tests:
        print(f"[{name}]")
        fn()
    print(f"\n{_PASSED} passed, {len(_FAILED)} failed")
    if _FAILED:
        print("FAILED:", _FAILED)
        sys.exit(1)
    print("ALL TESTS PASS")


if __name__ == "__main__":
    main()
