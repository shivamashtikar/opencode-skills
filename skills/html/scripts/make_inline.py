#!/usr/bin/env python3
"""Convert a CDN-mode report into a single self-contained offline file.

Usage:
    python3 make_inline.py report.html                    # -> report_inline.html
    python3 make_inline.py report.html -o final.html       # chosen output path
    python3 make_inline.py report.html -o report.html     # overwrite in place

Replaces the jsDelivr <link>/<script src> tags that build_head(mode="cdn")
emits for Bootstrap CSS/JS and Chart.js with inline <style>/<script> content
read from the skill's vendored assets/ directory. Mermaid stays on CDN — it
is too heavy to inline (~3MB); see references/asset-urls.md.

Typical flow: copy skills/html/template.html, edit it, then run this script
on the finished report to produce the single offline file for delivery.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from html_lib import ASSETS_DIR, CDN

# (exact tag emitted by build_head(mode="cdn"), vendored asset, element kind)
TAGS = [
    (f'<link rel="stylesheet" href="{CDN["bootstrap_css"]}">',
     "bootstrap.min.css", "style"),
    (f'<script src="{CDN["bootstrap_js"]}"></script>',
     "bootstrap.bundle.min.js", "script"),
    (f'<script src="{CDN["chartjs"]}"></script>',
     "chart.umd.min.js", "script"),
]


def inline_assets(html):
    """Return (html with CDN tags swapped for inline assets, [asset names])."""
    changed = []
    for tag, asset, kind in TAGS:
        if tag not in html:
            continue
        content = (ASSETS_DIR / asset).read_text()
        if kind == "style":
            repl = f"<style>\n{content}\n</style>"
        else:
            repl = f"<script>\n{content}\n</script>"
        html = html.replace(tag, repl)
        changed.append(asset)
    return html, changed


def main():
    ap = argparse.ArgumentParser(
        description="Inline the Bootstrap + Chart.js CDN tags of a report "
                    "using the skill's vendored assets (mermaid stays on CDN).")
    ap.add_argument("input", help="report HTML in CDN mode")
    ap.add_argument("-o", "--output",
                    help="output path (default: <stem>_inline.html)")
    args = ap.parse_args()

    src = Path(args.input)
    if not src.is_file():
        sys.exit(f"error: no such file: {src}")
    html = src.read_text()

    new_html, changed = inline_assets(html)
    if not changed:
        print("No CDN asset tags found — file already inline? Nothing to do.")
        return

    out = Path(args.output) if args.output else src.with_name(src.stem + "_inline.html")
    out.write_text(new_html)
    print(f"Inlined: {', '.join(changed)}")
    print(f"Output:  {out.resolve()} ({len(new_html):,} bytes, was {len(html):,})")
    print("Mermaid still loads from CDN — the report needs network for diagrams.")


if __name__ == "__main__":
    main()
