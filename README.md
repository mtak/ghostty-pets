# Ghostty Pets 🐕

A tiny autonomous pixel-art pet living inside Ghostty, drawn by a self-contained GLSL post-processing shader.

**Status:** M1, M2, and M3 approved; M4 corgi/backyard implementation is awaiting visual approval. **First release:** a tricolor Pembroke Welsh Corgi in a cozy backyard. Supported targets: Ghostty on macOS and Linux.

## Start here

1. Read `docs/PRODUCT_SPEC.md` for what to build.
2. Read `docs/ARCHITECTURE.md` and `docs/adr/` for how and why.
3. Read `docs/DELIVERY_PLAN.md` for phased validation and acceptance gates.
4. Open Codex in this repository; `AGENTS.md` constrains how the agent should proceed.
5. Use the prompt in `CODEX_START.md`. **Do not start with the complete feature set.**

The intended end-user installation is manual: copy one prebuilt `.glsl` file to the Ghostty config directory and add the `custom-shader` setting. Python is a build-time dependency only.

## M1 proof build and preview

The current artifacts are a static silhouette for testing the rendering path, not the v1 pet. With Python 3.10+ and Pillow 12.1.1 installed from `requirements-build.txt`:

```sh
python3 tools/build_m1.py --scale 1 --output dist/m1-corgi-1x.glsl
python3 tools/build_m1.py --scale 2 --output dist/m1-corgi-2x.glsl
python3 -m unittest discover -s tests -v
```

To preview one file, add these lines to a test Ghostty config, using the **absolute path** to the chosen shader on your machine:

```ini
custom-shader = /absolute/path/to/ghostty-pets/dist/m1-corgi-2x.glsl
custom-shader-animation = true
```

Remove the `custom-shader` line and reload or restart Ghostty to disable the proof. See [M1 report](docs/M1_REPORT.md) for validation results, limitations, and the Linux/macOS test checklist. The PNG source is `assets/pets/corgi/m1-silhouette.png`; opaque colors are indexed in first-appearance order, transparent pixels use index zero, and eight four-bit indices are packed into each GLSL `uint`. This encoding is provisional until broader compiler and color tests.

## M2 visibility proof

M2 uses the same placeholder sprite and leaves the M1 artifacts byte-identical. Build the 1× or 2× conservative text-aware proof with:

```sh
python3 tools/build_m2.py --scale 2 --policy conservative --output dist/m2-corgi-2x-conservative.glsl
python3 -m unittest discover -s tests -v
```

Choose the M2 file in the `custom-shader` config line above to preview it. The `cursor-only` policy is a comparison build: `python3 tools/build_m2.py --scale 2 --policy cursor-only --output dist/m2-corgi-2x-cursor-only.glsl`. It removes text detection and is **not** an accepted replacement for text-aware protection. See the [M2 report](docs/M2_REPORT.md) for observed behavior and remaining tests.

## M3 animation prototype

M3 adds a small placeholder sprite sheet and versioned pet/environment JSON definitions. The generated 2× shader is a standalone preview of timed clips, horizontal movement, focus-aware sleep/wake, and the M2 text/cursor fading policy. Cursor input does not change the animation timeline. It is not final corgi art or the backyard.

```sh
python3 tools/build_m3.py --output dist/m3-placeholder-2x.glsl
python3 -m unittest discover -s tests -v
```

Set `custom-shader` to the absolute path of `dist/m3-placeholder-2x.glsl` and keep `custom-shader-animation = true`. Remove the line and reload/restart Ghostty to disable it. See the [M3 format](docs/M3_FORMAT.md) for editable source fields and the [M3 report](docs/M3_REPORT.md) for the manual validation checklist and current limits.

## M4 corgi and backyard preview

M4 adds editable tricolor corgi frames and a layered backyard with doghouse, tree, flowers, grass, leaf, butterfly, and a tennis ball synchronized to the pet's play episode. Unfocused panes select an upright doze pose. The 2× shader is an M4 review artifact; M5 will make the final responsive size variants.

```sh
python3 tools/make_m4_art.py
python3 tools/build_m4.py --output dist/m4-corgi-backyard-2x.glsl
python3 -m unittest discover -s tests -v
```

Preview with `custom-shader = /absolute/path/to/ghostty-pets/dist/m4-corgi-backyard-2x.glsl` and `custom-shader-animation = true`. [Source-art preview](docs/evidence/m4/source-preview.png), [focus preview](docs/evidence/m4/focus-preview.png), [animation contact sheet](docs/evidence/m4/animation-contact-sheet.png), [format](docs/M4_FORMAT.md), and [milestone report](docs/M4_REPORT.md) document what to review. Removing `custom-shader` safely disables the overlay.

## Documentation

- [`docs/PRODUCT_SPEC.md`](docs/PRODUCT_SPEC.md) — frozen product scope, functional requirements, UX and non-goals.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — shader constraints, proposed architecture, asset format and algorithms.
- [`docs/DELIVERY_PLAN.md`](docs/DELIVERY_PLAN.md) — M1–M5 milestones, test matrices, review gates and release criteria.
- [`docs/M3_FORMAT.md`](docs/M3_FORMAT.md) — versioned M3 pet/scene source format.
- [`docs/M4_FORMAT.md`](docs/M4_FORMAT.md) — M4 pet and layered backyard source format.
- [`docs/adr/`](docs/adr/) — independently reviewable architecture decisions.

## Authoritative references

- Ghostty custom shaders and their uniforms: https://ghostty.org/docs/config/reference
- Ghostty config file locations and reload behavior: https://ghostty.org/docs/config

Technical assumptions must be rechecked against the **installed Ghostty version**, not only the online docs.
