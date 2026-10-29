# ADR-0007 — Manual installation, prebuilt size variants

**Status:** Accepted

**Context:** Users should not need compilers, installers, services or package managers.

**Decision:** Distribute a small collection of ready-made `.glsl` shaders. Users copy a selected artifact into Ghostty's config directory and add a `custom-shader` line (and `custom-shader-animation = true`). No installer CLI.

**Consequences:** Switching pets, environments, or presets means changing a shader path. Document config locations and safe recovery from a broken shader.
