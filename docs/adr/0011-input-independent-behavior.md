# ADR-0011 — Input-independent behavior timeline

**Status:** Accepted for M3 after user validation feedback

**Context:** Cursor-change-driven Quiet mode still changed the animation on the first keypress after an Active episode. Removing frame-clock resets did not solve the visible behavior reset. Ghostty provides only the latest cursor-change timestamp, so a stateless shader cannot reliably preserve an interrupted episode while also immediately changing modes on input.

**Decision:** Supersede the cursor-driven behavior portions of ADR-0004, ADR-0008, and ADR-0010 for M3. Select focused behavior episodes from an absolute time-indexed deterministic timeline. Cursor changes have no effect on episode, clip, frame, position, or global opacity. Retain the accepted M2 cursor-proximity and text-aware visibility fading. Focus still selects sleep while unfocused and a short wake transition on refocus. After refocus, rest at home until the next episode boundary to avoid entering a partly completed walk.

**Consequences:** Typing cannot reset an animation or cause a global behavior fade. The cursor-based Quiet mode and two-minute inactivity sleep are removed; this is the user's explicit M3/v1 scope change to FR-10 and the activity row of the product specification. The pet remains mostly relaxed through weighted complete episodes and sleeps when its pane is unfocused. Focus loss can still change pose immediately on a rendered frame because Ghostty exposes no focus-loss timestamp. The same input-independent timeline remains deterministic and requires no runtime state.
