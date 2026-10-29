# ADR-0001 — Shader-only end-user runtime

**Status:** Accepted

**Context:** The user wants the pet literally inside a Ghostty terminal, as an overlay, with no pane/padding and no separate app.

**Decision:** Use Ghostty's custom GLSL post-processing interface. Publish complete standalone shader files with no helper process, network dependency, plugin API, or native overlay.

**Consequences:** Portable deployment and no input hooks; no real mouse hover, file IO, shell-event integration, or persisted pet state. Revisit only if the product scope changes explicitly.
