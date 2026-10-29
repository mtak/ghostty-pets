# ADR-0004 — Deterministic timeline rather than persistent state

**Status:** Accepted

**Context:** The shader has no conventional writable application state. The corgi should still feel autonomous and respond to focus/activity.

**Decision:** Model behaviors as time-indexed deterministic episodes and use Ghostty-provided timing/focus uniforms. Use horizontal movement and synchronized object interaction scripts. Quiet and sleep modes are derived heuristically from cursor-change/focus signals.

**Consequences:** No persistent memory, no real day/night or needs simulation, and imperfect active-input detection. Sequence continuity and timestamp gaps require M3 validation.
