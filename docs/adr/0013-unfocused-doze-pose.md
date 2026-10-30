# ADR-0013 — Upright doze for unfocused panes

**Status:** Accepted for M4 after user visual feedback

**Context:** The first M4 shader immediately selected the prone `sleep` clip when a pane lost focus. The user confirmed focus sleep worked but said the change looked like the corgi dropped dead. Ghostty exposes the last focus-gain time, not a focus-loss timestamp, so a stateless shader cannot time a sit-down transition at the loss event.

**Decision:** Add a scene-selected `unfocused_clip` and an upright, eyes-closed `doze` clip to the corgi sheet. On an unfocused frame, render that in-place resting pose at home. Keep the prone `sleep` clip for complete scheduled nap episodes and retain the M3 wake/refocus logic. The clip name is validated metadata, not a corgi-specific shader branch.

**Consequences:** Focus loss still changes pose immediately on a rendered frame, and an inactive surface may freeze before redrawing. The silhouette change is smaller and reads as resting. Scene schema 3 gains one required clip reference; the source remains PNG/JSON and the runtime remains stateless.
