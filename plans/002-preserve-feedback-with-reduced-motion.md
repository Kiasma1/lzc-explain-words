# 002 — Preserve feedback with reduced motion

- **Status**: DONE
- **Commit**: a830ee2
- **Implemented by**: 8bbd342
- **Severity**: MEDIUM
- **Category**: Accessibility
- **Estimated scope**: 3 files, about 45 lines

## Problem

Both generated surfaces globally reduce every transition to `0.01ms`. This correctly
removes movement, but it also removes color and opacity changes that communicate
copy success, errors, hover/focus, and the current section.

```css
/* assets/word_card.html:1257 — current */
@media (prefers-reduced-motion: reduce) {
  html {
    scroll-behavior: auto;
  }

  *,
  *::before,
  *::after {
    scroll-behavior: auto !important;
    transition-duration: 0.01ms !important;
    transition-delay: 0ms !important;
  }
}
```

```css
/* scripts/render_word_cards.py:446 — current index CSS */
@media (prefers-reduced-motion: reduce) {
  * {
    transition-duration: 0.01ms !important;
  }
}
```

## Target

Remove position and rotation motion while retaining short state feedback. If Plan 003
has already introduced motion tokens, use those tokens; otherwise use the exact values
below.

```css
@media (prefers-reduced-motion: reduce) {
  html {
    scroll-behavior: auto;
  }

  .skip-link,
  .section-nav-link,
  .action-button,
  .etymology-supplement-toggle::after {
    transform: none !important;
  }

  .skip-link,
  .etymology-supplement-toggle::after {
    transition: none;
  }

  .action-button,
  .section-nav-link {
    transition-property: background-color, border-color, color, opacity;
    transition-duration: 180ms;
    transition-timing-function: ease;
  }
}
```

The collection index should retain its color and border feedback:

```css
@media (prefers-reduced-motion: reduce) {
  a {
    transform: none !important;
    transition: border-color 180ms ease, color 180ms ease, opacity 180ms ease;
  }
}
```

## Repo conventions to follow

- The existing main template keeps all accessibility media queries near
  `assets/word_card.html:1257`.
- The collection index is an inline template inside
  `scripts/render_word_cards.py:290-465`; do not create a separate stylesheet.
- `tests/test_word_card_ui.py:91-95` already verifies the presence of reduced-motion
  handling; strengthen that test instead of creating another parser.

## Steps

1. Replace the universal reduced-motion transition override in
   `assets/word_card.html` with component-scoped rules.
2. Explicitly disable smooth scrolling, translation, scaling, and chevron rotation.
3. Preserve 180 ms color/opacity transitions for action and navigation state.
4. Apply the equivalent policy to the generated collection index.
5. Add tests that reject universal `transition-duration: 0.01ms` rules and confirm
   color feedback remains declared.

## Boundaries

- Do NOT remove `prefers-reduced-motion` support.
- Do NOT retain transform movement under reduced motion.
- Do NOT hide focus outlines or live-region feedback.
- Do NOT add JavaScript media-query listeners for behavior CSS can express.
- If Plan 003 changed selector names, adapt only the selector references; preserve
  the policy and exact timings.

## Verification

- **Mechanical**: run `python -m unittest discover -s tests -v`.
- **Mechanical**: render both showcase and extreme-stress inputs.
- **Feel check**:
  - Enable reduced motion in DevTools Rendering.
  - Activate section links and confirm scrolling is instant.
  - Copy the Epiphany and confirm success/error color feedback remains legible.
  - Open etymology notes and confirm the chevron changes orientation without rotating.
- **Done when**: reduced-motion users see no positional motion but retain clear,
  short state feedback.
