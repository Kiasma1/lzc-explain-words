# 001 — Bound Mermaid readiness polling

- **Status**: DONE
- **Commit**: a830ee2
- **Implemented by**: 8bbd342
- **Severity**: MEDIUM
- **Category**: Performance
- **Estimated scope**: 2 files, about 30 lines

## Problem

The generated readiness helper polls every animation frame until Mermaid creates an
SVG. Its independent four-second fallback marks the page ready but does not stop the
poll. If Mermaid fails, the page keeps scheduling work for the lifetime of the tab.

```javascript
/* scripts/render_word_cards.py:74 — current */
def inject_ready_script(document: str) -> str:
    marker = "data-card-ready"
    if marker in document:
        return document
    snippet = """<script>
  (function waitForCardReady() {
    const ready = () => {
      if (document.querySelector('.mermaid svg')) {
        document.body.setAttribute('data-card-ready', '1');
      } else {
        requestAnimationFrame(ready);
      }
    };
    const fallback = () => document.body.setAttribute('data-card-ready', '1');
    window.addEventListener('load', () => {
      setTimeout(ready, 250);
      setTimeout(fallback, 4000);
    });
  })();
</script>
</body>"""
```

## Target

Keep the existing readiness contract and timings, but make completion idempotent and
cancel the outstanding frame as soon as either Mermaid succeeds or the fallback fires.

```javascript
(function waitForCardReady() {
  let frameId = 0;
  let finished = false;

  const finish = () => {
    if (finished) return;
    finished = true;
    if (frameId) cancelAnimationFrame(frameId);
    document.body.setAttribute('data-card-ready', '1');
  };

  const ready = () => {
    if (finished) return;
    if (document.querySelector('.mermaid svg')) {
      finish();
    } else {
      frameId = requestAnimationFrame(ready);
    }
  };

  window.addEventListener('load', () => {
    setTimeout(ready, 250);
    setTimeout(finish, 4000);
  }, { once: true });
})();
```

## Repo conventions to follow

- Keep the helper dependency-free and inline because generated cards must remain
  offline.
- Preserve `data-card-ready="1"` because `scripts/record_showcase.py` and the
  extreme-stress capture workflow use it as the readiness signal.
- Tests use the standard-library `unittest` framework; extend
  `tests/test_word_card_ui.py` or `tests/test_run_extreme_stress_test.py`.

## Steps

1. In `scripts/render_word_cards.py`, replace only the script inside
   `inject_ready_script()` with the bounded implementation above.
2. Preserve the 250 ms first check and 4000 ms fallback.
3. Add a regression test that renders an entry and asserts the injected script
   contains `cancelAnimationFrame`, an idempotent completion flag, and a one-time load
   listener.
4. Do not change Mermaid initialization or screenshot tooling.

## Boundaries

- Do NOT replace `requestAnimationFrame` with a new dependency.
- Do NOT change `data-card-ready`, the 250 ms delay, or the 4000 ms deadline.
- Do NOT edit `assets/vendor/mermaid.min.js`.
- If capture code no longer waits on `data-card-ready`, STOP and report the drift.

## Verification

- **Mechanical**: run `python -m unittest discover -s tests -v`; all tests must pass.
- **Mechanical**: run `python -m py_compile scripts/render_word_cards.py`.
- **Feel check**:
  - Render the showcase normally and confirm the page becomes ready after Mermaid.
  - Temporarily block the Mermaid asset in DevTools, wait more than four seconds, and
    confirm the page still becomes ready.
  - In the Performance panel, confirm no continuing frame callback appears after the
    fallback.
- **Done when**: both success and failure paths stop polling after setting
  `data-card-ready="1"`.
