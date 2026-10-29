# ADR-0003 — Fixed palette, bottom-right overlay, responsive modes

**Status:** Accepted

**Context:** The scene must remain cute but never reserve terminal space.

**Decision:** Fixed natural-color pixel palette; bottom-right anchored with no container rectangle, no padding. Provide small/medium/large artifacts and responsive full-scene → reduced-scene → pet-only → hidden fallback using pixel-perfect integer scaling.

**Consequences:** An overlay may cover content; the visibility subsystem must mitigate it. HiDPI and very small panes need actual testing. Native source dimensions are provisional until M1 screenshots.
