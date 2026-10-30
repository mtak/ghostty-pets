# Ghostty Pets — Product specification

**Status:** frozen v1 product scope; M1–M5 approved, with macOS/Metal validation pending under a platform-limited release label.
**Design baseline:** Q1–Q22 agreed 29 October 2026.  
**Target:** Ghostty on Linux and macOS.

## 1. Vision

Create a charming, unobtrusive miniature pixel-art world rendered **inside** each Ghostty terminal surface. The first companion is a **black, tan and white tricolor Pembroke Welsh Corgi** living in a cozy backyard. The world should feel alive without competing with terminal work. Installation must be as simple as copying a single shader file and adding a Ghostty config line.

### Principles

1. **Readability first.** The terminal is a tool, the pet is decoration.
2. **Quiet personality.** Subtle micro-animations and occasional coherent interactions—not constant motion.
3. **Self-contained release.** No runtime daemon, companion application, network connection, or external textures.
4. **Editable source.** Art and animation metadata are source assets; GLSL is compiled output.
5. **Cross-platform.** The same `.glsl` release artifacts are intended for Ghostty on macOS and Linux, subject to platform testing.
6. **Composable future.** Pets and environments can eventually be mixed and matched.

## 2. Frozen decisions

| Dimension | Approved behavior |
|---|---|
| First pet | Tricolor Pembroke Welsh Corgi |
| Art | Classic handcrafted pixel art; fixed natural palette, **not** theme-aware |
| Placement | Bottom-right **overlay**, no reserved padding or separate pane |
| Environment | Cozy backyard: grassy floor, small wooden doghouse, small tree, flowers, ball |
| Environment architecture | Interchangeable environments, starting with backyard |
| Motion | Horizontal pet movement only; no 2D navigation/pathfinding |
| Behavior | Curious companion; approximately 60% relaxed and 40% playful/exploratory in normal idle/focused conditions |
| Animation | Expressive pixel frames, generally 4–8 per major animation, fewer when appropriate |
| Scenery | Occasional subtle swaying, falling leaves, butterfly, rolling ball |
| Visibility | Cursor-aware fading plus experimental text-aware protection; localized by element/region |
| Mouse hover | Desired future capability; **not v1** without supported mouse uniform |
| Sizing | Three selectable presets, responsive fallback, pixel-perfect integer scaling |
| Activity | Cursor-change-based quiet mode; calm while actively working; sleep on prolonged idle |
| Unfocused surfaces | Simulate elapsed time on return; inactive panes behave as sleeping/resting when rendered |
| Split panes | One independent pet per pane; focus governs active vs inactive presentation |
| Small panes | Full scene → reduced scene → corgi only → hidden |
| Art pipeline | PNG sprite sheets + JSON metadata → Python/Pillow generator → standalone GLSL |
| Distribution | **Manual** download/copy and Ghostty config; no installer |

**M3 amendment approved after manual feedback:** [ADR-0011](adr/0011-input-independent-behavior.md) supersedes the Activity row, FR-10, and the Quiet-mode part of FR-14 for the current v1 direction. Cursor input affects only visibility, not pet or environment behavior. Focus controls sleep/wake. The two-minute cursor-idle sleep rule and cursor-based Quiet mode are retired. The original rows below remain as design history.

## 3. V1 functional requirements

### Visual and scene

- **FR-01:** Render one tricolor corgi with recognizable tall ears, short legs, long body, expressive eyes, and characteristic waddle. Show black, tan and white fur even on dark backgrounds.
- **FR-02:** Render an open, transparent-background backyard scene containing grassy ground, doghouse, small tree, a few flowers, and a ball. **No opaque widget rectangle.**
- **FR-03:** Anchor the complete scene to the lower-right within a configurable inset (initial design target ~12 screen pixels; configurable at build time).
- **FR-04:** Use a fixed handcrafted palette on light and dark terminal themes; no automatic recoloring.
- **FR-05:** Select `small`, `medium`, or `large` via different prebuilt shader variants. Maintain crisp integer-pixel rendering (no blurred resampling).
- **FR-06:** Adapt to restricted terminal dimensions. Prefer smaller complete scene, then pet-only, then hide. Preserve legibility and avoid clipping/negative positions.

### Character behavior

