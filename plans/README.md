# Animation improvement plans

These plans were produced from a read-only audit of commit `a830ee2` and implemented
on the UI branch in commit `8bbd342`.

| Plan | Title | Severity | Status | Dependencies |
| --- | --- | --- | --- | --- |
| [001](001-bound-mermaid-readiness-polling.md) | Bound Mermaid readiness polling | MEDIUM | DONE | None |
| [002](002-preserve-feedback-with-reduced-motion.md) | Preserve feedback with reduced motion | MEDIUM | DONE | Execute after 003 |
| [003](003-unify-press-hover-and-motion-tokens.md) | Unify press, hover, and motion tokens | MEDIUM | DONE | None |
| [004](004-make-copy-feedback-interruptible.md) | Make copy feedback interruptible | MEDIUM | DONE | Prefer 003 first |
| [005](005-support-reduced-transparency.md) | Support reduced transparency | MEDIUM | DONE | None |
| [006](006-reveal-etymology-notes.md) | Reveal etymology notes without layout animation | LOW | DONE | Prefer 003 first |
| [007](007-glide-section-indicator.md) | Glide one shared section indicator | LOW | DONE | Execute after 003 and 002 |
| [008](008-reveal-epiphany-once.md) | Reveal the Epiphany once | LOW | DONE | Execute after 003 and 002 |

## Recommended execution order

1. **001** — remove the failure-path performance leak independently.
2. **003** — establish motion tokens and correct press/hover behavior used downstream.
3. **002** — apply the final reduced-motion policy to the selectors from 003.
4. **005** — complete material accessibility independently.
5. **004** — make copy feedback retargetable using the motion foundation.
6. **006** — add the lightweight disclosure reveal.
7. **007** — add the shared navigation indicator after navigation states are stable.
8. **008** — add the single decorative Epiphany reveal last.

## Execution rules

- Execute one plan at a time and run its verification before starting the next.
- Keep the generated page dependency-free and fully offline.
- Do not modify `assets/vendor/mermaid.min.js`.
- Treat the commit stamp as a drift guard. If cited source no longer matches, stop and
  refresh the plan rather than improvising.
- After implementation, update each plan's status from `TODO` to `DONE` and record the
  implementing commit.
