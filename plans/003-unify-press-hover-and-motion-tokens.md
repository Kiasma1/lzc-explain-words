# 003 — Unify press, hover, and motion tokens

- **Status**: DONE
- **Commit**: a830ee2
- **Implemented by**: 8bbd342
- **Severity**: MEDIUM
- **Category**: Physicality, Performance, Accessibility, Cohesion
- **Estimated scope**: 3 files, about 90 lines

## Problem

Interactive elements use repeated `180ms ease` declarations, animate large
`box-shadow` values, expose hover states to touch devices, and have no pointer-down
press response.

```css
/* assets/word_card.html:354 — current */
.action-button {
  /* ... */
  transition: background-color 180ms ease, border-color 180ms ease,
    color 180ms ease, box-shadow 180ms ease;
}

.action-button:hover {
  border-color: var(--alpha-indigo-18);
  background: var(--alpha-indigo-06);
  color: var(--color-action);
  box-shadow: 0 8px 20px var(--alpha-ink-08);
}
```

```css
/* assets/word_card.html:420 — current */
.section-nav-link {
  /* ... */
  transition: background-color 180ms ease, color 180ms ease;
}

.section-nav-link:hover,
.section-nav-link[aria-current="location"] {
  background: var(--color-text-primary);
  color: var(--color-paper-0);
}
```

```css
/* scripts/render_word_cards.py:381 — current index CSS */
a {
  /* ... */
  box-shadow: 0 10px 28px var(--color-shadow);
  transition: border-color 180ms ease, box-shadow 180ms ease, color 180ms ease;
}

a:hover {
  border-color: var(--color-indigo-600);
  color: var(--color-indigo-700);
  box-shadow: 0 16px 34px var(--color-shadow);
}
```

## Target

Add the same motion primitives to both template roots:

```css
--duration-press: 160ms;
--duration-state: 180ms;
--ease-out: cubic-bezier(0.23, 1, 0.32, 1);
--ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);
```

Pressable controls must respond immediately and only animate compositor-friendly
movement plus lightweight state properties:

```css
.action-button,
.section-nav-link {
  transition:
    transform var(--duration-press) var(--ease-out),
    background-color var(--duration-state) ease,
    border-color var(--duration-state) ease,
    color var(--duration-state) ease;
}

.action-button:active,
.section-nav-link:active {
  transform: scale(0.97);
}

.section-nav-link[aria-current="location"] {
  background: var(--color-text-primary);
  color: var(--color-paper-0);
}

.section-nav-link[aria-current="location"] .nav-index {
  color: var(--color-indigo-100);
}

@media (hover: hover) and (pointer: fine) {
  .action-button:hover {
    border-color: var(--alpha-indigo-18);
    background: var(--alpha-indigo-06);
    color: var(--color-action);
  }

  .section-nav-link:hover {
    background: var(--color-text-primary);
    color: var(--color-paper-0);
  }

  .section-nav-link:hover .nav-index {
    color: var(--color-indigo-100);
  }
}
```

Keep the existing base shadow static; remove shadow changes from hover and transition
lists. Apply the same policy to collection links:

```css
a {
  transition:
    transform var(--duration-press) var(--ease-out),
    border-color var(--duration-state) ease,
    color var(--duration-state) ease;
}

a:active {
  transform: scale(0.97);
}

@media (hover: hover) and (pointer: fine) {
  a:hover {
    border-color: var(--color-indigo-600);
    color: var(--color-indigo-700);
  }
}
```

Use `var(--duration-state) var(--ease-in-out)` for the etymology chevron rotation and
`var(--duration-state) var(--ease-out)` for the skip-link entrance.

## Repo conventions to follow

- Primitive, semantic, and component tokens live in the single `:root` at
  `assets/word_card.html:9-107`.
- The collection index has its own `:root` inside
  `scripts/render_word_cards.py:297-316`.
- State selectors already use `aria-current` and `data-state`; do not replace them.
- The project avoids dependencies and must remain a standalone offline document.

## Steps

1. Add the four exact motion tokens to the main template root and collection-index
   root.
2. Update action-button transitions and add `:active { transform: scale(0.97); }`.
3. Separate navigation's persistent `aria-current` selectors from hover selectors.
4. Gate action, navigation, and index hover styles with
   `@media (hover: hover) and (pointer: fine)`.
5. Remove `box-shadow` from transition lists and remove the larger hover shadow;
   preserve the existing static base shadow.
6. Apply motion tokens to skip-link and chevron transform transitions.
7. Extend UI tests to assert active feedback, hover gating, token presence, and the
   absence of `box-shadow` in transition declarations.

## Boundaries

- Do NOT add bounce, keyframes, or spring libraries.
- Do NOT animate width, height, padding, margin, top, or left.
- Do NOT change persistent success/error or `aria-current` semantics.
- Do NOT remove the base shadows; only stop animating between shadow geometries.
- Do NOT apply hover-only styles outside fine-pointer media queries.

## Verification

- **Mechanical**: run `python -m unittest discover -s tests -v`.
- **Mechanical**: run `git diff --check`.
- **Feel check**:
  - On desktop, press each action, section link, and index card; confirm immediate,
    subtle `0.97` compression and a fast release.
  - In DevTools slow motion, confirm only transform and lightweight color/border
    properties interpolate.
  - Emulate touch and confirm taps do not leave stale hover styling.
  - Scroll after tapping a nav item and confirm only the actual `aria-current` item
    remains selected.
- **Done when**: all pressables respond on pointer-down, hover is pointer-appropriate,
  and no large shadow is animated.