- **FR-07:** Provide idle/sit, blink, look, stand, walk, lie/sleep, wake/stretch, scratch, happy, and play states with coherent transitions.
- **FR-08:** Support short, complete scripts for interacting with objects, e.g. stand → walk to ball → nudge → chase → return → sit. Never teleport the ball or pet between consecutive normal animation frames.
- **FR-09:** Derive apparent activity from deterministic time-based scheduling, not mutable long-lived state.
- **FR-10:** Prioritize low-motion animations when the terminal appears active based on available cursor/focus signals. Under longer inactivity, the corgi should settle and sleep. These signals are imperfect and cannot be treated as literal keystroke events.
- **FR-11:** On refocus, restore an appropriate current pose without trying to replay all missed animation frames; a short waking/reorientation transition is acceptable.
- **FR-12:** Each terminal surface maintains its own visible pet, bounded to its surface. Inactive surfaces should present a resting/sleeping pose on frames when they render; continuous animation while unfocused is not required.

### Environment behavior

- **FR-13:** Implement occasional low-intensity plant movement, a falling leaf, infrequent butterfly, and ball motion **only** in synchronized interaction sequences.
- **FR-14:** Reduce environmental motion in quiet mode. The backyard does not implement weather, seasons, a simulated clock, or separate environmental persistence in v1.

### Visibility and compositing

- **FR-15:** Outside the scene footprint, return the original terminal image unchanged.
- **FR-16:** Around the *terminal text cursor*, soften/hide only nearby scene elements. Prefer object-level/region-based fades rather than removing isolated sprite pixels.
- **FR-17:** Explore text-aware opacity based on `iChannel0` and `iBackgroundColor`. Readability wins over pet visibility. The detection is heuristic; visually validate with light/dark themes, ANSI colors, selection, and full-screen TUIs.
- **FR-18:** If heuristic text detection is unreliable, make the visibility strategy configurable at **build time** and report the limitation. Do not pretend an unreliable heuristic can guarantee clear text; a fallback to cursor-aware fading needs explicit human sign-off.

### Delivery

- **FR-19:** Produce three default files: `corgi-backyard-small.glsl`, `corgi-backyard-medium.glsl`, and `corgi-backyard-large.glsl`.
- **FR-20:** Each generated GLSL release file is usable by itself. No PNG, JSON, interpreter, GPU texture server, or helper service at runtime.
- **FR-21:** Document copy-and-config installation, switching presets, safe disable, and how to add new pet/environment source assets.

## 4. Visual and interaction direction

- Pixel-art baseline target: approximately **110 × 45 source pixels for the complete backyard**, yielding roughly 220 × 90 pixels at 2× (medium). Treat dimensions as a *starting art budget*, not a locked constraint. The first render proof must validate them.
- A corgi sprite might occupy about 24–28 × 20–25 source pixels at rest. Use an appropriate multiple for a recognizable profile while retaining room for scenery.
- Suggested scene x regions: tree at far left, doghouse at middle-left, ball on ground, corgi usually right of center. The corgi travels horizontally along the ground.
- Sprites use sharp edges and transparent holes; avoid alpha-blurred pixels. The background color of the user’s terminal shows through.
- Representative gestures: blink, ear flick, tail wiggle, low-slung trot/waddle, tongue flick, stretch, circle before sleeping.
- Behavior should feel **random but believable**. Avoid conspicuous periodic repetitions; maintain intentional quiet stretches.
- The scene does not react to mouse clicks and does not accept input.

## 5. Scope boundaries / explicit non-goals

Not in v1: mouse-hover hiding, click/feed/pet interactions, shell-command sensing, a local status database, day/night cycles, weather, sound, push notifications, interactive UI, terminal padding, overlay windows, install script, automatic updates, runtime plugin system, runtime image loading, realistic pathfinding, and multi-day simulated care needs.

Future pets and environments are an **architecture affordance**, not a requirement to ship extra assets in v1.

## 6. Definition of done

V1 can be considered complete **only after**:

- All five milestones in `DELIVERY_PLAN.md` are reviewed and accepted.
- Every confirmed v1 requirement is either met or an exception is explicitly documented and approved.
- At least one tested macOS Ghostty environment and one tested Linux Ghostty environment run the same generated shader, or the release is truthfully labeled platform-limited until that evidence exists.
- Compilation, startup, resizing, focus changes, split panes, light/dark themes and terminal-heavy content have been tested.
- Users can install/uninstall manually and recover from a broken shader without modifying code.
