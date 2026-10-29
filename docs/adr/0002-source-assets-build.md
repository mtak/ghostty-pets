# ADR-0002 — PNG/JSON source assets and Python compiler

**Status:** Accepted

**Context:** Hand-writing complex sprite frames in GLSL would make future pets difficult to maintain.

**Decision:** Keep RGBA PNG sprite sheets and JSON animations/environment metadata as editable sources. Use a Python + Pillow offline build to produce deterministic, self-contained GLSL. Encoding details remain open until M1 measurements.

**Consequences:** Developer tooling is required but end users install only GLSL. The schema must be validated and versioned. New combinations are built, not selected dynamically at runtime.
