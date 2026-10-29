# M1 — static sprite rendering proof

- **Status:** APPROVED. Linux sprite feasibility passed; macOS remains NOT TESTED. The user additionally reports manual validation in Ghostty; platform, version, and screenshots for that validation were not supplied.
- **Branch:** `codex/m1-sprite-proof` (commit recorded when report is finalized).
- **Scope:** one editable 32 × 24 RGBA placeholder PNG, a Python/Pillow compiler, two standalone GLSL proofs (1× and 2×), and offline tests. No behavior, backyard, visibility detection, runtime service, or installer.

## Decision log

1. The user approved two generated scale artifacts and Git initialization. The original design documents are the initial `main` commit; M1 work is on `codex/m1-sprite-proof`.
2. M1 uses a provisional four-bit indexed encoding: index zero is transparent; at most 15 opaque RGB colors; eight indices per GLSL `uint`. Colors are assigned in first-appearance order. This is a measurement choice, not a final asset format or M2/M3 commitment.
3. The test config uses an absolute shader path because relative `custom-shader` resolution was not verified. Removing that line disables the proof.
4. Linux X11 captures showed that fragment Y increases upward from the bottom edge. The shader anchors Y to the bottom inset and reverses PNG row order.

## Verification evidence

**Environment:** Linux, Ghostty `1.3.0-dev+0000000`, GTK/OpenGL build, X11 backend under an available Wayland session. The EGL log reports AMD device authorization failure and a fallback path; the exact active GPU/driver was not determined. Ghostty was launched with isolated `/tmp` configs, leaving the user's config untouched.

**Automated:** `python3 -m unittest discover -s tests -v` passed all three checks. They cover committed artifact equivalence to generator output, exact nibble round trip for every source pixel, and rejection of partial alpha. Rebuilding both artifacts produced byte-identical files. `git diff --check` passed.

**Ghostty render:** The 1× and 2× shaders loaded without a shader compilation error in the process log. The paired X11 window captures below show the sprite at the lower right. Against an equally sized shader-off capture, automated comparison of each 200 × 120 crop found **zero changed pixels outside the sprite rectangle**, **zero changed transparent pixels**, **zero nonuniform integer-scale blocks**, and **zero differences between corresponding 1× and 2× source pixels**. Both shader files are 3,517 bytes; the PNG is 363 bytes.

| Capture | Evidence |
|---|---|
| Shader off | [Linux baseline](evidence/m1/linux-shader-off-bottom-right.png) |
| 1× | [Linux 1×](evidence/m1/linux-1x-bottom-right.png) |
| 2× | [Linux 2×](evidence/m1/linux-2x-bottom-right.png) |
| 2× on white background | [Linux light theme](evidence/m1/linux-2x-light-bottom-right.png) |
| 2× after resizing from 10,240 × 2,836 to 3,072 × 1,876 window pixels | [Linux resized](evidence/m1/linux-2x-resized-bottom-right.png) |

The settled resized crop is byte-identical to the pre-resize 2× crop. An immediate capture during the resize was blank while Ghostty redrew; only the settled frame supports the position finding. The window manager would not resize this test window below 3,072 × 1,876, so ordinary small-window and split-pane behavior remains untested.

**Load time:** A single measured 2× launch reached a visible window at 0.65 s and a visible sprite at 0.666 s. This is an end-to-end startup observation on this machine, **not** isolated shader compile time. Ghostty did not expose a compile duration in the captured log. The compact 3.5 KiB shader produced no observed compile error or abnormal startup pause in this run.

**Color observation:** The tricolor silhouette is visually recognizable on dark and white backgrounds, though the white fur has low contrast on white. Captured RGB does not equal PNG RGB under this Linux Ghostty blending setup (for example, source tan `#d58b46` appeared as `#ecc38f`). Ghostty's documented `alpha-blending` defaults differ between Linux and macOS. Exact displayed RGB across platforms is therefore **not verified** and may need a deliberate color-space policy before final art. No automatic color compensation was added in M1.

## Platform test checklist

Use the same generated files on both systems. Record OS version, Ghostty version, backend/GPU where known, display scale, artifact checksum, result, and screenshots. Mark unavailable cases **NOT TESTED**.

### Linux — performed and remaining

1. Install the build dependency from `requirements-build.txt`; run both build commands and the unit tests in the README. **PASS** on this machine with Pillow 12.1.1.
2. In a temporary Ghostty config, set `custom-shader` to the absolute 1× path and `custom-shader-animation = true`. Open a blank prompt on a dark theme; capture the lower-right area. Repeat with the 2× path. **PASS** with X11-backed Ghostty captures.
3. Disable the shader in an otherwise equal window, capture the same area, and compare outside and inside the sprite rectangle, including transparent holes. **PASS** for the captured blank background; text-overlap cases remain untested and belong to M2.
4. Resize narrower and shorter, wait for the redraw, and verify the inset and complete sprite. **PASS** for 10,240 × 2,836 → 3,072 × 1,876; smaller windows **NOT TESTED** because this window manager refused them.
5. Repeat on a light theme and a scaled Linux display; inspect color and crispness. White-background light theme **PASS** for visible silhouette and crispness, with low white-fur contrast; scaled display **NOT TESTED**.
6. Remove `custom-shader`, reload or restart Ghostty, and verify the ordinary terminal returns. An isolated shader-off window was captured; live config removal/reload is **NOT TESTED**.

### macOS — NOT TESTED; exact human procedure

1. Record macOS version, Ghostty version, GPU/Metal backend, Retina scale, and checksum of each M1 `.glsl` file. Use the same files as Linux.
2. Put `custom-shader = /absolute/path/to/m1-corgi-1x.glsl` and `custom-shader-animation = true` in a temporary Ghostty config. Check which config file is actually active; Ghostty can load both XDG and Application Support locations, with later values overriding earlier ones.
3. Open a blank dark-theme terminal. Confirm the 1× sprite appears at the bottom right with a 12-render-pixel inset and transparent holes. Capture a screenshot and inspect the Ghostty log for shader compile errors.
4. Repeat with the 2× shader. Confirm each source pixel occupies a uniform 2 × 2 block and that the sprite stays complete after resizing narrower, shorter, and back. Repeat on a Retina display if available.
5. Switch to a light theme and check that black, tan, and white remain distinct; note any RGB/color-space difference from the PNG and Linux captures.
6. Remove the `custom-shader` line and reload with **Cmd+Shift+,** or restart. Confirm Ghostty returns to normal. If the shader obscures the window, remove the line from the config file outside Ghostty and restart.

## Limits and gate

- **Verified:** Linux X11/GTK/OpenGL rendering at 1× and 2×, transparent pass-through on a blank background, dark and white backgrounds, lower-right anchoring in two large window sizes, reproducible output, and standalone shader loading.
- **Inferred:** the small source and bounded lookup should avoid major shader compilation costs; the startup observation supports this on one machine but does not quantify GPU use or isolate compile time.
- **Untested:** macOS/Metal, small panes, HiDPI/scaled displays, exact cross-platform RGB, text legibility under the sprite, live config reload, and real GPU cost. These do not imply M2 work has begun.
- **Accepted for M1:** the observed tricolor palette passed the feasibility gate. Exact displayed RGB and a cross-platform color-space policy remain open for later review.

**Gate: M1 approved by the user. M2 requires its own implementation plan and approval before code changes.**
