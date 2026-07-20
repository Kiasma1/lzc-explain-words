from __future__ import annotations

import shutil
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import run_extreme_stress_test as stress_test


class RenderCardsTests(unittest.TestCase):
    def test_uses_the_current_python_interpreter(self) -> None:
        with TemporaryDirectory() as temp_dir:
            with patch.object(stress_test.subprocess, "run") as run:
                stress_test.render_cards(Path("input.json"), Path(temp_dir))

        command = run.call_args.args[0]
        self.assertEqual(sys.executable, command[0])
        self.assertTrue(run.call_args.kwargs["check"])


class ScreenshotCommandTests(unittest.TestCase):
    def test_uses_the_resolved_npm_executable(self) -> None:
        expected = shutil.which("npm") or "npm"
        calls = (
            lambda: stress_test.screenshot_desktop(
                Path("card.html"), Path("desktop.png"), 0, "none"
            ),
            lambda: stress_test.screenshot_mobile(
                Path("card.html"), Path("mobile.png"), 0, "iPhone 14"
            ),
        )

        for call in calls:
            with self.subTest(call=call), patch.object(
                stress_test.subprocess, "run"
            ) as run:
                call()

            command = run.call_args.args[0]
            self.assertEqual(expected, command[0])


class SummaryPathTests(unittest.TestCase):
    def test_uses_relative_paths_inside_the_repository(self) -> None:
        with TemporaryDirectory() as root_dir:
            root = Path(root_dir)
            path = root / "output" / "summary.json"

            self.assertEqual(
                str(Path("output") / "summary.json"),
                stress_test.path_for_summary(path, root),
            )

    def test_keeps_absolute_paths_outside_the_repository(self) -> None:
        with TemporaryDirectory() as root_dir, TemporaryDirectory() as output_dir:
            root = Path(root_dir)
            path = Path(output_dir) / "summary.json"

            self.assertEqual(str(path), stress_test.path_for_summary(path, root))


if __name__ == "__main__":
    unittest.main()
