# Asset URLs — pinned versions and re-vendor commands

`html_lib.build_head(mode="inline")` reads vendored files from this skill's
`assets/` directory. Keep versions pinned; re-vendor deliberately.

## Current pins

| Asset | Version | Vendored at |
|---|---|---|
| Bootstrap CSS | 5.3.8 | `assets/bootstrap.min.css` (232 KB) |
| Bootstrap JS bundle | 5.3.8 | `assets/bootstrap.bundle.min.js` (80 KB) |
| Chart.js UMD | 4.5.1 | `assets/chart.umd.min.js` (209 KB) |
| Mermaid ESM | 12.1.0 | **not vendored** (CDN only, ~3 MB) |

## CDN URLs (mode="cdn" and the inline-missing fallback)

```text
https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css
https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js
https://cdn.jsdelivr.net/npm/chart.js@4.5.1/dist/chart.umd.min.js
https://cdn.jsdelivr.net/npm/mermaid@12.1.0/dist/mermaid.esm.min.mjs   (module import)
```

## Re-vendor (update a pin)

```bash
cd skills/html/assets
curl -sSL -o bootstrap.min.css        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css"
curl -sSL -o bootstrap.bundle.min.js  "https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js"
# for a Chart.js bump, resolve the new 4.x version first:
#   curl -s "https://data.jsdelivr.com/v1/packages/npm/chart.js/resolved?specifier=4"
curl -sSL -o chart.umd.min.js         "https://cdn.jsdelivr.net/npm/chart.js@4.5.1/dist/chart.umd.min.js"
```

Then update `BOOTSTRAP_VERSION` / `CHARTJS_VERSION` / the `CDN` dict in
`scripts/html_lib.py`, update the table above, and re-run
`python3 scripts/test_html_lib.py`.

## SRI integrity hashes (optional, for CDN mode)

When linking from CDN in security-sensitive contexts, add
`integrity="sha384-..." crossorigin="anonymous"`. Generate per file:

```bash
openssl dgst -sha384 -binary bootstrap.min.css | openssl base64 -A
```

If the hash differs between CDNs for the same version, do not use that file.

## Mermaid — why not vendored

The ESM build pulls lazy chunks and the whole package is ~3 MB — too heavy to
inline into every report. Options, in order:

1. **CDN (default)** — `mermaid_init(cdn=True)`; diagrams need network.
2. **Local copy for offline reports** — vendor mermaid's `dist/` folder next
   to the report and pass `mermaid_init(local_path="./assets/mermaid.esm.min.mjs")`.
   The entire dist folder must be present (chunk imports are relative).

## What inlining costs

A single inline-mode report is ~500 KB–1 MB (Bootstrap + Chart.js + content).
That is the trade for a file that opens fully styled anywhere, offline —
keep it. If a report must stay small, use `mode="cdn"` and accept the
network requirement.

For reports started from `template.html` (CDN mode), finish with
`scripts/make_inline.py report.html` — it swaps the jsDelivr tags for the
vendored assets and writes `report_inline.html` (`-o` to choose the path).
Mermaid stays on CDN either way (see above).
