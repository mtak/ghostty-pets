# M5 release candidate — installation and validation

The three standalone shaders are [small](../dist/corgi-backyard-small.glsl), [medium](../dist/corgi-backyard-medium.glsl), and [large](../dist/corgi-backyard-large.glsl). They contain the pet, backyard, animation, and visibility data; Ghostty needs no Python, PNG, JSON, service, installer, or network connection at runtime. **The user approved M5 after reporting that it works well in Ghostty; the test platform and detailed measurements were not supplied. Linux shader loading was checked locally. macOS/Metal remains untested.** See the [M5 report](M5_REPORT.md) for the evidence limits.

## Choose a size

| File | Maximum integer scale | Full-scene minimum surface size (physical pixels) |
|---|---:|---:|
| `corgi-backyard-small.glsl` | 1× | 134 × 69 |
| `corgi-backyard-medium.glsl` | 2× | 244 × 114 |
| `corgi-backyard-large.glsl` | 3× | 354 × 159 |

Medium is the starting choice. Each shader first tries the largest complete backyard that fits, up to its maximum. If the complete scene cannot fit even at 1×, it shows a stationary idle corgi, or an upright doze when unfocused, at the largest fitting integer scale. It hides entirely if the 1× pet cannot fit with the 12 px inset (52 × 48 surface pixels). The shader uses `iResolution` pixels, which may differ from logical points on HiDPI displays. A resize can switch mode or size immediately.

## Manual install

1. Download or copy **one** `.glsl` file from `dist/` into a directory you control, such as `~/.config/ghostty/shaders/` on Linux or a `shaders` directory beside the Ghostty config on macOS. Keep the file extension `.glsl`.
2. Open your existing Ghostty config, or create `~/.config/ghostty/config.ghostty` on Linux. On macOS, Ghostty also reads `~/Library/Application Support/com.mitchellh.ghostty/config.ghostty`; an existing macOS file can override an XDG config. Older Ghostty versions may use the filename `config`.
3. Add **one** `custom-shader` line with the **absolute path** to the copied file, plus animation:

   ```ini
   custom-shader = /absolute/path/to/corgi-backyard-medium.glsl
   custom-shader-animation = true
   ```

   Quote the value if its path contains spaces, for example `custom-shader = "/Users/you/Library/Application Support/com.mitchellh.ghostty/shaders/corgi-backyard-medium.glsl"`.
4. Reload Ghostty (`Ctrl+Shift+,` on Linux, `Cmd+Shift+,` on macOS) or restart it. Choose another preset by copying that file and changing the path in the single `custom-shader` line. Keep `custom-shader-animation = true`: Ghostty animates focused surfaces but normally stops continuous redraw for unfocused surfaces.

If another `custom-shader` line is already present, Ghostty chains shaders in listed order. Its output may affect the pet's text-detection heuristic. Test this combination before relying on readability.

## Disable and recover

Delete the `custom-shader` line, or comment it out by placing `#` at the start of that line, then reload/restart Ghostty. If a bad shader makes the Ghostty window unreadable, edit the config with another terminal or text editor and remove that line. Removing the line restores normal Ghostty rendering; no project process or stored state remains. Ghostty may ignore a shader that fails compilation and log the error rather than show it as a config error, so check the Ghostty log if the pet does not appear.

## Build from editable source

Python 3.10+ and the pinned `Pillow==12.1.1` in `requirements-build.txt` are needed **only by builders**. From a clean checkout:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-build.txt
.venv/bin/python tools/build_m5.py --output-dir dist
.venv/bin/python -m unittest discover -s tests -v
```

The corgi sheet and backyard layers remain editable RGBA PNGs with JSON metadata described in [M3 format](M3_FORMAT.md) and [M4 format](M4_FORMAT.md). For another pet/scene combination, provide both manifests and a safe output prefix; the generic compiler validates names, dimensions, palette, and movement paths:

```sh
python3 tools/build_m5.py --pet /path/to/pet.json --scene /path/to/scene.json --output-prefix new-pet-scene --output-dir dist
```

The source paths are build inputs only. Generated GLSL files are release artifacts, not hand-edited source.

The project-authored source, artwork, documentation, and generated release shaders are distributed under [GNU GPL version 3 or later](../LICENSE). Each M5 release shader embeds the `GPL-3.0-or-later` SPDX identifier so the license remains clear when the single file is copied elsewhere.

## Known limitations

- Text protection estimates occupancy from terminal image colors. It can miss text or fade scenery unnecessarily, especially with selections, ANSI colors, graphics, or a chained shader. It is not a semantic text mask.
- Cursor proximity uses the terminal text cursor, not mouse hover. Typing does not reset the activity timeline.
- An unfocused pane may keep its last drawn frame until Ghostty redraws it. When it does redraw, the pet-only and full-scene modes select an upright doze pose.
- Very small panes hide the scene. Large and small presets are caps; they can automatically fall back to a smaller integer scale.
- macOS/Metal appearance and performance are pending. Linux shader loading in a constrained EGL-fallback session does not establish responsive visual behavior or frame cost on a hardware GPU.

Ghostty's [configuration guide](https://ghostty.org/docs/config) documents config locations and reload keys; its [option reference](https://ghostty.org/docs/config/reference) documents custom shader paths, uniforms, chaining, animation, and recovery.
