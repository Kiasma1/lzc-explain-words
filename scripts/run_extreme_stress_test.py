#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


DEFAULT_ROOT = Path("examples/extreme-stress")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render and screenshot the bundled extreme stress-test cards."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_ROOT / "input.json",
        help="Structured entries JSON for the stress-test suite.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_ROOT / "results",
        help="Directory to write rendered HTML and screenshots into.",
    )
    parser.add_argument(
        "--desktop-channel",
        default="chrome",
        help="Chromium channel for desktop screenshots.",
    )
    parser.add_argument(
        "--mobile-device",
        default="iPhone 14",
        help="Playwright device preset for mobile screenshots.",
    )
    parser.add_argument(
        "--wait-ms",
        type=int,
        default=3000,
        help="Wait time before each screenshot.",
    )
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def render_cards(input_path: Path, html_dir: Path) -> list[Path]:
    script = repo_root() / "scripts" / "render_word_cards.py"
    subprocess.run(
        ["python3", str(script), "--input", str(input_path), "--output-dir", str(html_dir)],
        check=True,
    )
    return sorted(html_dir.glob("word_card_*.html"))


def file_url(path: Path) -> str:
    return path.resolve().as_uri()


def screenshot_desktop(html_path: Path, output_path: Path, wait_ms: int, channel: str) -> None:
    cmd = [
        "npm",
        "exec",
        "--yes",
        "--package=playwright",
        "--",
        "playwright",
        "screenshot",
        "--full-page",
        "--wait-for-timeout",
        str(wait_ms),
        "--timeout",
        "60000",
        "--browser",
        "chromium",
        "--viewport-size",
        "1440,2200",
    ]
    if channel.lower() not in {"", "none", "bundled"}:
        cmd.extend(["--channel", channel])
    cmd.extend([file_url(html_path), str(output_path)])
    subprocess.run(cmd, check=True)


def screenshot_mobile(html_path: Path, output_path: Path, wait_ms: int, device: str) -> None:
    subprocess.run(
        [
            "npm",
            "exec",
            "--yes",
            "--package=playwright",
            "--",
            "playwright",
            "screenshot",
            "--full-page",
            "--wait-for-timeout",
            str(wait_ms),
            "--timeout",
            "60000",
            "--browser",
            "webkit",
            "--device",
            device,
            file_url(html_path),
            str(output_path),
        ],
        check=True,
    )


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as fh:
        header = fh.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Not a PNG file: {path}")
    width = int.from_bytes(header[16:20], "big")
    height = int.from_bytes(header[20:24], "big")
    return width, height


def main() -> int:
    args = parse_args()
    root = repo_root()
    input_path = (root / args.input).resolve() if not args.input.is_absolute() else args.input
    output_root = (root / args.output_root).resolve() if not args.output_root.is_absolute() else args.output_root

    html_dir = output_root / "html"
    desktop_dir = output_root / "screenshots" / "desktop"
    mobile_dir = output_root / "screenshots" / "mobile"
    html_dir.mkdir(parents=True, exist_ok=True)
    desktop_dir.mkdir(parents=True, exist_ok=True)
    mobile_dir.mkdir(parents=True, exist_ok=True)

    cards = render_cards(input_path, html_dir)
    summary: list[dict[str, object]] = []

    for html_path in cards:
        desktop_path = desktop_dir / f"{html_path.stem}.png"
        mobile_path = mobile_dir / f"{html_path.stem}.mobile.png"
        screenshot_desktop(html_path, desktop_path, args.wait_ms, args.desktop_channel)
        screenshot_mobile(html_path, mobile_path, args.wait_ms, args.mobile_device)
        desktop_size = png_size(desktop_path)
        mobile_size = png_size(mobile_path)
        summary.append(
            {
                "card": html_path.name,
                "desktop_screenshot": str(desktop_path.relative_to(root)),
                "desktop_size": {"width": desktop_size[0], "height": desktop_size[1]},
                "mobile_screenshot": str(mobile_path.relative_to(root)),
                "mobile_size": {"width": mobile_size[0], "height": mobile_size[1]},
            }
        )

    summary_path = output_root / "summary.json"
    summary_path.write_text(
        json.dumps(
            {
                "input": str(input_path.relative_to(root)),
                "cards": [str(path.relative_to(root)) for path in cards],
                "results": summary,
                "desktop_channel": args.desktop_channel,
                "mobile_device": args.mobile_device,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"summary": str(summary_path.relative_to(root)), "count": len(summary)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
