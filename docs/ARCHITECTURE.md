# Ghostty Pets — Technical architecture

## 1. Deployment architecture

```
Editable PNG sprite sheets + JSON manifests
                     |
                     v
       Python + Pillow build/validation
                     |
                     v
           GLSL source templates
                     |
                     v
          One standalone .glsl file
                     |
                     v
 Ghostty Shadertoy-style custom post-processing
      iChannel0 + documented uniforms
                     |
                     v
        Pixel-art overlay in each surface
```

The build pipeline runs on a developer's machine. Only the final shader is installed by users. No runtime dependency, operating-system hook, or custom rendering extension is allowed in v1.

## 2. Verified Ghostty API contract (check against installed version)

Authoritative reference: https://ghostty.org/docs/config/reference

| Uniform | Use | Caution |
|---|---|---|
| `iChannel0` | Sample existing rendered terminal screen for compositing and tentative text detection | May contain colors/graphics, not a text mask |
| `iResolution` | Screen/pane dimensions in pixels | Test HiDPI and resizing behavior |
| `iTime` | Stateless animation clock | Does not survive Ghostty restarts |
| `iTimeDelta` | Timing diagnostics | Not required for simulation correctness; focus gaps may be large |
| `iCurrentCursor` | Cursor cell position/dimensions | Terminal cursor, **not mouse** |
| `iTimeCursorChange` | Heuristic activity signal | Not actual keyboard or shell event feed |
| `iFocus` | Surface focus behavior | Rendering may stop on unfocused surfaces |
| `iTimeFocus` | Refocus transition | Current docs define last focus-gain time |
| `iBackgroundColor` | Approximate background difference detection | May be misleading for selections and full-screen UIs |

`iMouse` is documented **unsupported**. `iDate` is documented **unsupported**. Never rely on either. Ghostty expects a Shadertoy-like `mainImage(out vec4 fragColor, in vec2 fragCoord)` function. The same GLSL source is intended to work on macOS and Linux; actual compilation is a release test, not an assumption.

Use `custom-shader-animation = true`, **not `always`** by default: the focus-sensitive mode avoids continuous redraw on inactive panes. Because unfocused surfaces do not necessarily redraw on the precise focus-change frame, the requirement to show sleeping inactive pets must be validated; make it best-effort if no last-frame update is available.

## 3. Candidate repo layout (Codex may propose small improvements)

```
ghostty-pets/
  AGENTS.md
  assets/
    pets/corgi/{manifest.json,sprites/*.png}
    environments/backyard/{manifest.json,sprites/*.png}
  src/glsl/
    compose.glsl
    sprites.glsl
    timeline.glsl
    behavior.glsl
    visibility.glsl
  tools/build.py
  tests/{test_assets.py,test_build.py,test_timelines.py,fixtures/}
  dist/{corgi-backyard-small.glsl,corgi-backyard-medium.glsl,corgi-backyard-large.glsl}
  docs/{PRODUCT_SPEC.md,ARCHITECTURE.md,DELIVERY_PLAN.md,adr/}
  pyproject.toml
  README.md
```

Generated files must carry a generator version and source-content fingerprint, not platform-specific paths or timestamps, to support reproducible builds.

## 4. Source asset and data model

**PNG:** support sprite sheets with discrete frames on a regular grid; RGBA, consistent frame size per animation, only fully transparent or fully opaque pixels in v1 unless edge behavior is explicitly approved; no automatic blurry resizing. Transparent pixels must not be rendered into the terminal background.

**JSON:** validated with a versioned schema. The following illustrates design intent, not a finalized API:

```json
{
  "schema_version": 1,
  "id": "corgi",
  "palette": ["#000000", "#ffffff", "#d99048", "#2c2528"],
  "animations": {
    "idle": {"file": "sprites/idle.png", "frame_size": [26, 23], "durations_ms": [400, 400, 150, 400]},
    "walk": {"file": "sprites/walk.png", "frame_size": [28, 23], "durations_ms": [120, 120, 120, 120]}
  },
  "anchors": {"ground": [13, 22]},
  "behaviors": ["idle", "walk", "sleep", "play"]
}
```

Likewise an environment manifest declares a logical canvas, static placement of doghouse/tree/grass, a ground baseline, object anchor points for interactions, and optional ambient animations. Keep pet behavior separate from environmental layout so future combinations are realistic. Validate object names and shared anchors at build time.

### Build-time sprite encoding (prototype, don't prematurely commit)

A likely approach is a compact indexed-color bitmap stored as GLSL integer constants plus a palette lookup. Transparent = palette index 0; decode only pixels falling inside the active sprite. A small palette may be sufficient but **don't fix 4-bit encoding until M1 measures fidelity, shader source size, shader compilation, and cross-platform compatibility**. Evaluate 4-bit packing versus 8-bit indexing; favor portable GLSL with modest bounded loops and predictable compiler behavior. Other encodings may be approved via ADR.

