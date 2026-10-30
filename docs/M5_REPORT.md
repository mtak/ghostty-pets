# M5 — responsive layouts, performance, and release candidate

- **Status:** APPROVED — the user reported “All works very well. Approved” on 2026-10-30 after receiving the M5 Ghostty checklist. The release remains platform-limited: the user's test platform and itemized measurements were not supplied, and macOS/Metal remains pending by the approved release-label choice.
- **Branch/worktree:** `codex/m5-release` in `.worktrees/m5`.
- **Scope:** three standalone 1×/2×/3× capped shaders, complete-scene → smaller complete-scene → stationary pet-only → hidden layout, manual install/recovery guide, and reproducible checks. M1–M4 builders, art, and generated artifacts remain unchanged.

## Decision log

1. [ADR-0014](adr/0014-responsive-release-layout.md) implements the previously accepted responsive hierarchy from ADR-0003. Each preset sets a maximum integer scale. The shader tries every complete-scene scale first, then pet-only scales. Source dimensions and the scene's 12 px inset determine fit; no platform-specific pixel threshold is hard-coded.
2. The user selected stationary idle/doze for pet-only panes. The new branch uses the same decoded pet frames and M2 localized visibility, but omits the backyard, ball, and walking/play episodes so no action lacks its object.
3. The user chose to label macOS testing pending rather than make a macOS result a prerequisite for the Linux release candidate. The same GLSL is intended for macOS, but Metal compilation, HiDPI layout, readability, and performance are **NOT TESTED** here.
4. M5 imports M4's validated data definition and shared shader functions. The approved M4 proof output is byte-identical; the release builder owns only responsive layout and the pet-only branch. Source-content fingerprints and a generator version identify output without checkout paths or timestamps.
5. After receiving the exact M5 checklist, the user reported that everything worked very well and approved the milestone. This is human acceptance of the release candidate, not a detailed measurement or a separately recorded macOS result.

## Checks and measured evidence

**Local environment:** Linux; Ghostty `1.3.0-dev+0000000`, GTK/OpenGL build; AMD Radeon 680M device present, but Mesa/EGL reported `amdgpu_get_auth` failure and fallback, so the actual rendering GPU was not established. 1920 × 1200 desktop at about 60 Hz. macOS/Metal: **NOT TESTED**.

- `/usr/bin/python3 tools/build_m5.py`: generated `corgi-backyard-small.glsl`, `-medium.glsl`, and `-large.glsl`, **45,610 bytes each** after adding a GPL-3.0-or-later SPDX notice, under the 128 KiB source budget. Each contains all art and timeline data, `mainImage`, the source SHA-256, and no runtime asset path.
- `/usr/bin/python3 -m unittest discover -s tests -v`: **28 passed**. New cases cover exact fit thresholds, every mode's bounds and margins across a grid of sizes, scale caps, hidden fallback, byte-for-byte release generation, path-independent output, unsafe output-prefix rejection, and unchanged M4 artifact. Existing M1–M4 tests cover earlier output preservation, metadata validation, timeline, sprite encoding, and visibility builder output.
- Three fresh Ghostty process launches with isolated default config and a two-second child each exited `0` with no fatal shader compilation failure: small **3.84 s**, medium **3.74 s**, large **3.77 s** wall time. Mesa emitted the same two `Shader Compiler: Other` generated-parameter warnings seen with M4. These wall times include Ghostty startup and child lifetime; they are not isolated compile times.
- After the publication pass added an SPDX license comment to each generated shader, all three files again loaded in local Linux Ghostty without fatal shader compilation failure. The [README screenshot](evidence/release/ghostty-pets-medium-linux.png) is an actual medium-shader Ghostty capture with only scripted sample text; [capture details](evidence/release/CAPTURE.md) record its checksum and environment. Existing M1/M2 evidence crops and the new screenshot were reviewed for private content; none showed user files, account names, hostnames, or credentials.
- A **single** six-second-child comparison in the same session gave the following process totals (Ghostty startup and child lifetime included). This is a regression sample, **not** a reliable warmed GPU frame-time or battery benchmark:

  | Shader | User CPU | System CPU | Wall time | Peak RSS |
  |---|---:|---:|---:|---:|
  | None | 2.46 s | 0.25 s | 6.60 s | 305,032 KiB |
  | M4 fixed 2× | 15.59 s | 0.78 s | 7.92 s | 327,844 KiB |
  | M5 medium | 15.63 s | 0.87 s | 7.73 s | 328,688 KiB |

  M5 medium was close to M4 in this one constrained run. The high shader-on CPU totals and EGL fallback prevent a claim of acceptable hardware GPU cost. Rendering FPS, frame latency, typing latency, battery use, and three-pane resource impact are **unmeasured**.
