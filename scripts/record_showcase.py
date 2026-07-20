#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


DEFAULT_OUTPUT = Path("examples/showcase/showcase.gif")
FFMPEG_FILTER = (
    "fps=8,"
    "crop=1440:900:0:'(ih-oh)*if(lt(t,1),0,if(lt(t,9),(t-1)/8,1))',"
    "scale=720:450:flags=lanczos,split[s0][s1];"
    "[s0]palettegen=max_colors=96:stats_mode=diff[p];"
    "[s1][p]paletteuse=dither=bayer:bayer_scale=3:diff_mode=rectangle"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Re-record the Serendipity README showcase GIF."
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--desktop-channel",
        default="chrome",
        help="Chromium channel for the full-page capture; use 'none' for bundled Chromium.",
    )
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def require_executable(name: str) -> str:
    executable = shutil.which(name)
    if executable is None:
        raise FileNotFoundError(f"Required executable not found on PATH: {name}")
    return executable


def render_card(root: Path, html_dir: Path) -> Path:
    subprocess.run(
        [
            sys.executable,
            str(root / "scripts" / "render_word_cards.py"),
            "--input",
            str(root / "examples" / "showcase" / "input.json"),
            "--output-dir",
            str(html_dir),
        ],
        check=True,
    )
    return html_dir / "word_card_serendipity.html"


def capture_full_page(html_path: Path, output_path: Path, channel: str) -> None:
    command = [
        require_executable("npm"),
        "exec",
        "--yes",
        "--package=playwright",
        "--",
        "playwright",
        "screenshot",
        "--full-page",
        "--wait-for-timeout",
        "2000",
        "--timeout",
        "60000",
        "--browser",
        "chromium",
        "--viewport-size",
        "1440,900",
    ]
    if channel.lower() not in {"", "none", "bundled"}:
        command.extend(["--channel", channel])
    command.extend([html_path.resolve().as_uri(), str(output_path)])
    subprocess.run(command, check=True)


def create_gif(full_page_png: Path, output_path: Path) -> None:
    subprocess.run(
        [
            require_executable("ffmpeg"),
            "-hide_banner",
            "-loglevel",
            "error",
            "-loop",
            "1",
            "-t",
            "10",
            "-i",
            str(full_page_png),
            "-filter_complex",
            FFMPEG_FILTER,
            "-loop",
            "0",
            "-y",
            str(output_path),
        ],
        check=True,
    )


def main() -> int:
    args = parse_args()
    root = repo_root()
    output_path = args.output if args.output.is_absolute() else root / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with TemporaryDirectory(prefix=".showcase-", dir=root) as temp_dir:
        working_dir = Path(temp_dir)
        html_path = render_card(root, working_dir / "html")
        full_page_png = working_dir / "showcase-full.png"
        capture_full_page(html_path, full_page_png, args.desktop_channel)
        create_gif(full_page_png, output_path)

    print(
        json.dumps(
            {"output": str(output_path), "bytes": output_path.stat().st_size},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
