#!/usr/bin/env python3
"""Tests for pdf_lib. Run: python3 skills/pdf/scripts/test_pdf_lib.py

Smoke tests — the helpers come from the proven chat-analyzer PDF generators.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pdf_lib as P  # noqa: E402

_FAILED = []
_PASSED = 0


def check(cond, name):
    global _PASSED
    if cond:
        _PASSED += 1
    else:
        _FAILED.append(name)
        print(f"  FAIL: {name}")


def test_build_styles():
    styles = P.build_styles()
    for key in ("ReportTitle", "ReportSubtitle", "SectionHeading", "SubHeading",
                "BodyTextCustom", "SmallNote", "VerdictText", "BulletItem"):
        check(key in styles, f"build_styles has {key}")
    check(styles["SectionHeading"].fontName == "Helvetica-Bold", "SectionHeading bold")


def test_make_table():
    data = [["H1", "H2"], ["a", "1"], ["b", "2"]]
    t = P.make_table(data, col_widths=[10, 10])
    check(len(t._cellvalues) == 3, "make_table row count")
    check(len(t._cellvalues[0]) == 2, "make_table col count")
    check(t.repeatRows == 1, "make_table repeats header row")
    data_wide = [["A", "B", "C"]] + [[str(i), str(i), str(i)] for i in range(30)]
    tw = P.make_table(data_wide)
    check(len(tw._cellvalues) == 31, "make_table long table keeps rows")


def test_blocks():
    styles = P.build_styles()
    story = []
    P.cover_page(story, styles, "Title", "Subtitle",
                 config_rows=[["k", "v"], ["a", "b"]], verdict_text="verdict text")
    check(len(story) >= 6, "cover_page appends flowables")
    check(any(getattr(f, "text", "") == "Title" for f in story), "cover_page title")
    check(story[-1].__class__.__name__ == "PageBreak", "cover_page ends with PageBreak")

    story2 = []
    P.verdict_box(story2, styles, "box text")
    check(len(story2) == 2, "verdict_box heading + table")


def test_charts(tmp):
    labels = ["a", "b", "c"]
    line = P.mpl_line_chart(labels, [("s1", "#3FB950", [1, 2, 3]),
                                     ("s2", "#58A6FF", [3, None, 1])],
                            title="T", y_label="y", out_path=tmp / "line.png")
    check(line.exists() and line.stat().st_size > 1000, "mpl_line_chart writes PNG")
    bar = P.mpl_bar_chart(labels, [("s1", "#3FB950", [1, 2, 3])],
                           title="T", y_label="y", out_path=tmp / "bar.png")
    check(bar.exists() and bar.stat().st_size > 1000, "mpl_bar_chart writes PNG")

    styles = P.build_styles()
    story = []
    P.chart_pair(story, [("Line", line), ("Bar", bar)], styles)
    check(len(story) == 1 and story[0].__class__.__name__ == "KeepTogether",
          "chart_pair wraps 2-up in KeepTogether")
    story2 = []
    P.chart_pair(story2, [("A", line), ("B", bar), ("C", line)], styles)
    check(len(story2) == 2, "chart_pair groups 3 charts into 2 groups")


def test_full_build(tmp):
    out = tmp / "full.pdf"
    styles = P.build_styles()
    story = []
    P.cover_page(story, styles, "Full Report", "Subtitle",
                 verdict_text="v" * 50)
    line = P.mpl_line_chart(["a", "b", "c"], [("s", "#3FB950", [1, 2, 3])],
                            title="T", y_label="y", out_path=tmp / "fl.png")
    P.chart_pair(story, [("Chart", line)], styles)
    story.append(P.make_table([["H", "V"]] + [[str(i), str(i)] for i in range(60)],
                              col_widths=[12, 12]))
    doc = P.new_doc(out, title="Full Report", author="test")
    doc.build(story, onFirstPage=P.add_page_decorations("Full Report"),
              onLaterPages=P.add_page_decorations("Full Report"))
    data = out.read_bytes()
    check(data[:5] == b"%PDF-", "built file starts with %PDF-")
    check(len(data) > 5000, "built file > 5KB")
    pages = max(data.count(b"/Type /Page"), data.count(b"/Type/Page"))
    check(pages >= 2, f"built file has >=2 pages (got {pages})")


def main():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for name, fn in sorted(globals().items()):
            if name.startswith("test_"):
                print(f"[{name}]")
                if name in ("test_charts", "test_full_build"):
                    fn(tmp)
                else:
                    fn()
    print(f"\n{_PASSED} passed, {len(_FAILED)} failed")
    if _FAILED:
        print("FAILED:", _FAILED)
        sys.exit(1)
    print("ALL TESTS PASS")


if __name__ == "__main__":
    main()
