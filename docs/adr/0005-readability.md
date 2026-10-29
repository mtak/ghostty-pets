# ADR-0005 — Localized cursor-aware and experimental text-aware fading

**Status:** Accepted, subject to M2 feasibility gate

**Context:** Overlay scenery could obscure terminal content. Priority is readability, while preserving a recognizable little world.

**Decision:** Fade relevant scene objects/regions near the text cursor. Experiment with terminal-image heuristics to detect occupied text areas and reduce alpha. Preserve input texture outside the overlay exactly.

**Consequences:** No semantic text mask; heuristics can be wrong. If results are poor, M2 must stop for a human decision—never silently downgrade the promised UX. Mouse-hover detection is future only.
