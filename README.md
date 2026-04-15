# lzc-explain-words

[中文说明 / Chinese README](README.zh-CN.md)

A Codex skill for deep English word mastery. It renders premium bilingual HTML word cards with:

- core semantic framing
- etymology and cognates
- nuance comparisons
- Mermaid semantic topology
- bilingual epiphany lines
- reproducible extreme stress-test artifacts

## Highlights

- Supports one word or multiple words from a single JSON input.
- Handles long titles and long phonetics without horizontal overflow.
- Ships Mermaid locally via `assets/vendor/mermaid.min.js` instead of a CDN.
- Copies the Mermaid runtime into each render output directory automatically.
- Includes an extreme stress-test suite with desktop and iPhone-class screenshots.

## Repository Layout

- `SKILL.md` — skill instructions and usage contract
- `assets/word_card.html` — museum-style HTML template
- `assets/vendor/mermaid.min.js` — vendored Mermaid runtime
- `scripts/render_word_cards.py` — renderer for one or many entries
- `scripts/run_extreme_stress_test.py` — reproducible render + screenshot verification
- `examples/extreme-stress/input.json` — six hard-case entries
- `examples/extreme-stress/results/` — latest HTML, screenshots, and summary JSON
- `docs/extreme-stress-results.md` — human-readable stress-test summary

## Quick Start

Render from structured JSON:

```bash
python3 scripts/render_word_cards.py \
  --input /path/to/words.json \
  --output-dir /path/to/output
```

The renderer writes HTML files and also copies `mermaid.min.js` into the same output directory, so the cards stay self-contained for local viewing.

## Stress-Test Pipeline

Install the Playwright browser needed for mobile verification:

```bash
npm exec --yes --package=playwright -- playwright install webkit
```

Run the bundled extreme stress suite:

```bash
python3 scripts/run_extreme_stress_test.py
```

Notes:

- Desktop screenshots default to Playwright Chromium using the local `chrome` channel.
- If Chrome is unavailable, run `python3 scripts/run_extreme_stress_test.py --desktop-channel none` to use Playwright's bundled Chromium.
- Mobile screenshots use Playwright WebKit with the `iPhone 14` preset.

## Example Screenshots

### Desktop

![Desktop stress sample](examples/extreme-stress/results/screenshots/desktop/word_card_floccinaucinihilipilification.png)

### Mobile

![Mobile stress sample](examples/extreme-stress/results/screenshots/mobile/word_card_floccinaucinihilipilification.mobile.png)

## Extreme Stress-Test Result Snapshot

Latest checked-in run covers:

- `floccinaucinihilipilification`
- `honorificabilitudinitatibus`
- `psychoneuroendocrinological`
- `thyroparathyroidectomized`
- `otorhinolaryngological`
- `deinstitutionalization`

Evidence captured in-repo:

- Input: `examples/extreme-stress/input.json`
- HTML outputs: `examples/extreme-stress/results/html`
- Desktop screenshots: `examples/extreme-stress/results/screenshots/desktop`
- Mobile screenshots: `examples/extreme-stress/results/screenshots/mobile`
- Summary JSON: `examples/extreme-stress/results/summary.json`
- Narrative summary: `docs/extreme-stress-results.md`

## Input Shape

Required base fields remain:

- `word`
- `phonetic`
- `definition_deep`
- `etymology`
- `nuance_text`
- `example_sentence`
- `epiphany`
- `mermaid_code`

`etymology` still accepts raw HTML for backward compatibility.

For clearer etymology mapping, the renderer now also supports these optional structured fields:

- `etymology_origin` — compact origin formula such as `flocci + nauci + nihili + pili + -fication`
- `etymology_formula` — legacy alias of `etymology_origin`
- `etymology_origin_note` — short note explaining the overall source pattern
- `etymology_chunks` — actual morpheme/chunk cards, each with `form`, `gloss`, `explanation`, optional `role`
- `etymology_development` — semantic build-up stages, each with `label`, `title`, `explanation`, optional `kind`
- `etymology_cognates` — cognate/family cards, each with `term`, `note`, optional `relation`

