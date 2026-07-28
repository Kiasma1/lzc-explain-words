# 005 — Support reduced transparency

- **Status**: DONE
- **Commit**: a830ee2
- **Implemented by**: 8bbd342
- **Severity**: MEDIUM
- **Category**: Accessibility and materials
- **Estimated scope**: 3 files, about 35 lines

## Problem

The hero and sticky navigation use translucent surfaces with 14–16px backdrop blur,
but there is no `prefers-reduced-transparency` fallback.

```css
/* assets/word_card.html:201 — current */
.hero {
  background: var(--surface);
  backdrop-filter: blur(14px);
}

/* assets/word_card.html:399 — current */
.section-nav {
  background: var(--nav-bg);
  backdrop-filter: blur(16px);
}
```

The collection header also uses a translucent surface:

```css
/* scripts/render_word_cards.py:334 — current index CSS */
header {
  background: var(--color-surface-translucent);
}
```

## Target

Add an explicit solid-material fallback near the existing accessibility queries:

```css
@media (prefers-reduced-transparency: reduce) {
  :root {
    --color-surface-translucent: var(--color-paper-0);
    --color-surface-muted: var(--color-paper-0);
    --nav-bg: var(--color-paper-0);
  }

  .hero,
  .section-nav {
    backdrop-filter: none;
    -webkit-backdrop-filter: none;
  }
}
```

Add the equivalent index fallback:

```css
@media (prefers-reduced-transparency: reduce) {
  header {
    background: var(--color-paper-0);
  }
}
```

Also add `-webkit-backdrop-filter` next to each normal `backdrop-filter` declaration so
Safari uses the intended material when transparency is allowed.

## Repo conventions to follow

- Accessibility media queries live after responsive rules and before print rules in
  `assets/word_card.html`.
- Use existing paper and surface tokens; introduce no new colors.
- The index remains self-contained in `build_index()`.
- Tests already inspect accessibility query presence in `tests/test_word_card_ui.py`.

## Steps

1. Add the prefixed normal backdrop-filter declarations for hero and section nav.
2. Add the exact reduced-transparency block to the main template.
3. Add the solid header fallback to collection-index CSS.
4. Extend tests to require the media query and verify both backdrop-filter properties
   are disabled within it.

## Boundaries

- Do NOT remove transparency for users who have not requested it.
- Do NOT change blur radii, shadows, borders, or palette.
- Do NOT use JavaScript feature detection.
- Do NOT add a translucent layer on top of another translucent layer.

## Verification

- **Mechanical**: run `python -m unittest discover -s tests -v`.
- **Mechanical**: render one word card and a multi-word collection.
- **Feel check**:
  - Toggle reduced transparency in a supporting browser/OS.
  - Confirm hero and sticky nav become solid without losing text contrast.
  - Scroll content beneath the nav and confirm no content shows through.
  - Confirm normal mode retains the current light glass material.
- **Done when**: both generated surfaces provide solid, legible materials when reduced
  transparency is requested.
