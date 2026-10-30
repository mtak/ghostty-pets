"""Build the three standalone, responsive Ghostty Pets release shaders."""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

if __package__:
    from .build_m4 import DEFAULT_PET, DEFAULT_SCENE, SHADER, _definitions
    from .m3_model import load_pet
    from .m4_model import load_scene
else:
    from build_m4 import DEFAULT_PET, DEFAULT_SCENE, SHADER, _definitions
    from m3_model import load_pet
    from m4_model import load_scene


ROOT = Path(__file__).resolve().parents[1]
PRESETS = {"small": 1, "medium": 2, "large": 3}
SHADER_CORE, MAIN_MARKER, _ = SHADER.partition("void mainImage(")
if not MAIN_MARKER:
    raise RuntimeError("M4 shader core has no mainImage boundary")


RESPONSIVE_MAIN = r"""void mainImage(out vec4 fragColor, in vec2 fragCoord) {
    vec2 uv = (floor(fragCoord) + vec2(0.5)) / iResolution.xy;
    vec4 terminal = texture(iChannel0, uv);
    fragColor = terminal;
    ivec2 resolution = ivec2(floor(iResolution.xy));
    ivec2 screenPx = ivec2(floor(fragCoord));

    // Complete scene has priority. A preset is an upper bound, not a fixed scale.
    int scale = 0;
    bool full = false;
    for (int candidate = M4_SCALE; candidate >= 1; candidate--) {
        if (resolution.x >= M4_SCENE_WIDTH * candidate + 2 * M4_INSET &&
            resolution.y >= M4_SCENE_HEIGHT * candidate + 2 * M4_INSET) {
            scale = candidate;
            full = true;
            break;
        }
    }
    if (!full) {
        for (int candidate = M4_SCALE; candidate >= 1; candidate--) {
            if (resolution.x >= M4_PET_WIDTH * candidate + 2 * M4_INSET &&
                resolution.y >= M4_PET_HEIGHT * candidate + 2 * M4_INSET) {
                scale = candidate;
                break;
            }
        }
    }
    if (scale == 0) return;

    ivec2 layoutSize = (full ? ivec2(M4_SCENE_WIDTH, M4_SCENE_HEIGHT)
                             : ivec2(M4_PET_WIDTH, M4_PET_HEIGHT)) * scale;
    ivec2 layoutOrigin = ivec2(resolution.x - M4_INSET - layoutSize.x, M4_INSET);
    if (screenPx.x < layoutOrigin.x || screenPx.y < layoutOrigin.y ||
        screenPx.x >= layoutOrigin.x + layoutSize.x ||
        screenPx.y >= layoutOrigin.y + layoutSize.y) return;

    int clip, flip;
    float clipMs, petX, objectX, petFade;
    if (full) {
        m4Pose(clip, clipMs, petX, flip, objectX, petFade);
        // Preserve M4's ordered, transparent environment and localized visibility.
        for (int layer = 0; layer < M4_LAYER_COUNT; layer++) {
            vec2 position;
            float frameMs;
            bool visible;
            m4LayerState(layer, objectX, position, frameMs, visible);
            if (!visible) continue;
            ivec2 origin = layoutOrigin + ivec2(round(position)) * scale;
            ivec2 local = screenPx - origin;
            if (local.x < 0 || local.y < 0 ||
                local.x >= M4_LAYER_WIDTH[layer] * scale ||
                local.y >= M4_LAYER_HEIGHT[layer] * scale) continue;
            ivec2 pixel = local / scale;
            int frame = m4EnvFrame(layer, frameMs);
            int linear = M4_ENV_FRAME_START[frame] +
                         (M4_LAYER_HEIGHT[layer] - 1 - pixel.y) * M4_LAYER_WIDTH[layer] + pixel.x;
            uint word = M4_ENV_DATA[linear / 8];
            uint index = (word >> uint(4 * (linear % 8))) & 15u;
            if (index == 0u) continue;
            vec4 region = vec4(float(origin.x), float(origin.y),
                               float(origin.x + M4_LAYER_WIDTH[layer] * scale),
                               float(origin.y + M4_LAYER_HEIGHT[layer] * scale));
            float opacity = m4Opacity(region, 1.0);
            fragColor = mix(fragColor, vec4(M4_ENV_PALETTE[int(index)], terminal.a), opacity);
        }
    } else {
        // The ball and scene are absent: no unpaired walk or play activity.
        clip = iFocus == 0 ? M4_UNFOCUSED : M4_IDLE;
        clipMs = iTime * 1000.0;
        petX = 0.0;
        objectX = 0.0;
        flip = 0;
        petFade = 1.0;
    }

    int frame = m4PetFrame(clip, clipMs);
    ivec2 petOrigin = layoutOrigin;
    if (full) {
        int petOriginX = M4_HOME_X + int(round(petX)) - M4_PET_ANCHOR_X;
        int petOriginY = M4_GROUND_Y - (M4_PET_HEIGHT - 1 - M4_PET_ANCHOR_Y);
        petOrigin += ivec2(petOriginX, petOriginY) * scale;
    }
    ivec2 petLocal = screenPx - petOrigin;
    if (petLocal.x < 0 || petLocal.y < 0 ||
        petLocal.x >= M4_PET_WIDTH * scale || petLocal.y >= M4_PET_HEIGHT * scale) return;
    ivec2 petPixel = petLocal / scale;
    int sourceX = flip == 1 ? M4_PET_WIDTH - 1 - petPixel.x : petPixel.x;
    int linear = M4_PET_FRAME_START[frame] +
                 (M4_PET_HEIGHT - 1 - petPixel.y) * M4_PET_WIDTH + sourceX;
    uint word = M4_PET_DATA[linear / 8];
    uint index = (word >> uint(4 * (linear % 8))) & 15u;
    if (index == 0u) return;
    int first = M4_PET_WIDTH / 3;
    int second = (M4_PET_WIDTH * 2) / 3;
    int left = petPixel.x < first ? 0 : (petPixel.x < second ? first : second);
    int right = petPixel.x < first ? first : (petPixel.x < second ? second : M4_PET_WIDTH);
    vec4 region = vec4(float(petOrigin.x + left * scale), float(petOrigin.y),
                       float(petOrigin.x + right * scale),
                       float(petOrigin.y + M4_PET_HEIGHT * scale));
    float opacity = m4Opacity(region, petFade);
    fragColor = mix(fragColor, vec4(M4_PET_PALETTE[int(index)], terminal.a), opacity);
}
"""


