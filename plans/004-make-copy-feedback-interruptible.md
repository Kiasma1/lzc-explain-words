# 004 — Make copy feedback interruptible

- **Status**: DONE
- **Commit**: a830ee2
- **Implemented by**: 8bbd342
- **Severity**: MEDIUM
- **Category**: Interruptibility and state feedback
- **Estimated scope**: 2 files, about 70 lines

## Problem

Every copy click creates a new reset timer. Rapid clicks allow an older timer to reset
a newer success state early. The label also changes from “Copy Epiphany” to a shorter
string instantly, changing the flex layout and moving the neighboring button.

```javascript
/* assets/word_card.html:1607 — current */
if (copyButton && copyButtonLabel && epiphanyText) {
  copyButton.addEventListener('click', async () => {
    const text = epiphanyText.textContent.trim();
    let copied = false;
    /* clipboard work */
    copyButton.dataset.state = copied ? 'success' : 'error';
    copyButtonLabel.textContent = copied ? 'Copied' : 'Copy failed';

    window.setTimeout(() => {
      copyButton.dataset.state = 'idle';
      copyButtonLabel.textContent = 'Copy Epiphany';
    }, 1800);
  });
}
```

## Target

Reserve the label footprint, make repeated invocations retargetable, and use a subtle
state materialization that does not delay the result.

```css
#copy-epiphany .action-label {
  min-inline-size: 8.5em;
  text-align: center;
}
```

```javascript
let copyRequestId = 0;
let copyResetTimer = 0;
let copyLabelAnimation = null;
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

const setCopyState = (state, label, message) => {
  window.clearTimeout(copyResetTimer);
  copyLabelAnimation?.cancel();

  copyButton.dataset.state = state;
  copyButtonLabel.textContent = label;
  copyStatus.textContent = message;

  if (!reduceMotion.matches) {
    copyLabelAnimation = copyButtonLabel.animate(
      [
        { opacity: 0.6, filter: 'blur(2px)' },
        { opacity: 1, filter: 'blur(0)' }
      ],
      {
        duration: 180,
        easing: 'ease',
        fill: 'both'
      }
    );
  }
};
```

At the beginning of each click, capture `const requestId = ++copyRequestId;`. After
the asynchronous clipboard operation, return without updating UI when
`requestId !== copyRequestId`. After showing the latest result:

```javascript
copyResetTimer = window.setTimeout(() => {
  setCopyState('idle', 'Copy Epiphany', '');
}, 1800);
```

`setCopyState()` must avoid scheduling a new timer itself, so resetting to idle does
not recurse.

## Repo conventions to follow

- Success/error color states already use `data-state` at
  `assets/word_card.html:380-390`; retain them.
- Screen-reader feedback uses `#copy-status[role="status"]`; update it immediately.
- Keep the Clipboard API plus `document.execCommand('copy')` fallback.
- Use WAAPI for the programmatic crossfade; do not add an animation library.

## Steps

1. Add the copy-label minimum inline size without affecting the Print / Save label.
2. Add one request-generation counter, one reset-timer handle, and one WAAPI animation
   handle next to the existing copy variables.
3. Extract state updates into `setCopyState()` using the exact 180 ms opacity/2px blur
   transition above.
4. Ignore stale asynchronous clipboard completions.
5. Clear and replace the reset timer on each current result.
6. Under reduced motion, skip WAAPI but still update colors, text, and the live region.
7. Add tests for the timer clearing, request id, fixed footprint, and reduced-motion
   branch.

## Boundaries

- Do NOT disable the button while copying; input must stay interruptible.
- Do NOT delay live-region or visible result text until an exit animation finishes.
- Do NOT animate width or use an auto-width transition.
- Keep blur at exactly 2px and duration at 180 ms.
- Do NOT change clipboard behavior or message wording except clearing the idle status.

## Verification

- **Mechanical**: run `python -m unittest discover -s tests -v`.
- **Mechanical**: validate the inline script with Node's `new Function(...)` syntax
  check used during the UI refactor.
- **Feel check**:
  - Click Copy repeatedly and confirm the newest state always owns the full 1800 ms.
  - Confirm Print / Save never shifts horizontally when the copy label changes.
  - Slow playback to 10% and confirm the label materializes as one state, not two
    readable strings overlapping.
  - Enable reduced motion and confirm the label changes immediately without blur.
- **Done when**: repeated copy actions retarget cleanly, stale results cannot win, and
  the action row never jumps.
