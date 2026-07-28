# 007 — Glide one shared section indicator

- **Status**: DONE
- **Commit**: a830ee2
- **Implemented by**: 8bbd342
- **Severity**: LOW
- **Category**: Missed opportunity and spatial consistency
- **Estimated scope**: 2 files, about 100 lines

## Problem

Every navigation link paints its own selected background. When
`IntersectionObserver` changes `aria-current`, one pill fades out while another fades
in. The transition communicates state but not the spatial relationship between
adjacent sections.

```html
<!-- assets/word_card.html:1382 — current -->
<nav class="section-nav" aria-label="Word card sections" lang="en">
  <a class="section-nav-link" href="#meaning" aria-current="location">...</a>
  <a class="section-nav-link" href="#etymology">...</a>
  <a class="section-nav-link" href="#nuance">...</a>
  <a class="section-nav-link" href="#topology">...</a>
  <a class="section-nav-link" href="#epiphany">...</a>
</nav>
```

```javascript
/* assets/word_card.html:1651 — current */
navLinks.forEach((link) => {
  const isCurrent = link.getAttribute('href') === `#${activeEntry.target.id}`;
  if (isCurrent) {
    link.setAttribute('aria-current', 'location');
  } else {
    link.removeAttribute('aria-current');
  }
});
```

## Target

Add one decorative indicator before the links:

```html
<span class="section-nav-indicator" aria-hidden="true"></span>
```

```css
.section-nav {
  position: sticky;
  isolation: isolate;
}

.section-nav-indicator {
  position: absolute;
  z-index: -1;
  top: var(--space-2);
  left: 0;
  height: var(--control-height);
  width: 0;
  border-radius: var(--radius-pill);
  background: var(--color-text-primary);
  opacity: 0;
  pointer-events: none;
  transition:
    transform 220ms cubic-bezier(0.77, 0, 0.175, 1),
    width 220ms cubic-bezier(0.77, 0, 0.175, 1),
    opacity 120ms ease;
}

.section-nav-link {
  position: relative;
  z-index: 1;
}

.section-nav-link[aria-current="location"] {
  background: transparent;
  color: var(--color-paper-0);
}

@media (prefers-reduced-motion: reduce) {
  .section-nav-indicator {
    transition: opacity 120ms ease;
  }
}
```

Update the indicator whenever current state changes:

```javascript
const sectionNav = document.querySelector('.section-nav');
const navIndicator = document.querySelector('.section-nav-indicator');
const reduceMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

const positionNavIndicator = (link, immediate = false) => {
  if (!sectionNav || !navIndicator || !link) return;
  navIndicator.style.transitionDuration = immediate || reduceMotionQuery.matches
    ? '0ms'
    : '';
  navIndicator.style.width = `${link.offsetWidth}px`;
  navIndicator.style.transform = `translateX(${link.offsetLeft}px)`;
  navIndicator.style.opacity = '1';
  if (immediate && !reduceMotionQuery.matches) {
    requestAnimationFrame(() => {
      navIndicator.style.transitionDuration = '';
    });
  }
};
```

Call `positionNavIndicator(currentLink)` immediately after updating
`aria-current`. On initialization, call it with `immediate = true`. Use one
`ResizeObserver` to reposition the current link after responsive layout changes.

## Repo conventions to follow

- `aria-current="location"` remains the source of truth.
- The existing section observer and root margins remain unchanged.
- The indicator is decorative and must be `aria-hidden="true"`.
- Use exact existing tokens for height, spacing, radius, and colors.
- Plan 003 supplies the motion easing token; use the raw exact cubic-bezier if it has
  not been executed.

## Steps

1. Add exactly one indicator span as the first child of `.section-nav`.
2. Add indicator CSS and place links above it.
3. Remove the selected link's own opaque background while preserving selected text
   and index colors.
4. Extract the existing current-state update into a function that also positions the
   indicator.
5. Position the first current link without motion after DOM initialization.
6. Reposition after current-section changes and through one `ResizeObserver`.
7. Disable transform/width interpolation under reduced motion; retain a 120 ms
   opacity cue.
8. Add tests for one indicator, unchanged `aria-current`, and reduced-motion behavior.

## Boundaries

- Do NOT replace `aria-current` with visual-only state.
- Do NOT animate `left`; move the indicator with `transform`.
- Width interpolation is allowed only for this single small indicator. Do not animate
  widths of links or content.
- Do NOT add bounce or overshoot.
- Do NOT alter scroll targets, sticky positioning, or observer thresholds.
- If horizontal scrolling causes offset coordinates to differ in the target browser,
  STOP and use measured `link.offsetLeft`; do not guess pixel corrections.

## Verification

- **Mechanical**: run `python -m unittest discover -s tests -v`.
- **Mechanical**: validate inline JavaScript syntax.
- **Feel check**:
  - Click and scroll through all five sections; one pill must glide between items.
  - Slow playback to 10% and confirm the indicator starts from its current onscreen
    position without snapping back.
  - Resize across 900px and 640px breakpoints; the pill must realign exactly.
  - Horizontally scroll the mobile nav and confirm indicator/link alignment.
  - Enable reduced motion and confirm selection updates without traveling movement.
- **Done when**: there is always exactly one visual current indicator and it tracks
  the semantic current link across scroll and resize.
