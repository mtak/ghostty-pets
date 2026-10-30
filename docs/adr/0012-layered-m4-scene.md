# ADR-0012 — Layered PNG scene and synchronized object paths

**Status:** Accepted for the approved M4 implementation

**Context:** M3 renders one animated pet on an empty stage. M4 needs scenery, ambient motion, and a ball that moves with a complete pet episode. The standalone shader and input-independent timeline remain requirements.

**Decision:** Add a versioned scene-3 JSON manifest containing ordered RGBA PNG layers. Each layer has a fixed local frame size, position, frame durations, and one bounded motion mode: static, looping in place, periodic path, or interactive. Compile layer pixels into a separate four-bit indexed palette from the pet. One named interactive layer is supported in scene schema 3; each episode phase can declare connected horizontal offsets for it. The pet and interactive object use the same phase clock, so their paths are evaluated together and return to home at the episode boundary. Periodic leaf/butterfly paths derive solely from `iTime`. Existing M1–M3 builders and outputs remain unchanged.

**Consequences:** The M4 generator emits a larger shader and adds per-layer decoding and visibility probes. The schema bounds layer count, frame count, palette size, and source size; generation rejects invalid geometry and discontinuous object paths. Static scenery and ambient elements fade by their own bounds, while pet fading retains M2/M3 behavior. The one-interactive-object limit is explicit for v1 and may need a later schema revision for scenes with several coordinated objects. The scene remains transparent and all runtime data is embedded in GLSL.
