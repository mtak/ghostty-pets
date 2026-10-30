# ADR-0014 — Responsive release layouts

**Status:** Accepted for M5 after user choices on 2026-10-30

**Context:** M4's fixed 2× backyard disappears when a pane is too small. ADR-0003 and FR-05/FR-06 require three integer-scale presets and full scene → smaller full scene → pet-only → hidden fallback. A pet-only pane cannot show the ball that motivates a play or chase clip. There is no retained layout state in a Ghostty fragment shader.

**Decision:** Build three standalone shaders with maximum integer scales 1, 2, and 3. On each rendered frame, select the largest full-scene scale not above the preset that fits the surface with the scene inset on all sides. If no complete scene fits, select the largest fitting pet-only integer scale; display a stationary `idle` clip while focused or the scene's `unfocused_clip` while unfocused. If even the 1× pet does not fit, return the terminal pixel unchanged. The pet-only mode uses the same sprite decoder and localized visibility policy as the complete scene. Keep the episode timeline, scene composition, and M1–M4 artifacts unchanged.

**Consequences:** A resize can change the selected integer scale or layout immediately; the stateless shader cannot interpolate between prior and current sizes. The corgi may change apparent size at a full-scene to pet-only boundary because each mode independently chooses its largest fitting scale. Pet-only panes intentionally omit walking, play, scenery, and ball to keep the pose coherent. No runtime process or extra asset is required. The release will be labeled Linux-validated with macOS testing pending, as the user chose; macOS/Metal behavior remains a release gate for a full cross-platform claim.
