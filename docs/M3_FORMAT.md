# M3 source format (pet schema 1, scene schema 2)

M3 uses an RGBA PNG sprite sheet, a pet JSON manifest beside it, and an environment JSON manifest. The Python compiler reads all three at build time and emits one standalone GLSL file. The PNG is the editable art source; the generated shader is not edited by hand.

## Pet manifest

`assets/pets/corgi/m3-pet.json` is the minimal example. `sheet` is a PNG filename in the same directory. `frame_size` is the size of every sheet cell, and `anchor` is the pixel in each top-down cell placed on the environment's home/ground point. Each named clip occupies one row starting at `row`, with frames left to right. The number of `durations_ms` entries determines its frame count (1–8). `loop` selects modulo playback or a held final frame. `speed` multiplies elapsed clip time and accepts 0.1–4.0.

All frame cells share a size in version 1; clips can have different counts, durations, loop policies, and speeds. Fully transparent and fully opaque pixels are supported. The compiler creates a palette of at most 15 opaque colors in first-use order and packs four-bit indices. No PNG or palette file is needed at runtime.

## Environment manifest

`assets/environments/m3-empty.json` demonstrates a schema-2 placeholder stage with no backyard art. `canvas` is the source-pixel scene size; `home_x` and `ground_y` locate the pet anchor within it, with Y counted upward from the bottom. `inset` is a screen-pixel right/bottom margin. `seed` controls repeatable episode selection. `slot_ms` is the fixed episode period. Schema 2 rejects cursor-activity modes and thresholds.

Each `episode` has an `id`, a positive `weight`, and 1–16 ordered `phases`. A phase names a pet clip, duration, horizontal start/end offsets from home, and `left`/`right` facing. Every episode must begin and end at horizontal offset zero, and adjacent phases must meet. The validator rejects positions that leave the scene. A short episode rests at home for the unused portion of its slot. Sleeping and waking use clips named `sleep` and `wake`; an `idle` clip fills episode tails. The manifest weights make the focused pet mostly relaxed while still allowing walks and play.

The same compiler accepts a different pet PNG/manifest and scene JSON without pet-specific branches. The M3 test suite builds a second dummy pet and alternate scene. The M3 empty stage has no environment objects or art; M4 will supply the backyard and interactions.

## Build

From a checkout with Python 3.10+ and `requirements-build.txt` installed:

```sh
python3 tools/build_m3.py --pet assets/pets/corgi/m3-pet.json --scene assets/environments/m3-empty.json --scale 2 --output dist/m3-placeholder-2x.glsl
python3 -m unittest discover -s tests -v
```

The commands require `python3` to have the pinned Pillow dependency. The prototype supports integer `--scale` values 1, 2, and 3. M5 will define responsive preset selection and compact-pane fallbacks.

## Runtime and limits

The generated shader is a pure function of `iTime`, `iTimeFocus`, `iFocus`, resolution, cursor uniforms, and `iChannel0`. It selects a weighted episode using a deterministic hash of the absolute time slot. Motion uses a smoothstep horizontal path; frame selection uses explicit durations. There is no persistence, event listener, extra process, or runtime image load. Cursor changes never alter behavior or global opacity. An unfocused pane selects sleep on frames it renders. Focus gain runs a brief wake transition, then holds at home until the next complete episode can start. M2 cursor/text fading remains localized to the pet region.

Unfocused surfaces may stop redrawing. Identical surfaces can have identical schedules. Long-lived float32 shader time loses subsecond resolution eventually. The M2 text detector remains heuristic and may fade the pet on terminal graphics or miss unusual glyphs. Remove the `custom-shader` line and reload or restart Ghostty to disable the prototype.
