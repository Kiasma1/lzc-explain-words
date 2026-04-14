# Extreme Stress Test Results

This repository now ships an offline Mermaid runtime and a reproducible screenshot pipeline.
The latest extreme stress run was generated from `examples/extreme-stress/input.json` with:

```bash
python3 scripts/run_extreme_stress_test.py
```

## What was verified

- Long titles and long phonetics still wrap without horizontal overflow.
- Mermaid renders from the vendored `assets/vendor/mermaid.min.js` copy, not a CDN.
- Desktop screenshots use Playwright Chromium with the `chrome` channel.
- Mobile screenshots use Playwright WebKit with the `iPhone 14` device preset.

## Latest run summary

| Word | Desktop | Mobile |
| --- | --- | --- |
| `deinstitutionalization` | `1440×3101` | `1170×10164` |
| `floccinaucinihilipilification` | `1440×3101` | `1170×10431` |
| `honorificabilitudinitatibus` | `1440×3101` | `1170×10287` |
| `otorhinolaryngological` | `1440×3003` | `1170×9996` |
| `psychoneuroendocrinological` | `1440×3068` | `1170×10623` |
| `thyroparathyroidectomized` | `1440×3068` | `1170×10491` |

## Example screenshots

### Desktop

![Desktop stress sample](../examples/extreme-stress/results/screenshots/desktop/word_card_floccinaucinihilipilification.png)

### Mobile

![Mobile stress sample](../examples/extreme-stress/results/screenshots/mobile/word_card_floccinaucinihilipilification.mobile.png)

## Artifacts

- Input: `examples/extreme-stress/input.json`
- HTML: `examples/extreme-stress/results/html`
- Screenshots: `examples/extreme-stress/results/screenshots`
- Machine-readable summary: `examples/extreme-stress/results/summary.json`
