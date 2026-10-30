# M4 source format

M4 keeps pet sheet schema 1 and introduces **scene schema 3** for layered environments. The source of truth is RGBA PNG plus JSON; `tools/build_m4.py` embeds the required data into one standalone GLSL file. [ADR-0012](adr/0012-layered-m4-scene.md) records the layering and object-motion choice.

## Pet

`assets/pets/corgi/corgi-v1.json` points to `corgi-v1.png`. It uses the [M3 pet format](M3_FORMAT.md): 28 × 24 cells, named animation rows, 1–8 frame durations, loop policy, playback speed, and a ground anchor. The M4 sheet has 4–6 frames per clip for idle, breathing, look, stand, walk, play, sit, stretch, sleep, wake, scratch, happy, and blink. The generator deduplicates identical frame pixels before embedding them; the PNG still contains every editable frame.

## Environment

`assets/environments/backyard/backyard-v1.json` declares a 110 × 45 source-pixel canvas, ground and home anchors, inset, deterministic seed, episode slot length, ordered `layers`, and complete `episodes`.

Each layer has a unique `id`, a same-directory RGBA `file`, `frame_size`, positive `durations_ms`, and one `motion`:

| Motion | Required fields | Meaning |
|---|---|---|
| `static` | `position` | One frame at a fixed bottom-left source-pixel position. |
| `loop` | `position` | Multiple frames loop in place; an unfocused pane shows frame zero when rendered. |
| `path` | `from`, `to`, `period_ms`, `active_ms`, optional `phase_ms` | Appears only during a bounded window in each deterministic period, travelling between two source-pixel positions. An unfocused pane hides it. |
| `interactive` | `position` | One scene object follows the current episode's object offset. Frame selection tracks displacement, so the ball rolls only as it moves. |

Schema 3 supports at most one interactive layer and twelve total layers. Frames are horizontal cells in a sheet. All pixels must be fully transparent or opaque. The whole environment uses at most 15 opaque palette colors and 16,384 source pixels across used frames. A layer path and every episode position must stay within the canvas.

Each episode has a positive `weight` and 1–16 `phases`. A phase references a pet clip and declares duration, facing, and connected horizontal pet offsets. It may also declare `object_from_x` and `object_to_x` for the interactive layer; omitted values are zero. Both pet and object must start and finish at home and stay within bounds. The ball-play episode uses the same phase time for pet and ball, including the return path. Short episodes rest at home until their fixed slot ends.

## Build and preview

```sh
python3 tools/make_m4_art.py
python3 tools/build_m4.py --output dist/m4-corgi-backyard-2x.glsl
python3 tools/preview_m4.py
python3 -m unittest discover -s tests -v
```

The two art previews under `docs/evidence/m4/` show PNG source composited offline; they are **not Ghostty screenshots**. Use an absolute `custom-shader` path to the generated file and `custom-shader-animation = true` for runtime review. Remove the `custom-shader` line and reload/restart Ghostty to disable the project. M5 will supply the three release presets and responsive compact-pane fallback.

## Rendering and limits

The shader samples the unchanged terminal image, returns it outside the scene, and composites ordered transparent layers followed by the pet. Each opaque scene layer has its own M2-style cursor/text fade region; the pet retains three horizontal regions at its animated position. The text detector remains heuristic. The timeline is independent of typing and uses only shader time plus focus for sleep/wake. All sprite data and palettes are embedded; no runtime PNG load or helper process is used.
