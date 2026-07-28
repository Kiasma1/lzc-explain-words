# 008 — Reveal the Epiphany once

- **Status**: DONE
- **Commit**: a830ee2
- **Implemented by**: 8bbd342
- **Severity**: LOW
- **Category**: Missed opportunity and delight
- **Estimated scope**: 2 files, about 60 lines

## Problem

The Epiphany is the narrative climax of the card, but it appears exactly like every
other section. This is a rare, high-emotion moment where one restrained entrance can
reinforce hierarchy.

```html
<!-- assets/word_card.html:1449 — current -->
<section class="epiphany-box" id="epiphany" aria-labelledby="epiphany-title">
  <h2 class="epiphany-label" id="epiphany-title">Epiphany · 一语道破</h2>
  <blockquote class="epiphany-text">{{EPIPHANY}}</blockquote>
</section>
```

```css
/* assets/word_card.html:1068 — current */
.epiphany-box {
  position: relative;
  overflow: hidden;
  padding: var(--space-10) var(--space-8);
  /* no reveal state */
}
```

## Target

Progressive enhancement must keep content visible when JavaScript, observers, or
motion are unavailable. Only a box confirmed to be below the initial viewport becomes
pending.

```css
.epiphany-box[data-reveal="pending"] {
  opacity: 0;
  transform: translateY(6px);
}

.epiphany-box[data-reveal="revealed"] {
  opacity: 1;
  transform: translateY(0);
  transition:
    opacity 240ms cubic-bezier(0.23, 1, 0.32, 1),
    transform 240ms cubic-bezier(0.23, 1, 0.32, 1);
}

@media (prefers-reduced-motion: reduce) {
  .epiphany-box[data-reveal] {
    opacity: 1;
    transform: none;
    transition: none;
  }
}
```

```javascript
const epiphany = document.querySelector('.epiphany-box');
const reduceMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

if (
  epiphany
  && 'IntersectionObserver' in window
  && !reduceMotionQuery.matches
  && epiphany.getBoundingClientRect().top > window.innerHeight * 0.9
) {
  epiphany.dataset.reveal = 'pending';
  const epiphanyObserver = new IntersectionObserver((entries, observer) => {
    const entry = entries.find((item) => item.isIntersecting);
    if (!entry) return;
    epiphany.dataset.reveal = 'revealed';
    observer.disconnect();
  }, {
    rootMargin: '0px 0px -10% 0px',
    threshold: 0.2
  });
  epiphanyObserver.observe(epiphany);
}
```

If the page loads at `#epiphany`, the box begins inside the initial viewport and must
remain visible without an entrance.

## Repo conventions to follow

- Reuse native `IntersectionObserver`, already used for section navigation.
- Use the strong ease-out from Plan 003:
  `cubic-bezier(0.23, 1, 0.32, 1)`.
- The movement is exactly 6px, duration exactly 240 ms, with no bounce.
- State uses `data-reveal`, matching existing `data-state` conventions.

## Steps

1. Add pending/revealed CSS states to the Epiphany block.
2. Add the reduced-motion override that leaves the content immediately visible.
3. Add progressive-enhancement JavaScript after navigation observer setup.
4. Only mark the block pending when it begins below 90% of the viewport height.
5. Reveal on 20% intersection with a bottom root margin of `-10%`.
6. Disconnect the observer after the first reveal.
7. Add tests for exact timing, distance, one-shot disconnect, direct-anchor safety,
   and reduced-motion visibility.

## Boundaries

- Do NOT hide the Epiphany by default in CSS.
- Do NOT animate on direct anchor navigation or when it is initially visible.
- Do NOT replay the animation when scrolling away and back.
- Do NOT add blur, scale, bounce, parallax, or background motion.
- Do NOT change Epiphany typography or content.

## Verification

- **Mechanical**: run `python -m unittest discover -s tests -v`.
- **Mechanical**: validate inline JavaScript syntax.
- **Feel check**:
  - Load at the page top and scroll to Epiphany; confirm one calm 240 ms arrival.
  - Scroll away and back; confirm it never replays.
  - Load with `#epiphany`; confirm content is visible immediately with no flash.
  - Slow playback to 10% and confirm the box moves only 6px with no overshoot.
  - Enable reduced motion and confirm it is always visible with no transform.
- **Done when**: the climax receives one restrained reveal without delaying access or
  replaying.
