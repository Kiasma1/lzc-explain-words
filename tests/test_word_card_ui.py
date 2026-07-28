from __future__ import annotations

import json
import re
import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import render_word_cards


class DocumentProbe(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tags: list[str] = []
        self.ids: list[str] = []
        self.headings: list[int] = []
        self.links: list[str] = []
        self.buttons: list[dict[str, str | None]] = []
        self.labelled_by: list[str] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attributes = dict(attrs)
        self.tags.append(tag)

        if element_id := attributes.get("id"):
            self.ids.append(element_id)
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.headings.append(int(tag[1]))
        if tag == "a" and (href := attributes.get("href")):
            self.links.append(href)
        if tag == "button":
            self.buttons.append(attributes)
        if labelled_by := attributes.get("aria-labelledby"):
            self.labelled_by.append(labelled_by)


class WordCardTemplateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.template = (REPO_ROOT / "assets" / "word_card.html").read_text(
            encoding="utf-8"
        )
        [cls.showcase_entry] = json.loads(
            (REPO_ROOT / "examples" / "showcase" / "input.json").read_text(
                encoding="utf-8"
            )
        )
        cls.rendered = render_word_cards.render_entry(
            cls.template, cls.showcase_entry
        )
        cls.probe = DocumentProbe()
        cls.probe.feed(cls.rendered)

    def test_uses_semantic_landmarks_and_unique_ids(self) -> None:
        self.assertEqual(1, self.probe.tags.count("main"))
        self.assertEqual(1, self.probe.tags.count("nav"))
        self.assertEqual(1, self.probe.tags.count("h1"))
        self.assertIn("blockquote", self.probe.tags)
        self.assertEqual(len(self.probe.ids), len(set(self.probe.ids)))
        self.assertTrue(set(self.probe.labelled_by).issubset(self.probe.ids))

    def test_heading_levels_never_skip(self) -> None:
        for previous, current in zip(self.probe.headings, self.probe.headings[1:]):
            self.assertLessEqual(current - previous, 1)

    def test_navigation_targets_the_five_word_lenses(self) -> None:
        self.assertEqual(
            ["#meaning", "#etymology", "#nuance", "#topology", "#epiphany"],
            [href for href in self.probe.links if href.startswith("#")][1:],
        )

    def test_actions_are_native_buttons(self) -> None:
        self.assertEqual(2, len(self.probe.buttons))
        self.assertTrue(
            all(button.get("type") == "button" for button in self.probe.buttons)
        )
        self.assertIn("window.print()", self.template)
        self.assertIn("navigator.clipboard", self.template)
        self.assertIn("document.execCommand('copy')", self.template)

    def test_ready_helper_stops_polling_after_completion(self) -> None:
        self.assertIn("let finished = false", self.rendered)
        self.assertIn("if (finished) return", self.rendered)
        self.assertIn("cancelAnimationFrame(frameId)", self.rendered)
        self.assertIn("setTimeout(ready, 250)", self.rendered)
        self.assertIn("setTimeout(finish, 4000)", self.rendered)
        self.assertIn("{ once: true }", self.rendered)

    def test_visual_system_is_tokenized_and_accessible(self) -> None:
        root_end = self.template.index("\n  }\n\n  *")
        component_css_and_markup = self.template[root_end:]
        self.assertNotRegex(component_css_and_markup, r"#[0-9a-fA-F]{3,8}")
        self.assertNotRegex(component_css_and_markup, r"rgba\(")
        self.assertIn("@media (prefers-reduced-motion: reduce)", self.template)
        self.assertIn("@media print", self.template)
        self.assertIn(":focus-visible", self.template)

    def test_motion_tokens_press_feedback_and_pointer_hover_are_scoped(self) -> None:
        for declaration in (
            "--duration-press: 160ms",
            "--duration-state: 180ms",
            "--ease-out: cubic-bezier(0.23, 1, 0.32, 1)",
            "--ease-in-out: cubic-bezier(0.77, 0, 0.175, 1)",
        ):
            self.assertIn(declaration, self.template)

        self.assertIn(".action-button:active", self.template)
        self.assertIn(".section-nav-link:active", self.template)
        self.assertGreaterEqual(self.template.count("transform: scale(0.97)"), 2)
        self.assertIn(
            "@media (hover: hover) and (pointer: fine)", self.template
        )
        transition_declarations = re.findall(
            r"transition(?:-property)?:\s*(.*?);",
            self.template,
            flags=re.DOTALL,
        )
        self.assertFalse(
            any("box-shadow" in declaration for declaration in transition_declarations)
        )

    def test_reduced_motion_preserves_non_positional_feedback(self) -> None:
        self.assertNotIn("transition-duration: 0.01ms", self.template)
        self.assertIn(
            "transition-property: background-color, border-color, color, opacity",
            self.template,
        )
        self.assertIn(
            ".skip-link {\n      transform: translateY(-160%) !important;",
            self.template,
        )
        self.assertIn(
            ".skip-link:focus {\n      transform: translateY(0) !important;",
            self.template,
        )
        self.assertIn('content: "▴"', self.template)
        self.assertIn(".section-nav-indicator {\n      transition: opacity 120ms ease;", self.template)
        self.assertIn(".epiphany-box[data-reveal] {", self.template)
        self.assertIn("transform: none;", self.template)

    def test_reduced_transparency_uses_solid_materials(self) -> None:
        self.assertIn(
            "@media (prefers-reduced-transparency: reduce)", self.template
        )
        self.assertIn("-webkit-backdrop-filter: blur(14px)", self.template)
        self.assertIn("-webkit-backdrop-filter: blur(16px)", self.template)
        self.assertIn("backdrop-filter: none", self.template)
        self.assertIn("-webkit-backdrop-filter: none", self.template)

    def test_copy_feedback_is_interruptible_and_layout_stable(self) -> None:
        self.assertIn("#copy-epiphany .action-label", self.template)
        self.assertIn("min-inline-size: 8.5em", self.template)
        self.assertIn("let copyRequestId = 0", self.template)
        self.assertIn("window.clearTimeout(copyResetTimer)", self.template)
        self.assertIn("copyLabelAnimation?.cancel()", self.template)
        self.assertIn("const requestId = ++copyRequestId", self.template)
        self.assertIn("if (requestId !== copyRequestId) return", self.template)
        self.assertIn("{ opacity: 0.6, filter: 'blur(2px)' }", self.template)
        self.assertIn("duration: 180", self.template)
        self.assertIn("if (!reduceMotionQuery.matches)", self.template)

    def test_etymology_notes_reveal_without_layout_animation(self) -> None:
        self.assertIn(
            "document.querySelectorAll('.etymology-supplement-details')",
            self.template,
        )
        self.assertIn(
            "content.getAnimations().forEach((animation) => animation.cancel())",
            self.template,
        )
        self.assertIn("if (!details.open) return", self.template)
        self.assertIn("duration: reduced ? 120 : 180", self.template)
        self.assertIn("transform: 'translateY(-6px)'", self.template)
        reveal_script = self.template.split(
            "document.querySelectorAll('.etymology-supplement-details')", 1
        )[1].split("const sectionNav", 1)[0]
        self.assertNotRegex(reveal_script, r"\b(?:height|max-height|padding|margin)\b")

    def test_section_navigation_has_one_semantic_shared_indicator(self) -> None:
        self.assertEqual(1, self.template.count('class="section-nav-indicator"'))
        self.assertIn('aria-hidden="true"', self.template)
        self.assertEqual(
            1,
            len(
                re.findall(
                    r'<a class="section-nav-link"[^>]*aria-current="location"',
                    self.template,
                )
            ),
        )
        self.assertIn("transform 220ms var(--ease-in-out)", self.template)
        self.assertIn("width 220ms var(--ease-in-out)", self.template)
        self.assertIn("link.offsetLeft", self.template)
        self.assertIn("new ResizeObserver", self.template)
        self.assertIn(
            '.section-nav-link[aria-current="location"] {\n'
            "    background: var(--color-text-primary);",
            self.template,
        )
        self.assertIn(
            '.section-nav.has-indicator .section-nav-link[aria-current="location"]',
            self.template,
        )
        self.assertIn("sectionNav.classList.add('has-indicator')", self.template)
        self.assertIn(
            "if (sectionNav && navIndicator && initialCurrentLink)", self.template
        )
        self.assertIn("positionNavIndicator(initialCurrentLink, true)", self.template)

    def test_epiphany_reveal_is_progressive_and_one_shot(self) -> None:
        epiphany_markup = re.search(
            r'<section class="epiphany-box"[^>]*>', self.template
        )
        self.assertIsNotNone(epiphany_markup)
        self.assertNotIn("data-reveal", epiphany_markup.group(0))
        self.assertIn('.epiphany-box[data-reveal="pending"]', self.template)
        self.assertIn("transform: translateY(6px)", self.template)
        self.assertIn("opacity 240ms var(--ease-out)", self.template)
        self.assertIn(
            "epiphany.getBoundingClientRect().top > window.innerHeight * 0.9",
            self.template,
        )
        self.assertIn("window.location.hash !== '#epiphany'", self.template)
        self.assertIn("rootMargin: '0px 0px -10% 0px'", self.template)
        self.assertIn("threshold: 0.2", self.template)
        self.assertIn("observer.disconnect()", self.template)

    def test_mermaid_diagrams_do_not_upscale_small_graphs(self) -> None:
        svg_rule = re.search(
            r"\.mermaid svg\s*\{(?P<body>.*?)\}",
            self.template,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(svg_rule)
        rule_body = svg_rule.group("body")
        self.assertIn("width: auto", rule_body)
        self.assertIn("max-width: 100%", rule_body)
        self.assertNotRegex(rule_body, r"(?m)^\s*width:\s*100%")

    def test_render_is_offline_and_has_no_placeholders(self) -> None:
        self.assertIn('src="./mermaid.min.js"', self.rendered)
        self.assertNotRegex(self.rendered, r'<script[^>]+src=["\']https?://')
        self.assertNotRegex(self.rendered, r"\{\{[A-Z_]+\}\}")


class ExtremeWordCardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.template = (REPO_ROOT / "assets" / "word_card.html").read_text(
            encoding="utf-8"
        )
        cls.entries = json.loads(
            (REPO_ROOT / "examples" / "extreme-stress" / "input.json").read_text(
                encoding="utf-8"
            )
        )

    def test_extreme_words_keep_valid_structure(self) -> None:
        for entry in self.entries:
            with self.subTest(word=entry["word"]):
                rendered = render_word_cards.render_entry(self.template, entry)
                probe = DocumentProbe()
                probe.feed(rendered)

                self.assertEqual(1, probe.tags.count("main"))
                self.assertEqual(1, probe.tags.count("h1"))
                self.assertEqual(len(probe.ids), len(set(probe.ids)))
                self.assertTrue(set(probe.labelled_by).issubset(probe.ids))
                self.assertNotRegex(rendered, r"\{\{[A-Z_]+\}\}")


class WordCardIndexTests(unittest.TestCase):
    def test_index_is_an_accessible_ordered_collection(self) -> None:
        entries = [{"word": "Serendipity"}, {"word": "Lucid"}]
        outputs = [Path("word_card_serendipity.html"), Path("word_card_lucid.html")]
        document = render_word_cards.build_index(entries, outputs)
        probe = DocumentProbe()
        probe.feed(document)

        self.assertEqual(1, probe.tags.count("main"))
        self.assertEqual(1, probe.tags.count("ol"))
        self.assertEqual(0, probe.tags.count("ul"))
        self.assertEqual(
            ["word_card_serendipity.html", "word_card_lucid.html"], probe.links
        )
        self.assertIn("@media (prefers-reduced-motion: reduce)", document)
        self.assertIn("@media (hover: hover) and (pointer: fine)", document)
        self.assertIn("a:active", document)
        self.assertIn("transform: scale(0.97)", document)
        self.assertNotIn("transition-duration: 0.01ms", document)
        self.assertIn("prefers-reduced-transparency: reduce", document)
        self.assertIn("background: var(--color-paper-0)", document)


if __name__ == "__main__":
    unittest.main()