def generate(pet_path: Path, scene_path: Path, max_scale: int) -> str:
    if max_scale not in PRESETS.values():
        raise ValueError("max_scale must be 1, 2 or 3")
    pet = load_pet(pet_path)
    scene = load_scene(scene_path, pet)
    fingerprint = hashlib.sha256(
        pet_path.read_bytes() + pet.sheet.read_bytes() + scene_path.read_bytes()
        + b"".join(layer.file.read_bytes() for layer in scene.layers)
    ).hexdigest()
    header = ("// SPDX-License-Identifier: GPL-3.0-or-later\n"
              f"// Ghostty Pets M5 responsive release v1\n"
              f"// Source SHA-256: {fingerprint}; pet: {pet.name}; scene: {scene.name}; max scale: {max_scale}x\n")
    shader = header + _definitions(pet, scene, max_scale) + "\n" + SHADER_CORE + RESPONSIVE_MAIN
    if len(shader.encode("utf-8")) > 128 * 1024:
        raise ValueError("generated shader exceeds 128 KiB release budget")
    return shader


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pet", type=Path, default=DEFAULT_PET)
    parser.add_argument("--scene", type=Path, default=DEFAULT_SCENE)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    parser.add_argument("--output-prefix", default="corgi-backyard",
                        help="safe filename prefix for an alternate pet/environment combination")
    args = parser.parse_args()
    if re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.output_prefix) is None:
        parser.error("--output-prefix must contain lowercase letters, digits and single hyphens")
    shaders = {preset: generate(args.pet, args.scene, max_scale)
               for preset, max_scale in PRESETS.items()}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for preset, shader in shaders.items():
        output = args.output_dir / f"{args.output_prefix}-{preset}.glsl"
        output.write_text(shader, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
