# Extreme Stress Test Reproduction Guide

This repository ships an offline Mermaid runtime and a reproducible screenshot pipeline.
Generated evidence is intentionally gitignored to keep the current checkout lightweight. Existing Git history still contains earlier artifacts, so use the README's shallow-clone install when history is unnecessary. Install the browser needed for mobile verification, then run the suite from the repository root:

```bash
npm exec --yes --package=playwright -- playwright install webkit
python3 scripts/run_extreme_stress_test.py
```

## Verification contract

- Long titles and long phonetics still wrap without horizontal overflow.
- Mermaid renders from the vendored `assets/vendor/mermaid.min.js` copy, not a CDN.
- Desktop screenshots use Playwright Chromium with the `chrome` channel.
- Mobile screenshots use Playwright WebKit with the `iPhone 14` device preset.

## Inputs and local outputs

- Input: `examples/extreme-stress/input.json`
- HTML: `examples/extreme-stress/results/html`
- Screenshots: `examples/extreme-stress/results/screenshots`
- Machine-readable summary: `examples/extreme-stress/results/summary.json`

Treat the generated `summary.json` as the source of truth for viewport dimensions and run metadata. These local outputs can be deleted and regenerated at any time.