Required build validations: frames align to sheet geometry, durations are positive, transparent pixels are preserved, every referenced state exists, palette limits are respected, sprites fit their logical bounding boxes, and output generation is deterministic.

## 5. Rendering and layering

For each fragment:

1. Sample `iChannel0` to obtain the unmodified terminal pixel.
2. Test whether it lies inside the responsive scene/pet bounding box; return sampled terminal pixel immediately if outside.
3. Derive apparent behavior and animation time from `iTime`, `iFocus`, `iTimeCursorChange`, and `iTimeFocus`.
4. Decode the relevant pixel-art sprite(s) and composite in a stable order: scenery/background objects → ground/flowers → interactive objects → corgi → foreground accents.
5. Calculate visibility alpha using cursor proximity and (if validated) local screen-occupancy detection.
6. Composite the scene pixel with the original terminal pixel; **never alter keyboard/mouse input or resize the actual terminal grid**.

Object-level fading is favored over pixel-by-pixel holes. For instance, sample representative underlying pixels in an object's bounding region, estimate text occupancy, and reduce that object's alpha. If text occupies only a few pixels, preserve readability while avoiding a cutout/swiss-cheese appearance. Calibration must cover antialiased glyphs and ANSI coloring. Prefer a conservative fade over false confidence.

**Important:** Neither background-difference heuristics nor cursor proximity can guarantee text protection in arbitrary TUIs, images, selections, or terminal gradients. Keep the protection policy honest and documented. Compare screenshots with shader disabled/enabled.

## 6. Stateless behavior scheduler

A pure function maps `(time, focus, activity heuristic, scene seed)` → `(behavior segment, within-segment phase, x position, animation frame, object positions)`.

- Use deterministic seeded pseudorandom selection across bounded segments.
- Build complete motion episodes (start/finish at defined home/anchor poses) so adjacent segments don't pop or teleport.
- Every object interaction is directed by the same timeline as the corgi; the ball does not independently roll.
- Keep horizontally constrained x-motion and fixed ground y.
- No dependence on `iFrame`, mutable buffers, `iTimeDelta` integration, or retained state.
- For larger `iTime` discontinuities and refocus, evaluate the current time directly, with optional short reorientation/wake animation from `iTimeFocus`.
- Quiet mode and sleep are overlays on the candidate schedule, with clean transitions where practicable. Cursor-change is just an approximate activity signal.
- Frequencies and timeout thresholds belong in source metadata/build-time constants, not hard-coded all over shader code.

Potential weakness: irregularly shaped activity segments may not join perfectly without state. **M3 must test deterministic transitions under simulated timestamp jumps before accepting this design.**

## 7. Adaptive sizing and positioning

The first candidate logical canvas is ~110×45 art pixels. Build variants propose integer scales 1×, 2× and 3× (approximately 110×45, 220×90, 330×135 screen pixels). These are starting points, not fixed UX sizes: revise based on M1 screenshots. Responsive mode selects the largest integer scale that fits the current surface (not exceeding the selected preset). If a whole scene cannot fit with margin, render a corgi-only layout; if even that is impractical, return the terminal image unmodified. The exact dimension thresholds should be chosen with screenshot evidence, then recorded in metadata/tests.

Anchor with a right and bottom inset; calculate bounds using actual `iResolution` and test the shader's coordinate origin. On HiDPI, **screen pixels are not necessarily desktop logical points**. Validate on Retina/macOS and scaled Linux displays.

## 8. Compatibility and performance

- GLSL must compile through Ghostty's macOS Metal-backed and Linux OpenGL-backed custom shader paths; don't assume a local generic GLSL validator alone is sufficient.
- Test small/narrow split panes, rapid resize, focus changes, large/small font sizes, and shader chains.
- Avoid rendering/decoding entire sprite atlases at every pixel; early-out outside the overlay.
- Instrument build time, generated GLSL size, Ghostty shader compile time, runtime FPS/latency when possible, and relative CPU/GPU/battery impact.
- If the performance or rendering trade-off is unacceptable, stop and propose a revised ADR before changing technical approach.

## 9. Manual installation contract

Place `corgi-backyard-medium.glsl` under `$HOME/.config/ghostty/shaders/` and add to the active Ghostty configuration file:

```ini
custom-shader = shaders/corgi-backyard-medium.glsl
custom-shader-animation = true
```

Ghostty's config may be `~/.config/ghostty/config.ghostty` or `config`; macOS also supports the Application Support config location. Use relative paths from the actual config file or an absolute path if resolution differs. Restore the terminal by commenting out the `custom-shader` line and reloading/restarting Ghostty if a generated shader misbehaves.

References: https://ghostty.org/docs/config and https://ghostty.org/docs/config/reference
