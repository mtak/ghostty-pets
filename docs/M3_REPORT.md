# M3 — animation and behavior engine

- **Status:** PARTIAL — implementation and automated checks pass; manual animation, focus, readability, and runtime performance validation remain.
- **Branch/worktree:** `codex/m3-animation` in `.worktrees/m3`.
- **Scope:** versioned pet/scene metadata, validated PNG sprite sheet, deterministic stateless episodes, variable animation clips, focus/activity modes, horizontal travel, preserved M2 localized visibility, and standalone GLSL. The art and empty stage are intentional M3 placeholders.

## Decision log

1. [ADR-0008](adr/0008-m3-episode-scheduling.md) records fixed-duration, hash-selected episodes with home-anchor endings. This refines ADR-0004 without changing its stateless runtime decision.
2. `quiet_ms = 10000` and `sleep_ms = 120000` are editable scene metadata. A focus gain resets the apparent activity age. Cursor-change age remains an imperfect proxy for work; it cannot observe every keypress.
3. A 0.65 s fade/recenter masks a mode switch after a cursor change or at the scheduled mode thresholds. A focus loss has no timestamp available to the shader, so an unfocused redraw may select sleep immediately. Ghostty may also stop redrawing an unfocused pane.
4. Clips define frame durations, loop policy, and playback speed. Episodes define clip references, connected horizontal paths, orientation, weights, and complete return-to-home sequences. The generic compiler contains no corgi-specific behavior branches.
5. M3 retains the M2 conservative text heuristic and cursor fading over three horizontal pet regions at the current animated position. The object remains subject to M2's known heuristic limitations. An empty environment has no other scene objects to fade.
6. Per-surface uniforms make evaluation independent, but no stable pane ID is available to seed distinct schedules. Two surfaces can select the same episode sequence.
7. The user approved deferring macOS performance testing to M5. No macOS runtime claim is made for M3.

## Automated and local evidence

**Environment:** Linux, Ghostty `1.3.0-dev+0000000`, GTK/OpenGL build. The EGL log reports AMD authorization failure and fallback; the actual rendering GPU was not established. macOS: **NOT TESTED**.

- `/usr/bin/python3 -m unittest discover -s tests -v`: **13 passed**. Coverage includes frame duration/speed/loop selection, deterministic and varied scheduling, walk orientation and position continuity, focus/cursor/time jumps, malformed metadata rejection, alternate dummy pet/scene build, and unchanged M1/M2 artifact generation.
- `/usr/bin/python3 tools/build_m3.py --output dist/m3-placeholder-2x.glsl`: generated reproducibly from PNG/JSON. Output is **16,145 bytes**, below the 128 KiB source budget. It embeds sprite pixels and palette and references no runtime asset.
- Ten in-process generation runs averaged **0.004 s** each on this Linux host. This is build time, not Ghostty shader compilation time.
- A Linux Ghostty launch with this M3 shader and `custom-shader-animation=true` exited normally and emitted **no shader compilation error**. A deliberately invalid control shader on the same Ghostty build emitted `GlslangFailed` and an explicit shader error. This supports successful M3 shader compilation, not visual correctness.
- `git diff --check`: pass. M1 and M2 builders and release shader files were not edited; the regression tests compare all six committed M1/M2 artifacts byte for byte.
- The generated shader uses bounded loops (at most 8 clip frames, 16 phases, 20 text probes per affected fragment). Fragments outside the scene return the sampled terminal pixel. GPU time, frame time, typing latency, and the 2 s compile-time target have **not been measured** reliably; a process launch includes startup and shell time.

## Manual Linux checklist (required for approval)

Use `dist/m3-placeholder-2x.glsl` from this worktree. Record OS, Ghostty version, backend/GPU when known, display scale, shader SHA-256, and a short screen recording or timestamped screenshots. Add to a test Ghostty config:

```ini
custom-shader = /home/mtak/dev/ghostty-pets/.worktrees/m3/dist/m3-placeholder-2x.glsl
custom-shader-animation = true
```

1. Start with a fresh focused terminal and no cursor movement. Observe the small pet at lower right. At approximately 10 s it begins Active mode. The seed schedules a left walk in the first Active slot, play around 34 s, right walk around 46 s, and stretch around 94 s. Confirm at least four visibly distinct animations and smooth left/right travel with the head facing the travel direction.
2. Watch a complete walk. Confirm stand → travel → look/play → return → sit, with no visible jump at phase or 12 s slot boundaries. The pixel edges should remain sharp at 2×. Repeat after resizing; an undersized pane may hide the pet in M3 because responsive fallback belongs to M5.
3. Move the text cursor repeatedly (for example, run commands and reposition it). The pet should become mostly stationary for 10 s after each change. If a walk is interrupted, note the brief fade/recenter and check that no fully visible teleport appears. Stop moving the cursor for two minutes; confirm sleeping. Typing that leaves the cursor unchanged may not reset Quiet mode.
4. Make two Ghostty panes. Put one in the background, then switch focus after 30 s and again after more than 2 min. An unfocused pane should show sleep when it renders; it may freeze until redraw. On refocus, check the brief wake/reorientation and fresh Quiet period. Check the pet stays inside its own pane.
5. Place plain and ANSI-colored text, a selection, and a TUI over the moving pet on dark and light themes. Compare with the shader disabled and with M2. Confirm cursor/text protection still fades only the pet region involved and the letters remain readable. Record false positives or misses.
6. Check normal typing, scrollback, and two-pane interaction for visible lag. If timing tools are available, capture warmed frame-time and shader load measurements; the proposed local target is 16.7 ms per frame and 2 s shader compile time. Record the method and hardware. Remove `custom-shader` and reload/restart Ghostty to confirm the normal terminal returns.

## macOS checklist (deferred to M5)

On macOS Ghostty/Metal, record version, Apple hardware, display scale, and shader SHA-256. Repeat the six Linux steps, including light/dark text overlap and split-pane focus. Measure shader load and warmed frame time where possible. This is an explicit M5 scope exception; M3 does not claim macOS validation.

## Gate

**Verified:** deterministic source compilation, metadata rejection, pure timeline tests, M1/M2 artifact preservation, and Linux Ghostty shader compilation.

**Inferred:** bounded source and loops limit shader work for this small placeholder. Actual GPU cost and visual continuity have not been established by automated evidence.

**Untested:** manual animation, split-pane focus redraw, visual M2 compatibility during motion, reliable Linux GPU/frame timing, and all macOS runtime/performance behavior.

**Stop: awaiting human M3 validation and approval. M4 has not started.**
