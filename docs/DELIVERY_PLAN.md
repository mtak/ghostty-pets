# Ghostty Pets — Milestones, tests, and approval gates

## Delivery contract

**Implement exactly one milestone at a time. Each gate requires human approval before work on the next milestone.** All tests must report platform, Ghostty version, GPU/backend where known, result and evidence. When a platform is unavailable, report `NOT TESTED`—never infer success from a generic shader validator.

## M1 — Sprite-rendering feasibility (first task)

**Status: COMPLETED and approved.** The user reports manual validation in Ghostty and approved M1. The manual test platform, Ghostty version, and screenshots were not supplied; recorded Linux evidence and the macOS checklist are in [M1_REPORT.md](M1_REPORT.md). The M1 palette shift remains documented for later review.

**Goal:** prove a small Python-generated GLSL shader can display a static PNG-derived sprite *inside* Ghostty on a real terminal screen.

**In scope:** a minimal source PNG, Python + Pillow encoder, one generated `.glsl`, Ghostty config snippet, 1×/2× pixel integrity, lower-right anchoring and transparent compositing. Art can be a rough tricolor silhouette, not final corgi artwork. A tiny unit test for reproducible output is appropriate.

**Out of scope:** complete backyard, sophisticated animations, text-aware fading, full JSON schema, user-facing CLI or installer.

**Gate acceptance:**

- [ ] A sprite created in PNG appears in Ghostty with correct palette and transparency.
- [ ] Outside sprite bounds, the terminal image remains visually unchanged.
- [ ] Position is pinned to bottom-right during resizing; no clipping in normal-sized windows.
- [ ] 1× and 2× output remain pixel-crisp; screenshot comparison documented.
- [ ] Generated output is fully standalone and deterministic.
- [ ] Source-size and compile-time findings recorded for at least one encoding approach.
- [ ] Actual macOS and Linux results recorded separately; untested platforms called out.
- [ ] Engineer reports technical risks and stops for approval.

## M2 — Smart visibility feasibility

**Goal:** show that the overlay can protect the terminal cursor area and substantially preserve text legibility.

**In scope:** object/region alpha, terminal-cursor proximity, transition smoothing, a small evidence-backed experiment detecting likely text via `iChannel0` against `iBackgroundColor`; fallback path.

**Gate acceptance:**

- [ ] Cursor proximity fades only relevant scene regions and returns smoothly when clear.
- [ ] Compare shader-on/off captures over blank terminal, colorful shell output, `vim`/Neovim or another TUI, selection, light/dark themes.
- [ ] Document false positives/negatives and acceptable usability thresholds.
- [ ] Cross-platform results reported where available.
- [ ] Explicit choice: accept text-aware strategy, improve it, or seek approval for cursor-only fallback.
- [ ] No release claims of guaranteed detection unless supported by testing.

**Stop condition:** If text protection is poor, do not proceed to full artwork; request a design decision.

## M3 — Animation and behavior engine

**Goal:** establish a reproducible, extensible timeline/animation layer with **placeholder** art.

**In scope:** versioned pet/environment manifests, validation, several frame animations, deterministic pseudorandom episodes, horizontal travel, transition sequences, quiet/activity-aware behavior, focus/refocus behavior and standalone generated GLSL.

**Gate acceptance:**

- [ ] Sprite sheet + metadata can declare variable frame counts/durations.
- [ ] Scripted walk→interaction→return has no visible position discontinuity.
- [ ] Animation is a pure function of documented timing/focus inputs.
- [ ] Fake/simulated time jumps and focus changes do not break pose lookup.
- [ ] Active shell use demonstrably reduces motion when cursor-change signal is available.
- [ ] Unfocused pane behavior confirmed on actual Ghostty frames; limitations documented.
- [ ] Validator rejects malformed frames, references, durations, palettes and layouts.
- [ ] Generated shader compiles without pathological load time.

## M4 — Corgi and living backyard

**Goal:** replace placeholders with release-quality art and coherent pet/environment interactions.

**In scope:** approved tricolor pixel art, sit/blink/look/walk/stand/stretch/scratch/sleep/wake/happy/play animations, doghouse/tree/grass/flowers/ball, modest breeze/leaf/butterfly motion, scripted ball interaction.

**Gate acceptance:**

- [ ] Corgi is recognizably tricolor and moves with a corgi-like short-legged waddle.
- [ ] Most time is calm; occasional activities are coherent rather than random frame changes.
- [ ] Ground and scenery share a consistent fixed palette with transparent background.
- [ ] Ball motion is linked to the corgi interaction; no teleport in ordinary playback.
- [ ] Quiet mode suppresses excessive environmental animation.
- [ ] New pet/environment could be added by source assets and manifests without rewriting core renderer (demonstrate with a simple dummy asset, not a second finished pet).

## M5 — Responsive layouts, performance, and release

**Goal:** package three manual-install `.glsl` variants with validated compact fallback and straightforward documentation.

**Gate acceptance:**

- [ ] Three prebuilt shader variants created and reproducible.
- [ ] Full → smaller full → pet-only → hidden transition tested in resized panes.
- [ ] Multiple split panes show independent corgis, and inactive panes settle appropriately when rendered.
- [ ] README describes manual install, safe removal, preset switching and limitations.
- [ ] No runtime dependency other than Ghostty; no installer or hidden helper process.
- [ ] macOS (including HiDPI) and Linux tested with recorded Ghostty/backend information, or release accurately labeled as partially validated.
- [ ] Terminal remains responsive during typing, scrollback, split-pane use and normal editing; comparative resource usage measured.
- [ ] Broken shader recovery documented, and build/test commands succeed from clean checkout.

## Required test matrix

| Area | Required cases |
|---|---|
| OS/backend | macOS + Metal; Linux + OpenGL where available |
| Terminal | empty prompt, large output, colored ANSI output, selection, shell prompt, full-screen editor/TUI |
| Theme | dark and light, including strong contrasting ANSI colors |
| Layout | normal window, narrow split, short split, three panes, maximize/unmaximize, resize during animation |
| Focus | active, tab/pane swap, window defocus, refocus after 30 s / 5 min (time behavior is approximate) |
| Size | small/medium/large variant, integer scaling, display DPI/scaling differences |
| Animation | every transition edge, segment boundaries, large timestamp jump, focus change mid-interaction |
| Safety | missing/broken shader, removal/reload, source validator rejection, no persistent or network side effects |

## Milestone report template

```markdown
# Mx — [title]
- Status: PASS / BLOCKED / PARTIAL
- Git commit/branch:
- Scope implemented:
- Tests run (commands, environments):
- Ghostty version and OS/backend:
- Artifacts and screenshots:
- Performance measurements:
- Accepted assumptions / disputed assumptions:
- Risks and proposed ADRs:
- Requirements not yet met:
- **Stop: awaiting human approval for next milestone.**
```

## Definition of evidence

Automated unit tests are necessary but not sufficient. Screen rendering, hover limitations, focus behavior, text opacity, GPU cost and cross-platform compatibility require actual Ghostty observation. Preserve concise screenshots or clips as evidence where useful. Any change to agreed scope should explicitly name the affected FR ID and ADR.
