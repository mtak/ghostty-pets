# ADR-0006 — Independent per-pane pets and focus-aware rendering

**Status:** Accepted, with Ghostty focus-redraw verification pending

**Context:** The user wants a corgi in each pane but inactive panes calm and battery cost low.

**Decision:** Use per-surface shader inputs, `iFocus`, `iTimeFocus` and `custom-shader-animation = true`, not `always`. The inactive pet's logical pose is resting/sleeping, computed when the surface renders; on refocus update from elapsed time with optional wake transition.

**Consequences:** Since unfocused surfaces may stop rendering, the pet may visually freeze in its last rendered frame until a redraw occurs; verify this in M3 and M5. A guaranteed immediate sleep-state frame must not be claimed without tests.
