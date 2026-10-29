# ADR-0009 — Steady opacity during cursor changes

**Status:** Accepted for M3 after user validation feedback

**Context:** The cursor-change timestamp updates on routine keypresses that move the terminal cursor. ADR-0008's 0.65-second fade/recenter ran after every such change, making the pet repeatedly flicker while typing. Ghostty exposes the latest cursor-change timestamp but not the previous timestamp or a semantic input event, so a stateless shader cannot know whether a change interrupted a walk.

**Decision:** Supersede the cursor-change fade/recenter policy in ADR-0008. A cursor change immediately selects the Quiet home pose at full scene opacity, still subject to M2 cursor/text visibility fading. Preserve the brief fade around the scheduled Active→Sleeping boundary and the focus-gain wake fade. The Quiet→Active boundary starts at home and needs no global fade.

**Consequences:** Routine typing no longer triggers a global pet fade. An input change during a walk may produce a visible recenter. The user explicitly accepted that tradeoff. M2's localized cursor-proximity fading remains active when the cursor actually approaches the pet. No new runtime state or input API is introduced.
