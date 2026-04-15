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
        origin_html = ['<section class="etymology-origin">', '<span class="etymology-kicker">Origin Formula · 构词公式</span>']
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
                + f"<h3>{form}</h3>"
                + (f"<p class=\"etymology-chunk-gloss\">{gloss}</p>" if gloss else "")
                + (f"<p class=\"etymology-chunk-note\">{explanation}</p>" if explanation else "")
                + "</article>"
            )
        parts.append(
            "<section class=\"etymology-group\">"
            "<span class=\"etymology-kicker\">Word Chunks · 词块对应</span>"
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
                + (f"<h3>{title}</h3>" if title else "")
                + (f"<p>{explanation}</p>" if explanation else "")
                + "</article>"
            )
        parts.append(
            "<section class=\"etymology-group\">"
            "<span class=\"etymology-kicker\">Meaning Build-up · 整体义怎么长出来</span>"
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
                + (f"<h3>{term}</h3>" if term else "")
                + (f"<p class=\"cognate-relation\">{relation}</p>" if relation else "")
                + (f"<p>{note}</p>" if note else "")
                + "</article>"
            )
        parts.append(
            "<section class=\"etymology-group\">"
            "<span class=\"etymology-kicker\">Cognates · 同族词</span>"
            "<div class=\"etymology-cognate-list\">"
            + "".join(cognate_cards)
            + "</div></section>"
        )

    has_structured_gaps = not all((chunks, development, cognates))
    if has_structured_gaps and has_meaningful_etymology_html(raw_etymology):
        open_attr = " open" if supplement_should_start_open(raw_etymology) else ""
        parts.append(
            "<section class=\"etymology-group etymology-supplement-group\">"
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
