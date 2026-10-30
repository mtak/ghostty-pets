# M4 — corgi and living backyard

- **Status:** PARTIAL — initial M4 behavior received positive user feedback; revised artwork and doze pose await Ghostty visual approval. Runtime performance remains unmeasured.
- **Branch/worktree:** `codex/m4-backyard` in `.worktrees/m4`.
- **Scope:** 14 tricolor corgi animation clips, eight ordered backyard layers, subtle tree/flower loops, periodic falling leaf and butterfly, one synchronized ball-play episode, versioned scene schema 3, and a standalone 2× review shader. M1–M3 source and artifacts remain unchanged.

## Decision log

1. [ADR-0012](adr/0012-layered-m4-scene.md) defines ordered RGBA layers and one interactive object for scene schema 3. The ball and pet share each episode phase clock, with validated connected paths and a home return. The generic compiler references asset IDs and metadata; no corgi-specific shader branch is required.
2. All animation and ambient scheduling stays input-independent under ADR-0011. Focus selects resting/wake behavior; unfocused layers stop periodic path motion when rendered. M2 cursor proximity and text-aware visibility remain a separate compositing layer.
3. The corgi sheet has 4–6 frames per clip and a fixed tricolor palette. The 110 × 45 backyard canvas contains open transparent gaps; source art remains editable PNG. The offline [scene preview](evidence/m4/source-preview.png), [animation contact sheet](evidence/m4/animation-contact-sheet.png), and [focus preview](evidence/m4/focus-preview.png) are review aids, **not Ghostty captures**.
4. The first compiled shader was 79,274 bytes and a Linux process launch with a 2 s child command took 9.02 s. Deduplicating identical pet frames reduced output to 42,065 bytes and the same launch method took 3.98 s. The revised 14-clip shader is **44,326 bytes**; its Linux launch took **5.35 s** with the same 2 s child. These wall times include Ghostty startup and child lifetime; they are not isolated shader-compile measurements. The optimization preserves all authored PNG frames.
5. M4 uses one whole-object visibility region for each environment layer and three horizontal pet regions. This prioritizes readable text but may fade a wide ground strip when only one part overlaps text. The denser scene needs manual text/TUI validation; the M2 heuristic cannot guarantee semantic text detection.
6. The user reported that the initial M4 scene looked good, animation continued during typing, text/cursor overlap faded, and focus loss selected sleep. They described the prone focus-loss pose as looking like the corgi dropped dead, the body as too long, an unclear shape in the doghouse, and the ball color as unsuitable. [ADR-0013](adr/0013-unfocused-doze-pose.md) changes unfocused panes to an upright doze selected by scene metadata. The art revision rounds and shortens the corgi, clears the doghouse opening, adds roof/wood details, and gives the ball yellow-green felt with white seams. These revisions await user review in Ghostty.

## Checks and evidence

**Local environment:** Linux, Ghostty `1.3.0-dev+0000000`, GTK/OpenGL build. EGL reported AMD device authorization failure and fallback; the actual rendering GPU was not established. macOS/Metal: **NOT TESTED**.

- `/usr/bin/python3 -m unittest discover -s tests -v`: **22 passed** after the art revision. Tests cover art regeneration and binary alpha, palette limits, all clips and layers, prone versus upright silhouettes, deterministic episode selection, ball/pet path continuity at every ball phase edge and slot boundary, ambient windows, focus behavior, invalid metadata rejection, alternate pet/scene build, packed-frame round trips after deduplication, standalone shader reproducibility, and byte-for-byte M1–M3 artifact preservation.
- `/usr/bin/python3 tools/build_m4.py --output dist/m4-corgi-backyard-2x.glsl`: deterministic **44,326-byte** standalone GLSL, below the 128 KiB M4 source budget. The previous 13-clip shader took an average of 0.0165 s across ten in-process generation runs; generation speed was not rebenchmarked after the art revision.
- Linux Ghostty loaded the deduplicated shader and the child command exited normally, with no shader-compilation failure. Mesa logged two `Shader Compiler: Other` warnings about generated temporary parameters. The same log reported EGL fallback. These warnings need observation on other drivers; successful load does not establish visual correctness.
- The source art was composited offline over dark and light backgrounds at selected timeline points. It shows the revised corgi, tree, empty doghouse opening, flowers, open grass, and tennis ball. The focus preview shows the upright doze against the focused pose. These are offline images, not runtime screenshots.
- **User-reported initial M4 visual check:** animation stayed continuous during typing; cursor and other text caused fading; loss of focus selected the prone sleep pose. The user did not provide OS, Ghostty version, screenshots, or a performance measurement for this report. The revised art and doze have not been manually validated.
- `git diff --check`: pass. The M1/M2/M3 builders and generated artifacts have no edits; tests regenerate and compare all seven previous shader files byte for byte.
- Runtime frame time, GPU utilization, battery cost, and typing latency remain **unmeasured**. The shader uses at most 12 scene layers, eight frames per clip/layer, 16 episode phases, and 20 text probes for an affected opaque fragment; transparent and out-of-scene fragments skip decoding/probing. The current art has at most about 6,300 opaque 2× fragments across simultaneously visible elements, implying a loose worst-case bound near 126,000 text probes per frame before early exits. This bound does not prove acceptable GPU cost.

