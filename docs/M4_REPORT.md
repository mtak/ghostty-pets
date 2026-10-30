# M4 — corgi and living backyard

- **Status:** PARTIAL — source art, layered renderer, and automated checks are ready; actual Ghostty visual and runtime-performance review remain.
- **Branch/worktree:** `codex/m4-backyard` in `.worktrees/m4`.
- **Scope:** 13 tricolor corgi animation clips, eight ordered backyard layers, subtle tree/flower loops, periodic falling leaf and butterfly, one synchronized ball-play episode, versioned scene schema 3, and a standalone 2× review shader. M1–M3 source and artifacts remain unchanged.

## Decision log

1. [ADR-0012](adr/0012-layered-m4-scene.md) defines ordered RGBA layers and one interactive object for scene schema 3. The ball and pet share each episode phase clock, with validated connected paths and a home return. The generic compiler references asset IDs and metadata; no corgi-specific shader branch is required.
2. All animation and ambient scheduling stays input-independent under ADR-0011. Focus selects sleep/wake; unfocused layers stop periodic path motion when rendered. M2 cursor proximity and text-aware visibility remain a separate compositing layer.
3. The corgi sheet has 4–6 frames per clip and a fixed tricolor palette. The 110 × 45 backyard canvas contains open transparent gaps; source art remains editable PNG. The offline [scene preview](evidence/m4/source-preview.png) and [animation contact sheet](evidence/m4/animation-contact-sheet.png) are review aids, **not Ghostty captures**.
4. The first compiled shader was 79,274 bytes and a Linux process launch with a 2 s child command took 9.02 s. Deduplicating identical pet frames reduced output to **42,065 bytes** and the same launch method took **3.98 s**. These wall times include Ghostty startup and child lifetime; they are not isolated shader-compile measurements. The optimization preserves all authored PNG frames.
5. M4 uses one whole-object visibility region for each environment layer and three horizontal pet regions. This prioritizes readable text but may fade a wide ground strip when only one part overlaps text. The denser scene needs manual text/TUI validation; the M2 heuristic cannot guarantee semantic text detection.

## Checks and evidence

**Local environment:** Linux, Ghostty `1.3.0-dev+0000000`, GTK/OpenGL build. EGL reported AMD device authorization failure and fallback; the actual rendering GPU was not established. macOS/Metal: **NOT TESTED**.

- `/usr/bin/python3 -m unittest discover -s tests -v`: **22 passed**. Tests cover art regeneration and binary alpha, palette limits, all clips and layers, deterministic episode selection, ball/pet path continuity at every ball phase edge and slot boundary, ambient windows, focus behavior, invalid metadata rejection, alternate pet/scene build, packed-frame round trips after deduplication, standalone shader reproducibility, and byte-for-byte M1–M3 artifact preservation.
- `/usr/bin/python3 tools/build_m4.py --output dist/m4-corgi-backyard-2x.glsl`: deterministic **42,065-byte** standalone GLSL, below the 128 KiB M4 source budget. Ten in-process generation runs averaged **0.0165 s** on this host.
- Linux Ghostty loaded the deduplicated shader and the child command exited normally, with no shader-compilation failure. Mesa logged two `Shader Compiler: Other` warnings about generated temporary parameters. The same log reported EGL fallback. These warnings need observation on other drivers; successful load does not establish visual correctness.
- The source art was composited offline over dark and light backgrounds at selected timeline points. It shows a black/tan/white corgi, tree, house, flowers, open grass, and ball. Actual Ghostty color/blending and text overlap are **not yet observed** for M4.
- `git diff --check`: pass. The M1/M2/M3 builders and generated artifacts have no edits; tests regenerate and compare all seven previous shader files byte for byte.
- Runtime frame time, GPU utilization, battery cost, and typing latency remain **unmeasured**. The shader uses at most 12 scene layers, eight frames per clip/layer, 16 episode phases, and 20 text probes for an affected opaque fragment; transparent and out-of-scene fragments skip decoding/probing. The current art has at most about 6,300 opaque 2× fragments across simultaneously visible elements, implying a loose worst-case bound near 126,000 text probes per frame before early exits. This bound does not prove acceptable GPU cost.

## Exact Linux Ghostty visual checklist

Use the shader in this worktree, record OS, Ghostty version, backend/GPU when known, display scale, shader SHA-256, theme, and screenshots or a short clip. Add to a test config:

```ini
custom-shader = /home/mtak/dev/ghostty-pets/.worktrees/m4/dist/m4-corgi-backyard-2x.glsl
custom-shader-animation = true
```

1. At a normal terminal size, check the corgi's tall ears, short legs, long body, and black/tan/white patches; tree, doghouse, grass, three flowers, and ball should be visible without an opaque panel. Repeat on light and dark themes. Compare the scene with the [offline preview](evidence/m4/source-preview.png); report palette shifts or missing layers.
2. Watch the first minute. The seed selects a left walk at startup, a ball-play episode at roughly 24 s, a right walk around 36 s, a falling leaf around 31–34 s, and a butterfly around 44–48 s. Confirm crisp integer pixels, correct horizontal orientation, subtle ambient motion, and idle/breathe/look frames between activities. Later slots include scratch, stretch, and a short nap. Unfocused panes may freeze until redrawn.
3. During the ball-play episode, check stand → approach → nudge → chase → return → sit. The ball should roll only with the interaction, remain inside the scene, and return smoothly without a position jump. Check pet and ball at the phase boundaries, especially near 26–30 s.
4. Type repeatedly during a walk with the cursor away from the scene. The pet and ball timeline should continue without resetting. Move the cursor onto the pet and scene elements; only the nearby region should fade and restore. Place plain/ANSI text, a selection, and a full-screen TUI over pet, house, tree, and ground on both themes. Check that letters remain readable and note excessive or missed fading.
5. Use two panes, switch focus mid-walk and mid-ball play, and return after 30 s and 5 min. An unfocused pane logically selects sleep on frames it renders; it may visually freeze. On refocus, check the wake transition and home rest until the next complete episode, with no ball teleport. Resize to a narrow/short pane and note where M4 hides the scene; responsive fallbacks are M5 scope.
6. Check typing, scrolling, and split-pane responsiveness for lag. If timing tools are available, measure warmed frame time, shader load, and resource use against M3 in the same setup; record the method. Remove the `custom-shader` line and reload/restart Ghostty to confirm the normal terminal returns.

## macOS checklist (runtime untested)

On macOS Ghostty/Metal, record version, Apple hardware, Retina/display scale, and shader checksum. Repeat the six Linux visual steps, with special attention to integer-pixel scaling and light/dark text-aware fading. macOS performance remains an M5 gate by the user's approved exception; no macOS M4 runtime success is inferred.

## Gate

**Verified:** editable PNG regeneration, source-geometry/palette validation, deterministic layered shader generation, synchronized ball movement in the pure timeline, prior-artifact preservation, offline art composition, and Linux shader load without a compilation failure.

**Inferred:** the bounded scene representation and deduplication reduce source/compile load. They do not establish GPU frame cost or readability in Ghostty.

**Untested:** actual M4 Ghostty visuals and motion, M2 visibility over the expanded scene, focus redraw appearance, reliable runtime performance, and macOS behavior.

**Stop: awaiting human M4 visual validation and approval. M5 has not started.**
