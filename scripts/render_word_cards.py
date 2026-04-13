#!/usr/bin/env python3

from __future__ import annotations

import argparse
import html
import json
import re
import unicodedata
from pathlib import Path


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--template", type=Path)
    parser.add_argument("--index-name", default="word_cards_index.html")
    return parser.parse_args()


def normalize_entries(raw: object) -> list[dict[str, str]]:
    if isinstance(raw, dict):
        raw_entries = raw.get("entries", raw)
        if isinstance(raw_entries, dict):
            raw_entries = [raw_entries]
    elif isinstance(raw, list):
        raw_entries = raw
    else:
        raise ValueError("Input JSON must be an object or an array.")

    entries: list[dict[str, str]] = []
    for index, item in enumerate(raw_entries, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Entry {index} must be an object.")
        normalized: dict[str, str] = {}
        for field in REQUIRED_FIELDS:
            value = item.get(field)
            if value is None:
                raise ValueError(f"Entry {index} is missing required field: {field}")
            normalized[field] = str(value)
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
    window.addEventListener('load', () => setTimeout(ready, 250));
  })();
</script>
</body>"""
    return document.replace("</body>", snippet)


def render_entry(template: str, entry: dict[str, str]) -> str:
    rendered = template
    for field, placeholder in REQUIRED_FIELDS.items():
        rendered = rendered.replace(placeholder, entry[field])
    return inject_ready_script(rendered)


def build_index(entries: list[dict[str, str]], outputs: list[Path]) -> str:
    items = []
    for entry, output in zip(entries, outputs):
        items.append(
            f"<li><a href=\"{html.escape(output.name)}\">{html.escape(entry['word'])}</a></li>"
        )
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Word Cards</title>
  <style>
    body {{
      margin: 0;
      padding: 40px 24px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: linear-gradient(180deg, #f8fafc 0%, #eef2f7 100%);
      color: #111827;
    }}
    main {{
      max-width: 760px;
      margin: 0 auto;
      background: rgba(255,255,255,0.88);
      border: 1px solid rgba(17,24,39,0.08);
      border-radius: 24px;
      padding: 28px;
      box-shadow: 0 12px 32px rgba(15,23,42,0.08);
    }}
    h1 {{
      margin: 0 0 12px;
      font-size: clamp(30px, 5vw, 48px);
    }}
    p {{
      color: #4b5563;
      line-height: 1.7;
    }}
    ul {{
      margin: 24px 0 0;
      padding-left: 20px;
    }}
    li + li {{
      margin-top: 12px;
    }}
    a {{
      color: #1d4ed8;
      text-decoration: none;
      font-weight: 600;
    }}
  </style>
</head>
<body>
  <main>
    <h1>Word Cards</h1>
    <p>已根据本次输入生成以下词卡：</p>
    <ul>
      {''.join(items)}
    </ul>
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