## Exact Linux Ghostty visual checklist

Use the shader in this worktree, record OS, Ghostty version, backend/GPU when known, display scale, shader SHA-256, theme, and screenshots or a short clip. Add to a test config:

```ini
custom-shader = /home/mtak/dev/ghostty-pets/.worktrees/m4/dist/m4-corgi-backyard-2x.glsl
custom-shader-animation = true
```

1. At a normal terminal size, check the corgi's tall ears, short legs, rounded body, and black/tan/white patches. Confirm the doghouse opening looks empty, roof and wood detail remain legible, and the ball reads as yellow-green tennis felt with white seams. Tree, grass, and three flowers should remain visible without an opaque panel. Repeat on light and dark themes. Compare with the [offline preview](evidence/m4/source-preview.png); report palette shifts or missing layers.
2. Watch the first minute. The seed selects a left walk at startup, a ball-play episode at roughly 24 s, a right walk around 36 s, a falling leaf around 31–34 s, and a butterfly around 44–48 s. Confirm crisp integer pixels, correct horizontal orientation, subtle ambient motion, and idle/breathe/look frames between activities. Later slots include scratch, stretch, and a short nap. Unfocused panes may freeze until redrawn.
3. During the ball-play episode, check stand → approach → nudge → chase → return → sit. The ball should roll only with the interaction, remain inside the scene, and return smoothly without a position jump. Check pet and ball at the phase boundaries, especially near 26–30 s.
4. Type repeatedly during a walk with the cursor away from the scene. The pet and ball timeline should continue without resetting. Move the cursor onto the pet and scene elements; only the nearby region should fade and restore. Place plain/ANSI text, a selection, and a full-screen TUI over pet, house, tree, and ground on both themes. Check that letters remain readable and note excessive or missed fading.
5. Use two panes, switch focus mid-walk and mid-ball play, and return after 30 s and 5 min. An unfocused pane should show the upright, eyes-closed doze pose if it redraws; it may visually freeze. The scheduled short nap should still use the prone sleep pose. On refocus, check the wake transition and home rest until the next complete episode, with no ball teleport. Resize to a narrow/short pane and note where M4 hides the scene; responsive fallbacks are M5 scope.
6. Check typing, scrolling, and split-pane responsiveness for lag. If timing tools are available, measure warmed frame time, shader load, and resource use against M3 in the same setup; record the method. Remove the `custom-shader` line and reload/restart Ghostty to confirm the normal terminal returns.

## macOS checklist (runtime untested)

On macOS Ghostty/Metal, record version, Apple hardware, Retina/display scale, and shader checksum. Repeat the six Linux visual steps, with special attention to integer-pixel scaling and light/dark text-aware fading. macOS performance remains an M5 gate by the user's approved exception; no macOS M4 runtime success is inferred.

## Gate

**Verified:** editable PNG regeneration, source-geometry/palette validation, deterministic layered shader generation, synchronized ball movement in the pure timeline, prior-artifact preservation, offline art composition, and Linux shader load without a compilation failure. The user reported initial M4 typing, visibility, and focus behavior working.

**Inferred:** the bounded scene representation and deduplication reduce source/compile load. They do not establish GPU frame cost or readability in Ghostty.

**Untested:** revised artwork and doze appearance in Ghostty, detailed visual/motion checks, reliable runtime performance, and macOS behavior. The user-reported initial behavior does not establish these checks.

**Stop: awaiting human M4 visual validation and approval. M5 has not started.**