When those structured fields are present, the renderer will prefer them over the raw `etymology` HTML so that real chunks stay visually separate from meaning-development commentary.

If the structured fields cover only part of the etymology lane, the existing raw `etymology` HTML is preserved under `Additional Notes · 补充说明` instead of being silently discarded.

Single entry:

```json
{
  "word": "Excerpt",
  "phonetic": "ˈek.sɝːpt",
  "definition_deep": "<p>...</p>",
  "etymology": "<p>...</p>",
  "nuance_text": "<ul class=\"nuance-list\"><li class=\"nuance-item\">...</li></ul>",
  "example_sentence": "She quoted a brief excerpt.",
  "epiphany": "An excerpt is a chosen window. 摘录是被选择出来的一扇窗。",
  "mermaid_code": "graph TD\\nA[whole text] --> B[selected passage]"
}
```

Single entry with structured etymology:

```json
{
  "word": "Floccinaucinihilipilification",
  "phonetic": "ˌflɒk.sɪ.nɔː.sɪˌnaɪ.hɪ.lɪˌpɪl.ɪ.fɪˈkeɪ.ʃən",
  "definition_deep": "<p>...</p>",
  "etymology": "<p>Legacy fallback HTML still works.</p>",
  "etymology_origin": "flocci + nauci + nihili + pili + -fication",
  "etymology_origin_note": "A learned stack of low-value Latin forms plus a nominalizing suffix.",
  "etymology_chunks": [
    {
      "form": "flocci",
      "gloss": "of little value",
      "explanation": "Starts the downward valuation.",
      "role": "chunk"
    }
  ],
  "etymology_development": [
    {
      "label": "Step 1",
      "title": "semantic move",
      "explanation": "Multiple low-value forms reinforce the same belittling judgment.",
      "kind": "meaning build-up"
    }
  ],
  "etymology_cognates": [
    {
      "term": "nil",
      "relation": "shared low-value idea",
      "note": "Modern English echo of the zero-value sense."
    }
  ],
  "nuance_text": "<ul class=\"nuance-list\"><li class=\"nuance-item\">...</li></ul>",
  "example_sentence": "He treated the objection with floccinaucinihilipilification.",
  "epiphany": "A giant word can dramatize a tiny valuation. 冗长本身，也能参与轻视的语气。",
  "mermaid_code": "graph TD\\nA[low value] --> B[stacked learned forms] --> C[performative dismissal]"
}
```

Multiple entries:

```json
[
  {
    "word": "Excerpt",
    "phonetic": "ˈek.sɝːpt",
    "definition_deep": "<p>...</p>",
    "etymology": "<p>...</p>",
    "nuance_text": "<ul class=\"nuance-list\"><li class=\"nuance-item\">...</li></ul>",
    "example_sentence": "She quoted a brief excerpt.",
    "epiphany": "An excerpt is a chosen window. 摘录是被选择出来的一扇窗。",
    "mermaid_code": "graph TD\\nA[whole text] --> B[selected passage]"
  },
  {
    "word": "Serendipity",
    "phonetic": "ˌser.ənˈdɪp.ə.ti",
    "definition_deep": "<p>...</p>",
    "etymology": "<p>...</p>",
    "nuance_text": "<ul class=\"nuance-list\"><li class=\"nuance-item\">...</li></ul>",
    "example_sentence": "Their meeting was pure serendipity.",
    "epiphany": "Serendipity is chance meeting a prepared soul. 机缘是偶然遇见了有准备的灵魂。",
    "mermaid_code": "graph TD\\nA[searching] --> B[finding]"
  }
]
```

## Output

- one entry → one `word_card_<slug>.html`
- multiple entries → multiple HTML cards + `word_cards_index.html`

## License

This repository is licensed as `GPL-2.0-only`. See `LICENSE` for the full text.