- `git diff --check`: pass. After candidate commit `68f31ff`, a temporary clean checkout made with `git archive HEAD` ran all **28 tests** and rebuilt all three release shaders **byte for byte** against the committed files. This used the host's installed Python/Pillow; a fresh virtualenv dependency install was not separately tested.

## Exact Linux Ghostty visual checklist

Use the release shader from this worktree first; record Ghostty version (`ghostty --version`), OS/session/backend/GPU, theme, display scaling, selected preset, shader SHA-256 (`sha256sum`), and screenshots or a short recording. Add to an isolated Ghostty config:

```ini
custom-shader = /home/mtak/dev/ghostty-pets/.worktrees/m5/dist/corgi-backyard-medium.glsl
custom-shader-animation = true
```

1. **Presets and resizing:** Show each of small, medium, and large at a normal window size. Confirm crisp 1×/2×/3× integer pixels and bottom-right inset. With medium, shrink the pane until the full scene changes 2× → 1×, then to a stationary pet only, then to no pet. Grow it back through all modes. With large, also confirm 3× → 2× → 1×. The mathematical full-scene minimum surface sizes are 134 × 69, 244 × 114, and 354 × 159 physical pixels; pet-only minimum is 52 × 48. The usable terminal surface, not outer window chrome, determines the boundary. Check no clipping, negative positions, blurry resizing, or opaque panel.
2. **Terminal content and visibility:** Compare shader on/off over an empty prompt, large scrolling output, colored ANSI text, selected text, and a full-screen editor/TUI. On light and dark themes, move the terminal cursor onto the pet and scene elements. Only nearby regions should fade and restore smoothly; letters must remain readable. Note false fades and missed text. Repeat in the 1× full scene and pet-only mode.
3. **Behavior and panes:** Type during walking and ball play in a full scene. The activity and ball path must continue without input reset. Create three split panes; each should show a bounded pet. Focus changes should select the upright doze in inactive panes **when Ghostty redraws them**. Refocus mid-walk and mid-ball play, and after about 30 seconds and five minutes; verify wake/home rest and no pet/ball teleport. Pet-only should show stationary idle while focused and doze while unfocused, with no ball or stray scenery.
4. **Responsiveness:** Resize rapidly during animation, maximize/unmaximize, type normally, scroll, and use a full-screen editor with one and three panes. Check for stutter, delayed input, or failure to redraw. If hardware metrics are available, collect warmed 60-second measurements for shader-off, M4 fixed 2×, and M5 medium at the same pane geometry and theme; repeat with three panes. Record CPU, GPU/frame-time or FPS, memory, monitor refresh rate, measurement tool, and exact Ghostty/backend. Any material regression or typing lag blocks an unqualified performance claim.
5. **Install and recovery:** Copy one release file outside the repo, switch to another preset by changing its absolute path, reload, then remove the `custom-shader` line and reload/restart. Confirm plain Ghostty rendering returns. If safe, test a nonexistent path in an isolated config and confirm the documented removal path works.

## macOS/Metal checklist — NOT TESTED

On a macOS Ghostty build, record the version, Apple hardware, Metal backend, Retina scale, monitor resolution, shader SHA-256, theme, and config file location. Install **the same** release artifacts and repeat all five Linux steps. In particular, compare physical-pixel integer scaling on Retina and non-Retina displays, verify each responsive boundary, test three panes and focus redraw, and measure warmed shader-off/M4/M5 resource use. Report failures separately from Linux. After the Linux visual gate passes, label the project **Linux-validated candidate; macOS testing pending** until these macOS checks are done.

## Gate

**Verified:** reproducible standalone release artifacts; bounded layout reference tests; existing source validation and prior-artifact preservation; local Linux Ghostty shader load without fatal compilation failure; a single environment-specific M4/M5 CPU/RSS comparison. The user approved M5 after reporting success in Ghostty.

**Inferred:** dynamic layout selection should use little extra GPU work because it checks at most three scales before the same M4 decoder; this is not established by frame-time data. The pure Python layout model and GLSL are intentionally parallel implementations, so actual responsive transitions require Ghostty observation.

**Not independently measured or itemized:** responsive screenshots, pet-only and split-pane observations, hardware GPU frame cost, typing latency, and a fresh dependency install. macOS/Metal/HiDPI behavior is **NOT TESTED**.

**M5 approved. The v1 artifacts are platform-limited until macOS/Metal testing is recorded.**
