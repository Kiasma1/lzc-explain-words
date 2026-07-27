#!/usr/bin/env python3

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import unicodedata
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = {
    "word": "{{WORD}}",
    "phonetic": "{{PHONETIC}}",
    "definition_deep": "{{DEFINITION_DEEP}}",
    "etymology": "{{ETYMOLOGY}}",
    "nuance_text": "{{NUANCE_TEXT}}",
    "example_sentence": "{{EXAMPLE_SENTENCE}}",
    "epiphany": "{{EPIPHANY}}",
    "mermaid_code": "{{MERMAID_CODE}}",
}

MERMAID_SCRIPT_PLACEHOLDER = "{{MERMAID_SCRIPT_TAG}}"
LOCAL_MERMAID_FILENAME = "mermaid.min.js"
SUPPLEMENT_OPEN_TEXT_THRESHOLD = 140


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--template", type=Path)
    parser.add_argument("--index-name", default="word_cards_index.html")
    return parser.parse_args()


def normalize_entries(raw: object) -> list[dict[str, Any]]:
    if isinstance(raw, dict):
        raw_entries = raw.get("entries", raw)
        if isinstance(raw_entries, dict):
            raw_entries = [raw_entries]
    elif isinstance(raw, list):
        raw_entries = raw
    else:
        raise ValueError("Input JSON must be an object or an array.")

    entries: list[dict[str, Any]] = []
    for index, item in enumerate(raw_entries, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Entry {index} must be an object.")
        normalized: dict[str, Any] = {}
        for field in REQUIRED_FIELDS:
            value = item.get(field)
            if value is None:
                raise ValueError(f"Entry {index} is missing required field: {field}")
            normalized[field] = str(value)
        for key, value in item.items():
            if key not in normalized:
                normalized[key] = value
        entries.append(normalized)
    return entries


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", ascii_only).strip("_").lower()
    return slug or "word"


def inject_ready_script(document: str) -> str:
    marker = "data-card-ready"
    if marker in document:
        return document
    snippet = """<script>
  (function waitForCardReady() {
    const ready = () => {
      if (document.querySelector('.mermaid svg')) {
        document.body.setAttribute('data-card-ready', '1');
      } else {
        requestAnimationFrame(ready);
      }
    };
    const fallback = () => document.body.setAttribute('data-card-ready', '1');
    window.addEventListener('load', () => {
      setTimeout(ready, 250);
      setTimeout(fallback, 4000);
    });
  })();
</script>
</body>"""
    return document.replace("</body>", snippet)


def mermaid_asset_path() -> Path:
    path = Path(__file__).resolve().parent.parent / "assets" / "vendor" / LOCAL_MERMAID_FILENAME
    if not path.exists():
        raise FileNotFoundError(
            f"Missing Mermaid runtime asset: {path}. "
            "Restore assets/vendor/mermaid.min.js before rendering."
        )
    return path


def inject_runtime_assets(document: str) -> str:
    script_tag = f'<script src="./{LOCAL_MERMAID_FILENAME}"></script>'
    if MERMAID_SCRIPT_PLACEHOLDER in document:
        return document.replace(MERMAID_SCRIPT_PLACEHOLDER, script_tag)
    return document.replace(
        '<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>',
        script_tag,
    )


def ensure_str(value: Any) -> str:
    return "" if value is None else str(value)


def as_list_of_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def extract_text_from_html(value: str) -> str:
    text = re.sub(r"<[^>]+>", " ", value)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def has_meaningful_etymology_html(value: str) -> bool:
    text = extract_text_from_html(value)
    if not text:
        return False
    lowered = text.lower()
    placeholder_texts = {
        "...",
        "{{etymology}}",
        "legacy fallback html still works.",
        "旧版兼容兜底 html。",
    }
    if lowered in placeholder_texts:
        return False
    return True


def supplement_should_start_open(value: str) -> bool:
    return len(extract_text_from_html(value)) <= SUPPLEMENT_OPEN_TEXT_THRESHOLD


def render_structured_etymology(entry: dict[str, Any]) -> str | None:
    origin_formula = ensure_str(entry.get("etymology_origin") or entry.get("etymology_formula")).strip()
    origin_note = ensure_str(entry.get("etymology_origin_note")).strip()
    chunks = as_list_of_dicts(entry.get("etymology_chunks"))
    development = as_list_of_dicts(entry.get("etymology_development"))
    cognates = as_list_of_dicts(entry.get("etymology_cognates"))
    raw_etymology = ensure_str(entry.get("etymology")).strip()

    if not any((origin_formula, origin_note, chunks, development, cognates)):
        return None

    parts: list[str] = []

    if origin_formula or origin_note:
        origin_html = [
            '<section class="etymology-origin" aria-labelledby="origin-formula-heading">',
            '<h3 class="etymology-kicker" id="origin-formula-heading">Origin Formula · 构词公式</h3>',
        ]
        if origin_formula:
            origin_html.append(f'<div class="etymology-origin-formula">{html.escape(origin_formula)}</div>')
        if origin_note:
            origin_html.append(f'<p class="etymology-origin-note">{html.escape(origin_note)}</p>')
        origin_html.append('</section>')
        parts.append("".join(origin_html))

    if chunks:
        chunk_cards = []
        for item in chunks:
            form = html.escape(ensure_str(item.get("form")))
            gloss = html.escape(ensure_str(item.get("gloss")))
            explanation = html.escape(ensure_str(item.get("explanation")))
            role = html.escape(ensure_str(item.get("role")))
            chunk_cards.append(
                "<article class=\"etymology-chunk-card\">"
                + (f"<span class=\"etymology-chip\">{role}</span>" if role else "")
                + f"<h4>{form}</h4>"
                + (f"<p class=\"etymology-chunk-gloss\">{gloss}</p>" if gloss else "")
                + (f"<p class=\"etymology-chunk-note\">{explanation}</p>" if explanation else "")
                + "</article>"
            )
        parts.append(
            "<section class=\"etymology-group\" aria-labelledby=\"word-chunks-heading\">"
            "<h3 class=\"etymology-kicker\" id=\"word-chunks-heading\">Word Chunks · 词块对应</h3>"
            "<div class=\"etymology-chunk-grid\">"
            + "".join(chunk_cards)
            + "</div></section>"
        )

    if development:
        dev_cards = []
        for item in development:
            label = html.escape(ensure_str(item.get("label")))
            title = html.escape(ensure_str(item.get("title")))
            explanation = html.escape(ensure_str(item.get("explanation")))
            kind = html.escape(ensure_str(item.get("kind")))
            dev_cards.append(
                "<article class=\"etymology-development-card\">"
                + (f"<span class=\"etymology-chip\">{kind}</span>" if kind else "")
                + (f"<span class=\"stage-label\">{label}</span>" if label else "")
                + (f"<h4>{title}</h4>" if title else "")
                + (f"<p>{explanation}</p>" if explanation else "")
                + "</article>"
            )
        parts.append(
            "<section class=\"etymology-group\" aria-labelledby=\"meaning-build-up-heading\">"
            "<h3 class=\"etymology-kicker\" id=\"meaning-build-up-heading\">Meaning Build-up · 整体义怎么长出来</h3>"
            "<div class=\"etymology-development-list\">"
            + "".join(dev_cards)
            + "</div></section>"
        )

    if cognates:
        cognate_cards = []
        for item in cognates:
            term = html.escape(ensure_str(item.get("term")))
            note = html.escape(ensure_str(item.get("note")))
            relation = html.escape(ensure_str(item.get("relation")))
            cognate_cards.append(
                "<article class=\"etymology-cognate-card family-mini\">"
                "<span class=\"family-label\">Family · 同族词</span>"
                + (f"<h4>{term}</h4>" if term else "")
                + (f"<p class=\"cognate-relation\">{relation}</p>" if relation else "")
                + (f"<p>{note}</p>" if note else "")
                + "</article>"
            )
        parts.append(
            "<section class=\"etymology-group\" aria-labelledby=\"cognates-heading\">"
            "<h3 class=\"etymology-kicker\" id=\"cognates-heading\">Cognates · 同族词</h3>"
            "<div class=\"etymology-cognate-list\">"
            + "".join(cognate_cards)
            + "</div></section>"
        )

    has_structured_gaps = not all((chunks, development, cognates))
    if has_structured_gaps and has_meaningful_etymology_html(raw_etymology):
        open_attr = " open" if supplement_should_start_open(raw_etymology) else ""
        parts.append(
            "<section class=\"etymology-group etymology-supplement-group\" aria-label=\"Additional etymology notes\">"
            + f"<details class=\"etymology-supplement-details\"{open_attr}>"
            "<summary class=\"etymology-supplement-summary\">"
            "<span class=\"etymology-kicker\">Additional Notes · 补充说明</span>"
            "<span class=\"etymology-supplement-toggle\" aria-hidden=\"true\"></span>"
            "</summary>"
            "<div class=\"etymology-supplement\">"
            + raw_etymology
            + "</div>"
            "</details></section>"
        )

    return "".join(parts)


def render_entry(template: str, entry: dict[str, Any]) -> str:
    entry = dict(entry)
    structured_etymology = render_structured_etymology(entry)
    if structured_etymology:
        entry["etymology"] = structured_etymology
    rendered = template
    for field, placeholder in REQUIRED_FIELDS.items():
        rendered = rendered.replace(placeholder, ensure_str(entry[field]))
    rendered = inject_runtime_assets(rendered)
    return inject_ready_script(rendered)


def build_index(entries: list[dict[str, Any]], outputs: list[Path]) -> str:
    items = []
    for position, (entry, output) in enumerate(zip(entries, outputs), start=1):
        items.append(
            "<li>"
            f"<a href=\"{html.escape(output.name)}\">"
            f"<span class=\"card-number\" aria-hidden=\"true\">{position:02d}</span>"
            f"<span class=\"card-name\" lang=\"en\">{html.escape(entry['word'])}</span>"
            "<span class=\"card-cta\" lang=\"en\">Open card</span>"
            "</a>"
            "</li>"
        )
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Word Card Collection</title>
  <style>
    :root {{
      --color-paper-0: #ffffff;
      --color-paper-50: #fbfaf7;
      --color-paper-100: #f4f0e8;
      --color-ink-950: #171717;
      --color-ink-700: #44403c;
      --color-ink-500: #78716c;
      --color-indigo-700: #3730a3;
      --color-indigo-600: #4f46e5;
      --color-border: rgba(23, 23, 23, 0.12);
      --color-border-subtle: rgba(23, 23, 23, 0.08);
      --color-shadow: rgba(23, 23, 23, 0.08);
      --color-surface-translucent: rgba(255, 255, 255, 0.88);
      --color-indigo-soft: rgba(79, 70, 229, 0.06);
      --font-serif: "Iowan Old Style", "Palatino Linotype", "Book Antiqua", Georgia, serif;
      --font-sans: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      --font-mono: "SFMono-Regular", "Cascadia Code", "Menlo", monospace;
      --radius-lg: 22px;
      --radius-xl: 30px;
    }}
    * {{
      box-sizing: border-box;
    }}
    body {{
      margin: 0;
      min-height: 100vh;
      padding: 40px 20px 64px;
      font-family: var(--font-sans);
      background:
        radial-gradient(circle at 12% 0%, var(--color-indigo-soft), transparent 30%),
        linear-gradient(180deg, var(--color-paper-50), var(--color-paper-100));
      color: var(--color-ink-950);
    }}
    main {{
      max-width: 900px;
      margin: 0 auto;
    }}
    header {{
      padding: 32px;
      border: 1px solid var(--color-border-subtle);
      border-radius: var(--radius-xl);
      background: var(--color-surface-translucent);
      box-shadow: 0 18px 48px var(--color-shadow);
    }}
    h1 {{
      margin: 0;
      font-family: var(--font-serif);
      font-size: clamp(38px, 7vw, 64px);
      line-height: 1;
      letter-spacing: -0.035em;
    }}
    header p {{
      max-width: 620px;
      margin: 16px 0 0;
      color: var(--color-ink-700);
      font-family: var(--font-serif);
      font-size: 18px;
      line-height: 1.7;
    }}
    .collection-meta {{
      display: inline-flex;
      align-items: center;
      min-height: 32px;
      margin-bottom: 18px;
      padding: 4px 12px;
      border: 1px solid var(--color-border-subtle);
      border-radius: 999px;
      color: var(--color-ink-500);
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.1em;
      text-transform: uppercase;
    }}
    ol {{
      display: grid;
      gap: 12px;
      margin: 24px 0 0;
      padding: 0;
      list-style: none;
    }}
    li {{
      min-width: 0;
    }}
    a {{
      min-height: 72px;
      display: grid;
      grid-template-columns: auto minmax(0, 1fr) auto;
      gap: 16px;
      align-items: center;
      padding: 14px 18px;
      border: 1px solid var(--color-border);
      border-radius: var(--radius-lg);
      background: var(--color-paper-0);
      color: var(--color-ink-950);
      text-decoration: none;
      box-shadow: 0 10px 28px var(--color-shadow);
      transition: border-color 180ms ease, box-shadow 180ms ease, color 180ms ease;
    }}
    a:hover {{
      border-color: var(--color-indigo-600);
      color: var(--color-indigo-700);
      box-shadow: 0 16px 34px var(--color-shadow);
    }}
    a:focus-visible {{
      outline: 3px solid var(--color-indigo-600);
      outline-offset: 3px;
    }}
    .card-number {{
      width: 36px;
      height: 36px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border-radius: 999px;
      background: var(--color-indigo-soft);
      color: var(--color-indigo-700);
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 800;
    }}
    .card-name {{
      overflow-wrap: anywhere;
      font-family: var(--font-serif);
      font-size: 22px;
      font-weight: 700;
    }}
    .card-cta {{
      color: var(--color-ink-500);
      font-size: 12px;
      font-weight: 750;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
    @media (max-width: 640px) {{
      body {{
        padding: 12px 12px 40px;
      }}
      header {{
        padding: 24px 20px;
        border-radius: var(--radius-lg);
      }}
      a {{
        grid-template-columns: auto minmax(0, 1fr);
      }}
      .card-cta {{
        grid-column: 2;
      }}
    }}
    @media (prefers-reduced-motion: reduce) {{
      * {{
        transition-duration: 0.01ms !important;
      }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <span class="collection-meta">{len(items):02d} cards · 词卡合集</span>
      <h1 lang="en">Word Card Collection</h1>
      <p>按输入顺序打开每一张双语词卡，从核心语义一路看到词源、语感与结构拓扑。</p>
    </header>
    <ol aria-label="Generated word cards">
      {''.join(items)}
    </ol>
  </main>
</body>
</html>"""


def main() -> None:
    args = parse_args()
    template_path = args.template or Path(__file__).resolve().parent.parent / "assets" / "word_card.html"
    template = template_path.read_text(encoding="utf-8")
    raw = json.loads(args.input.read_text(encoding="utf-8"))
    entries = normalize_entries(raw)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(mermaid_asset_path(), args.output_dir / LOCAL_MERMAID_FILENAME)
    outputs: list[Path] = []

    for entry in entries:
        slug = slugify(entry["word"])
        output_path = args.output_dir / f"word_card_{slug}.html"
        output_path.write_text(render_entry(template, entry), encoding="utf-8")
        outputs.append(output_path)

    if len(outputs) > 1:
        index_path = args.output_dir / args.index_name
        index_path.write_text(build_index(entries, outputs), encoding="utf-8")

    print(json.dumps({
        "count": len(outputs),
        "files": [str(path) for path in outputs],
        "index": str(args.output_dir / args.index_name) if len(outputs) > 1 else None,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
