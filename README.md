<sub>🌐 <b>English</b> · <a href="README.zh-CN.md">中文</a></sub>

<div align="center">

# lzc-explain-words

> *“A dictionary tells you what a word means. This Skill shows you how the meaning was built.”*

[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-compatible-6f42c1)](SKILL.md)
[![Offline HTML](https://img.shields.io/badge/output-offline%20HTML-1f6feb)](#what-you-get)
[![Multi-runtime](https://img.shields.io/badge/runtime-Claude%20Code%20%7C%20Codex%20%7C%20more-2ea44f)](#requirements)
[![License: GPL-2.0-only](https://img.shields.io/badge/license-GPL--2.0--only-blue)](LICENSE)

**Turn one English word—or a whole list—into collectible bilingual HTML cards with etymology, nuance, semantic topology, and a memorable final insight.**

[See the result](#see-it-in-action) · [Install](#quick-start) · [Try a prompt](#trigger-phrases) · [Verify it](#reproduce-and-verify) · [Safety](#offline-by-default)

</div>

---

![Serendipity word card showcase](examples/showcase/showcase.gif)

<sub>Real replay from [`examples/showcase/input.json`](examples/showcase/input.json), recorded by [`scripts/record_showcase.py`](scripts/record_showcase.py).</sub>

---

## Why this exists

You can look up *serendipity* in seconds. The definition is easy to find—and easy to forget.

What usually goes missing is the mental model: the word's original image, how its parts relate, why a nearby synonym feels different, and the one sentence that makes the idea stick. `lzc-explain-words` packages that deeper explanation into a visual artifact you can keep, reopen, and compare later.

It is an Agent Skill first and a renderer second: your Agent develops the linguistic content, then the bundled script turns it into an offline bilingual card instead of leaving the answer buried in chat history.

---

## What you get

| Layer | What the card makes visible |
| --- | --- |
| Core semantic frame | The physical image and conceptual formula beneath the definition |
| Etymology map | Real morphemes, meaning development, and related words kept distinct |
| Nuance contrast | Why the word feels different from its nearest alternatives |
| Semantic topology | A Mermaid graph from origin and core action to modern usage |
| Bilingual epiphany | One English-Chinese line designed to make the word memorable |
| Offline artifact | A local HTML card bundle with no Mermaid CDN dependency |

One word produces one card. Multiple words produce multiple cards plus a local index page.

---

## See it in action

Give the Agent one natural-language request:

```text
Deeply explain the word “Serendipity” and generate an HTML word card.
```

The Skill turns the request into structured content, renders `word_card_serendipity.html`, copies the local Mermaid runtime beside it, and returns the card path with its bilingual epiphany.

The GIF above is generated from the checked-in showcase input—not a hand-built mockup. Re-record it at any time with:

```bash
python scripts/record_showcase.py
```

---

## Quick start

Install with one command:

```bash
npx skills add Kiasma1/lzc-explain-words
```

Then tell your Agent:

```text
Deeply explain the word “incubate” and generate a word card.
```

The one-line installer has been tested against the public GitHub repository. It detects supported Agent environments and installs the root [`SKILL.md`](SKILL.md).

### Manual install

If you prefer to inspect or link the repository yourself:

```bash
git clone --depth 1 https://github.com/Kiasma1/lzc-explain-words.git
```

Place or link the cloned directory in your runtime's skills directory. `--depth 1` avoids downloading legacy generated screenshots that remain in Git history; omit it only when you need the full contribution history.

---

## Trigger phrases

Try any of these after installation:

- `Deeply explain the word Serendipity.`
- `Generate a word card for incubate.`
- `Explain excerpt, lucid, and serendipity as HTML cards.`
- `讲透这个单词：resilience。`
- `用语感对比讲清 ingenious 和 ingenuous。`
- `词源解构 floccinaucinihilipilification，并生成词卡。`

This Skill is deliberately not triggered for plain translation, vocabulary drilling, phonetic-only lookups, or casual explanations that do not need an HTML artifact.

---

## Render structured data directly

The Agent workflow writes structured JSON and calls the renderer. You can use the renderer yourself:

```bash
python scripts/render_word_cards.py \
  --input examples/showcase/input.json \
  --output-dir ./word-cards
```

Use `python3` instead of `python` on systems where that is the configured command.

Required fields:

```text
word · phonetic · definition_deep · etymology · nuance_text
example_sentence · epiphany · mermaid_code
```

Optional structured etymology fields keep real word parts separate from the later development of meaning:

| Field | Purpose |
| --- | --- |
| `etymology_origin` | Compact origin or construction formula |
| `etymology_origin_note` | Short explanation of the overall source pattern |
| `etymology_chunks` | Real morpheme or word-part cards |
| `etymology_development` | Stages showing how the whole meaning developed |
| `etymology_cognates` | Related-word cards and their relationships |

Raw `etymology` HTML remains supported for backward compatibility. See the complete, real input in [`examples/showcase/input.json`](examples/showcase/input.json).

---

## What makes it different

| Dimension | A typical chat explanation | `lzc-explain-words` |
| --- | --- | --- |
| Final form | A transient message | A reusable offline HTML artifact |
| Etymology | Often one prose paragraph | Word parts, meaning development, and cognates are visually separated |
| Nuance | A synonym list | Contrast focused on how nearby words actually feel |
| Semantic model | Text only | A rendered Mermaid topology alongside the explanation |
| Multiple words | Easy to lose ordering or skip one | Ordered cards plus an index page; failures must be reported |
| Verification | Depends on the current Agent run | Checked-in prompts, unit tests, showcase recorder, and a stress pipeline |

---

## Offline by default

- Rendering needs no API key and makes no network request.
- Mermaid is vendored at [`assets/vendor/mermaid.min.js`](assets/vendor/mermaid.min.js) and copied beside every output.
- The Skill must not write API keys, private paths, or real account details into a card.
- Uncertain etymology must be marked as uncertain; authoritative-looking invented roots are forbidden.
- Missing required fields fail visibly instead of producing a plausible but incomplete card.
- If screenshot tooling is unavailable, the HTML card is still delivered and the skipped visual check is reported.

The linguistic content is generated by the active Agent. Treat etymological claims as analysis to verify when accuracy is critical.

---

## Reproduce and verify

Run the lightweight regression suite:

```bash
python -m unittest discover -s tests -v
```

Run the six-word extreme layout suite on desktop Chromium and an iPhone 14 WebKit preset:

```bash
npm exec --yes --package=playwright -- playwright install webkit
python scripts/run_extreme_stress_test.py
```

The latest local replay produced six HTML cards, six 1440-pixel desktop screenshots, six 1170-pixel mobile screenshots, six local Mermaid references, and zero remote script references. The suite writes its machine-readable summary to `examples/extreme-stress/results/summary.json`.

Generated HTML, screenshots, and summaries are gitignored to keep the checked-out Skill lightweight. The input and verification contract remain checked in:

- [`examples/extreme-stress/input.json`](examples/extreme-stress/input.json)
- [`docs/extreme-stress-results.md`](docs/extreme-stress-results.md)
- [`tests/test_run_extreme_stress_test.py`](tests/test_run_extreme_stress_test.py)

Re-record the README animation with `python scripts/record_showcase.py`. This recorder additionally needs Chrome installed, with npm and `ffmpeg` available on `PATH`.

---

## Project layout

```text
SKILL.md                              Agent-facing workflow and guardrails
assets/word_card.html                 Museum-style HTML template
assets/vendor/mermaid.min.js          Vendored offline Mermaid runtime
scripts/render_word_cards.py          JSON-to-HTML renderer
scripts/record_showcase.py             Reproducible README GIF recorder
scripts/run_extreme_stress_test.py     Desktop and mobile stress pipeline
examples/showcase/                     Everyday-word input and showcase GIF
examples/extreme-stress/input.json     Six hard layout cases
docs/                                  Stress-test reproduction notes
tests/                                 Cross-platform regression tests
test-prompts.json                      Standard Agent acceptance prompts
```

---

## Requirements

- An Agent runtime that supports repository-based Agent Skills, such as Claude Code, Codex, or another compatible runtime.
- Python 3.10+ for direct rendering and repository tests.
- No network connection or API key for opening generated cards.
- Optional: npm + Playwright for screenshots; an installed Chrome browser plus `ffmpeg` on `PATH` for rebuilding the GIF.

---

## Acknowledgements

Offline graphs are rendered with [Mermaid](https://mermaid.js.org/). Cross-browser layout replay uses [Playwright](https://playwright.dev/).

## License

Licensed under [`GPL-2.0-only`](LICENSE).

---

<div align="center">

*One prompt in. One word understood. One card kept.*

</div>
